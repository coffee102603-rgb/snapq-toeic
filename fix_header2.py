f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('.ah h1{font-family:\'Orbitron\',monospace!important;font-size:1.4rem;','.ah h1{font-family:\'Orbitron\',monospace!important;font-size:0.95rem;',1)
c=c.replace('.ah{text-align:center;padding:0;margin:0;line-height:0.7;}','.ah{text-align:center;padding:0;margin:-4px 0 -4px 0;line-height:0.6;}',1)
c=c.replace('.bt{display:flex;align-items:center;justify-content:space-between;padding:0.02rem 0.8rem;border-radius:8px;margin-bottom:0.01rem;}','.bt{display:flex;align-items:center;justify-content:space-between;padding:0.01rem 0.8rem;border-radius:6px;margin-bottom:0;transform:scale(0.85);transform-origin:top center;margin-top:-4px;}')
open(f,'w',encoding='utf-8').write(c)
print('done!')
