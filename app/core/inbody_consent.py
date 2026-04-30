"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     app/core/inbody_consent.py
ROLE:     인바디 시스템 미니 동의서 화면
VERSION:  SnapQ TOEIC V3 — 2026.04.30
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE:
    from app.core.inbody_consent import (
        ensure_inbody_consent,
        has_inbody_consent,
        withdraw_inbody_consent,
    )

    # 메인 페이지 진입 직후
    ensure_inbody_consent(nickname)
    # → 동의 안 했으면 동의서 화면 표시 + st.stop()
    # → 동의했거나 거부했으면 그대로 통과

    # 동의 여부 확인 (인바디 표시 여부 결정 시)
    if has_inbody_consent(nickname):
        show_inbody_overlay(nickname)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESIGN PRINCIPLES:
    1. 게임 톤이지만 정보는 명확 (학생 이해 우선)
    2. 동의 안 해도 학습은 정상 — 인바디 기능만 비활성화
    3. 삭제 안내는 표시, 실제 버튼은 추후 추가
    4. 한 번 거부하면 세션 동안 다시 안 물음 (귀찮게 안 함)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DB:
    students.consent_inbody:
        0  = 미결정 (아직 안 물음 or 거부)
        1  = 동의함

    st.session_state['_inbody_consent_decided']:
        True  = 이번 세션에 이미 결정함 (다시 안 물음)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Optional

import streamlit as st

from app.core.inbody_db import get_conn
from app.core.inbody_logger import grant_consent


# ─────────────────────────────────────────────────────────────
# 핵심 API
# ─────────────────────────────────────────────────────────────

def has_inbody_consent(nickname: str) -> bool:
    """
    학생이 인바디 동의를 했는지 확인.

    RETURNS:
        True:  동의함 (인바디 기능 정상 표시)
        False: 미동의 or 거부 (인바디 기능 비활성화)
    """
    if not nickname:
        return False
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT consent_inbody FROM students WHERE nickname = ?",
            (nickname,)
        )
        row = cur.fetchone()
        conn.close()
        return bool(row and row["consent_inbody"] == 1)
    except Exception:
        return False


def has_decided_this_session() -> bool:
    """이번 세션에 이미 동의/거부 결정을 했는지."""
    return bool(st.session_state.get("_inbody_consent_decided", False))


def mark_decided_this_session() -> None:
    """결정 완료 표시 — 같은 세션 내 재질문 방지."""
    st.session_state["_inbody_consent_decided"] = True


def ensure_inbody_consent(nickname: str) -> bool:
    """
    동의 여부에 따라 분기:
      - 이미 동의함 → 그대로 통과 (True)
      - 이미 이번 세션에 거부함 → 그대로 통과 (False)
      - 아직 안 물음 → 동의서 화면 표시 후 st.stop()

    USAGE:
        # 메인 페이지 진입 직후
        consent = ensure_inbody_consent(nickname)
        if consent:
            show_inbody_overlay(...)

    RETURNS:
        True: 동의함 (인바디 기능 활성)
        False: 미동의 (인바디 기능 비활성, 학습은 정상)
    """
    if not nickname:
        return False

    # 이미 동의함 → 통과
    if has_inbody_consent(nickname):
        return True

    # 이번 세션에 이미 결정 (거부) → 통과
    if has_decided_this_session():
        return False

    # 아직 안 물음 → 동의서 화면 표시
    _show_consent_form(nickname)
    return False  # st.stop() 위에서 호출되므로 사실 도달 안 함


def withdraw_inbody_consent(nickname: str) -> bool:
    """
    학생이 동의 철회를 요청. consent_inbody = 0으로 되돌림.
    실제 데이터 삭제는 별도 함수 (delete_my_data) 추후 추가.
    """
    if not nickname:
        return False
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "UPDATE students SET consent_inbody = 0 WHERE nickname = ?",
            (nickname,)
        )
        conn.commit()
        conn.close()
        # 세션 결정 플래그 초기화 (다음 로그인 시 다시 물음)
        st.session_state.pop("_inbody_consent_decided", None)
        return True
    except Exception as e:
        print(f"[inbody_consent] withdraw 실패: {e}")
        return False


# ─────────────────────────────────────────────────────────────
# 내부: 동의서 UI
# ─────────────────────────────────────────────────────────────

def _show_consent_form(nickname: str) -> None:
    """
    동의서 화면을 표시하고 st.stop()으로 정지.
    학생이 버튼 클릭 → grant_consent() or 거부 처리 → rerun.
    """

    # 전체 페이지 다크 테마 (Snap 토익 톤 유지)
    st.markdown("""
    <style>
    .stApp { background: #0D0F1A !important; }
    .block-container {
        max-width: 540px !important;
        margin: 0 auto !important;
        padding-top: 30px !important;
    }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    # 동의서 본문 (캐릭터 톤 + 명확한 정보)
    st.markdown(f"""
    <div style="background:#0a1218;border:2px solid #00d4aa;border-radius:16px;
                padding:28px 24px;margin-bottom:6px;">

      <div style="text-align:center;margin-bottom:6px;">
        <div style="font-size:28px;margin-bottom:8px;">🪖</div>
        <div style="color:#00d4aa;font-size:13px;font-weight:900;letter-spacing:1px;">
          전사 등록 안내
        </div>
        <div style="color:#557766;font-size:12px;margin-top:6px;letter-spacing:2px;">
          BATTLE INBODY CONSENT
        </div>
      </div>

      <div style="background:#050910;border-radius:10px;padding:16px;
                  border-left:3px solid #00d4aa;margin-bottom:6px;">
        <div style="color:#00ffcc;font-size:12px;font-weight:700;
                    font-style:italic;line-height:1.3;">
          "전장에 들어오기 전, 한 가지만 확인하자."
        </div>
        <div style="color:#557766;font-size:11px;margin-top:6px;letter-spacing:1px;">
          — 해골 · 단어 포로수용소장
        </div>
      </div>

      <div style="color:#aabbcc;font-size:12px;line-height:1.7;margin-bottom:6px;">
        <p style="margin:0 0 10px;font-weight:700;color:#00d4aa;">
          📊 너의 전투 기록을 인바디에 표시하려면, 이게 필요해:
        </p>
        <ul style="margin:0;padding-left:20px;font-size:13px;">
          <li>정답률 · 학습 시간 · 출석</li>
          <li>카테고리별 강·약점 (수동태 · 관계대명사 등)</li>
          <li>틀린 단어 (포로수용소 자동 등록)</li>
        </ul>
      </div>

      <div style="background:#1a0a08;border-left:3px solid #ff8844;
                  border-radius:6px;padding:8px;margin-bottom:6px;">
        <p style="color:#ffaa66;font-size:12px;margin:0;line-height:1.3;">
          <strong>중요</strong> — 이 데이터는 <strong>네 인바디 화면에만</strong> 사용돼.
          연구·분석엔 절대 안 쓰여 (IRB 별도 동의 후에만 가능).
        </p>
      </div>

      <div style="background:#080a18;border-radius:6px;padding:10px 12px;
                  margin-bottom:18px;">
        <p style="color:#557788;font-size:11px;margin:0;line-height:1.3;">
          🚪 언제든 빠져나갈 수 있어. 데이터 삭제는 추후 메뉴에 추가될 예정.
        </p>
      </div>

      <div style="background:#0e0620;border-left:3px solid #cc44ff;
                  border-radius:6px;padding:10px 12px;margin-bottom:8px;">
        <p style="color:#dd99ff;font-size:11px;margin:0;line-height:1.3;">
          💡 <strong>거부해도 학습은 정상</strong>이야. 인바디 화면만 안 보일 뿐.
        </p>
      </div>

    </div>
    """, unsafe_allow_html=True)

    # 버튼 영역
    col1, col2 = st.columns([2, 1])

    with col1:
        if st.button(
            "⚡ 좋아, 인바디 받자!",
            use_container_width=True,
            type="primary",
            key="btn_consent_yes"
        ):
            ok = grant_consent(nickname)
            mark_decided_this_session()
            if ok:
                st.success("등록 완료! 잠시만...")
            st.rerun()

    with col2:
        if st.button(
            "🚪 나중에",
            use_container_width=True,
            key="btn_consent_no"
        ):
            mark_decided_this_session()
            st.rerun()

    # 페이지 하단 안내
    st.markdown("""
    <div style="text-align:center;margin-top:24px;color:#334455;font-size:11px;">
        선택은 언제든 바꿀 수 있어. 학습은 어느 쪽이든 그대로 가능.
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ─────────────────────────────────────────────────────────────
# 자가 점검 (직접 실행 시 — Streamlit 없이 로직만 검증)
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    """
    Streamlit UI는 streamlit run으로만 작동하므로,
    여기선 DB 로직만 검증.
    """
    from app.core.inbody_db import init_db
    from app.core.inbody_logger import ensure_student

    print("=" * 60)
    print("SnapQ inbody_consent 자가 점검 (로직만)")
    print("=" * 60)

    init_db()

    # 1. 학생 등록 (동의 X)
    print("\n[1] 학생 등록 (동의 X)")
    ensure_student("테스트2", cohort="2026-05", consent_inbody=False)
    print(f"    has_inbody_consent: {has_inbody_consent('테스트2')}")
    assert has_inbody_consent("테스트2") == False, "동의 안 했는데 True 나옴!"
    print("    ✅ 미동의 확인")

    # 2. 동의 처리
    print("\n[2] grant_consent 호출")
    grant_consent("테스트2")
    print(f"    has_inbody_consent: {has_inbody_consent('테스트2')}")
    assert has_inbody_consent("테스트2") == True, "동의했는데 False 나옴!"
    print("    ✅ 동의 확인")

    # 3. 동의 철회
    print("\n[3] withdraw_inbody_consent 호출")
    # st.session_state 없이 시뮬 — 직접 DB만 변경
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE students SET consent_inbody = 0 WHERE nickname = ?", ("테스트2",))
    conn.commit()
    conn.close()
    print(f"    has_inbody_consent: {has_inbody_consent('테스트2')}")
    assert has_inbody_consent("테스트2") == False, "철회했는데 True 나옴!"
    print("    ✅ 철회 확인")

    # 정리
    print("\n[4] 테스트 데이터 정리")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE nickname = '테스트2'")
    cur.execute("DELETE FROM sync_queue WHERE row_data LIKE '%테스트2%'")
    conn.commit()
    conn.close()
    print("    완료")

    print("\n" + "=" * 60)
    print("자가 점검 완료! ✅")
    print("Streamlit UI는 실제 페이지에 통합 후 검증 필요.")
    print("=" * 60)
