# -*- coding: utf-8 -*-
content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

# 해골 5rem → 4rem
old1 = '.skull{{font-size:5rem;animation:shakeX 0.4s ease-in-out infinite;display:inline-block;margin-bottom:10px;}}'
new1 = '.skull{{font-size:4rem;animation:shakeX 0.4s ease-in-out infinite;display:inline-block;margin-bottom:6px;}}'
r1 = content.replace(old1, new1, 1)
print('skull ok:', r1 != content); content = r1

# GAME OVER 3.5rem → 2.8rem
old2 = '.lost-txt{{font-size:3.5rem;font-weight:900;color:#ff0000;text-shadow:0 0 20px #ff0000,0 0 60px #cc0000;animation:flicker 0.3s infinite;letter-spacing:4px;}}'
new2 = '.lost-txt{{font-size:2.8rem;font-weight:900;color:#ff0000;text-shadow:0 0 20px #ff0000,0 0 60px #cc0000;animation:flicker 0.3s infinite;letter-spacing:4px;}}'
r2 = content.replace(old2, new2, 1)
print('lost-txt ok:', r2 != content); content = r2

# reason 1.4rem → 1.1rem
old3 = '.reason{{font-size:1.4rem;color:#ff6644;font-weight:700;margin:8px 0;letter-spacing:2px;}}'
new3 = '.reason{{font-size:1.1rem;color:#ff6644;font-weight:700;margin:5px 0;letter-spacing:2px;}}'
r3 = content.replace(old3, new3, 1)
print('reason ok:', r3 != content); content = r3

# score 4rem → 3.2rem
old4 = '.score{{font-size:4rem;font-weight:900;color:#ffcc00;text-shadow:0 0 30px #ffaa00;margin:10px 0;}}'
new4 = '.score{{font-size:3.2rem;font-weight:900;color:#ffcc00;text-shadow:0 0 30px #ffaa00;margin:6px 0;}}'
r4 = content.replace(old4, new4, 1)
print('score ok:', r4 != content); content = r4

# taunt 1.3rem → 1.05rem
old5 = '.taunt{{font-size:1.3rem;color:#ff8888;font-weight:700;margin:6px 0;}}'
new5 = '.taunt{{font-size:1.05rem;color:#ffe066;font-weight:900;margin:4px 0;text-shadow:0 0 8px rgba(255,200,0,0.8);}}'
r5 = content.replace(old5, new5, 1)
print('taunt ok:', r5 != content); content = r5

# wrap padding 줄이기
old6 = '.wrap{{text-align:center;animation:crashIn 0.6s cubic-bezier(0.34,1.56,0.64,1) forwards;z-index:10;position:relative;padding:20px;}}'
new6 = '.wrap{{text-align:center;animation:crashIn 0.6s cubic-bezier(0.34,1.56,0.64,1) forwards;z-index:10;position:relative;padding:10px;}}'
r6 = content.replace(old6, new6, 1)
print('wrap ok:', r6 != content); content = r6

# height 420 → 360
old7 = '), height=420)'
new7 = '), height=360)'
r7 = content.replace(old7, new7, 1)
print('height ok:', r7 != content); content = r7

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done!')
