"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     app/core/inbody_db.py
ROLE:     인바디 시스템 SQLite DB 관리
VERSION:  SnapQ TOEIC V3 — 2026.04.30
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE:
    from app.core.inbody_db import init_db, get_conn

    init_db()  # 앱 시작 시 1회 호출
    conn = get_conn()
    # ... SQL 실행
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESIGN:
    학습 진단(인바디) 전용 DB. IRB 연구 데이터와 분리.
    학생 본인의 진단 표시 용도 — 미니 동의서로 처리.

    빠른 클릭 응답 = SQLite 1차 저장
    안전한 백업    = 5분 주기 + 세션 종료 시 Sheets 푸시
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TABLES:
    1. students     — 학생 + 동의 상태
    2. sessions     — 접속 세션 (시작/종료/시간)
    3. responses    — 문제 응답 (★ 카테고리별 정답률 핵심)
    4. word_prison  — 단어 포로 (오답 단어 누적 추적)
    5. sync_queue   — Sheets 동기화 대기열
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SAFETY:
    Streamlit Cloud는 파일 시스템이 일시적이라
    .db 파일이 컨테이너 재시작 시 사라질 수 있음.
    → 5분 주기로 Sheets에 백업, 컨테이너 시작 시 복원.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# ─────────────────────────────────────────────────────────────
# 경로 설정
# ─────────────────────────────────────────────────────────────
BASE = Path(__file__).parent.parent.parent
DB_DIR = BASE / "data"
DB_PATH = DB_DIR / "inbody.db"


# ─────────────────────────────────────────────────────────────
# 스키마 정의
# ─────────────────────────────────────────────────────────────
SCHEMA = {
    # ─────────────────────────────────────────────────────────
    # 1. 학생 테이블
    # ─────────────────────────────────────────────────────────
    "students": """
        CREATE TABLE IF NOT EXISTS students (
            nickname            TEXT PRIMARY KEY,
            cohort              TEXT,
            consent_inbody      INTEGER DEFAULT 0,    -- 인바디 동의 (0/1)
            consent_inbody_at   TEXT,                  -- 동의 시각
            consent_research    INTEGER DEFAULT 0,    -- 연구 동의 (IRB 후)
            consent_research_at TEXT,
            registered_at       TEXT NOT NULL,
            last_seen_at        TEXT
        )
    """,

    # ─────────────────────────────────────────────────────────
    # 2. 접속 세션 테이블
    # ─────────────────────────────────────────────────────────
    "sessions": """
        CREATE TABLE IF NOT EXISTS sessions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname     TEXT NOT NULL,
            start_ts     TEXT NOT NULL,
            end_ts       TEXT,
            duration_sec INTEGER,
            FOREIGN KEY (nickname) REFERENCES students(nickname)
        )
    """,

    # ─────────────────────────────────────────────────────────
    # 3. 문제 응답 테이블 ★ 핵심
    # ─────────────────────────────────────────────────────────
    "responses": """
        CREATE TABLE IF NOT EXISTS responses (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname         TEXT NOT NULL,
            session_id       INTEGER,
            arena            TEXT NOT NULL,    -- 'P5' / 'P7' / 'POW_*'
            sub_type         TEXT,              -- 'grammar' / 'vocab' / 'cipher' / ...
            q_id             TEXT NOT NULL,    -- 'G1' / 'V42' / ...
            category         TEXT,              -- cat 필드: '수동태' / '관계대명사' / ...
            diff             TEXT,              -- 'easy' / 'mid' / 'hard'
            q_type           TEXT,              -- P7: 'purpose' / 'detail' / 'inference'
            target_words     TEXT,              -- JSON: ["allocate", ...]
            is_correct       INTEGER NOT NULL, -- 0/1
            response_time_ms INTEGER,
            ts               TEXT NOT NULL,
            FOREIGN KEY (nickname) REFERENCES students(nickname),
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """,

    # ─────────────────────────────────────────────────────────
    # 4. 단어 포로 테이블
    # ─────────────────────────────────────────────────────────
    "word_prison": """
        CREATE TABLE IF NOT EXISTS word_prison (
            nickname     TEXT NOT NULL,
            word         TEXT NOT NULL,
            wrong_count  INTEGER DEFAULT 1,
            first_wrong  TEXT NOT NULL,
            last_wrong   TEXT NOT NULL,
            released     INTEGER DEFAULT 0,    -- 0=수감중 / 1=석방
            released_at  TEXT,
            PRIMARY KEY (nickname, word)
        )
    """,

    # ─────────────────────────────────────────────────────────
    # 5. Sheets 동기화 큐
    # ─────────────────────────────────────────────────────────
    "sync_queue": """
        CREATE TABLE IF NOT EXISTS sync_queue (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name  TEXT NOT NULL,
            row_data    TEXT NOT NULL,        -- JSON
            created_at  TEXT NOT NULL,
            synced      INTEGER DEFAULT 0,    -- 0=대기 / 1=완료
            synced_at   TEXT
        )
    """,

    # ─────────────────────────────────────────────────────────
    # 6. 단어 마스터 테이블 ★ 새 포로수용소 시스템 (2026.04.30)
    # ─────────────────────────────────────────────────────────
    # 단어별 학습 진행도 추적.
    # 마스터 = 2번 연속 정답 (consecutive_correct >= 2 → mastered = 1)
    # ─────────────────────────────────────────────────────────
    "word_mastery": """
        CREATE TABLE IF NOT EXISTS word_mastery (
            nickname            TEXT NOT NULL,
            word                TEXT NOT NULL,
            pos                 TEXT,              -- noun/verb/adjective/adverb
            consecutive_correct INTEGER DEFAULT 0, -- 연속 정답 횟수
            mastered            INTEGER DEFAULT 0, -- 마스터 여부 (0/1)
            mastered_at         TEXT,              -- 마스터 달성 시각
            total_seen          INTEGER DEFAULT 0, -- 총 노출
            total_correct       INTEGER DEFAULT 0, -- 총 정답
            total_wrong         INTEGER DEFAULT 0, -- 총 오답
            last_seen           TEXT,              -- 마지막 노출
            PRIMARY KEY (nickname, word)
        )
    """,
}


# ─────────────────────────────────────────────────────────────
# 인덱스 (조회 성능 향상)
# ─────────────────────────────────────────────────────────────
INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_responses_nick_ts     ON responses(nickname, ts)",
    "CREATE INDEX IF NOT EXISTS idx_responses_nick_cat    ON responses(nickname, category)",
    "CREATE INDEX IF NOT EXISTS idx_responses_nick_arena  ON responses(nickname, arena)",
    "CREATE INDEX IF NOT EXISTS idx_sessions_nick         ON sessions(nickname, start_ts)",
    "CREATE INDEX IF NOT EXISTS idx_sync_pending          ON sync_queue(synced) WHERE synced = 0",
    "CREATE INDEX IF NOT EXISTS idx_mastery_nick_pos      ON word_mastery(nickname, pos)",
    "CREATE INDEX IF NOT EXISTS idx_mastery_nick_mastered ON word_mastery(nickname, mastered)",
]


# ─────────────────────────────────────────────────────────────
# 핵심 함수
# ─────────────────────────────────────────────────────────────

def get_conn() -> sqlite3.Connection:
    """
    SQLite 연결 반환.
    - foreign_keys ON
    - row_factory = Row (딕셔너리처럼 접근 가능)
    """
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> bool:
    """
    DB 초기화. 테이블/인덱스가 없으면 생성, 있으면 그대로 둠.
    앱 시작 시 1회 호출.

    Returns:
        True: 초기화 성공
        False: 실패 (예외는 잡고 False 반환)
    """
    try:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        conn = get_conn()
        cur = conn.cursor()

        # 테이블 생성
        for table_name, ddl in SCHEMA.items():
            cur.execute(ddl)

        # 인덱스 생성
        for idx_sql in INDEXES:
            cur.execute(idx_sql)

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[inbody_db] init_db 실패: {e}")
        return False


def db_exists() -> bool:
    """DB 파일이 존재하는지 확인."""
    return DB_PATH.exists()


def get_db_info() -> dict:
    """
    DB 상태 정보 반환 (디버깅용).
    """
    if not db_exists():
        return {"exists": False, "path": str(DB_PATH)}

    try:
        conn = get_conn()
        cur = conn.cursor()
        info = {
            "exists":   True,
            "path":     str(DB_PATH),
            "size_kb":  round(DB_PATH.stat().st_size / 1024, 2),
            "tables":   {},
        }
        for table_name in SCHEMA.keys():
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            info["tables"][table_name] = cur.fetchone()[0]
        conn.close()
        return info
    except Exception as e:
        return {"exists": True, "error": str(e), "path": str(DB_PATH)}


# ─────────────────────────────────────────────────────────────
# 자가 점검 (직접 실행 시)
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("SnapQ inbody_db 자가 점검")
    print("=" * 60)

    print(f"\nDB 경로: {DB_PATH}")
    print(f"DB 존재 여부 (실행 전): {db_exists()}")

    print("\n[1] init_db() 실행...")
    success = init_db()
    print(f"    결과: {'성공 ✅' if success else '실패 ❌'}")

    print("\n[2] DB 상태 확인:")
    info = get_db_info()
    print(json.dumps(info, ensure_ascii=False, indent=2))

    print("\n[3] 스키마 검증 (테이블 목록):")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cur.fetchall()]
    for t in tables:
        if t.startswith("sqlite_"):
            continue
        print(f"  ✓ {t}")
    conn.close()

    print("\n" + "=" * 60)
    print("자가 점검 완료!")
    print("=" * 60)
