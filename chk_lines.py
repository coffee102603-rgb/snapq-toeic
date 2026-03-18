f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

# 줄 번호 확인
for i,l in enumerate(lines):
    if 'was_victory' in l and 'if' in l:
        print(f'{i+1}: {l.rstrip()}')
    if 'bc[0]' in l or 'bc[1]' in l or 'bc[2]' in l:
        print(f'{i+1}: {l.rstrip()}')
