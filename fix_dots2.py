f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

# 556~561 dot_html → st.button으로 교체
new_dots=[
'    dot_cols = st.columns(num_qs)\n',
'    for _di in range(num_qs):\n',
'        with dot_cols[_di]:\n',
'            _bt = "primary" if _di == bi else "secondary"\n',
'            if st.button(str(_di+1), key=f"brd_{_di}", type=_bt, use_container_width=True):\n',
'                st.session_state.br_idx = _di; st.rerun()\n',
]
lines[555:561]=new_dots

with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)

import ast
src=open(f,'r',encoding='utf-8').read()
try:
    ast.parse(src)
    print('syntax OK!')
except SyntaxError as e:
    print(f'error line {e.lineno}: {e.msg}')
