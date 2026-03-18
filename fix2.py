import shutil
shutil.copy('main_hub.py', 'main_hub.py.bak2')

# 원본 내용 직접 복구 - page_icon 라인 수정
content = open('main_hub.py', 'r', encoding='utf-8').read()

# page_icon 깨진 거 복구
import re
content = re.sub(r"page_icon='[^']*',", "page_icon='⚡',", content)

# 그래프선 색상 수정
content = content.replace('    if last_two[1] > last_two[0]: lc = "#00ff88"', '    if last_two[1] > last_two[0]: lc = color')

# go-btn CSS 변수화
content = content.replace('background:linear-gradient(270deg,#ff6600,#ffcc00,#ff3300,#ffaa00);', 'background:var(--go-bg,linear-gradient(270deg,#ff6600,#ffcc00,#ff3300,#ffaa00));')
content = content.replace('border:2.5px solid rgba(255,220,100,0.95);', 'border:2.5px solid var(--go-border,rgba(255,220,100,0.95));')

# 카드별 go-btn 색상
content = content.replace('_hc.html(_CSS + _GO_STYLE + _mk_card("p5c"', '_hc.html(_CSS + _GO_STYLE + """<style>.p5c .go-btn{--go-bg:linear-gradient(270deg,#1565c0,#4fc3f7,#0d47a1,#29b6f6);--go-border:rgba(79,195,247,0.9);}</style>""" + _mk_card("p5c"')
content = content.replace('_hc.html(_CSS + _GO_STYLE + _mk_card("p7c"', '_hc.html(_CSS + _GO_STYLE + """<style>.p7c .go-btn{--go-bg:linear-gradient(270deg,#6a1b9a,#ce93d8,#4a148c,#ab47bc);--go-border:rgba(155,127,212,0.9);}</style>""" + _mk_card("p7c"')
content = content.replace('_hc.html(_CSS + _GO_STYLE + _mk_card("arc"', '_hc.html(_CSS + _GO_STYLE + """<style>.arc .go-btn{--go-bg:linear-gradient(270deg,#e65100,#ffd54f,#bf360c,#ffca28);--go-border:rgba(255,215,0,0.95);}</style>""" + _mk_card("arc"')

open('main_hub.py', 'w', encoding='utf-8').write(content)
print('완료! page_icon 확인:', "page_icon='⚡'" in content)
