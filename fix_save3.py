f='C:/Users/최정은/Desktop/snapq_toeic_V3/pages/02_P5_Arena.py'
with open(f,'r',encoding='utf-8') as fp:
    lines=fp.readlines()

# 저장 query_params 처리 추가 - br_q 처리 바로 뒤에 삽입
for i,l in enumerate(lines):
    if 'st.session_state.br_idx = int(_br_q)' in l:
        sv_handler=[
'    _br_save = st.query_params.get("br_save","")\n',
'    if _br_save != "":\n',
'        st.query_params.clear()\n',
'        _sq = rqs[bi] if "rqs" in dir() else st.session_state.round_qs[st.session_state.br_idx]\n',
'        _sitem = {"id":_sq["id"],"text":_sq["text"],"ch":_sq["ch"],"a":_sq["a"],"ex":_sq.get("ex",""),"exk":_sq.get("exk",""),"cat":_sq.get("cat",""),"kr":_sq.get("kr",""),"tp":_sq.get("tp","grammar")}\n',
'        save_to_storage([_sitem])\n',
'        st.session_state["_saved_ok"] = True\n',
'        st.rerun()\n',
]
        for j,sl in enumerate(sv_handler):
            lines.insert(i+1+j, sl)
        print(f'handler inserted at {i+2}')
        break

with open(f,'w',encoding='utf-8') as fp:
    fp.writelines(lines)

# 새 줄번호 확인
with open(f,'r',encoding='utf-8') as fp:
    lines2=fp.readlines()
for i,l in enumerate(lines2):
    if 'sv_c1' in l:
        print(f'sv_c1 at: {i+1}')
        break
print('step1 done!')
