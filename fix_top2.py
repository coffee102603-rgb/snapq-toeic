f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('.block-container{padding-top:0.3rem!important;padding-bottom:0.5rem!important;}','.block-container{padding-top:0.1rem!important;padding-bottom:0.3rem!important;}')
c=c.replace('.rd-dots{display:flex;justify-content:center;gap:0.6rem;margin:0.1rem 0;}','.rd-dots{display:flex;justify-content:center;gap:0.6rem;margin:0 0;}')
c=c.replace('""", height=60)','""", height=48)')
open(f,'w',encoding='utf-8').write(c)
print('done!')
