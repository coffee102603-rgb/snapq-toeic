"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     app/core/inbody_overlay.py
ROLE:     인바디 현수막 오버레이 UI
VERSION:  SnapQ TOEIC V3 — 2026.04.30
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE:
    # main_hub.py 진입 직후 한 줄 추가:
    from app.core.inbody_overlay import maybe_show_inbody

    maybe_show_inbody(nickname)
    # → 자동으로:
    #   - 동의 안 했으면 동의서 표시
    #   - 오늘 이미 봤으면 스킵
    #   - 신규(데이터 0)면 환영 시퀀스
    #   - 그 외엔 인바디 시퀀스 표시
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESIGN:
    [자동 분기]
        ① 동의 X    → inbody_consent.ensure_inbody_consent()
        ② 오늘 본 적 → 스킵
        ③ 신규      → 환영 시퀀스 (TORI → HAE → 해골)
        ④ 기존      → 인바디 시퀀스 (메인 1 + 서브 2)

    [등장 연출]
        - 메인 카드 큰 등장
        - 2.5초 후 서브로 작아지며 위로
        - 다음 메인 카드 큰 등장
        - 반복 → 마지막에 ⚡ 출동! 버튼 활성화

    [닫기]
        ⚡ 출동! 클릭 → 오늘 봤다 표시 → 메인 화면 표시
        (포로소탕 게임 통합은 7단계에서 추가)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from datetime import date
from typing import List, Dict

import streamlit as st

from app.core.inbody_consent import (
    ensure_inbody_consent,
    has_inbody_consent,
)
from app.core.inbody_brain import build_inbody_messages, get_student_stats
from app.core.inbody_messages import render_message


# ─────────────────────────────────────────────────────────────
# 캐릭터 시각 정보
# ─────────────────────────────────────────────────────────────

CHARACTER_INFO = {
    "tori": {
        "emoji":  "🐱",
        "name":   "TORI",
        "role":   "P5 화력전 사령관",
        "color":  "#00d4aa",
        "bg":     "#041810",
        "msgClr": "#00ffcc",
    },
    "hae": {
        "emoji":  "🥷",
        "name":   "HAE",
        "role":   "P7 암호해독 사령관",
        "color":  "#7766ff",
        "bg":     "#0a0820",
        "msgClr": "#aabbff",
    },
    "skull": {
        "emoji":  "💀",
        "name":   "해골",
        "role":   "단어 포로수용소장",
        "color":  "#cc44ff",
        "bg":     "#1a0a20",
        "msgClr": "#dd99ff",
    },
}


# ─────────────────────────────────────────────────────────────
# 메인 진입점
# ─────────────────────────────────────────────────────────────

def maybe_show_inbody(nickname: str) -> None:
    """
    인바디 표시 여부를 자동으로 판단하고 처리.

    USAGE:
        # main_hub.py에서 한 줄 추가
        maybe_show_inbody(nickname)
        # 그 아래 메인 화면 코드는 그대로

    BEHAVIOR:
        - 동의 안 했으면 동의서 화면 (그 안에서 st.stop)
        - 오늘 이미 봤으면 그냥 통과
        - 신규는 환영 시퀀스
        - 기존은 인바디 시퀀스
        - 모두 ⚡ 출동! 누를 때까지 st.stop()
    """
    if not nickname:
        return

    # ─── ① 동의 게이트 ─────────────────────────────────
    consent = ensure_inbody_consent(nickname)
    if not consent:
        # 거부한 경우 - 그냥 통과 (학습 도구 정상 작동)
        return

    # ─── ② 오늘 이미 봤는지 체크 ───────────────────────
    today_key = f"_inbody_shown_{date.today().isoformat()}"
    if st.session_state.get(today_key):
        return

    # ─── ③ 신규 vs 기존 분기 ───────────────────────────
    stats = get_student_stats(nickname)

    if stats["is_first_visit"]:
        _show_welcome_sequence(nickname)
    else:
        _show_inbody_sequence(nickname)

    # 여기까지 도달 = 사용자가 ⚡ 출동! 클릭함
    st.session_state[today_key] = True
    st.rerun()


# ─────────────────────────────────────────────────────────────
# 환영 시퀀스 (첫 접속)
# ─────────────────────────────────────────────────────────────

def _show_welcome_sequence(nickname: str) -> None:
    """첫 접속 환영 시퀀스 — TORI → HAE → 해골 순차 등장."""

    welcome_msgs = [
        {
            "character": "tori",
            "lines": ['"P5 훈련 담당. 30문제 10분, 내가 만든다."'],
        },
        {
            "character": "hae",
            "lines": ['"P7 담당. 첫 줄에 99%. 감 잡는 법, 가르친다."'],
        },
        {
            "character": "skull",
            "lines": [
                '"틀린 P5, 버벅인 P7 — 내가 다 가뒀다."',
                '"빈출 어휘만 추출해 단어 포로로. 도망 못 가."',
            ],
        },
    ]

    _render_overlay(
        nickname=nickname,
        title="⚡ WELCOME, 새내기 ⚡",
        subtitle="첫 등록 — 캐릭터들이 너를 맞이한다",
        cards=welcome_msgs,
        is_welcome=True,
    )


# ─────────────────────────────────────────────────────────────
# 인바디 시퀀스 (2일차+)
# ─────────────────────────────────────────────────────────────

def _show_inbody_sequence(nickname: str) -> None:
    """기존 학생 — 데이터 기반 인바디 시퀀스."""

    messages = build_inbody_messages(nickname, max_count=3)
    if not messages:
        # 시그널이 없으면 그냥 통과 (희박한 케이스)
        return

    # 시그널 → 텍스트로 변환
    cards = []
    for sig in messages:
        text = render_message(sig)
        if not text:
            continue
        cards.append({
            "character": sig["character"],
            "lines": [text],
        })

    if not cards:
        return

    _render_overlay(
        nickname=nickname,
        title="🪖 BATTLE INBODY",
        subtitle=f"오늘의 전투 보고 · {nickname}",
        cards=cards,
        is_welcome=False,
    )


# ─────────────────────────────────────────────────────────────
# 공통 오버레이 렌더링
# ─────────────────────────────────────────────────────────────

def _render_overlay(nickname: str, title: str, subtitle: str,
                    cards: List[Dict], is_welcome: bool) -> None:
    """
    오버레이 화면 표시 + ⚡ 출동! 버튼.
    클릭 시 함수 종료 (호출자가 st.rerun 처리).

    cards: [{"character": "tori"/"hae"/"skull", "lines": [str, ...]}, ...]
    """

    # 페이지 다크 테마
    st.markdown("""
    <style>
    .stApp { background: #0D0F1A !important; }
    .block-container {
        max-width: 540px !important;
        margin: 0 auto !important;
        padding-top: 20px !important;
    }
    #MainMenu, footer, header { visibility: hidden; }

    /* 큰 카드 등장 애니메이션 */
    @keyframes slideInBig {
        from { opacity: 0; transform: translateY(30px) scale(0.95); }
        to   { opacity: 1; transform: translateY(0) scale(1); }
    }
    @keyframes slideInSub {
        from { opacity: 0; transform: translateY(-10px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .big-card {
        animation: slideInBig 0.55s cubic-bezier(.4,0,.2,1);
    }
    .sub-card {
        animation: slideInSub 0.4s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)

    # 헤더
    st.markdown(f"""
    <div style="text-align:center;margin-bottom:14px;">
        <div style="color:#00d4aa;font-size:18px;font-weight:900;letter-spacing:2px;">
            {title}
        </div>
        <div style="color:#557766;font-size:11px;margin-top:4px;letter-spacing:1px;">
            {subtitle}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 카드 영역 — 메인 1개 + 서브 N개
    main_card = cards[0]
    sub_cards = cards[1:] if len(cards) > 1 else []

    # 서브 카드들 (위쪽에 작게 — 이미 등장한 카드들의 흔적)
    if sub_cards:
        sub_html = ""
        for c in sub_cards:
            info = CHARACTER_INFO.get(c["character"], CHARACTER_INFO["skull"])
            line = c["lines"][0] if c["lines"] else ""
            sub_html += f"""
            <div class="sub-card" style="
                background:{info['bg']};
                border:1px solid {info['color']}55;
                border-radius:8px;
                padding:8px 12px;
                margin-bottom:6px;
                display:flex;
                align-items:center;
                gap:10px;
            ">
                <span style="font-size:18px;">{info['emoji']}</span>
                <div style="flex:1;">
                    <span style="color:{info['color']};font-size:10px;font-weight:800;
                                 letter-spacing:1px;">{info['name']}</span>
                    <div style="color:{info['msgClr']};font-size:12px;font-weight:600;
                                font-style:italic;line-height:1.4;margin-top:2px;">
                        {line}
                    </div>
                </div>
            </div>
            """
        st.markdown(sub_html, unsafe_allow_html=True)

    # 메인 카드 (큰 등장)
    info = CHARACTER_INFO.get(main_card["character"], CHARACTER_INFO["skull"])
    main_lines_html = "".join(
        f'<div style="color:{info["msgClr"]};font-size:15px;font-weight:700;'
        f'font-style:italic;line-height:1.6;margin-top:{6 if i > 0 else 0}px;">'
        f'{line}</div>'
        for i, line in enumerate(main_card["lines"])
    )

    st.markdown(f"""
    <div class="big-card" style="
        background:{info['bg']};
        border:2.5px solid {info['color']};
        border-radius:14px;
        padding:18px 20px;
        margin-bottom:18px;
        display:flex;
        gap:14px;
        align-items:flex-start;
        box-shadow:0 0 24px {info['color']}33;
    ">
        <div style="
            width:54px;height:54px;
            background:#0D0F1A;
            border:2px solid {info['color']};
            border-radius:50%;
            display:flex;align-items:center;justify-content:center;
            font-size:28px;flex-shrink:0;
        ">{info['emoji']}</div>
        <div style="flex:1;">
            {main_lines_html}
            <div style="color:{info['color']}99;font-size:10px;margin-top:8px;
                        letter-spacing:1.5px;">
                — {info['name']} · {info['role']}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ⚡ 출동! 버튼
    if st.button(
        "⚡ 출동!",
        use_container_width=True,
        type="primary",
        key=f"btn_inbody_depart_{nickname}"
    ):
        return  # 호출자가 st.session_state 표시 + rerun 처리

    # 포로수용소 안내 (해골 톤)
    st.markdown("""
    <div style="text-align:center;margin-top:12px;color:#cc44ff;font-size:12px;
                font-style:italic;letter-spacing:0.5px;">
        💀 <strong style="color:#dd99ff;">단어 포로수용소</strong>부터 가자!
    </div>
    """, unsafe_allow_html=True)

    # 버튼 안 누르면 여기서 정지
    st.stop()


# ─────────────────────────────────────────────────────────────
# 자가 점검 (로직만 — Streamlit UI는 실제 통합 후 검증)
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("SnapQ inbody_overlay 자가 점검 (로직만)")
    print("=" * 60)

    from app.core.inbody_db import init_db, get_conn
    from app.core.inbody_logger import (
        ensure_student, start_session, end_session,
        log_response, update_word_prison,
    )

    init_db()

    # 시나리오: 약점 + 포로 학생 → 인바디 시퀀스 생성 시뮬
    print("\n[시나리오] 풍부한 데이터 학생 → 메시지 생성")
    nick = "오버레이테스트"
    ensure_student(nick, cohort="2026-05", consent_inbody=True)
    sid = start_session(nick)

    # 약점 데이터
    for i, ok in enumerate([True, False, False, False, False]):
        log_response(
            nickname=nick, session_id=sid,
            arena="P5", sub_type="grammar", q_id=f"G{1000+i}",
            category="수동태", diff="easy",
            is_correct=ok, response_time_ms=2000,
        )

    # 반복 오답
    for _ in range(3):
        update_word_prison(nick, "allocate", is_correct=False)

    end_session(sid)

    # 메시지 빌더 호출
    messages = build_inbody_messages(nick, max_count=3)
    print(f"\n생성된 메시지: {len(messages)}개\n")

    for i, sig in enumerate(messages):
        text = render_message(sig)
        info = CHARACTER_INFO.get(sig["character"], {})
        size_label = "메인" if i == 0 else f"서브{i}"
        print(f"  [{size_label}] {info.get('emoji','?')} {info.get('name','?'):5s}")
        print(f"          → {text}")

    # 정리
    print("\n[정리] 테스트 데이터 삭제")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM responses WHERE nickname = ?", (nick,))
    cur.execute("DELETE FROM word_prison WHERE nickname = ?", (nick,))
    cur.execute("DELETE FROM sessions WHERE nickname = ?", (nick,))
    cur.execute("DELETE FROM students WHERE nickname = ?", (nick,))
    cur.execute("DELETE FROM sync_queue WHERE row_data LIKE ?", (f"%{nick}%",))
    conn.commit()
    conn.close()
    print("  완료")

    print("\n" + "=" * 60)
    print("자가 점검 완료! ✅")
    print("Streamlit UI는 실제 main_hub 통합 후 검증.")
    print("=" * 60)
