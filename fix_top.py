f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('.block-container{padding-top:0.7rem!important;padding-bottom:1rem!important;}','.block-container{padding-top:0.3rem!important;padding-bottom:0.5rem!important;}')
open(f,'w',encoding='utf-8').write(c)
print('done!')
