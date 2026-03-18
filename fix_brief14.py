f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

# 523번(0-indexed:522) - 저장 버튼 아이콘 제거
lines[522]=lines[522].replace('\\U0001f4be \\uc800\\uc7a5','\\uc800\\uc7a5')

with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)

# CSS 글자 작게+가늘게
c=open(f,'r',encoding='utf-8').read()
bi=c.find('elif st.session_state.phase=="briefing"')
old='font-size:0.5rem!important;font-weight:400!important;padding:0 8px!important;min-height:0!important;height:44px!important;text-align:center!important;white-space:nowrap!important;overflow:hidden!important;transition:none!important;animation:p5bounce 1.4s ease-in-out infinite,p5flash 3s ease-in-out infinite!important;}button[kind="primary"]{font-size:0.9rem!important;padding:0 12px!important;white-space:nowrap!important;}'
new='font-size:0.35rem!important;font-weight:300!important;padding:0 8px!important;min-height:0!important;height:44px!important;text-align:center!important;white-space:nowrap!important;overflow:hidden!important;transition:none!important;animation:p5bounce 1.4s ease-in-out infinite,p5flash 3s ease-in-out infinite!important;}button[kind="primary"]{font-size:0.65rem!important;font-weight:300!important;padding:0 12px!important;white-space:nowrap!important;}'
idx=c.find(old,bi)
if idx!=-1:
    c=c[:idx]+c[idx:].replace(old,new,1)
    print('CSS updated!')
else:
    print('CSS not found')
open(f,'w',encoding='utf-8').write(c)
print('done!')
