f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

for i in range(415,430):
    print(f'{i+1}: {lines[i].rstrip()}')
