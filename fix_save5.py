f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

new_save=[
'    saved_ok = st.session_state.pop("_saved_ok", False)\n',
'    save_lbl = "\u2705 \uc644\ub8cc!" if saved_ok else "\uc800\uc7a5"\n',
'    sv_c1, sv_c2, sv_c3 = st.columns([2, 3, 2])\n',
'    with sv_c2:\n',
'        if st.button(save_lbl, key=f"sv_{q[\'id\']}_{bi}", type="primary", use_container_width=True):\n',
'            item = {"id":q["id"],"text":q["text"],"ch":q["ch"],"a":q["a"],"ex":q.get("ex",""),"exk":q.get("exk",""),"cat":q.get("cat",""),"kr":q.get("kr",""),"tp":q.get("tp","grammar")}\n',
'            save_to_storage([item])\n',
'            st.session_state["_saved_ok"] = True\n',
'            st.rerun()\n',
]
lines[546:550]=new_save

with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)

import ast
src=open(f,'r',encoding='utf-8').read()
try:
    ast.parse(src)
    print('syntax OK!')
except SyntaxError as e:
    print(f'error line {e.lineno}: {e.msg}')
