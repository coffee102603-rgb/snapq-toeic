f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()
lines[636]=lines[636].replace('font-size:0.7rem!important;font-weight:300!important;padding:0.1rem 0.3rem!important;text-align:center!important;transition:none!important;animation:p5bounce 1.4s ease-in-out infinite,p5flash 3s ease-in-out infinite!important;}','font-size:0.56rem!important;font-weight:300!important;padding:0.1rem 0.3rem!important;text-align:center!important;transition:none!important;}')
lines[637]=lines[637].replace('font-size:0.7rem!important;font-weight:300!important;','font-size:0.56rem!important;font-weight:300!important;')
with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)
print('done!')
