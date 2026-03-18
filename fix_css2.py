f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

css=[
'    st.markdown(\'\'\'<style>\n',
'    div[data-testid="stButton"] > button { font-size:0.75rem!important; font-weight:300!important; animation:none!important; transition:none!important; }\n',
'    div[data-testid="stButton"] > button p { font-size:0.75rem!important; font-weight:300!important; }\n',
'    div[data-testid="stButton"] > button span { font-size:0.75rem!important; font-weight:300!important; }\n',
'    </style>\'\'\', unsafe_allow_html=True)\n',
]
lines[546:546]=css

with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)

import ast
src=open(f,'r',encoding='utf-8').read()
try:
    ast.parse(src)
    print('syntax OK!')
except SyntaxError as e:
    print(f'error line {e.lineno}: {e.msg}')
