# -*- coding: utf-8 -*-
content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

# 1. ms-title CSS 교체 - 로고 숨기고 서브타이틀 날아오는 애니메이션
old1 = '.ms-title{text-align:center;padding:14px 8px 6px 8px;animation:stageIn 0.5s ease;}\n.ms-title h1{font-size:2.2rem;font-weight:900;color:#00d4ff;letter-spacing:3px;animation:titleGlow 3s ease infinite;margin:0;}\n.ms-title p{font-size:0.9rem;color:#666;letter-spacing:2px;margin:3px 0 0 0;}'
new1 = '.ms-title{text-align:center;padding:6px 8px 4px 8px;}\n.ms-title h1{display:none;}\n.ms-title p{font-size:0.9rem;color:#555;letter-spacing:2px;margin:0;}\n.ms-sub-anim{display:flex;justify-content:center;flex-wrap:wrap;gap:4px;padding:4px 0 2px 0;}\n.ms-sub-anim span{font-size:0.85rem;font-weight:700;color:#00d4ff;letter-spacing:2px;opacity:0;animation:flyIn 0.5s ease forwards;}\n@keyframes flyIn{0%{opacity:0;transform:translateY(-20px) scale(0.7);}100%{opacity:1;transform:translateY(0) scale(1);}}'
count1 = content.count(old1)
content = content.replace(old1, new1)
print(f'ms-title css: {count1}곳')

# 2. confirmed 스팬 크게 + 강조
old2 = '.confirmed{text-align:center;padding:6px;margin-bottom:8px;}\n.confirmed span{font-size:0.9rem;color:#ffd700;font-weight:900;background:rgba(255,215,0,0.1);padding:4px 12px;border-radius:20px;border:1px solid rgba(255,215,0,0.4);}'
new2 = '.confirmed{text-align:center;padding:4px;margin-bottom:6px;}\n.confirmed span{font-size:1.0rem;color:#ffd700;font-weight:900;background:rgba(255,215,0,0.15);padding:5px 16px;border-radius:20px;border:2px solid rgba(255,215,0,0.6);box-shadow:0 0 12px rgba(255,215,0,0.3);letter-spacing:1px;}'
count2 = content.count(old2)
content = content.replace(old2, new2)
print(f'confirmed: {count2}곳')

# 3. stage 카드 padding 줄이기
old3 = '.stage{animation:stageIn 0.4s ease;border-radius:16px;padding:14px 12px;margin:3px 0;}'
new3 = '.stage{animation:stageIn 0.4s ease;border-radius:12px;padding:8px 10px;margin:2px 0;}'
count3 = content.count(old3)
content = content.replace(old3, new3)
print(f'stage: {count3}곳')

# 4. act-msg 글자 작게
old4 = '.act-msg{font-size:1.2rem;font-weight:900;color:#fff;text-align:center;margin-bottom:10px;line-height:1.3;}'
new4 = '.act-msg{font-size:1.0rem;font-weight:900;color:#fff;text-align:center;margin-bottom:6px;line-height:1.3;}'
count4 = content.count(old4)
content = content.replace(old4, new4)
print(f'act-msg: {count4}곳')

# 5. 타이틀 HTML 교체 - 로고 제거, 날아오는 단어 애니메이션
old5 = "    st.markdown(f'<div class=\"ms-title\"><h1>⚔️ P5 ARENA ⚔️</h1><p>TOEIC PART 5 · 5문제 서바이벌</p>{round_txt}</div>', unsafe_allow_html=True)"
new5 = "    _words = ['TOEIC','PART','5','·','5문제','서바이벌']\n    _spans = ''.join([f'<span style=\"animation-delay:{i*0.12}s\">{w}</span>' for i,w in enumerate(_words)])\n    st.markdown(f'<div class=\"ms-title\"><div class=\"ms-sub-anim\">{_spans}</div>{round_txt}</div>', unsafe_allow_html=True)"
r5 = content.replace(old5, new5, 1)
print('title html ok:', r5 != content); content = r5

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done!')
