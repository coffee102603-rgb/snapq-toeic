# app/core/posttest_gate.py
# ============================================
# SnapQ Posttest Gate (사후 설문 1회)
# - Pre와 동일 문항(Q1~Q7) + Post 전용 Q8(차별성 인식)
# - 결과는 profile["surveys"]["post"]에 논문용 구조로 저장
# - MISSION GATE: 통과 전에는 다음 화면 진행 불가 (UI/세션 고정)
# ============================================

from __future__ import annotations

from datetime import datetime
import streamlit as st

from app.core.battle_state import load_profile, save_profile


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _ensure_profile() -> dict:
    if "profile" not in st.session_state or not isinstance(st.session_state.profile, dict):
        st.session_state.profile = load_profile()
        if not isinstance(st.session_state.profile, dict):
            st.session_state.profile = {}
    return st.session_state.profile


def _ensure_surveys(profile: dict) -> None:
    if "surveys" not in profile or not isinstance(profile["surveys"], dict):
        profile["surveys"] = {}
    if "pre" not in profile["surveys"]:
        profile["surveys"]["pre"] = {}
    if "post" not in profile["surveys"]:
        profile["surveys"]["post"] = {}


def _likert_to_int(x: str) -> int | None:
    x = (x or "").strip()
    if x.startswith("1"):
        return 1
    if x.startswith("2"):
        return 2
    if x.startswith("3"):
        return 3
    if x.startswith("4"):
        return 4
    if x.startswith("5"):
        return 5
    return None


def _render_mission_complete(context_tag: str = "") -> None:
    """통과 연출: 사용자가 '통과했다'는 감각을 갖게 하는 화면."""
    st.markdown("## ✅ MISSION COMPLETE")
    st.success("사후 설문 인증 완료! 이제 전장 접근이 가능합니다.")
    if context_tag:
        st.caption(f"CONTEXT: {context_tag}")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("▶ 계속 진행", use_container_width=True):
            st.session_state["_posttest_gate_shown_done"] = True
            st.rerun()
    with col2:
        if st.button("🔄 새로고침", use_container_width=True):
            st.rerun()

    st.stop()


def require_posttest_gate(context_tag: str = "") -> None:
    """
    context_tag: 예) 'P5', 'P7' 등
    """
    profile = _ensure_profile()
    _ensure_surveys(profile)

    # 이미 완료했으면 통과(세션 고정) + 1회만 '통과 연출' 화면 보여주기
    post = profile.get("surveys", {}).get("post", {})
    if isinstance(post, dict) and post.get("submitted_at"):
        st.session_state["posttest_gate_passed"] = True

        # 통과 연출은 최초 1회만 띄우고, 이후엔 조용히 통과
        if not st.session_state.get("_posttest_gate_shown_done", False):
            _render_mission_complete(context_tag=context_tag)

        st.session_state.profile = profile
        save_profile(profile)
        return

    # 아직 미완료면: 여기서 막는다(게이트)
    st.session_state["posttest_gate_passed"] = False

    st.markdown("# 🧾 사후 조사 (MISSION GATE)")
    st.info("※ 이 설문은 훈련 후 **1회만** 진행됩니다. (논문 분석용)")

    likert = [
        "선택하세요",
        "1 (전혀 그렇지 않다)",
        "2",
        "3",
        "4",
        "5 (매우 그렇다)",
    ]

    with st.form("posttest_form", clear_on_submit=False):
        st.subheader("Ⅰ. 학습 성향 (1~5점)")

        q1 = st.selectbox("Q1. TOEIC 문제를 풀 때, 시간 압박을 크게 느낀다.", likert, index=0)
        q2 = st.selectbox("Q2. 문제를 읽을 때 핵심 정보를 빠르게 찾는 데 자신이 있다.", likert, index=0)
        q3 = st.selectbox("Q3. TOEIC 문제 풀이에 일정한 전략(읽는 순서·판단 기준)이 있다.", likert, index=0)
        q4 = st.selectbox("Q4. 실전과 유사한 환경에서 연습했다고 느낀다.", likert, index=0)
        q5 = st.selectbox("Q5. TOEIC 문제 풀이 중 긴장으로 실수가 잦은 편이다.", likert, index=0)
        q6 = st.selectbox("Q6. 제한 시간 내 정확도를 유지하는 것이 어렵다.", likert, index=0)
        q7 = st.selectbox("Q7. TOEIC 학습이 지루하거나 반복적이라고 느낀다.", likert, index=0)

        st.divider()
        q8 = st.selectbox(
            "Q8. 이번 훈련 방식은 기존 TOEIC 학습 방식과 분명히 다르다고 느꼈다.",
            likert,
            index=0,
        )

        submitted = st.form_submit_button("✅ 저장", use_container_width=True)

    # 제출 전이면 여기서 차단(게이트 유지)
    if not submitted:
        st.stop()

    must = [q1, q2, q3, q4, q5, q6, q7, q8]
    if any(x == "선택하세요" for x in must):
        st.error("⚠️ 모든 문항을 선택해야 저장됩니다.")
        st.stop()

    labels = {
        "Q1": q1, "Q2": q2, "Q3": q3, "Q4": q4,
        "Q5": q5, "Q6": q6, "Q7": q7, "Q8": q8,
    }

    items = {}
    for k, v in labels.items():
        n = _likert_to_int(v)
        if n is None:
            st.error("⚠️ 점수 변환 오류가 발생했습니다.")
            st.stop()
        items[k] = n

    ts = _now_iso()

    profile["surveys"]["post"] = {
        "meta": {
            "context": context_tag,
        },
        "items": items,
        "labels": labels,
        "submitted_at": ts,
    }

    st.session_state.profile = profile
    save_profile(profile)

    # 통과 플래그 고정 + 통과 연출을 다음 rerun에서 1회 보여주기
    st.session_state["posttest_gate_passed"] = True
    st.session_state["_posttest_gate_shown_done"] = False

    st.rerun()
