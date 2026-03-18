# -*- coding: utf-8 -*-
content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

# 전장 4개 세로 → 2x2 배열 (이미 2열이지만 CSS 확인)
# act-label 글자 줄이기
old1 = '.act-label{font-size:0.75rem;font-weight:900;letter-spacing:4px;color:#00d4ff;margin-bottom:8px;text-align:center;}'
new1 = '.act-label{font-size:0.65rem;font-weight:900;letter-spacing:3px;color:#00d4ff;margin-bottom:4px;text-align:center;}'
r1 = content.replace(old1, new1)
print(f'act-label: {content.count(old1)}곳'); content = r1

# confirmed 위 공간 줄이기 + TOEIC 타이틀과 안 겹치게
old2 = '.confirmed{text-align:center;padding:4px;margin-bottom:6px;}\n.confirmed span{font-size:1.0rem;color:#ffd700;font-weight:900;background:rgba(255,215,0,0.15);padding:5px 16px;border-radius:20px;border:2px solid rgba(255,215,0,0.6);box-shadow:0 0 12px rgba(255,215,0,0.3);letter-spacing:1px;}'
new2 = '.confirmed{text-align:center;padding:2px;margin-bottom:4px;margin-top:2px;}\n.confirmed span{font-size:1.0rem;color:#ffd700;font-weight:900;background:rgba(255,215,0,0.15);padding:4px 14px;border-radius:20px;border:2px solid rgba(255,215,0,0.6);box-shadow:0 0 12px rgba(255,215,0,0.3);letter-spacing:1px;}'
r2 = content.replace(old2, new2)
print(f'confirmed: {content.count(old2)}곳'); content = r2

# 전장 버튼 세로4개 → 2x2로 교체
old3 = '''        b1,b2 = st.columns(2)
        with b1:
            if st.button("⚔ 문법력\\n수일치·시제·수동", key="sg1", type="secondary", use_container_width=True):
                st.session_state.sel_mode="g1"; st.rerun()
        with b2:
            if st.button("⚔ 구조력\\n가정법·도치·당위", key="sg2", type="secondary", use_container_width=True):
                st.session_state.sel_mode="g2"; st.rerun()
        b3,b4 = st.columns(2)
        with b3:
            if st.button("⚔ 연결력\\n접속사·관계사·분사", key="sg3", type="secondary", use_container_width=True):
                st.session_state.sel_mode="g3"; st.rerun()
        with b4:
            if st.button("📘 어휘력\\n품사·동사·콜로케이션", key="svc", type="secondary", use_container_width=True):
                st.session_state.sel_mode="vocab"; st.rerun()'''

new3 = '''        st.markdown(\'<style>.cat-btn button{padding:0.5rem 0.3rem!important;}.cat-btn button p{font-size:1.1rem!important;line-height:1.3!important;}</style>\', unsafe_allow_html=True)
        b1,b2 = st.columns(2)
        with b1:
            st.markdown(\'<div class="cat-btn">\', unsafe_allow_html=True)
            if st.button("⚔ 문법력\\n수일치·시제·수동", key="sg1", type="secondary", use_container_width=True):
                st.session_state.sel_mode="g1"; st.rerun()
            st.markdown(\'</div>\', unsafe_allow_html=True)
        with b2:
            st.markdown(\'<div class="cat-btn">\', unsafe_allow_html=True)
            if st.button("⚔ 구조력\\n가정법·도치·당위", key="sg2", type="secondary", use_container_width=True):
                st.session_state.sel_mode="g2"; st.rerun()
            st.markdown(\'</div>\', unsafe_allow_html=True)
        b3,b4 = st.columns(2)
        with b3:
            st.markdown(\'<div class="cat-btn">\', unsafe_allow_html=True)
            if st.button("⚔ 연결력\\n접속사·관계사·분사", key="sg3", type="secondary", use_container_width=True):
                st.session_state.sel_mode="g3"; st.rerun()
            st.markdown(\'</div>\', unsafe_allow_html=True)
        with b4:
            st.markdown(\'<div class="cat-btn">\', unsafe_allow_html=True)
            if st.button("📘 어휘력\\n품사·동사·콜로케이션", key="svc", type="secondary", use_container_width=True):
                st.session_state.sel_mode="vocab"; st.rerun()
            st.markdown(\'</div>\', unsafe_allow_html=True)'''

r3 = content.replace(old3, new3, 1)
print('2x2 ok:', r3 != content); content = r3

open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done!')
