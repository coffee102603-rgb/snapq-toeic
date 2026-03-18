f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('.ah{text-align:center;padding:0.05rem 0 0.05rem 0;}','.ah{text-align:center;padding:0 0 0 0;}')
c=c.replace('.bt{display:flex;align-items:center;justify-content:space-between;padding:0.3rem 0.8rem;border-radius:10px;margin-bottom:0.1rem;}','.bt{display:flex;align-items:center;justify-content:space-between;padding:0.15rem 0.8rem;border-radius:10px;margin-bottom:0.05rem;}')
c=c.replace('""", height=72)','""", height=60)')
open(f,'w',encoding='utf-8').write(c)
print('done!')
