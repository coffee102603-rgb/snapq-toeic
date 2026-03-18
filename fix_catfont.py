# -*- coding: utf-8 -*-
content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

old = 'font-size:1.52rem;font-weight:900;color:#fff;line-height:1.4;'
new = 'font-size:1.37rem;font-weight:900;color:#fff;line-height:1.4;'
r = content.replace(old, new)
print('replaced:', content.count(old), '곳')
content = r

old2 = 'font-size:1.1rem;font-weight:800;color:#ccc;line-height:1.3;'
new2 = 'font-size:1.0rem;font-weight:800;color:#ccc;line-height:1.3;'
r2 = content.replace(old2, new2)
print('replaced2:', content.count(old2), '곳')
content = r2

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done!')
