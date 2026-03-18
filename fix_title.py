f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace("    st.markdown(f'<div class=\"ms-title\"><h1>⚔️ P5 ARENA ⚔️</h1><p>TOEIC PART 5 · 5문제 서바이벌</p>{round_txt}</div>', unsafe_allow_html=True)","    st.markdown(f'<div class=\"ms-title\"><p>TOEIC PART 5 · 5문제 서바이벌</p>{round_txt}</div>', unsafe_allow_html=True)")
open(f,'w',encoding='utf-8').write(c)
print('done!')
