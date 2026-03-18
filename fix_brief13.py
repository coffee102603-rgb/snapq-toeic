f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

# 538~583 (0-indexed: 537~582) 교체
new_lines=[
'    if was_victory:\r\n',
'        bc = st.columns(2)\r\n',
'        with bc[0]:\r\n',
'            if st.button("로비", type="secondary", use_container_width=True):\r\n',
'                for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx"]:\r\n',
'                    if k in st.session_state: del st.session_state[k]\r\n',
'                for k,v in D.items():\r\n',
'                    if k not in st.session_state: st.session_state[k]=v\r\n',
'                st.session_state.phase = "lobby"; st.rerun()\r\n',
'        with bc[1]:\r\n',
'            if st.button("메인", type="secondary", use_container_width=True):\r\n',
'                st.session_state._p5_just_left = True\r\n',
'                st.session_state.ans = False\r\n',
'                st.session_state["_battle_entry_ans_reset"] = True\r\n',
'                st.switch_page("main_hub.py")\r\n',
'    else:\r\n',
'        bc = st.columns(2)\r\n',
'        with bc[0]:\r\n',
'            if st.button("로비", type="secondary", use_container_width=True):\r\n',
'                for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx"]:\r\n',
'                    if k in st.session_state: del st.session_state[k]\r\n',
'                for k,v in D.items():\r\n',
'                    if k not in st.session_state: st.session_state[k]=v\r\n',
'                st.session_state.phase = "lobby"; st.rerun()\r\n',
'        with bc[1]:\r\n',
'            if st.button("메인", type="secondary", use_container_width=True):\r\n',
'                st.session_state._p5_just_left = True\r\n',
'                st.session_state.ans = False\r\n',
'                st.session_state["_battle_entry_ans_reset"] = True\r\n',
'                st.switch_page("main_hub.py")\r\n',
]
lines[537:582]=new_lines
with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)
print('done! lines:', len(lines))
