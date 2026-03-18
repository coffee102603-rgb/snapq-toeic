f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('border-radius:10px!important;font-size:0.85rem!important;font-weight:900!important;\n        padding:4px 4px!important;color:#e0e0e0!important;min-height:28px!important;','border-radius:10px!important;font-size:0.85rem!important;font-weight:900!important;\n        padding:10px 4px!important;color:#e0e0e0!important;min-height:52px!important;')
c=c.replace('<a href="?nav=stg" target="_self" style="padding:6px 18px;font-size:0.85rem;font-weight:700;color:#aaa;border:1px solid #333;border-radius:8px;text-decoration:none;background:#0a0a0a;">🔥 역전장</a>','<a href="?nav=stg" target="_self" style="padding:10px 18px;font-size:0.85rem;font-weight:700;color:#aaa;border:1px solid #333;border-radius:8px;text-decoration:none;background:#0a0a0a;">🔥 역전장</a>')
c=c.replace('<a href="?nav=hub" target="_self" style="padding:6px 18px;font-size:0.85rem;font-weight:700;color:#aaa;border:1px solid #333;border-radius:8px;text-decoration:none;background:#0a0a0a;">🏠 메인</a>','<a href="?nav=hub" target="_self" style="padding:10px 18px;font-size:0.85rem;font-weight:700;color:#aaa;border:1px solid #333;border-radius:8px;text-decoration:none;background:#0a0a0a;">🏠 메인</a>')
open(f,'w',encoding='utf-8').write(c)
print('done!')
