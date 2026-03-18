import re
c = open('pages/02_P5_Arena.py', encoding='utf-8').read()

# 이전 주입 모두 제거
c = re.sub(r'        _t30 = st\.button.*?""", height=155\)', '', c, flags=re.DOTALL)
c = re.sub(r'        import streamlit\.components.*?""", height=\d+\)', '', c, flags=re.DOTALL)
c = re.sub(r'        st\.markdown\("""<style>button.*?</style>""", unsafe_allow_html=True\)\n', '', c, flags=re.DOTALL)
c = re.sub(r'        # hide streamlit.*?\n', '', c)

# 타이머 CSS 애니메이션을 전역 스타일로 추가
anim_css = '''        st.markdown("""
<style>
div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
  background: #0d0d0d !important;
  border: 2px solid rgba(255,80,0,0.3) !important;
  animation: zap30 3.6s ease-in-out infinite !important;
  font-size: 1.6rem !important;
  min-height: 120px !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
  background: #0d0d0d !important;
  border: 2px solid rgba(255,200,0,0.3) !important;
  animation: zap40 3.6s ease-in-out infinite !important;
  font-size: 1.6rem !important;
  min-height: 120px !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {
  background: #0d0d0d !important;
  border: 2px solid rgba(0,220,100,0.3) !important;
  animation: zap50 3.6s ease-in-out infinite !important;
  font-size: 1.6rem !important;
  min-height: 120px !important;
}
@keyframes zap30 {
  0%,25%,35%,100% {box-shadow:0 0 6px rgba(255,80,0,0.2);border-color:rgba(255,80,0,0.3);}
  28%,32% {box-shadow:0 0 40px #ff4400,0 0 80px #ff8800;border-color:#ff8800;background:rgba(255,80,0,0.08)!important;}
}
@keyframes zap40 {
  0%,58%,68%,100% {box-shadow:0 0 6px rgba(255,200,0,0.2);border-color:rgba(255,200,0,0.3);}
  61%,65% {box-shadow:0 0 40px #ffcc00,0 0 80px #ffee00;border-color:#ffee00;background:rgba(255,200,0,0.08)!important;}
}
@keyframes zap50 {
  0%,91%,100% {box-shadow:0 0 6px rgba(0,220,100,0.2);border-color:rgba(0,220,100,0.3);}
  94%,98% {box-shadow:0 0 40px #00ee66,0 0 80px #00ffaa;border-color:#00ffaa;background:rgba(0,220,100,0.08)!important;}
}
</style>
""", unsafe_allow_html=True)
'''

old = ('        tc1,tc2,tc3 = st.columns(3)\n'
       '        with tc1:\n'
       '            if st.button("\U0001f525\\n30\ucd08", key="t30", type="secondary", use_container_width=True):\n'
       '                st.session_state.tsec=30; st.session_state.tsec_chosen=True; st.rerun()\n'
       '        with tc2:\n'
       '            if st.button("\u26a1\\n40\ucd08", key="t40", type="secondary", use_container_width=True):\n'
       '                st.session_state.tsec=40; st.session_state.tsec_chosen=True; st.rerun()\n'
       '        with tc3:\n'
       '            if st.button("\u2705\\n50\ucd08", key="t50", type="secondary", use_container_width=True):\n'
       '                st.session_state.tsec=50; st.session_state.tsec_chosen=True; st.rerun()')

new = (anim_css +
       '        tc1,tc2,tc3 = st.columns(3)\n'
       '        with tc1:\n'
       '            if st.button("\U0001f525\\n30\ucd08", key="t30", type="secondary", use_container_width=True):\n'
       '                st.session_state.tsec=30; st.session_state.tsec_chosen=True; st.rerun()\n'
       '        with tc2:\n'
       '            if st.button("\u26a1\\n40\ucd08", key="t40", type="secondary", use_container_width=True):\n'
       '                st.session_state.tsec=40; st.session_state.tsec_chosen=True; st.rerun()\n'
       '        with tc3:\n'
       '            if st.button("\u2705\\n50\ucd08", key="t50", type="secondary", use_container_width=True):\n'
       '                st.session_state.tsec=50; st.session_state.tsec_chosen=True; st.rerun()')

print('OLD found:', old in c)
c2 = c.replace(old, new, 1)
open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(c2)
print('완료! 라인수:', c2.count(chr(10)))