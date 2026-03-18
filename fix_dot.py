f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

# 551번(0-indexed 550) 앞에 dot_html 초기화+루프 삽입
new_dots=[
'    dot_html = \'<div style="display:flex;gap:6px;margin:6px 0;">\'\n',
'    for _di in range(num_qs):\n',
'        _border = "2px solid #00d4ff" if _di == bi else "1px solid #444"\n',
'        dot_html += f\'<a href="?br_q={_di}" style="flex:1;display:flex;align-items:center;justify-content:center;height:36px;background:#0d0d0d;border:{_border};border-radius:8px;color:#fff;text-decoration:none;font-size:0.75rem;font-weight:300;">{_di+1}</a>\'\n',
]
lines[550:550]=new_dots

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
