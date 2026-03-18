f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()
del lines[502:516]
with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)
c=open(f,'r',encoding='utf-8').read()
OLD3='font-size:2.1rem!important;font-weight:700!important;padding:1.2rem 1.4rem!important;text-align:center!important;transition:none!important;animation:p5bounce'
NEW3='font-size:1rem!important;font-weight:700!important;padding:0.4rem 0.3rem!important;text-align:center!important;transition:none!important;animation:p5bounce'
bi=c.find('elif st.session_state.phase=="briefing"')
idx=c.find(OLD3,bi)
if idx!=-1:
    c=c[:idx]+c[idx:].replace(OLD3,NEW3,1)
    print('CSS updated!')
open(f,'w',encoding='utf-8').write(c)
print('nav removed:','br_p' not in c)
print('done!')
