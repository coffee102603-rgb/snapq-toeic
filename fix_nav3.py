f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
old="""# PHASE: LOBBY
# ════════════════════════════════════════
else:
    st.session_state.phase="lobby"
    if "sel_mode" not in st.session_state: st.session_state.sel_mode=None"""
new="""# PHASE: LOBBY
# ════════════════════════════════════════
else:
    _nav = st.query_params.get('nav', '')
    if _nav == 'hub':
        st.query_params.clear()
        st.session_state._p5_just_left = True
        st.session_state.ans = False
        st.session_state["_battle_entry_ans_reset"] = True
        st.switch_page("main_hub.py")
    elif _nav == 'stg':
        st.query_params.clear()
        st.switch_page("pages/03_역전장.py")
    st.session_state.phase="lobby"
    if "sel_mode" not in st.session_state: st.session_state.sel_mode=None"""
if old in c:
    open(f,'w',encoding='utf-8').write(c.replace(old,new))
    print('done!')
else:
    print('매칭실패')
