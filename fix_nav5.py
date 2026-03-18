content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

old = """    # ━━━ 항상 고정 네비게이션 ━━━
    st.markdown(\"\"\"<style>
.nav-row button{
    font-size:0.96rem!important;
    padding:5px 6px!important;
    border:1px solid rgba(255,255,255,0.2)!important;
    background:transparent!important;
    box-shadow:none!important;
    border-radius:8px!important;
    animation:none!important;
}
.nav-row button p{
    font-size:0.96rem!important;
    color:#888!important;
    font-weight:500!important;
}
</style>\"\"\", unsafe_allow_html=True)
    st.markdown('<div class="nav-row">', unsafe_allow_html=True)
    nc1,_,nc2 = st.columns([1,1,1])
    with nc1:
        if st.button("🔥 역전장", key="nav_stg", type="secondary", use_container_width=True):
            st.switch_page("pages/03_역전장.py")
    with nc2:
        if st.button("🏠 메인", key="nav_hub", type="secondary", use_container_width=True):
            st.session_state._p5_just_left = True
            st.session_state.ans = False
            st.session_state["_battle_entry_ans_reset"] = True
            st.switch_page("main_hub.py")
    st.markdown('</div>', unsafe_allow_html=True)"""

new = """    # ━━━ 항상 고정 네비게이션 ━━━
    st.markdown('<div style="margin-top:8px;padding-top:6px;border-top:1px solid rgba(255,255,255,0.08);text-align:center;"><span style="font-size:0.6rem;color:rgba(255,255,255,0.2);letter-spacing:2px;">─ 다른 곳으로 ─</span></div>', unsafe_allow_html=True)
    nc1,_,nc2 = st.columns([2,1,2])
    with nc1:
        if st.button("🔥 역전장", key="nav_stg", type="secondary", use_container_width=True):
            st.switch_page("pages/03_역전장.py")
    with nc2:
        if st.button("🏠 메인", key="nav_hub", type="secondary", use_container_width=True):
            st.session_state._p5_just_left = True
            st.session_state.ans = False
            st.session_state["_battle_entry_ans_reset"] = True
            st.switch_page("main_hub.py")"""

content = content.replace(old, new)
print('nav replaced:', '다른 곳으로' in content)

old2 = """[data-testid="stHorizontalBlock"]{gap:5px!important;margin:0!important;}"""
new2 = """[data-testid="stHorizontalBlock"]{gap:5px!important;margin:0!important;}
[data-testid="stHorizontalBlock"]:last-of-type button{font-size:0.85rem!important;padding:5px 4px!important;border:1px solid rgba(255,255,255,0.15)!important;background:transparent!important;box-shadow:none!important;animation:none!important;}
[data-testid="stHorizontalBlock"]:last-of-type button p{font-size:0.85rem!important;color:#555!important;font-weight:500!important;}"""

content = content.replace(old2, new2, 1)
print('css replaced:', 'last-of-type' in content)

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done')