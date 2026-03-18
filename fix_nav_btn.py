f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

# 568~572 (0-indexed 567~571) nav_html 블록을 st.button으로 교체
new_lines = [
    '    _nav_cols = st.columns(2)\n',
    '    with _nav_cols[0]:\n',
    '        if st.button("로비", key="br_nav_lobby", use_container_width=True):\n',
    '            for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx"]:\n',
    '                if k in st.session_state: del st.session_state[k]\n',
    '            st.session_state.phase = "lobby"; st.rerun()\n',
    '    with _nav_cols[1]:\n',
    '        if st.button("메인", key="br_nav_main", use_container_width=True):\n',
    '            for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx","phase"]:\n',
    '                if k in st.session_state: del st.session_state[k]\n',
    '            st.switch_page("main_hub.py")\n',
]
lines[567:572] = new_lines

with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)

import ast
src=open(f,'r',encoding='utf-8').read()
try:
    ast.parse(src)
    print('syntax OK!')
except SyntaxError as e:
    print(f'error line {e.lineno}: {e.msg}')
