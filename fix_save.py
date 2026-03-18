f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('sv_c1, sv_c2, sv_c3 = st.columns([1, 3, 1])','sv_c1, sv_c2, sv_c3 = st.columns([1, 5, 1])')
open(f,'w',encoding='utf-8').write(c)
print('done!')
