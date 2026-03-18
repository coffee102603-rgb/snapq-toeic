f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
old='button[kind="primary"],button[kind="secondary"]{background:#0d0d0d!important;color:#fff!important;border:1.5px solid rgba(0,212,255,0.5)!important;border-radius:8px!important;font-family:\'Rajdhani\',sans-serif!important;font-size:0.75rem!important;font-weight:400!important;padding:0.05rem 0.1rem!important;min-height:0!important;height:32px!important;text-align:center!important;transition:none!important;animation:p5bounce 1.4s ease-in-out infinite,p5flash 3s ease-in-out infinite!important;}'
new='button[kind="primary"],button[kind="secondary"]{background:#0d0d0d!important;color:#fff!important;border:1.5px solid rgba(0,212,255,0.5)!important;border-radius:8px!important;font-family:\'Rajdhani\',sans-serif!important;font-size:0.9rem!important;font-weight:400!important;padding:0!important;min-height:0!important;height:40px!important;text-align:center!important;transition:none!important;animation:p5bounce 1.4s ease-in-out infinite,p5flash 3s ease-in-out infinite!important;}'
if old in c:
    c=c.replace(old,new)
    print('updated!')
else:
    print('not found')
open(f,'w',encoding='utf-8').write(c)
print('done!')
