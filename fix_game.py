content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

# ── 1. 타이머 버튼 3개 교체 (난이도 선택 느낌)
content = content.replace(
    'if st.button("🔥  30초  ·  고수의 선택", key="t30", type="secondary", use_container_width=True):\n            st.session_state.tsec=30; st.session_state.tsec_chosen=True; st.rerun()\n        if st.button("⚡  40초  ·  표준 전투", key="t40", type="secondary", use_container_width=True):\n            st.session_state.tsec=40; st.session_state.tsec_chosen=True; st.rerun()\n        if st.button("✅  50초  ·  여유로운 전투", key="t50", type="secondary", use_container_width=True):\n            st.session_state.tsec=50; st.session_state.tsec_chosen=True; st.rerun()',
    '''st.markdown("""
<style>
.timer-wrap{display:flex;flex-direction:column;gap:8px;margin:6px 0;}
.t-hard{background:linear-gradient(135deg,#1a0000,#3d0000)!important;border:2px solid #ff2244!important;box-shadow:0 0 18px rgba(255,34,68,0.6),inset 0 1px 0 rgba(255,100,100,0.2)!important;border-radius:14px!important;padding:14px!important;}
.t-norm{background:linear-gradient(135deg,#00091a,#001a3d)!important;border:2px solid #00d4ff!important;box-shadow:0 0 18px rgba(0,212,255,0.6),inset 0 1px 0 rgba(100,220,255,0.2)!important;border-radius:14px!important;padding:14px!important;}
.t-easy{background:linear-gradient(135deg,#001a08,#003d15)!important;border:2px solid #00ff88!important;box-shadow:0 0 18px rgba(0,255,136,0.6),inset 0 1px 0 rgba(100,255,180,0.2)!important;border-radius:14px!important;padding:14px!important;}
button.t-hard,button.t-norm,button.t-easy{font-size:1.3rem!important;font-weight:900!important;padding:14px!important;border-radius:14px!important;}
@keyframes tPulseR{0%,100%{box-shadow:0 0 18px rgba(255,34,68,0.6);}50%{box-shadow:0 0 35px rgba(255,34,68,1),0 0 60px rgba(255,0,50,0.5);}}
@keyframes tPulseB{0%,100%{box-shadow:0 0 18px rgba(0,212,255,0.6);}50%{box-shadow:0 0 35px rgba(0,212,255,1),0 0 60px rgba(0,150,255,0.5);}}
@keyframes tPulseG{0%,100%{box-shadow:0 0 18px rgba(0,255,136,0.6);}50%{box-shadow:0 0 35px rgba(0,255,136,1),0 0 60px rgba(0,200,100,0.5);}}
</style>""", unsafe_allow_html=True)
        c1=st.columns(1)
        if st.button("🔥  HARD  ·  30초  고수의 선택", key="t30", type="secondary", use_container_width=True):
            st.session_state.tsec=30; st.session_state.tsec_chosen=True; st.rerun()
        if st.button("⚡  NORMAL  ·  40초  표준 전투", key="t40", type="secondary", use_container_width=True):
            st.session_state.tsec=40; st.session_state.tsec_chosen=True; st.rerun()
        if st.button("✅  EASY  ·  50초  여유로운 전투", key="t50", type="secondary", use_container_width=True):
            st.session_state.tsec=50; st.session_state.tsec_chosen=True; st.rerun()'''
)

# ── 2. 역전장/메인 버튼 작고 조용하게
content = content.replace(
    "st.markdown('<div style=\"height:2px;\"></div>', unsafe_allow_html=True)\n    nc1,nc2 = st.columns(2)\n    with nc1:\n        if st.button(\"🔥 역전장\", key=\"nav_stg\", type=\"secondary\", use_container_width=True):\n            st.switch_page(\"pages/03_역전장.py\")\n    with nc2:\n        if st.button(\"🏠 메인\", key=\"nav_hub\", type=\"secondary\", use_container_width=True):\n            st.session_state._p5_just_left = True\n            st.session_state.ans = False\n            st.session_state[\"_battle_entry_ans_reset\"] = True\n            st.switch_page(\"main_hub.py\")",
    """st.markdown('<div style="height:4px;border-top:1px solid #1a1a1a;margin-top:6px;"></div>', unsafe_allow_html=True)
    st.markdown(\"\"\"<style>
.nav-btn button{background:transparent!important;border:1px solid #222!important;color:#444!important;font-size:0.85rem!important;padding:6px!important;box-shadow:none!important;border-radius:8px!important;}
.nav-btn button p{font-size:0.85rem!important;color:#555!important;font-weight:600!important;}
.nav-btn button:hover{border-color:#444!important;color:#888!important;background:rgba(255,255,255,0.03)!important;}
</style>\"\"\", unsafe_allow_html=True)
    nc1,nc2 = st.columns(2)
    with nc1:
        with st.container():
            st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
            if st.button("🔥 역전장", key="nav_stg", type="secondary", use_container_width=True):
                st.switch_page("pages/03_역전장.py")
            st.markdown('</div>', unsafe_allow_html=True)
    with nc2:
        with st.container():
            st.markdown('<div class="nav-btn">', unsafe_allow_html=True)
            if st.button("🏠 메인", key="nav_hub", type="secondary", use_container_width=True):
                st.session_state._p5_just_left = True
                st.session_state.ans = False
                st.session_state["_battle_entry_ans_reset"] = True
                st.switch_page("main_hub.py")
            st.markdown('</div>', unsafe_allow_html=True)"""
)

# ── 3. 시작 버튼 골드 펄스로 강조
content = content.replace(
    "if st.button(f\"▶  {_cat} 전투 시작!\", key=\"go_start\", type=\"primary\", use_container_width=True):",
    """st.markdown(\"\"\"<style>
@keyframes goldPulse{0%,100%{box-shadow:0 0 20px rgba(255,215,0,0.7),0 0 40px rgba(255,150,0,0.4);border-color:rgba(255,215,0,0.9);}50%{box-shadow:0 0 40px rgba(255,215,0,1),0 0 80px rgba(255,150,0,0.8),0 0 120px rgba(255,100,0,0.4);border-color:#fff;}}
[data-testid="stButton"]:first-of-type button{background:linear-gradient(135deg,#1a0d00,#3d2000,#1a0d00)!important;border:2px solid rgba(255,215,0,0.9)!important;animation:goldPulse 1.5s ease-in-out infinite!important;font-size:1.6rem!important;padding:18px!important;border-radius:16px!important;color:#ffd700!important;letter-spacing:2px!important;}
</style>\"\"\", unsafe_allow_html=True)
        if st.button(f"▶  {_cat} 전투 시작!", key="go_start", type="primary", use_container_width=True):"""
)

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done')