content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

# HTML 버튼 + 숨기기 코드 전부 제거하고 원래 버튼으로 복원
import re

# components.html 블록 제거
content = re.sub(
    r"        st\.markdown\(\"\"\"<style>\ndiv\[data-testid.*?</style>\"\"\", unsafe_allow_html=True\)\n",
    "",
    content,
    flags=re.DOTALL
)
content = re.sub(
    r"        import streamlit\.components\.v1 as _hc2\n        _hc2\.html\(\"\"\".*?height=180\)\n",
    "",
    content,
    flags=re.DOTALL
)
content = re.sub(
    r"        st\.markdown\('<div style=\"position:absolute;opacity:0.*?</div>', unsafe_allow_html=True\)\n",
    "",
    content,
    flags=re.DOTALL
)

# nth-child CSS로 각 버튼 색상 주입
old = '''        if st.button("🔥  HARD  ·  30초  고수의 선택", key="t30", type="secondary", use_container_width=True):
            st.session_state.tsec=30; st.session_state.tsec_chosen=True; st.rerun()
        if st.button("⚡  NORMAL  ·  40초  표준 전투", key="t40", type="secondary", use_container_width=True):
            st.session_state.tsec=40; st.session_state.tsec_chosen=True; st.rerun()
        if st.button("✅  EASY  ·  50초  여유로운 전투", key="t50", type="secondary", use_container_width=True):
            st.session_state.tsec=50; st.session_state.tsec_chosen=True; st.rerun()'''

new = '''        st.markdown("""<style>
@keyframes pR{0%,100%{box-shadow:0 0 22px rgba(255,34,68,0.8);}50%{box-shadow:0 0 50px rgba(255,34,68,1),0 0 90px rgba(255,0,50,0.6);}}
@keyframes pB{0%,100%{box-shadow:0 0 22px rgba(0,212,255,0.8);}50%{box-shadow:0 0 50px rgba(0,212,255,1),0 0 90px rgba(0,150,255,0.6);}}
@keyframes pG{0%,100%{box-shadow:0 0 22px rgba(0,255,136,0.8);}50%{box-shadow:0 0 50px rgba(0,255,136,1),0 0 90px rgba(0,200,100,0.6);}}
div[data-testid="stVerticalBlock"] > div:nth-child(3) button {
    background:linear-gradient(135deg,#1a0000,#3d0000) !important;
    border:2px solid #ff2244 !important;
    animation:pR 1.8s ease-in-out infinite !important;
    font-size:1.25rem !important; padding:15px !important;
}
div[data-testid="stVerticalBlock"] > div:nth-child(4) button {
    background:linear-gradient(135deg,#00091a,#001a3d) !important;
    border:2px solid #00d4ff !important;
    animation:pB 1.8s ease-in-out infinite !important;
    font-size:1.25rem !important; padding:15px !important;
}
div[data-testid="stVerticalBlock"] > div:nth-child(5) button {
    background:linear-gradient(135deg,#001a08,#003d15) !important;
    border:2px solid #00ff88 !important;
    animation:pG 1.8s ease-in-out infinite !important;
    font-size:1.25rem !important; padding:15px !important;
}
div[data-testid="stVerticalBlock"] > div:nth-child(7) button,
div[data-testid="stVerticalBlock"] > div:nth-child(8) button {
    background:transparent !important;
    border:1px solid #1e1e1e !important;
    box-shadow:none !important; animation:none !important;
    font-size:0.85rem !important; padding:6px !important;
}
div[data-testid="stVerticalBlock"] > div:nth-child(7) button p,
div[data-testid="stVerticalBlock"] > div:nth-child(8) button p {
    font-size:0.85rem !important; color:#444 !important;
}
</style>""", unsafe_allow_html=True)
        if st.button("🔥  HARD  ·  30초  고수의 선택", key="t30", type="secondary", use_container_width=True):
            st.session_state.tsec=30; st.session_state.tsec_chosen=True; st.rerun()
        if st.button("⚡  NORMAL  ·  40초  표준 전투", key="t40", type="secondary", use_container_width=True):
            st.session_state.tsec=40; st.session_state.tsec_chosen=True; st.rerun()
        if st.button("✅  EASY  ·  50초  여유로운 전투", key="t50", type="secondary", use_container_width=True):
            st.session_state.tsec=50; st.session_state.tsec_chosen=True; st.rerun()'''

content = content.replace(old, new)
open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done')