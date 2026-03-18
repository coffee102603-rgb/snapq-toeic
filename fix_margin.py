# -*- coding: utf-8 -*-
content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

# margin-top:-1rem 제거 (브리핑도 영향받아서)
old = '.block-container{padding-top:0!important;padding-bottom:0!important;margin-top:-1rem!important;}'
new = '.block-container{padding-top:0!important;padding-bottom:0!important;}'
r = content.replace(old, new)
print('margin ok:', r != content)
content = r

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done!')
