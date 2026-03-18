f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

# 637번줄에 올바른 선택자 추가
add='.stButton button p,.stButton button span{font-size:0.56rem!important;font-weight:300!important;}div[data-testid="stButton"] button{font-size:0.56rem!important;font-weight:300!important;}.stButton>button{font-size:0.56rem!important;font-weight:300!important;}'
lines[637]=lines[637].rstrip().rstrip('\r\n')+add+'\r\n'
with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)
print('done!')
