# -*- coding: utf-8 -*-
content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

# 1. 타이틀 + _tsec_chosen 정의 순서 바꾸기
old1 = "    st.markdown(f'<div class=\"ms-title\"><h1>\u2694\ufe0f P5 ARENA \u2694\ufe0f</h1><p>TOEIC PART 5 \u00b7 5\ubb38\uc81c \uc11c\ubc14\uc774\ubc8c</p>{round_txt}</div>', unsafe_allow_html=True)\n\n    _tsec = st.session_state.get('tsec', 30)\n    _tsec_chosen = st.session_state.get('tsec_chosen', False)"
new1 = "    _tsec = st.session_state.get('tsec', 30)\n    _tsec_chosen = st.session_state.get('tsec_chosen', False)\n    if _tsec_chosen:\n        st.markdown(f'<div class=\"ms-title\"><p>TOEIC PART 5 \u00b7 5\ubb38\uc81c \uc11c\ubc14\uc774\ubc8c</p>{round_txt}</div>', unsafe_allow_html=True)\n    else:\n        st.markdown(f'<div class=\"ms-title\"><h1>\u2694\ufe0f P5 ARENA \u2694\ufe0f</h1><p>TOEIC PART 5 \u00b7 5\ubb38\uc81c \uc11c\ubc14\uc774\ubc8c</p>{round_txt}</div>', unsafe_allow_html=True)"
r1 = content.replace(old1, new1, 1)
print('title ok:', r1 != content); content = r1

# 2. 카테고리 버튼 글자 10% 작게
old2 = "+'<span class=\"p5l1\" style=\"display:block;font-size:1.52rem;font-weight:900;color:#fff;line-height:1.4;\">'+parts[0]+'</span>'\n                            +'<span style=\"display:block;font-size:1.1rem;font-weight:800;color:#ccc;line-height:1.3;\">'+parts.slice(1).join(' ')+'</span>';"
new2 = "+'<span class=\"p5l1\" style=\"display:block;font-size:1.37rem;font-weight:900;color:#fff;line-height:1.4;\">'+parts[0]+'</span>'\n                            +'<span style=\"display:block;font-size:1.0rem;font-weight:800;color:#ccc;line-height:1.3;\">'+parts.slice(1).join(' ')+'</span>';"
r2 = content.replace(old2, new2, 1)
print('cat font ok:', r2 != content); content = r2

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done!')
