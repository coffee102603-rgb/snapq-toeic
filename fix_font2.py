f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()
lines[636]=lines[636].replace('font-size:1rem!important;font-weight:700!important;padding:0.4rem 0.3rem!important;','font-size:0.7rem!important;font-weight:300!important;padding:0.1rem 0.3rem!important;')
lines[638]=lines[638].replace('font-size:2.1rem!important;font-weight:700!important;','font-size:0.7rem!important;font-weight:300!important;')
with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)
print('done!')
