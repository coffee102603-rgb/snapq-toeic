f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()

# 1. </div> 버그 수정 - round_txt가 비어있을때 </div>텍스트 노출 방지
c=c.replace("    st.markdown(f'''<div class=\"ms-title\">\n        <h1>⚔️ P5 ARENA ⚔️</h1>\n        <p>TOEIC PART 5 · 5문제 서바이벌</p>\n        {round_txt}\n    </div>''', unsafe_allow_html=True)","    st.markdown(f'<div class=\"ms-title\"><h1>⚔️ P5 ARENA ⚔️</h1><p>TOEIC PART 5 · 5문제 서바이벌</p>{round_txt}</div>', unsafe_allow_html=True)")

# 2. 역전장/메인 버튼 → 작고 가로 나란히 (HTML로 교체)
c=c.replace(
"    st.markdown('<div style=\"font-size:0.7rem;color:#333;text-align:center;letter-spacing:3px;margin-top:16px;padding-top:12px;border-top:1px solid #111;\">N A V I G A T E</div>', unsafe_allow_html=True)\n    nc1,nc2 = st.columns(2)\n    with nc1:\n        if st.button(\"🔥 역전장\", key=\"nav_stg\", type=\"secondary\", use_container_width=True):\n            st.switch_page(\"pages/03_역전장.py\")\n    with nc2:\n        if st.button(\"🏠 메인\", key=\"nav_hub\", type=\"secondary\", use_container_width=True):\n            st.session_state._p5_just_left = True\n            st.session_state.ans = False\n            st.session_state[\"_battle_entry_ans_reset\"] = True\n            st.switch_page(\"main_hub.py\")",
"    st.markdown('<div style=\"margin-top:16px;padding-top:10px;border-top:1px solid #111;text-align:center;\"><span style=\"font-size:0.6rem;color:#333;letter-spacing:3px;\">N A V I G A T E</span><div style=\"display:flex;gap:8px;justify-content:center;margin-top:6px;\"><a href=\"?nav=stg\" target=\"_self\" style=\"padding:6px 18px;font-size:0.85rem;font-weight:700;color:#aaa;border:1px solid #333;border-radius:8px;text-decoration:none;background:#0a0a0a;\">🔥 역전장</a><a href=\"?nav=hub\" target=\"_self\" style=\"padding:6px 18px;font-size:0.85rem;font-weight:700;color:#aaa;border:1px solid #333;border-radius:8px;text-decoration:none;background:#0a0a0a;\">🏠 메인</a></div></div>', unsafe_allow_html=True)"
)

open(f,'w',encoding='utf-8').write(c)
print('done!')
