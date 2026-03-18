f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
old='font-size:0.9rem!important;font-weight:400!important;padding:0!important;min-height:0!important;height:44px!important;text-align:center!important;transition:none!important;animation:p5bounce 1.4s ease-in-out infinite,p5flash 3s ease-in-out infinite!important;}[data-testid="stHorizontalBlock"]{display:flex!important;flex-direction:row!important;flex-wrap:nowrap!important;gap:4px!important;}[data-testid="stHorizontalBlock"] [data-testid="stColumn"]{flex:1!important;min-width:0!important;max-width:20%!important;}'
new='font-size:0.63rem!important;font-weight:400!important;padding:0!important;min-height:0!important;height:44px!important;text-align:center!important;transition:none!important;animation:p5bounce 1.4s ease-in-out infinite,p5flash 3s ease-in-out infinite!important;}[data-testid="stHorizontalBlock"]{display:flex!important;flex-direction:row!important;flex-wrap:nowrap!important;gap:4px!important;}[data-testid="stHorizontalBlock"] [data-testid="stColumn"]{flex:1!important;min-width:0!important;max-width:20%!important;}'
bi=c.find('elif st.session_state.phase=="briefing"')
idx=c.find(old,bi)
if idx!=-1:
    c=c[:idx]+c[idx:].replace(old,new,1)
    print('숫자 updated!')
else:
    print('not found')
c=c.replace('"sv_c1, sv_c2, sv_c3 = st.columns([1, 2, 1])"','')
c=c.replace('sv_c1, sv_c2, sv_c3 = st.columns([1, 2, 1])','sv_c1, sv_c2, sv_c3 = st.columns([1, 4, 1])')
open(f,'w',encoding='utf-8').write(c)
print('done!')
