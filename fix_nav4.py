content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

old = """    # ━━━ 항상 고정 네비게이션 ━━━
    st.markdown('<div style="height:4px;border-top:1px solid #111;margin-top:6px;"></div>', unsafe_allow_html=True)
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
    st.markdown(\'\'\'<div style="margin-top:10px;padding-top:8px;border-top:1px solid rgba(255,255,255,0.1);display:flex;justify-content:space-between;gap:8px;">
        <div style="flex:1;"></div>
        <div style="color:rgba(255,255,255,0.15);font-size:0.6rem;letter-spacing:2px;text-align:center;padding-bottom:4px;">─ 다른 곳으로 ─</div>
        <div style="flex:1;"></div>
    </div>\'\'\', unsafe_allow_html=True)
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

# 전체 CSS에 nav 버튼 글로벌 스타일 추가 (로비 CSS 두번째 블록에)
old2 = """.stVerticalBlock{gap:0.2rem!important;}
[data-testid="stVerticalBlock"]>*{margin-bottom:0!important;}
[data-testid="stHorizontalBlock"]{gap:5px!important;margin:0!important;}"""

new2 = """.stVerticalBlock{gap:0.2rem!important;}
[data-testid="stVerticalBlock"]>*{margin-bottom:0!important;}
[data-testid="stHorizontalBlock"]{gap:5px!important;margin:0!important;}
[data-testid="stHorizontalBlock"]:last-of-type button{font-size:0.85rem!important;padding:5px 4px!important;border:1px solid rgba(255,255,255,0.15)!important;background:transparent!important;box-shadow:none!important;animation:none!important;color:#666!important;}
[data-testid="stHorizontalBlock"]:last-of-type button p{font-size:0.85rem!important;color:#666!important;font-weight:500!important;}"""

content = content.replace(old2, new2, 1)

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done')