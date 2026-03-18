f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('""", height=48)','""", height=80)')
c=c.replace('[data-testid="stVerticalBlock"]{gap:0.1rem!important;}' if '[data-testid="stVerticalBlock"]' in c else '','')
open(f,'w',encoding='utf-8').write(c)
print('done!')
