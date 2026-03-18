f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()
add='[data-testid="stBaseButton-primary"] p,[data-testid="stBaseButton-secondary"] p,[data-testid="stBaseButton-primary"] span,[data-testid="stBaseButton-secondary"] span{font-size:0.56rem!important;font-weight:300!important;}'
lines[637]=lines[637].rstrip().rstrip('\r\n')+add+'\r\n'
with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)
print('done!')
