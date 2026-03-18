f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
OLD3='font-size:0.75rem!important;font-weight:400!important;padding:0.15rem 0.2rem!important;text-align:center!important;transition:none!important;animation:p5bounce'
NEW3='font-size:0.75rem!important;font-weight:400!important;padding:0.05rem 0.1rem!important;min-height:0!important;height:32px!important;text-align:center!important;transition:none!important;animation:p5bounce'
bi=c.find('elif st.session_state.phase=="briefing"')
idx=c.find(OLD3,bi)
if idx!=-1:
    c=c[:idx]+c[idx:].replace(OLD3,NEW3,1)
    print('updated!')
else:
    print('not found')
open(f,'w',encoding='utf-8').write(c)
print('done!')
