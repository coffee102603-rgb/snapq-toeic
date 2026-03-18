f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('header[data-testid="stHeader"]{background:transparent!important;}','header[data-testid="stHeader"]{background:transparent!important;height:0!important;min-height:0!important;overflow:hidden!important;}')
open(f,'w',encoding='utf-8').write(c)
print('done!')
