f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
bi=c.find('elif st.session_state.phase=="briefing"')
print('briefing at:', bi)
print(c[bi+35000:bi+35200])
