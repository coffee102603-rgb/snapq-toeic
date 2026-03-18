content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

# 기존 timerBlaze 애니메이션 뒤에 색상 애니메이션 추가
old = "@keyframes timerBlaze{"
new = """@keyframes tPulseR{0%,100%{box-shadow:0 0 20px rgba(255,34,68,0.7),inset 0 0 20px rgba(255,0,50,0.1);border-color:#ff2244;}50%{box-shadow:0 0 45px rgba(255,34,68,1),0 0 80px rgba(255,0,50,0.5),inset 0 0 30px rgba(255,0,50,0.2);border-color:#ff6688;}}
@keyframes tPulseB{0%,100%{box-shadow:0 0 20px rgba(0,212,255,0.7),inset 0 0 20px rgba(0,150,255,0.1);border-color:#00d4ff;}50%{box-shadow:0 0 45px rgba(0,212,255,1),0 0 80px rgba(0,150,255,0.5),inset 0 0 30px rgba(0,150,255,0.2);border-color:#88eeff;}}
@keyframes tPulseG{0%,100%{box-shadow:0 0 20px rgba(0,255,136,0.7),inset 0 0 20px rgba(0,200,100,0.1);border-color:#00ff88;}50%{box-shadow:0 0 45px rgba(0,255,136,1),0 0 80px rgba(0,200,100,0.5),inset 0 0 30px rgba(0,200,100,0.2);border-color:#88ffcc;}}
@keyframes timerBlaze{"""

content = content.replace(old, new, 1)

# 타이머 버튼 직접 스타일 주입 (Python 레벨)
old2 = """        if st.button("🔥  HARD  ·  30초  고수의 선택", key="t30", type="secondary", use_container_width=True):
            st.session_state.tsec=30; st.session_state.tsec_chosen=True; st.rerun()
        if st.button("⚡  NORMAL  ·  40초  표준 전투", key="t40", type="secondary", use_container_width=True):
            st.session_state.tsec=40; st.session_state.tsec_chosen=True; st.rerun()
        if st.button("✅  EASY  ·  50초  여유로운 전투", key="t50", type="secondary", use_container_width=True):
            st.session_state.tsec=50; st.session_state.tsec_chosen=True; st.rerun()"""

new2 = """        st.markdown(\"\"\"<style>
div[data-testid="stButton"]:has(button[kind="secondary"]:nth-of-type(1)) button,
div[data-testid="element-container"]:has(#t30) button{background:linear-gradient(135deg,#1a0000,#3d0000)!important;border:2px solid #ff2244!important;animation:tPulseR 1.8s ease-in-out infinite!important;}
div[data-testid="element-container"]:has(#t40) button{background:linear-gradient(135deg,#00091a,#001a3d)!important;border:2px solid #00d4ff!important;animation:tPulseB 1.8s ease-in-out infinite!important;}
div[data-testid="element-container"]:has(#t50) button{background:linear-gradient(135deg,#001a08,#003d15)!important;border:2px solid #00ff88!important;animation:tPulseG 1.8s ease-in-out infinite!important;}
div[data-testid="element-container"]:has(#nav_stg) button,div[data-testid="element-container"]:has(#nav_hub) button{background:transparent!important;border:1px solid #1e1e1e!important;box-shadow:none!important;animation:none!important;}
div[data-testid="element-container"]:has(#nav_stg) button p,div[data-testid="element-container"]:has(#nav_hub) button p{font-size:0.85rem!important;color:#444!important;}
</style>\"\"\", unsafe_allow_html=True)
        if st.button("🔥  HARD  ·  30초  고수의 선택", key="t30", type="secondary", use_container_width=True):
            st.session_state.tsec=30; st.session_state.tsec_chosen=True; st.rerun()
        if st.button("⚡  NORMAL  ·  40초  표준 전투", key="t40", type="secondary", use_container_width=True):
            st.session_state.tsec=40; st.session_state.tsec_chosen=True; st.rerun()
        if st.button("✅  EASY  ·  50초  여유로운 전투", key="t50", type="secondary", use_container_width=True):
            st.session_state.tsec=50; st.session_state.tsec_chosen=True; st.rerun()"""

content = content.replace(old2, new2)
open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done:', 'tPulseR' in content)