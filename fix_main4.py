f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

lines[489]='            st.session_state.phase = "lobby"; st.rerun()\n'
lines[490]='        elif _br_nav == "main":\n'
lines[491]='            for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx","phase"]:\n'
lines[492]='                if k in st.session_state: del st.session_state[k]\n'
lines[493]='            st.switch_page("main_hub.py")\n'
lines[494]='    _br_q = st.query_params.get("br_q","")\n'
lines[495]='    if _br_q != "":\n'
lines[496]='        st.query_params.clear()\n'
lines[497]='        st.session_state.br_idx = int(_br_q); st.rerun()\n'

with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)

import ast
src=open(f,'r',encoding='utf-8').read()
try:
    ast.parse(src)
    print('syntax OK!')
except SyntaxError as e:
    print(f'error line {e.lineno}: {e.msg}')
