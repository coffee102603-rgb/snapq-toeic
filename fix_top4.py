f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('.ah{text-align:center;padding:0 0 0 0;}','.ah{text-align:center;padding:0;margin:0;line-height:0.7;}',1)
c=c.replace('.ah h1{font-family:\'Orbitron\',monospace!important;font-size:2rem;','.ah h1{font-family:\'Orbitron\',monospace!important;font-size:1.4rem;',1)
c=c.replace('.bt{display:flex;align-items:center;justify-content:space-between;padding:0.05rem 0.8rem;border-radius:10px;margin-bottom:0.02rem;}','.bt{display:flex;align-items:center;justify-content:space-between;padding:0.02rem 0.8rem;border-radius:8px;margin-bottom:0.01rem;}')
c=c.replace('""", height=52)','""", height=40)')
open(f,'w',encoding='utf-8').write(c)
print('done!')
