f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('background:linear-gradient(135deg,#ff4400,#ff8800,#ffaa00)!important;\n        border:3px solid #ffd700!important;font-size:1.6rem!important;font-weight:900!important;\n        padding:1.2rem!important;color:#fff!important;border-radius:16px!important;\n        animation:startPulse 1.5s ease infinite!important;\n        text-shadow:0 2px 8px rgba(0,0,0,0.5)!important;','background:linear-gradient(135deg,#ff4400,#ff8800,#ffaa00)!important;\n        border:2px solid #ffd700!important;font-size:1.05rem!important;font-weight:900!important;\n        padding:0.6rem!important;color:#fff!important;border-radius:12px!important;\n        animation:startPulse 1.5s ease infinite!important;\n        text-shadow:0 2px 8px rgba(0,0,0,0.5)!important;')
c=c.replace('.act-msg{font-size:1.1rem;font-weight:900;color:#fff;text-align:center;margin-bottom:6px;line-height:1.3;}','.act-msg{font-size:0.85rem;font-weight:900;color:#fff;text-align:center;margin-bottom:4px;line-height:1.2;}')
c=c.replace('style="text-align:center;padding:24px 12px;"','style="text-align:center;padding:10px 8px;"')
open(f,'w',encoding='utf-8').write(c)
print('done!')
