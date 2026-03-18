lines = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').readlines()

new_lobby = '''    # ━━━ 1막: 타이머 선택 ━━━
    if not _tsec_chosen:
        from streamlit_extras.stylable_container import stylable_container
        st.markdown(\'\'\'<div class="stage stage-act">
            <div class="act-label">🎬 1 막 · 전투 시간을 선택하라!</div>
            <div class="act-msg">전사여, <span class="hi">몇 초</span>의 시간을 원하느냐?</div>
        </div>\'\'\', unsafe_allow_html=True)
        st.markdown("""<style>
@keyframes pR{0%,100%{box-shadow:0 0 20px rgba(255,34,68,0.8);}50%{box-shadow:0 0 50px rgba(255,34,68,1),0 0 90px rgba(255,0,50,0.5);}}
@keyframes pB{0%,100%{box-shadow:0 0 20px rgba(0,212,255,0.8);}50%{box-shadow:0 0 50px rgba(0,212,255,1),0 0 90px rgba(0,150,255,0.5);}}
@keyframes pG{0%,100%{box-shadow:0 0 20px rgba(0,255,136,0.8);}50%{box-shadow:0 0 50px rgba(0,255,136,1),0 0 90px rgba(0,200,100,0.5);}}
</style>""", unsafe_allow_html=True)
        with stylable_container(key="t30", css_styles="""button{background:linear-gradient(135deg,#200008,#450010)!important;border:2px solid #ff2244!important;animation:pR 1.8s ease-in-out infinite!important;font-size:1.25rem!important;padding:15px!important;color:#ffaabb!important;}"""):
            if st.button("🔥  HARD · 30초  고수의 선택", key="t30", type="secondary", use_container_width=True):
                st.session_state.tsec=30; st.session_state.tsec_chosen=True; st.rerun()
        with stylable_container(key="t40", css_styles="""button{background:linear-gradient(135deg,#000820,#001045)!important;border:2px solid #00d4ff!important;animation:pB 1.8s ease-in-out infinite!important;font-size:1.25rem!important;padding:15px!important;color:#aaeeff!important;}"""):
            if st.button("⚡  NORMAL · 40초  표준 전투", key="t40", type="secondary", use_container_width=True):
                st.session_state.tsec=40; st.session_state.tsec_chosen=True; st.rerun()
        with stylable_container(key="t50", css_styles="""button{background:linear-gradient(135deg,#002010,#004525)!important;border:2px solid #00ff88!important;animation:pG 1.8s ease-in-out infinite!important;font-size:1.25rem!important;padding:15px!important;color:#aaffcc!important;}"""):
            if st.button("✅  EASY · 50초  여유로운 전투", key="t50", type="secondary", use_container_width=True):
                st.session_state.tsec=50; st.session_state.tsec_chosen=True; st.rerun()

    # ━━━ 2막: 카테고리 선택 ━━━
    elif _tsec_chosen and not (sm and sm in ["g1","g2","g3","vocab"]):
        from streamlit_extras.stylable_container import stylable_container
        st.markdown(f\'\'\'<div class="confirmed"><span>⏱ {_tsec}초 확정!</span></div>\'\'\', unsafe_allow_html=True)
        st.markdown(\'\'\'<div class="stage stage-act">
            <div class="act-label">🎬 2 막 · 전장을 선택하라!</div>
            <div class="act-msg">이제 <span class="gold">어느 전장</span>에서 싸울 것이냐?</div>
        </div>\'\'\', unsafe_allow_html=True)
        st.markdown("""<style>
@keyframes pBlu{0%,100%{box-shadow:0 0 18px rgba(79,195,247,0.8);}50%{box-shadow:0 0 45px rgba(79,195,247,1),0 0 80px rgba(30,150,255,0.5);}}
@keyframes pPur{0%,100%{box-shadow:0 0 18px rgba(155,127,212,0.8);}50%{box-shadow:0 0 45px rgba(155,127,212,1),0 0 80px rgba(120,60,200,0.5);}}
@keyframes pGrn{0%,100%{box-shadow:0 0 18px rgba(0,220,130,0.8);}50%{box-shadow:0 0 45px rgba(0,220,130,1),0 0 80px rgba(0,180,100,0.5);}}
@keyframes pGld{0%,100%{box-shadow:0 0 18px rgba(255,215,0,0.8);}50%{box-shadow:0 0 45px rgba(255,215,0,1),0 0 80px rgba(255,150,0,0.5);}}
</style>""", unsafe_allow_html=True)
        b1,b2 = st.columns(2)
        with b1:
            with stylable_container(key="sg1", css_styles="""button{background:linear-gradient(135deg,#020d1f,#0a2558)!important;border:2px solid #4fc3f7!important;animation:pBlu 1.8s ease-in-out infinite!important;color:#aaddff!important;white-space:pre-line!important;}"""):
                if st.button("⚔ 문법력\n수일치·시제·수동", key="sg1", type="secondary", use_container_width=True):
                    st.session_state.sel_mode="g1"; st.rerun()
        with b2:
            with stylable_container(key="sg2", css_styles="""button{background:linear-gradient(135deg,#0a0418,#2a1058)!important;border:2px solid #9b7fd4!important;animation:pPur 1.8s ease-in-out infinite!important;color:#ddbbff!important;white-space:pre-line!important;}"""):
                if st.button("⚔ 구조력\n가정법·도치·당위", key="sg2", type="secondary", use_container_width=True):
                    st.session_state.sel_mode="g2"; st.rerun()
        b3,b4 = st.columns(2)
        with b3:
            with stylable_container(key="sg3", css_styles="""button{background:linear-gradient(135deg,#021a08,#0a5025)!important;border:2px solid #00dc82!important;animation:pGrn 1.8s ease-in-out infinite!important;color:#aaffcc!important;white-space:pre-line!important;}"""):
                if st.button("⚔ 연결력\n접속사·관계사·분사", key="sg3", type="secondary", use_container_width=True):
                    st.session_state.sel_mode="g3"; st.rerun()
        with b4:
            with stylable_container(key="svc", css_styles="""button{background:linear-gradient(135deg,#1a0d00,#4a2800)!important;border:2px solid #ffd700!important;animation:pGld 1.8s ease-in-out infinite!important;color:#ffe88a!important;white-space:pre-line!important;}"""):
                if st.button("📘 어휘력\n품사·동사·콜로케이션", key="svc", type="secondary", use_container_width=True):
                    st.session_state.sel_mode="vocab"; st.rerun()

    # ━━━ 3막: START ━━━
    elif sm and sm in ["g1","g2","g3","vocab"]:
        from streamlit_extras.stylable_container import stylable_container
        _cat = lbl_map.get(sm,\'\')
        _t = f"{_tsec}초"
        st.markdown(f\'\'\'<div class="confirmed"><span>⏱ {_t} · {_cat} 확정!</span></div>\'\'\', unsafe_allow_html=True)
        st.markdown(f\'\'\'<div class="stage stage-act" style="text-align:center;padding:20px 12px;">
            <div class="act-label">🎬 3 막 · 전투 개시!</div>
            <div class="act-msg" style="font-size:1.4rem;margin-bottom:4px;">
                전사여... <span class="go">준비됐다면</span><br>지금 바로 <span class="gold">시작하라!!!</span>
            </div>
        </div>\'\'\', unsafe_allow_html=True)
        st.markdown("""<style>
@keyframes goldPulse{0%,100%{box-shadow:0 0 25px rgba(255,215,0,0.8);}50%{box-shadow:0 0 60px rgba(255,215,0,1),0 0 100px rgba(255,100,0,0.5);}}
</style>""", unsafe_allow_html=True)
        with stylable_container(key="go_start", css_styles="""button{background:linear-gradient(135deg,#1a0d00,#3d2000)!important;border:2px solid #ffd700!important;animation:goldPulse 1.5s ease-in-out infinite!important;font-size:1.5rem!important;padding:18px!important;color:#ffd700!important;letter-spacing:2px!important;}"""):
            if st.button(f"▶  {_cat} 전투 시작!", key="go_start", type="primary", use_container_width=True):
                md,grp=mode_map[sm]
                st.session_state.mode=md; qs=pick5(md,grp)
                st.session_state.round_qs=qs; st.session_state.cq=qs[0]
                st.session_state.qst=time.time(); st.session_state.phase="battle"; st.rerun()
        with stylable_container(key="reset_lobby", css_styles="""button{background:transparent!important;border:1px solid #1e1e1e!important;box-shadow:none!important;animation:none!important;padding:8px!important;} button p{font-size:0.9rem!important;color:#444!important;}"""):
            if st.button("↩ 다시 선택", key="reset_lobby", use_container_width=True):
                st.session_state.tsec=30; st.session_state.tsec_chosen=False; st.session_state.sel_mode=None; st.rerun()

    # ━━━ 네비게이션 ━━━
    st.markdown(\'<div style="height:4px;border-top:1px solid #111;margin-top:6px;"></div>\', unsafe_allow_html=True)
    from streamlit_extras.stylable_container import stylable_container
    nc1,nc2 = st.columns(2)
    with nc1:
        with stylable_container(key="nav_stg", css_styles="""button{background:transparent!important;border:1px solid #1a1a1a!important;box-shadow:none!important;animation:none!important;padding:7px!important;} button p{font-size:0.85rem!important;color:#444!important;}"""):
            if st.button("🔥 역전장", key="nav_stg", type="secondary", use_container_width=True):
                st.switch_page("pages/03_역전장.py")
    with nc2:
        with stylable_container(key="nav_hub", css_styles="""button{background:transparent!important;border:1px solid #1a1a1a!important;box-shadow:none!important;animation:none!important;padding:7px!important;} button p{font-size:0.85rem!important;color:#444!important;}"""):
            if st.button("🏠 메인", key="nav_hub", type="secondary", use_container_width=True):
                st.session_state._p5_just_left = True
                st.session_state.ans = False
                st.session_state["_battle_entry_ans_reset"] = True
                st.switch_page("main_hub.py")
'''

new_lines = lines[:755] + [new_lobby] + lines[821:]
open('pages/02_P5_Arena.py', 'w', encoding='utf-8').writelines(new_lines)
print('done')