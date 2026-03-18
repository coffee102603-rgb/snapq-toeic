# -*- coding: utf-8 -*-
content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

# 1. ms-title h1 숨기기 + padding 줄이기 (2곳 모두)
old1 = '.ms-title{text-align:center;padding:14px 8px 6px 8px;animation:stageIn 0.5s ease;}\n.ms-title h1{font-size:2.2rem;font-weight:900;color:#00d4ff;letter-spacing:3px;animation:titleGlow 3s ease infinite;margin:0;}\n.ms-title p{font-size:0.9rem;color:#666;letter-spacing:2px;margin:3px 0 0 0;}'
new1 = '.ms-title{text-align:center;padding:4px 8px 2px 8px;animation:stageIn 0.5s ease;}\n.ms-title h1{display:none;}\n.ms-title p{font-size:0.85rem;color:#666;letter-spacing:2px;margin:0;}'
count1 = content.count(old1)
content = content.replace(old1, new1)
print(f'ms-title: {count1}곳')

# 2. 카테고리 버튼 글자 10% 작게 (JS에서 1.52rem → 1.37rem, 1.1rem → 1.0rem)
old2 = "+'<span class=\"p5l1\" style=\"display:block;font-size:1.52rem;font-weight:900;color:#fff;line-height:1.4;\">'+parts[0]+'</span>'\n                            +'<span style=\"display:block;font-size:1.1rem;font-weight:800;color:#ccc;line-height:1.3;\">'+parts.slice(1).join(' ')+'</span>';"
new2 = "+'<span class=\"p5l1\" style=\"display:block;font-size:1.37rem;font-weight:900;color:#fff;line-height:1.4;\">'+parts[0]+'</span>'\n                            +'<span style=\"display:block;font-size:1.0rem;font-weight:800;color:#ccc;line-height:1.3;\">'+parts.slice(1).join(' ')+'</span>';"
r2 = content.replace(old2, new2, 1)
print('btn font ok:', r2 != content); content = r2

# 3. stage 카드 padding 줄이기
old3 = '.stage{animation:stageIn 0.4s ease;border-radius:16px;padding:14px 12px;margin:3px 0;}'
new3 = '.stage{animation:stageIn 0.4s ease;border-radius:12px;padding:8px 10px;margin:2px 0;}'
count3 = content.count(old3)
content = content.replace(old3, new3)
print(f'stage padding: {count3}곳')

# 4. act-msg 글자 작게
old4 = '.act-msg{font-size:1.2rem;font-weight:900;color:#fff;text-align:center;margin-bottom:10px;line-height:1.3;}'
new4 = '.act-msg{font-size:1.05rem;font-weight:900;color:#fff;text-align:center;margin-bottom:5px;line-height:1.3;}'
count4 = content.count(old4)
content = content.replace(old4, new4)
print(f'act-msg: {count4}곳')

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done!')
