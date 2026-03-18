f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

# query_params 처리 핸들러 삽입 (480번줄 앞)
qp='''    _br_nav = st.query_params.get("br_nav","")
    if _br_nav != "":
        st.query_params.clear()
        if _br_nav == "lobby":
            for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx"]:
                if k in st.session_state: del st.session_state[k]
            for k,v in D.items():
                if k not in st.session_state: st.session_state[k]=v
            st.session_state.phase = "lobby"; st.rerun()
        elif _br_nav == "main":
            st.session_state._p5_just_left = True
            st.session_state.ans = False
            st.session_state["_battle_entry_ans_reset"] = True
            st.switch_page("main_hub.py")
    _br_q = st.query_params.get("br_q","")
    if _br_q != "":
        st.query_params.clear()
        st.session_state.br_idx = int(_br_q); st.rerun()
'''
lines.insert(480, qp)

# 1~5 버튼 교체 (삽입 후 줄번호 +1)
new_dots='''    dot_html = \'<div style="display:flex;gap:6px;margin:6px 0;">\'
    for i in range(num_qs):
        border = "2px solid #00d4ff" if i == bi else "1px solid #444"
        dot_html += f\'<a href="?br_q={i}" style="flex:1;display:flex;align-items:center;justify-content:center;height:36px;background:#0d0d0d;border:{border};border-radius:8px;color:#fff;text-decoration:none;font-size:0.75rem;font-weight:300;">{i+1}</a>\'
    dot_html += \'</div>\'
    st.markdown(dot_html, unsafe_allow_html=True)
'''
lines[547:555]=new_dots.splitlines(keepends=True)

# 로비/메인 HTML 버튼
new_nav='''    st.markdown("---")
    nav_html = \'<div style="display:flex;gap:8px;margin:6px 0;"><a href="?br_nav=lobby" style="flex:1;display:flex;align-items:center;justify-content:center;height:40px;background:#0d0d0d;border:1px solid rgba(0,212,255,0.5);border-radius:8px;color:#fff;text-decoration:none;font-size:0.75rem;font-weight:300;">로비</a><a href="?br_nav=main" style="flex:1;display:flex;align-items:center;justify-content:center;height:40px;background:#0d0d0d;border:1px solid rgba(0,212,255,0.5);border-radius:8px;color:#fff;text-decoration:none;font-size:0.75rem;font-weight:300;">메인</a></div>\'
    st.markdown(nav_html, unsafe_allow_html=True)
'''
# 로비/메인 st.button 블록 찾아서 교체
start=-1
for i,l in enumerate(lines):
    if 'st.markdown("---")' in l and i>540:
        start=i; break
if start!=-1:
    end=start
    for i in range(start,start+70):
        if i>=len(lines): break
        if 'switch_page("main_hub.py")' in lines[i]:
            end=i+1
    lines[start:end]=new_nav.splitlines(keepends=True)
    print(f'replaced {start} to {end}')

with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)
print('done!')
