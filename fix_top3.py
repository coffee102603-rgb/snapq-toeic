f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('.block-container{padding-top:0.1rem!important;padding-bottom:0.3rem!important;}','.block-container{padding-top:0!important;padding-bottom:0.2rem!important;}')
c=c.replace('.bt{display:flex;align-items:center;justify-content:space-between;padding:0.15rem 0.8rem;border-radius:10px;margin-bottom:0.05rem;}','.bt{display:flex;align-items:center;justify-content:space-between;padding:0.05rem 0.8rem;border-radius:10px;margin-bottom:0.02rem;}')
open(f,'w',encoding='utf-8').write(c)
print('done!')
