f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

new_save=[
'    saved_ok = st.session_state.pop("_saved_ok", False)\n',
'    save_lbl = "\u2705 \uc644\ub8cc!" if saved_ok else "\uc800\uc7a5"\n',
'    save_html = \'<div style="display:flex;justify-content:center;margin:6px 0;"><a href="?br_save=1" style="display:flex;align-items:center;justify-content:center;height:36px;min-width:120px;padding:0 20px;background:#0d0d0d;border:1px solid rgba(0,212,255,0.5);border-radius:8px;color:#fff;text-decoration:none;font-size:0.75rem;font-weight:300;">\' + save_lbl + \'</a></div>\'\n',
'    st.markdown(save_html, unsafe_allow_html=True)\n',
]
lines[546:554]=new_save

with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)

import ast
with open(f,'r',encoding='utf-8') as fp:
    src=fp.read()
try:
    ast.parse(src)
    print('syntax OK!')
except SyntaxError as e:
    print(f'error line {e.lineno}: {e.msg}')
