f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

# 168번줄(0-indexed): phase 초기화를 _leaving__ 방어 추가
# 169~170번(0-indexed)을 교체
lines[169]='for k,v in D.items():\n'
lines[170]='    if k not in st.session_state: st.session_state[k]=v\n'

# 491번(0-indexed): main 핸들러에서 switch_page 직전에 phase를 dummy로 설정
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

for i,l in enumerate(lines):
    if 'st.switch_page("main_hub.py")' in l:
        print(f'{i+1}: {l.rstrip()}')
