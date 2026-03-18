c = open('main_hub.py', encoding='utf-8').read()

# 줄바꿈 없이 버튼 텍스트 교체
c = c.replace(
    'if st.button("⚡  P5 전장\n    시험장은 전쟁터다!", key="p5_btn"',
    'if st.button("⚡ P5 전장 - 시험장은 전쟁터다!", key="p5_btn"'
)
c = c.replace(
    'if st.button("📖  P7 전장\n    고득점, 원하니?", key="p7_btn"',
    'if st.button("📖 P7 전장 - 고득점, 원하니?", key="p7_btn"'
)
c = c.replace(
    'if st.button("🗡  역전장\n    오답 설욕전! 토익 역전! 인생 역전!", key="arm_btn"',
    'if st.button("역전장 - 오답 설욕전! 토익 역전! 인생 역전!", key="arm_btn"'
)

open('main_hub.py', 'w', encoding='utf-8').write(c)
import py_compile
py_compile.compile('main_hub.py', doraise=True)
print('OK!')