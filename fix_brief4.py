f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
OLD3='font-size:1rem!important;font-weight:700!important;padding:0.4rem 0.3rem!important;text-align:center!important;transition:none!important;animation:p5bounce'
NEW3='font-size:0.75rem!important;font-weight:400!important;padding:0.15rem 0.2rem!important;text-align:center!important;transition:none!important;animation:p5bounce'
bi=c.find('elif st.session_state.phase=="briefing"')
idx=c.find(OLD3,bi)
if idx!=-1:
    c=c[:idx]+c[idx:].replace(OLD3,NEW3,1)
    print('CSS updated!')
else:
    print('not found, trying fallback...')
    OLD3b='font-size:2.1rem!important;font-weight:700!important;padding:1.2rem 1.4rem!important;text-align:center!important;transition:none!important;animation:p5bounce'
    NEW3b='font-size:0.75rem!important;font-weight:400!important;padding:0.15rem 0.2rem!important;text-align:center!important;transition:none!important;animation:p5bounce'
    idx=c.find(OLD3b,bi)
    if idx!=-1:
        c=c[:idx]+c[idx:].replace(OLD3b,NEW3b,1)
        print('fallback CSS updated!')
open(f,'w',encoding='utf-8').write(c)
print('done!')
