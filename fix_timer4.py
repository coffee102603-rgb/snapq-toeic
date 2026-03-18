f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
c=open(f,'r',encoding='utf-8').read()
c=c.replace('#w{{text-align:center;}}','#w{{text-align:center;padding:0;margin:0;line-height:1;}}')
c=c.replace('*{{margin:0;padding:0;}}body{{background:transparent;overflow:hidden;font-family:sans-serif;}}','*{{margin:0;padding:0;box-sizing:border-box;}}body{{background:transparent;overflow:hidden;font-family:sans-serif;margin:0;padding:0;}}')
c=c.replace('""", height=80)','""", height=52)')
open(f,'w',encoding='utf-8').write(c)
print('done!')
