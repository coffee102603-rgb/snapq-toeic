content = open('pages/02_P5_Arena.py', 'r', encoding='utf-8').read()

old = "        if st.button(\"🔥  HARD  ·  30초  고수의 선택\", key=\"t30\", type=\"secondary\", use_container_width=True):\n            st.session_state.tsec=30; st.session_state.tsec_chosen=True; st.rerun()\n        if st.button(\"⚡  NORMAL  ·  40초  표준 전투\", key=\"t40\", type=\"secondary\", use_container_width=True):\n            st.session_state.tsec=40; st.session_state.tsec_chosen=True; st.rerun()\n        if st.button(\"✅  EASY  ·  50초  여유로운 전투\", key=\"t50\", type=\"secondary\", use_container_width=True):\n            st.session_state.tsec=50; st.session_state.tsec_chosen=True; st.rerun()"

new = """        st.markdown('<div style="position:absolute;opacity:0;pointer-events:none;height:0;overflow:hidden;">', unsafe_allow_html=True)
        if st.button("🔥  HARD  ·  30초  고수의 선택", key="t30", type="secondary", use_container_width=True):
            st.session_state.tsec=30; st.session_state.tsec_chosen=True; st.rerun()
        if st.button("⚡  NORMAL  ·  40초  표준 전투", key="t40", type="secondary", use_container_width=True):
            st.session_state.tsec=40; st.session_state.tsec_chosen=True; st.rerun()
        if st.button("✅  EASY  ·  50초  여유로운 전투", key="t50", type="secondary", use_container_width=True):
            st.session_state.tsec=50; st.session_state.tsec_chosen=True; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)"""

content = content.replace(old, new)
open('pages/02_P5_Arena.py', 'w', encoding='utf-8').write(content)
print('done')