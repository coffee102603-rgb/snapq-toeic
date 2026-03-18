# -*- coding: utf-8 -*-
content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

# 배틀 화면 padding-top 더 줄이기 (0.3rem → 0rem)
old1 = '.block-container{padding-top:0.3rem!important;padding-bottom:0.3rem!important;}'
new1 = '.block-container{padding-top:0!important;padding-bottom:0!important;}'
count = content.count(old1)
content = content.replace(old1, new1)
print(f'padding ok: {count}곳')

# 타이머 숫자 3rem → 2.4rem (조금 작게)
old2 = '#n{{font-size:3rem;font-weight:900;animation:p 1s ease-in-out infinite;}}'
new2 = '#n{{font-size:2.4rem;font-weight:900;animation:p 1s ease-in-out infinite;}}'
r2 = content.replace(old2, new2, 1)
print('timer font ok:', r2 != content); content = r2

# critical도 같이 줄이기
old3 = '.critical{{color:#ff0000;text-shadow:0 0 50px #ff0000;font-size:3.5rem!important;}}'
new3 = '.critical{{color:#ff0000;text-shadow:0 0 50px #ff0000;font-size:2.8rem!important;}}'
r3 = content.replace(old3, new3, 1)
print('critical ok:', r3 != content); content = r3

# height=70 → 55
old4 = '        </script>""", height=70)'
new4 = '        </script>""", height=55)'
r4 = content.replace(old4, new4, 1)
print('height ok:', r4 != content); content = r4

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done!')
