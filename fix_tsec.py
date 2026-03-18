f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
old="    if _tsec_chosen:\n        st.markdown(f'<div class=\"ms-title\"><p>TOEIC PART 5 · 5문제 서바이벌</p>{round_txt}</div>', unsafe_allow_html=True)\n    else:\n        _tsec = st.session_state.get('tsec', 30)\n    _tsec_chosen = st.session_state.get('tsec_chosen', False)\n    if _tsec_chosen:"
new="    _tsec_chosen = st.session_state.get('tsec_chosen', False)\n    _tsec = st.session_state.get('tsec', 30)\n    if _tsec_chosen:"
if old in c:
    open(f,'w',encoding='utf-8').write(c.replace(old,new))
    print('done!')
else:
    print('매칭실패')
