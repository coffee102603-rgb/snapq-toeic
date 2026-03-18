f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()

# 1. 저장 버튼 - 가운데 배열을 오른쪽으로 (column 비율 변경)
c=c.replace('sv_c1, sv_c2, sv_c3 = st.columns([1, 4, 1])','sv_c1, sv_c2, sv_c3 = st.columns([3, 2, 0])')

# 2. 브리핑 CSS에 버튼 white-space nowrap 추가 (한줄로 강제)
old='font-size:0.63rem!important;font-weight:400!important;padding:0!important;min-height:0!important;height:44px!important;text-align:center!important;transition:none!important;animation:p5bounce 1.4s ease-in-out infinite,p5flash 3s ease-in-out infinite!important;}'
new='font-size:0.63rem!important;font-weight:400!important;padding:0 4px!important;min-height:0!important;height:44px!important;text-align:center!important;white-space:nowrap!important;overflow:hidden!important;transition:none!important;animation:p5bounce 1.4s ease-in-out infinite,p5flash 3s ease-in-out infinite!important;}'
bi=c.find('elif st.session_state.phase=="briefing"')
idx=c.find(old,bi)
if idx!=-1:
    c=c[:idx]+c[idx:].replace(old,new,1)
    print('CSS updated!')
else:
    print('CSS not found')

open(f,'w',encoding='utf-8').write(c)
print('done!')
