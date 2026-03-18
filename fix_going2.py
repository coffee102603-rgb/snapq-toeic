f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

# 169번(0-indexed): _going_main 체크를 맨 앞에 삽입
lines.insert(169,'if st.session_state.pop("_p5_going_main", False):\n')
lines.insert(170,'    st.switch_page("main_hub.py")\n')

# 494번이 2줄 밀려서 496번이 됨
# switch_page 직전에 _p5_going_main 플래그+rerun으로 교체
for i,l in enumerate(lines):
    if 'st.switch_page("main_hub.py")' in l and i > 490 and i < 520:
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
