f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()
lines[637]=lines[637].replace('font-size:2.1rem!important;font-weight:700!important;','font-size:0.7rem!important;font-weight:300!important;')
with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)
print('done!')
