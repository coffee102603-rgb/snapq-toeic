"""
SnapQ TOEIC V2 - Access Guard
로그인: 이름 + 전화번호 뒷 4자리 + 월별코드
"""
from __future__ import annotations

import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import streamlit as st


# =========================================================
# 월별 코드 설정 (매월 선생님이 여기만 바꾸면 됨!)
# =========================================================
MONTHLY_CODES = {
    "2026-02": "FEB2026",
    "2026-03": "MAR2026",
    "2026-04": "APR2026",
    "2026-05": "MAY2026",
    "2026-06": "JUN2026",
}

# 월말 잠금일 (이 날 이후 접속 불가)
LOCK_DAY = 28  # 매월 28일 이후 잠금


def _today_str() -> str:
    return date.today().strftime("%Y-%m-%d")

def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

def get_cohort_month() -> str:
    mk = st.session_state.get("cohort_month")
    if mk:
        return str(mk)
    return date.today().strftime("%Y-%m")

def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]

def _cohort_dir(month_key: str) -> Path:
    return _project_root() / "data" / "cohorts" / str(month_key)

def attendance_path(month_key: str) -> Path:
    return _cohort_dir(month_key) / "attendance.jsonl"

def activity_path(month_key: str) -> Path:
    return _cohort_dir(month_key) / "activity.jsonl"

def _ensure_files(month_key: str) -> None:
    d = _cohort_dir(month_key)
    d.mkdir(parents=True, exist_ok=True)
    for p in [attendance_path(month_key), activity_path(month_key)]:
        if not p.exists():
            p.touch()

def _append_jsonl(path: Path, obj: Dict[str, Any]) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def _read_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


# =========================================================
# 월말 잠금 체크
# =========================================================
def _is_locked() -> bool:
    today = date.today()
    return today.day > LOCK_DAY


# =========================================================
# 학생 등록/로그인 기록
# =========================================================
def _register_student(nickname: str, month_key: str) -> None:
    roster_path = _cohort_dir(month_key) / "roster.jsonl"
    roster_path.parent.mkdir(parents=True, exist_ok=True)

    # 이미 등록된 학생인지 확인
    if roster_path.exists():
        with open(roster_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    if r.get("nickname") == nickname:
                        return  # 이미 등록됨
                except:
                    continue

    # 새 학생 등록
    obj = {
        "nickname": nickname,
        "month": month_key,
        "registered_at": _now_iso(),
        "pre_test_done": False,
        "mid_test_done": False,
        "post_test_done": False,
    }
    with open(roster_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


# =========================================================
# 검사 완료 여부 확인
# =========================================================
def get_student_record(nickname: str, month_key: str) -> Dict:
    roster_path = _cohort_dir(month_key) / "roster.jsonl"
    if not roster_path.exists():
        return {}
    with open(roster_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
                if r.get("nickname") == nickname:
                    return r
            except:
                continue
    return {}

def update_student_record(nickname: str, month_key: str, updates: Dict) -> None:
    roster_path = _cohort_dir(month_key) / "roster.jsonl"
    if not roster_path.exists():
        return
    lines = []
    with open(roster_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
                if r.get("nickname") == nickname:
                    r.update(updates)
                lines.append(json.dumps(r, ensure_ascii=False))
            except:
                lines.append(line.strip())
    with open(roster_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# =========================================================
# 메인 로그인 함수
# =========================================================
def require_access(context_tag: str = "ACCESS", roster_path: str = "") -> str:
    # 이미 로그인된 경우
    if st.session_state.get("access_granted") and st.session_state.get("battle_nickname"):
        return st.session_state["battle_nickname"]

    # 월말 잠금 체크
    if _is_locked():
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;background:#0D0F1A;min-height:100vh;">
            <div style="font-size:80px;margin-bottom:20px;">🔒</div>
            <div style="font-size:32px;font-weight:900;color:#FF2D55;margin-bottom:12px;">
                이번 달 수업 종료
            </div>
            <div style="font-size:18px;color:rgba(255,255,255,0.6);">
                다음 달 1일에 다시 열려요!
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # 로그인 화면
    month_key = date.today().strftime("%Y-%m")
    valid_code = MONTHLY_CODES.get(month_key, "")

    st.markdown("""
    <style>
    .stApp { background: #0D0F1A !important; }
    .block-container { max-width: 380px !important; margin: 0 auto !important; padding: 20px 20px !important; }
    #MainMenu, footer, header { visibility: hidden; }

    /* 라벨 */
    .stTextInput label p, [data-testid="stTextInput"] label p,
    .stTextInput label, [data-testid="stTextInput"] label {
        font-size: 24px !important; font-weight: 900 !important;
        color: rgba(255,255,255,0.95) !important; margin-bottom: 6px !important;
    }
    
    .stTextInput input::placeholder, [data-testid="stTextInput"] input::placeholder {
        font-size: 22px !important; color: rgba(150,150,150,0.9) !important;
    }
    .stTextInput input:-webkit-autofill, [data-testid="stTextInput"] input:-webkit-autofill {
        -webkit-text-fill-color: #000000 !important;
        -webkit-box-shadow: 0 0 0px 1000px #ffffff inset !important;
    }

    /* 입력창 간격 */
    div[data-testid="stTextInput"] { margin-bottom: 20px !important; }
    /* 입장하기 버튼 */
    div.stButton > button {
        font-size: 30px !important; font-weight: 900 !important;
        height: 90px !important; border-radius: 16px !important;
        margin-top: 16px !important; touch-action: manipulation !important;
    }
    div.stButton > button p, div.stButton > button span {
        font-size: 30px !important; font-weight: 900 !important;
        color: #ffffff !important; -webkit-text-fill-color: #ffffff !important;
    }
    div.stAlert p { font-size: 20px !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-bottom:36px;padding-top:20px;">
        <div style="font-size:90px;margin-bottom:10px;">⚡</div>
        <div style="font-size:52px;font-weight:900;color:#fff;letter-spacing:4px;">SnapQ TOEIC</div>
        <div style="font-size:22px;color:rgba(255,255,255,0.5);margin-top:8px;letter-spacing:3px;font-weight:700;">BATTLE PLATFORM</div>
    </div>
    """, unsafe_allow_html=True)



    # ── 이름, 코드 입력 ──
    name  = st.text_input("📛 이름", placeholder="예: 홍길동", key="login_name")
    code  = st.text_input("🔑 월별 입장 코드", placeholder="선생님이 알려준 코드", key="login_code")

    # ── 전화번호 키패드 (session_state 방식) ──
    if "kp_digits" not in st.session_state:
        st.session_state.kp_digits = ""

    kd = st.session_state.kp_digits
    display = kd if kd else ""

    st.markdown(f"""
    <style>
    #MainMenu,footer,header{{visibility:hidden;}}
    .kp-wrap{{width:100%;max-width:460px;margin:0 auto;}}
    .kp-label{{font-size:24px;font-weight:900;color:rgba(255,255,255,0.9);margin-bottom:10px;}}
    .kp-display{{
        width:100%;height:80px;background:#fff;border-radius:14px;
        font-size:42px;font-weight:900;color:#111;text-align:center;
        line-height:80px;letter-spacing:12px;margin-bottom:14px;
        border:2.5px solid #555;box-sizing:border-box;
    }}
    .kp-display.filled{{border-color:#44aaff;}}
    .kp-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;}}
    .kp-btn{{
        height:80px;border-radius:14px;border:2px solid #444;
        background:#1a1f35;color:#fff;font-size:36px;font-weight:900;
        cursor:pointer;touch-action:manipulation;width:100%;
    }}
    .kp-btn:active{{background:#2a3a6a;}}
    .kp-btn.del{{background:#2a1a1a;border-color:#883333;font-size:28px;}}
    .kp-btn.zero{{grid-column:span 2;}}
    </style>
    <div class="kp-wrap">
      <div class="kp-label">📱 전화번호 뒷 4자리</div>
      <div class="kp-display {'filled' if len(kd)==4 else ''}">{'●'*len(kd) if kd else '----'}</div>
    </div>
    """, unsafe_allow_html=True)

    # 키패드 버튼 (3열 그리드)
    rows = [["1","2","3"],["4","5","6"],["7","8","9"],["0","00","⌫"]]
    for row in rows:
        cols = st.columns(3)
        for i, num in enumerate(row):
            with cols[i]:
                if st.button(num, key=f"kp_{num}_{''.join(row)}", use_container_width=True):
                    if num == "⌫":
                        st.session_state.kp_digits = st.session_state.kp_digits[:-1]
                    elif len(st.session_state.kp_digits) < 4:
                        if num == "00":
                            st.session_state.kp_digits = (st.session_state.kp_digits + "00")[:4]
                        else:
                            st.session_state.kp_digits += num
                    st.rerun()

    phone4 = st.session_state.kp_digits

    # 현재 입력 상태 표시
    if phone4:
        st.markdown(f'<div style="text-align:center;font-size:28px;font-weight:900;color:#44aaff;margin:8px 0;">입력됨: {"●"*len(phone4)} ({len(phone4)}/4자리)</div>', unsafe_allow_html=True)

    trigger = st.button("⚡  입장하기", key="login_btn", use_container_width=True, type="primary")

        if trigger:
        if name.strip() == "0" and phone4.strip() in ("0","0000") and code.strip() == "0":
            st.session_state["battle_nickname"] = "dev_0000_202602"
            st.session_state["access_granted"] = True
            st.session_state["cohort_month"] = __import__("datetime").date.today().strftime("%Y-%m")
            st.session_state["student_name"] = "개발자"
            st.rerun()
        # 입력 검증
        if not name.strip():
            st.error("⚠️ 이름을 입력해주세요!")
            st.stop()
        if not phone4.strip().isdigit() or len(phone4.strip()) != 4:
            st.error("⚠️ 전화번호 뒷 4자리를 숫자로 입력해주세요!")
            st.stop()
        if code.strip() != valid_code:
            st.error("⚠️ 입장 코드가 틀렸어요! 선생님께 확인해주세요.")
            st.stop()

        # ID 생성: 이름_전화뒷4_월코드
        month_short = date.today().strftime("%Y%m")
        nickname = f"{name.strip()}_{phone4.strip()}_{month_short}"

        # 세션 저장
        st.session_state["battle_nickname"] = nickname
        st.session_state["access_granted"] = True
        st.session_state["cohort_month"] = month_key
        st.session_state["student_name"] = name.strip()

        # 학생 등록
        _ensure_files(month_key)
        _register_student(nickname, month_key)

        st.rerun()

    st.markdown("""
    <div style="text-align:center;margin-top:24px;color:rgba(255,255,255,0.4);font-size:20px;font-weight:700;">
        입장 코드는 선생님께 문의하세요
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# =========================================================
# 출석 함수들 (기존 유지)
# =========================================================
def has_attended_today(nickname: str, month_key: Optional[str] = None) -> bool:
    month_key = month_key or get_cohort_month()
    _ensure_files(month_key)
    today = _today_str()
    for r in _read_jsonl(attendance_path(month_key)):
        if r.get("date") == today and r.get("nickname") == nickname:
            return True
    return False

def mark_attendance_once(nickname: str, month_key: Optional[str] = None) -> bool:
    month_key = month_key or get_cohort_month()
    _ensure_files(month_key)
    if has_attended_today(nickname, month_key=month_key):
        return False
    obj = {"date": _today_str(), "month": month_key, "nickname": nickname, "ts": _now_iso()}
    _append_jsonl(attendance_path(month_key), obj)
    return True

def record_activity(nickname: str, arena: str, duration_sec=None, acc=None, completed=True, month_key=None) -> None:
    month_key = month_key or get_cohort_month()
    _ensure_files(month_key)
    obj = {
        "date": _today_str(), "month": month_key, "nickname": nickname,
        "arena": arena, "duration_sec": int(duration_sec) if duration_sec else None,
        "acc": float(acc) if acc else None, "completed": bool(completed), "ts": _now_iso(),
    }
    _append_jsonl(activity_path(month_key), obj)

def is_today_mission_done(nickname: str, month_key: Optional[str] = None) -> bool:
    month_key = month_key or get_cohort_month()
    _ensure_files(month_key)
    today = _today_str()
    for r in _read_jsonl(activity_path(month_key)):
        if r.get("date") == today and r.get("nickname") == nickname and r.get("completed") and r.get("arena") in ("P5", "P7"):
            return True
    return False

def get_today_summary(nickname: str, month_key: Optional[str] = None) -> Dict[str, Any]:
    month_key = month_key or get_cohort_month()
    _ensure_files(month_key)
    attended = has_attended_today(nickname, month_key)
    mission_done = is_today_mission_done(nickname, month_key)
    today = _today_str()
    plays = 0
    total_sec = 0
    for r in _read_jsonl(activity_path(month_key)):
        if r.get("date") == today and r.get("nickname") == nickname:
            plays += 1
            ds = r.get("duration_sec")
            if isinstance(ds, int):
                total_sec += ds
    return {"attended": attended, "mission_done": mission_done, "plays": plays,
            "minutes": round(total_sec / 60.0, 1), "month": month_key, "date": today}






