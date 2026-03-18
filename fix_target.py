f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()
lines[568]=lines[568].replace('href="?br_nav=lobby"','href="?br_nav=lobby" target="_self"')
lines[569]=lines[569].replace('href="?br_nav=main"','href="?br_nav=main" target="_self"')
with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)
print('done!')
