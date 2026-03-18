f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

# 현재 nav_html 블록 위치 확인
for i,l in enumerate(lines):
    if 'nav_html' in l and 'display:flex' in l:
        print(f'{i+1}: {l.rstrip()[:80]}')
