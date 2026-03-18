f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('.stage{animation:stageIn 0.5s ease;border-radius:20px;padding:20px 12px;margin:8px 0;}','.stage{animation:stageIn 0.5s ease;border-radius:14px;padding:10px 12px;margin:4px 0;}')
c=c.replace('.act-msg{font-size:1.3rem;font-weight:900;color:#fff;text-align:center;margin-bottom:14px;line-height:1.4;}','.act-msg{font-size:1.1rem;font-weight:900;color:#fff;text-align:center;margin-bottom:6px;line-height:1.3;}')
c=c.replace('.act-label{font-size:0.75rem;font-weight:900;letter-spacing:4px;color:#00d4ff;margin-bottom:10px;text-align:center;}','.act-label{font-size:0.7rem;font-weight:900;letter-spacing:3px;color:#00d4ff;margin-bottom:4px;text-align:center;}')
c=c.replace('[data-testid="stVerticalBlock"]{gap:0.2rem!important;}','[data-testid="stVerticalBlock"]{gap:0.1rem!important;}') if '[data-testid="stVerticalBlock"]' in c else c
open(f,'w',encoding='utf-8').write(c)
print('done!')
