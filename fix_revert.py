f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('\n    [data-testid="stVerticalBlock"]{gap:0.3rem!important;}','')
open(f,'w',encoding='utf-8').write(c)
print('done!')
