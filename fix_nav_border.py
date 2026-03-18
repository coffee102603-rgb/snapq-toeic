# -*- coding: utf-8 -*-
content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

old = 'border:1px solid rgba(255,255,255,0.15);border-radius:8px;text-decoration:none;background:transparent;">'
new = 'border:2px solid rgba(255,255,255,0.7);border-radius:8px;text-decoration:none;background:transparent;color:#ddd;font-weight:600;">'

r = content.replace(old, new)
print('replaced count:', content.count(old))
content = r

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done!')
