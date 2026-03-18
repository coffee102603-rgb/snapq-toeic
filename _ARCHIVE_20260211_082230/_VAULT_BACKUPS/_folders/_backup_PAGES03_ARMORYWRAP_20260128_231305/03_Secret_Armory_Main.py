# ===== SNAPQ ARMORY TRACE BANNER (AUTO) =====
try:
    import streamlit as st
    st.error("🔥 SECRET ARMORY FILE LOADED: __FILE__ = " + __file__)
except Exception:
    pass
# ===========================================
# pages/03_Secret_Armory_Main.py
# SnapQ TOEIC – Secret Armory Lobby (FINAL UX) - P5 BATTLE -> 55S FIXED

import os as _os
import streamlit as st

ARMORY_UI_BUILD = "ARMORY_LOBBY_FINAL__2026-01-27__P5_BATTLE_55S_LOCK"

st.set_page_config(
    page_title="🧨 Secret Armory · SnapQ TOEIC",
    page_icon="🧨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- global css ----------
def _snapq_load_global_css():
    for _p in ("styles/global.css", "assets/global.css"):
        if _os.path.exists(_p):
            try:
                with open(_p, "r", encoding="utf-8") as f:
                    st.markdown("<style>" + f.read() + "</style>", unsafe_allow_html=True)
                break
            except Exception:
                pass


_snapq_load_global_css()

try:
    from app.core.ui_shell import apply_ui_shell

    apply_ui_shell(theme="armory")
except Exception:
    pass

try:
    from app.core.battle_theme import apply_battle_theme

    apply_battle_theme()
except Exception:
    pass


# ---------- inventory count (SAFE) ----------
def _safe_inventory_counts():
    p5 = voca = None
    try:
        from app.arenas import secret_armory as arena

        items = arena._load_armory_items()
        p5 = voca = 0
        for it in items or []:
            blob = str(it).lower()
            if "p5" in blob or "grammar" in blob or "어법" in blob:
                p5 += 1
            if "voca" in blob or "word" in blob or "단어" in blob:
                voca += 1
    except Exception:
        pass
    return str(p5 if p5 is not None else "?"), str(voca if voca is not None else "?")


# ---------- page existence guard ----------
def _page_exists(rel_path: str) -> bool:
    # Streamlit's switch_page expects a path relative to main script directory.
    # We guard against missing files so the app doesn't crash.
    try:
        return _os.path.exists(rel_path)
    except Exception:
        return False


# ---------- CSS ----------
def _apply_css():
    st.markdown(
        """
<style>
section[data-testid="stAppViewContainer"]{
  background:
    radial-gradient(980px 680px at 10% 12%, rgba(255,80,90,.18), transparent 62%),
    radial-gradient(920px 660px at 90% 12%, rgba(80,220,200,.16), transparent 62%),
    linear-gradient(135deg, #101a28, #0f1724);
}
.block-container{max-width:1200px;padding-top:1.8rem;text-align:center;}
.arm-title{font-size:54px;font-weight:1000;}
.arm-titleline{width:320px;height:2px;margin:8px auto 12px;
  background:linear-gradient(90deg,#ff505a,#50dcc8);}
.inv-row{display:flex;gap:10px;justify-content:center;margin-bottom:16px;}
.inv-chip{padding:8px 14px;border-radius:999px;font-weight:900;}
.inv-p5{background:rgba(255,80,90,.25);}
.inv-voca{background:rgba(80,220,200,.25);}
.lane-wrap{border-radius:22px;padding:16px;margin-bottom:14px;
  background:rgba(255,255,255,.08);}
.lane-title{font-size:28px;font-weight:1000;}
.lane-mini{opacity:.9;font-weight:900;}
.stButton>button{min-height:64px;font-size:19px;font-weight:1000;border-radius:18px;}
.p5-train .stButton>button{background:#3cffaa;color:#061013;}
.p5-battle .stButton>button{background:#ff505a;color:#0b0e14;}
.voca-train .stButton>button{background:#50dcc8;color:#061013;}
.voca-battle .stButton>button{background:#78a0ff;color:#081018;}
.errbox{
  margin: 14px auto 0;
  max-width: 720px;
  border-radius: 16px;
  padding: 12px 14px;
  background: rgba(255,80,90,.12);
  border: 1px solid rgba(255,80,90,.25);
  color: rgba(255,255,255,.92);
  font-weight: 900;
}
</style>
        """,
        unsafe_allow_html=True,
    )


_apply_css()

st.markdown(f"<div class='arm-build-badge'>🧰 {ARMORY_UI_BUILD}</div>", unsafe_allow_html=True)

p5_cnt, voca_cnt = _safe_inventory_counts()

# ---------- Title ----------
st.markdown("<div class='arm-title'>🧨 Secret Armory</div>", unsafe_allow_html=True)
st.markdown("<div class='arm-titleline'></div>", unsafe_allow_html=True)
st.markdown("<b>틀린 걸 다시 씹어먹고, 시험으로 증명한다.</b>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="inv-row">
      <div class="inv-chip inv-p5">🧠 P5 <b>{p5_cnt}</b></div>
      <div class="inv-chip inv-voca">🧩 VOCA <b>{voca_cnt}</b></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Lanes ----------
colL, colR = st.columns(2, gap="large")

with colL:
    st.markdown(
        """
        <div class="lane-wrap">
          <div class="lane-title">🧠 P5 무기고</div>
          <div class="lane-mini">연습으로 준비하고, 시험으로 증명한다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='p5-train'>", unsafe_allow_html=True)
    if st.button("🟩 TRAIN", use_container_width=True, key="p5_train"):
        st.switch_page("pages/02_P5_Train_Arena.py")
    st.markdown("</div>", unsafe_allow_html=True)

    # ✅ P5 BATTLE: Always go to 55S page
    P5_BATTLE_TARGET = "pages/02_P5_Exam_10Q_55S.py"

    st.markdown("<div class='p5-battle'>", unsafe_allow_html=True)
    if st.button("🟥 BATTLE", use_container_width=True, key="p5_battle"):
        if _page_exists(P5_BATTLE_TARGET):
            st.switch_page(P5_BATTLE_TARGET)
        else:
            st.markdown(
                f"<div class='errbox'>⚠️ 페이지를 찾을 수 없습니다: <code>{P5_BATTLE_TARGET}</code><br>"
                f"pages 폴더에 파일이 있는지 확인하세요.</div>",
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

with colR:
    st.markdown(
        """
        <div class="lane-wrap">
          <div class="lane-title">🧩 VOCA 무기고</div>
          <div class="lane-mini">학습으로 익히고, 시험으로 반사한다.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='voca-train'>", unsafe_allow_html=True)
    if st.button("🟩 TRAIN", use_container_width=True, key="voca_train"):
        st.switch_page("pages/04_VOCA_Train_Arena.py")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='voca-battle'>", unsafe_allow_html=True)
    if st.button("🟥 BATTLE", use_container_width=True, key="voca_battle"):
        st.switch_page("pages/04_VOCA_Battle_Arena.py")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
if st.button("🏠 본부 복귀", use_container_width=True):
    st.switch_page("main_hub.py")

