f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

# 494번 중복 제거 (0-indexed=493): 두번째 phase=lobby 줄 삭제
lines[494]='            st.session_state.phase = "lobby"; st.rerun()\n'
lines[493]='\n'

# 170~176번 중복 정리 (0-indexed=169~175)
lines[169]='    if k not in st.session_state: st.session_state[k]=v\n'
lines[170]='if st.session_state.pop("_p5_going_main", False):\n'
lines[171]='    st.switch_page("main_hub.py")\n'
lines[172]='\n'
lines[173]='\n'
lines[174]='\n'
lines[175]='\n'

with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)

import ast
src=open(f,'r',encoding='utf-8').read()
try:
    ast.parse(src)
    print('syntax OK!')
except SyntaxError as e:
    print(f'error line {e.lineno}: {e.msg}')
