f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('.ah{text-align:center;padding:0.2rem 0 0.1rem 0;}','.ah{text-align:center;padding:0.05rem 0 0.05rem 0;}')
c=c.replace('padding:0.1rem 0.8rem;border-radius:10px;margin-bottom:0.05rem','padding:0.05rem 0.8rem;border-radius:10px;margin-bottom:0.02rem')
c=c.replace('.rd-dots{display:flex;justify-content:center;gap:0.6rem;margin:0.3rem 0;}','.rd-dots{display:flex;justify-content:center;gap:0.6rem;margin:0.1rem 0;}')
open(f,'w',encoding='utf-8').write(c)
print('done!')
