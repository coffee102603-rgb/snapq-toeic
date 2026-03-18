f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('#n{{font-size:2.4rem;font-weight:900;animation:p 1s ease-in-out infinite;}}','#n{{font-size:1.8rem;font-weight:900;animation:p 1s ease-in-out infinite;}}')
c=c.replace('.critical{{color:#ff0000;text-shadow:0 0 50px #ff0000;font-size:6rem!important;}}','.critical{{color:#ff0000;text-shadow:0 0 50px #ff0000;font-size:2.2rem!important;}}')
c=c.replace('""", height=60)','""", height=45)')
open(f,'w',encoding='utf-8').write(c)
print('done!')
