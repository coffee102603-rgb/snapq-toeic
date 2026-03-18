f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

# 169~170번(0-indexed): phase는 _p5_going_main 플래그가 없을 때만 초기화
lines[169]='_going_main = st.session_state.pop("_p5_going_main", False)\n'
lines[170]='for k,v in D.items():\n'
lines.insert(171,'    if k not in st.session_state: st.session_state[k]=v\n')
lines.insert(172,'if _going_main:\n')
lines.insert(173,'    st.switch_page("main_hub.py")\n')

# 494번(0-indexed=493): switch_page 직전에 _p5_going_main 플래그 설정
for i,l in enumerate(lines):
    if 'st.switch_page("main_hub.py")' in l and i > 480 and i < 510:
        lines[i]='            st.session_state["_p5_going_main"] = True\n'
        lines.insert(i+1,'            st.rerun()\n')
        break

with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)

import ast
src=open(f,'r',encoding='utf-8').read()
try:
    ast.parse(src)
    print('syntax OK!')
except SyntaxError as e:
    print(f'error line {e.lineno}: {e.msg}')
