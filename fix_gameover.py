# -*- coding: utf-8 -*-
content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

old = '.taunt{{font-size:1.3rem;color:#ff8888;font-weight:700;margin:6px 0;}}'
new = '.taunt{{font-size:1.3rem;color:#ffe066;font-weight:900;margin:6px 0;text-shadow:0 0 8px rgba(255,200,0,0.8);}}'

r = content.replace(old, new, 1)
print('replaced:', r != content)

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(r)
print('done!')
