import streamlit as st

st.set_page_config(page_title="🗡 Secret Armory Lobby", layout="wide")

# --- banner (debug) ---
st.markdown(
    f"<div style='padding:10px 14px;border-radius:14px;background:rgba(255,120,80,.18);"
    f"border:1px solid rgba(255,120,80,.35);font-weight:900;'>"
    f"🗡 ARMORY LOBBY LOADED: {__file__}"
    f"</div>",
    unsafe_allow_html=True,
)

st.markdown("## 🗡 Secret Armory")
st.caption("P5 저장 문제 / P7 저장 단어 — TRAIN(정리) / BATTLE(시험) 4갈래 입구")

# --- layout ---
left, right = st.columns(2, gap="large")

with left:
    st.markdown("### 🧨 P5 무기고")
    st.caption("저장된 P5 문제로 연습/시험")
    if st.button("🟩 P5 TRAIN", use_container_width=True, key="go_p5_train"):
        st.switch_page("pages/02_P5_Train_Arena.py")
    if st.button("🔥 P5 BATTLE", use_container_width=True, key="go_p5_battle"):
        st.switch_page("pages/02_P5_Armory_Battle.py")

with right:
    st.markdown("### 🧩 VOCA 무기고 (P7 저장 단어)")
    st.caption("저장된 단어로 정리/시험")
    if st.button("🟩 VOCA TRAIN", use_container_width=True, key="go_voca_train"):
        st.switch_page("pages/04_VOCA_Train_Arena.py")
    if st.button("🔥 VOCA BATTLE", use_container_width=True, key="go_voca_battle"):
        st.switch_page("pages/04_VOCA_Battle_Arena.py")

st.markdown("---")
c1, c2 = st.columns([1, 1])
with c1:
    if st.button("🏠 본부 복귀", use_container_width=True, key="go_home"):
        # main_hub는 보통 사이드바로 이동이 안전하지만, 시도는 해본다
        try:
            st.switch_page("main_hub.py")
        except Exception:
            st.info("좌측 사이드바에서 Main Hub로 이동해주세요.")
with c2:
    st.caption("✅ 로비만 복구. 내부 엔진/데이터는 그대로 유지됩니다.")
