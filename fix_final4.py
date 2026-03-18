# -*- coding: utf-8 -*-
content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

# 1. 저장 버튼 CSS 작게 + 가는 글씨
old1 = '    .save-btn button{background:transparent!important;border:1px solid #333!important;box-shadow:none!important;animation:none!important;}\n    .save-btn button p{font-size:0.85rem!important;color:#555!important;}'
new1 = '    .save-btn button{background:transparent!important;border:1px solid #333!important;box-shadow:none!important;animation:none!important;}\n    .save-btn button p{font-size:0.77rem!important;color:#555!important;font-weight:300!important;}'
r1 = content.replace(old1, new1, 1)
print('save-btn ok:', r1 != content)
content = r1

# 2. 하단 3개 버튼 글자 크게/굵게/흰테두리
old2 = '    _bs = "flex:1;display:block;text-align:center;padding:8px 2px;font-size:0.68rem;font-weight:300;border:1px solid #1a1a1a;border-radius:8px;text-decoration:none;background:transparent;color:#555;letter-spacing:0.5px;"'
new2 = '    _bs = "flex:1;display:block;text-align:center;padding:8px 2px;font-size:0.75rem;font-weight:600;border:1px solid rgba(255,255,255,0.3);border-radius:8px;text-decoration:none;background:transparent;color:#aaa;letter-spacing:0.3px;"'
r2 = content.replace(old2, new2, 1)
print('bot-btn ok:', r2 != content)
content = r2

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done!')
