f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()
for i,l in enumerate(lines):
    if 'sv_' in l and 'button' in l:
        print(f'{i+1}: {l.rstrip()}')
