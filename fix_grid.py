f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
old="""        b1,b2 = st.columns(2)
        with b1:
            if st.button("⚔\\n문법력\\n수일치·시제·수동", key="sg1", type="secondary", use_container_width=True):
                st.session_state.sel_mode="g1"; st.rerun()
        with b2:
            if st.button("⚔\\n구조력\\n가정법·도치·당위", key="sg2", type="secondary", use_container_width=True):
                st.session_state.sel_mode="g2"; st.rerun()
        b3,b4 = st.columns(2)
        with b3:
            if st.button("⚔\\n연결력\\n접속사·관계사·분사", key="sg3", type="secondary", use_container_width=True):
                st.session_state.sel_mode="g3"; st.rerun()
        with b4:
            if st.button("📘\\n어휘력\\n품사·동사·콜로케이션", key="svc", type="secondary", use_container_width=True):
                st.session_state.sel_mode="vocab"; st.rerun()"""
new="""        st.markdown(\'\'\'<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:4px 0;">
        <button onclick="window.location.href=\'?cat=g1\'" style="background:#060e18;border:2px solid rgba(0,212,255,0.35);border-radius:10px;padding:10px 4px;color:#e0e0e0;font-size:0.85rem;font-weight:900;cursor:pointer;line-height:1.3;text-align:center;">⚔<br>문법력<br><span style="font-size:0.75rem;color:#aaa;">수일치·시제·수동</span></button>
        <button onclick="window.location.href=\'?cat=g2\'" style="background:#060e18;border:2px solid rgba(0,212,255,0.35);border-radius:10px;padding:10px 4px;color:#e0e0e0;font-size:0.85rem;font-weight:900;cursor:pointer;line-height:1.3;text-align:center;">⚔<br>구조력<br><span style="font-size:0.75rem;color:#aaa;">가정법·도치·당위</span></button>
        <button onclick="window.location.href=\'?cat=g3\'" style="background:#060e18;border:2px solid rgba(0,212,255,0.35);border-radius:10px;padding:10px 4px;color:#e0e0e0;font-size:0.85rem;font-weight:900;cursor:pointer;line-height:1.3;text-align:center;">⚔<br>연결력<br><span style="font-size:0.75rem;color:#aaa;">접속사·관계사·분사</span></button>
        <button onclick="window.location.href=\'?cat=vc\'" style="background:#060e18;border:2px solid rgba(0,212,255,0.35);border-radius:10px;padding:10px 4px;color:#e0e0e0;font-size:0.85rem;font-weight:900;cursor:pointer;line-height:1.3;text-align:center;">📘<br>어휘력<br><span style="font-size:0.75rem;color:#aaa;">품사·동사·콜로케이션</span></button>
        </div>\'\'\', unsafe_allow_html=True)
        _cat = st.query_params.get('cat','')
        if _cat == 'g1': st.query_params.clear(); st.session_state.sel_mode="g1"; st.rerun()
        elif _cat == 'g2': st.query_params.clear(); st.session_state.sel_mode="g2"; st.rerun()
        elif _cat == 'g3': st.query_params.clear(); st.session_state.sel_mode="g3"; st.rerun()
        elif _cat == 'vc': st.query_params.clear(); st.session_state.sel_mode="vocab"; st.rerun()"""
if old in c:
    open(f,'w',encoding='utf-8').write(c.replace(old,new))
    print('done!')
else:
    print('매칭실패')
