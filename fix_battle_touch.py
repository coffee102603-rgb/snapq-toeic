# -*- coding: utf-8 -*-
content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

# 선택지 버튼 padding 크게 + 글자 5% 크게 (모든 CSS 섹션 적용)
# 0.55rem → 0.75rem (터치 영역 확대), 1.45rem → 1.52rem (글자 5% 크게)
old_btn = "font-size:1.45rem!important;font-weight:700!important;padding:0.55rem 0.6rem!important;"
new_btn = "font-size:1.52rem!important;font-weight:700!important;padding:0.75rem 0.6rem!important;"
count = content.count(old_btn)
content = content.replace(old_btn, new_btn)
print(f'button padding: {count}곳 교체')

old_p = "font-size:1.45rem!important;font-weight:700!important;text-align:center!important;"
new_p = "font-size:1.52rem!important;font-weight:700!important;text-align:center!important;"
count2 = content.count(old_p)
content = content.replace(old_p, new_p)
print(f'button p: {count2}곳 교체')

# 타이머 숫자 10% 작게 (bt 영역 축소)
old_bt = ".bt{display:flex;align-items:center;justify-content:space-between;padding:0.4rem 0.8rem;border-radius:10px;margin-bottom:0.2rem;}"
new_bt = ".bt{display:flex;align-items:center;justify-content:space-between;padding:0.25rem 0.8rem;border-radius:10px;margin-bottom:0.1rem;}"
count3 = content.count(old_bt)
content = content.replace(old_bt, new_bt)
print(f'timer bt: {count3}곳 교체')

old_bq = ".bq{font-family:'Orbitron',monospace;font-size:1.1rem;font-weight:900;}"
new_bq = ".bq{font-family:'Orbitron',monospace;font-size:1.0rem;font-weight:900;}"
count4 = content.count(old_bq)
content = content.replace(old_bq, new_bq)
print(f'timer font: {count4}곳 교체')

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done!')
