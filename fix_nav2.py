f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()

# nav=hub 파라미터 처리 추가
nav_check = """
_nav = st.query_params.get('nav', '')
if _nav == 'hub':
    st.query_params.clear()
    st.session_state._p5_just_left = True
    st.session_state.ans = False
    st.session_state['_battle_entry_ans_reset'] = True
    st.switch_page('main_hub.py')
if _nav == 'stg':
    st.query_params.clear()
    st.switch_page('pages/03_역전장.py')
"""

# 로비 시작 부분에 nav 처리 삽입
c=c.replace("if st.session_state.phase==\"lobby\":", "if st.session_state.phase==\"lobby\":\n" + nav_check)
open(f,'w',encoding='utf-8').write(c)
print('done!')
