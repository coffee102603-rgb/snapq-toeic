f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

# 491~494 (0-indexed 490~493) - phase 초기화 추가
lines[490]='            st.session_state._p5_just_left = True\n'
lines[491]='            st.session_state.ans = False\n'
lines[492]='            st.session_state["_battle_entry_ans_reset"] = True\n'
lines[493]='            for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx","phase"]:\n'
lines.insert(494, '                if k in st.session_state: del st.session_state[k]\n')
lines.insert(495, '            st.switch_page("main_hub.py")\n')

# 기존 switch_page 제거 (한줄 밀렸으므로)
del lines[496]

with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)

import ast
src=open(f,'r',encoding='utf-8').read()
try:
    ast.parse(src)
    print('syntax OK!')
except SyntaxError as e:
    print(f'error line {e.lineno}: {e.msg}')
