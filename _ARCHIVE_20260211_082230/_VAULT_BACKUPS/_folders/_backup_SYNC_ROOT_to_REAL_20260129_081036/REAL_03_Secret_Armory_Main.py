# ===== SNAPQ ARMORY TRACE BANNER (AUTO) =====
try:
    import streamlit as st
    st.error("🔥 SECRET ARMORY FILE LOADED: __FILE__ = " + __file__)
except Exception:
    pass
# ===========================================
import sys
import streamlit as st

ROOT = r"C:\Users\최정은\Desktop\SNAPQ_TOEIC"
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

def main():
    st.set_page_config(page_title="SnapQ TOEIC • Secret Armory", layout="wide")

    # bottom padding (avoid cut-off)
    st.markdown(
        '<style>.stApp{padding-bottom:220px!important;}.main .block-container{padding-bottom:220px!important;}</style>',
        unsafe_allow_html=True
    )

    from app.arenas import secret_armory as arena

    if hasattr(arena, "render") and callable(arena.render):
        arena.render()
    else:
        st.error("secret_armory.py has no callable render().")

    st.markdown('<div style="height:220px"></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

