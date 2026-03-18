f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('.critical{{color:#ff0000;text-shadow:0 0 50px #ff0000;font-size:4rem!important;}}','.critical{{color:#ff0000;text-shadow:0 0 50px #ff0000;font-size:1.8rem!important;}}')
c=c.replace('""", height=40)','""", height=44)')
open(f,'w',encoding='utf-8').write(c)
print('done!')
