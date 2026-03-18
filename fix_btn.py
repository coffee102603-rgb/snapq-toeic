f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('border-radius:14px!important;font-size:1.35rem!important;font-weight:900!important;\n        padding:14px 8px!important;color:#e0e0e0!important;min-height:60px!important;','border-radius:14px!important;font-size:1.08rem!important;font-weight:900!important;\n        padding:8px 8px!important;color:#e0e0e0!important;min-height:44px!important;')
c=c.replace('button[kind="secondary"] p{font-size:1.35rem!important;font-weight:900!important;white-space:pre-line!important;line-height:1.3!important;text-align:center!important;}','button[kind="secondary"] p{font-size:1.08rem!important;font-weight:900!important;white-space:pre-line!important;line-height:1.2!important;text-align:center!important;}')
open(f,'w',encoding='utf-8').write(c)
print('done!')
