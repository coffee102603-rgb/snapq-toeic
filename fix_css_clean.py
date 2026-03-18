f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

lines[636]='button[kind="primary"],button[kind="secondary"]{background:#0d0d0d!important;color:#fff!important;border:1.5px solid rgba(0,212,255,0.5)!important;border-radius:8px!important;font-size:0.56rem!important;font-weight:300!important;padding:0.1rem 0.3rem!important;text-align:center!important;transition:none!important;}\r\n'
lines[637]='button[kind="primary"] p,button[kind="primary"] span,button[kind="secondary"] p,button[kind="secondary"] span,.stButton button p,.stButton>button p,.stButton>button span{font-size:0.56rem!important;font-weight:300!important;}\r\n'

with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)
print('done!')
