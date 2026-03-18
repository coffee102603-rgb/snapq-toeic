f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('\U0001f30d \uba54\uc778\ud5c8\ube0c','\U0001f30d \uba54\uc778')
c=c.replace('🌍 메인허브','🌍 메인')
bi=c.find('elif st.session_state.phase=="briefing"')
old='font-size:0.63rem!important;font-weight:400!important;padding:0 4px!important;min-height:0!important;height:44px!important;text-align:center!important;white-space:nowrap!important;overflow:hidden!important;transition:none!important;animation:p5bounce'
new='font-size:0.5rem!important;font-weight:400!important;padding:0 8px!important;min-height:0!important;height:44px!important;text-align:center!important;white-space:nowrap!important;overflow:hidden!important;transition:none!important;animation:p5bounce'
idx=c.find(old,bi)
if idx!=-1:
    c=c[:idx]+c[idx:].replace(old,new,1)
    print('CSS updated!')
else:
    print('not found')
open(f,'w',encoding='utf-8').write(c)
print('done!')
