f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
add='[data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;}[data-testid="stHorizontalBlock"] [data-testid="stColumn"]{min-width:0!important;flex:1!important;}'
c=c.replace('.nav-bar-label{font-size:0.7rem;color:#333;text-align:center;letter-spacing:3px;margin-bottom:6px;}','.nav-bar-label{font-size:0.7rem;color:#333;text-align:center;letter-spacing:3px;margin-bottom:6px;}'+add)
open(f,'w',encoding='utf-8').write(c)
print('done!')
