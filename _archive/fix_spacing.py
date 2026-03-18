with open('main_hub.py', encoding='cp949') as f:
    content = f.read()

old1 = '# =========================================================\r\n# 환영/복귀 메시지'
new1 = 'st.markdown(\'<div style="height:24px"></div>\', unsafe_allow_html=True)\r\n\r\n# =========================================================\r\n# 환영/복귀 메시지'
content = content.replace(old1, new1)

old2 = '# ── 공통 go-btn 스타일 ──'
new2 = 'st.markdown(\'<div style="height:24px"></div>\', unsafe_allow_html=True)\r\n\r\n# ── 공통 go-btn 스타일 ──'
content = content.replace(old2, new2)

with open('main_hub.py', 'w', encoding='cp949') as f:
    f.write(content)

print('DONE - 적용된 줄수:', content.count('height:24px'))
