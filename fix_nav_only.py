# -*- coding: utf-8 -*-
content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

old = '    # ━━━ 항상 고정 네비게이션 ━━━\n    st.markdown(\'<div style="font-size:0.7rem;color:#333;text-align:center;letter-spacing:3px;margin-top:4px;padding-top:5px;border-top:1px solid #111;">N A V I G A T E</div>\', unsafe_allow_html=True)\n    nc1,nc2 = st.columns(2)\n    with nc1:\n        if st.button("\U0001f525 \uc5ed\uc804\uc7a5", key="nav_stg", type="secondary", use_container_width=True):\n            st.switch_page("pages/03_\uc5ed\uc804\uc7a5.py")\n    with nc2:\n        if st.button("\U0001f3e0 \uba54\uc778", key="nav_hub", type="secondary", use_container_width=True):\n            st.session_state._p5_just_left = True\n            st.session_state.ans = False\n            st.session_state["_battle_entry_ans_reset"] = True\n            st.switch_page("main_hub.py")'

new = '    # ━━━ 항상 고정 네비게이션 ━━━\n    _nav = st.query_params.get("nav","")\n    if _nav == "stg": st.switch_page("pages/03_\uc5ed\uc804\uc7a5.py")\n    if _nav == "hub":\n        st.session_state._p5_just_left = True\n        st.session_state.ans = False\n        st.session_state["_battle_entry_ans_reset"] = True\n        st.switch_page("main_hub.py")\n    st.markdown(\'<div style="margin-top:8px;padding-top:6px;border-top:1px solid rgba(255,255,255,0.08);text-align:center;"><span style="font-size:0.6rem;color:rgba(255,255,255,0.2);letter-spacing:2px;">\u2500 \ub2e4\ub978 \uacf3\uc73c\ub85c \u2500</span></div><div style="display:flex;gap:8px;margin-top:6px;"><a href="?nav=stg" target="_self" style="flex:0.8;display:block;text-align:center;padding:8px 4px;font-size:0.9rem;color:#666;border:1px solid rgba(255,255,255,0.15);border-radius:8px;text-decoration:none;background:transparent;">\U0001f525 \uc5ed\uc804\uc7a5</a><a href="?nav=hub" target="_self" style="flex:0.8;display:block;text-align:center;padding:8px 4px;font-size:0.9rem;color:#666;border:1px solid rgba(255,255,255,0.15);border-radius:8px;text-decoration:none;background:transparent;">\U0001f3e0 \uba54\uc778</a></div>\', unsafe_allow_html=True)'

r = content.replace(old, new, 1)
print('nav replaced:', r != content)
content = r

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
c = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()
print('다른 곳으로:', '다른 곳으로' in c)
print('done!')
# -*- coding: utf-8 -*-
content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

old = '    # ━━━ 항상 고정 네비게이션 ━━━\n    st.markdown(\'<div style="font-size:0.7rem;color:#333;text-align:center;letter-spacing:3px;margin-top:4px;padding-top:5px;border-top:1px solid #111;">N A V I G A T E</div>\', unsafe_allow_html=True)\n    nc1,nc2 = st.columns(2)\n    with nc1:\n        if st.button("\U0001f525 \uc5ed\uc804\uc7a5", key="nav_stg", type="secondary", use_container_width=True):\n            st.switch_page("pages/03_\uc5ed\uc804\uc7a5.py")\n    with nc2:\n        if st.button("\U0001f3e0 \uba54\uc778", key="nav_hub", type="secondary", use_container_width=True):\n            st.session_state._p5_just_left = True\n            st.session_state.ans = False\n            st.session_state["_battle_entry_ans_reset"] = True\n            st.switch_page("main_hub.py")'

new = '    # ━━━ 항상 고정 네비게이션 ━━━\n    _nav = st.query_params.get("nav","")\n    if _nav == "stg": st.switch_page("pages/03_\uc5ed\uc804\uc7a5.py")\n    if _nav == "hub":\n        st.session_state._p5_just_left = True\n        st.session_state.ans = False\n        st.session_state["_battle_entry_ans_reset"] = True\n        st.switch_page("main_hub.py")\n    st.markdown(\'<div style="margin-top:8px;padding-top:6px;border-top:1px solid rgba(255,255,255,0.08);text-align:center;"><span style="font-size:0.6rem;color:rgba(255,255,255,0.2);letter-spacing:2px;">\u2500 \ub2e4\ub978 \uacf3\uc73c\ub85c \u2500</span></div><div style="display:flex;gap:8px;margin-top:6px;"><a href="?nav=stg" target="_self" style="flex:0.8;display:block;text-align:center;padding:8px 4px;font-size:0.9rem;color:#666;border:1px solid rgba(255,255,255,0.15);border-radius:8px;text-decoration:none;background:transparent;">\U0001f525 \uc5ed\uc804\uc7a5</a><a href="?nav=hub" target="_self" style="flex:0.8;display:block;text-align:center;padding:8px 4px;font-size:0.9rem;color:#666;border:1px solid rgba(255,255,255,0.15);border-radius:8px;text-decoration:none;background:transparent;">\U0001f3e0 \uba54\uc778</a></div>\', unsafe_allow_html=True)'

r = content.replace(old, new, 1)
print('nav replaced:', r != content)
content = r

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
c = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()
print('다른 곳으로:', '다른 곳으로' in c)
print('done!')
