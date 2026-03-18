f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace(
'header[data-testid="stHeader"]{background:transparent!important;}\n.block-container{padding-top:0!important;padding-bottom:0.2rem!important;}\n.ah{text-align:center;padding:0 0 0 0;}',
'header[data-testid="stHeader"]{background:transparent!important;height:0!important;min-height:0!important;overflow:hidden!important;}\n.block-container{padding-top:0!important;padding-bottom:0.2rem!important;}\n.ah{text-align:center;padding:0 0 0 0;}',
1)
c=c.replace('#n{{font-size:3rem;font-weight:900;animation:p 1s ease-in-out infinite;}}','#n{{font-size:2.4rem;font-weight:900;animation:p 1s ease-in-out infinite;}}')
c=c.replace('""", height=48)','""", height=60)')
open(f,'w',encoding='utf-8').write(c)
print('done!')
