import sys, ast
sys.stdout.reconfigure(encoding="utf-8")

with open(r"C:\Users\최정은\Desktop\snapq_toeic_V3\pages\03_오답전장.py", "r", encoding="utf-8-sig") as f:
    content = f.read()

vault_start = content.find('if st.session_state.get("rv_mode") == "p7_vault":')
vault_end = content.find('# ════════════════════════════════\n# 콤보 러시 결과')
print(f"vault: {vault_start}~{vault_end}")

new_vault = (
'if st.session_state.get("rv_mode") == "p7_vault":\n'
'    st.markdown(\'\'\'<div style="text-align:center;padding:1rem 0;">\n'
'        <div style="font-size:1.8rem;font-weight:900;color:#185FA5;">📦 문장 저장고</div>\n'
'        <div style="font-size:0.9rem;color:#888;margin-top:4px;">저장한 문장으로 학습하고 시험 준비하세요</div>\n'
'    </div>\'\'\', unsafe_allow_html=True)\n'
'    storage2=load_storage()\n'
'    voca_list=storage2.get("saved_expressions",[])\n'
'    if not voca_list:\n'
'        st.markdown(\'\'\'<div style="text-align:center;background:#f8f8f8;border-radius:12px;padding:2rem;color:#888;">\n'
'            <div style="font-size:2rem;">📭</div>\n'
'            <div style="font-size:1rem;margin-top:8px;">저장된 문장이 없어요!</div>\n'
'            <div style="font-size:0.85rem;margin-top:4px;">P7전장 브리핑에서 어려운 문장을 저장하세요</div>\n'
'        </div>\'\'\', unsafe_allow_html=True)\n'
'    else:\n'
'        for idx,item in enumerate(voca_list):\n'
'            sentences=item.get("sentences",[])\n'
'            sentence=sentences[0] if sentences else item.get("expr","")\n'
'            kr_full=item.get("kr","") or item.get("meaning","")\n'
'            kr_sents=[x.strip() for x in kr_full.replace("!","!|").replace("?","?|").replace(".",".|").split("|") if x.strip()]\n'
'            sent_kr=kr_sents[0] if kr_sents else kr_full\n'
'            st.markdown(f\'\'\'<div style="background:#ffffff;border:0.5px solid #d3d1c7;border-radius:12px;padding:12px 14px;margin-bottom:4px;">\n'
'                <div style="font-size:15px;font-weight:700;color:#1a1a2e;line-height:1.6;">{sentence}</div>\n'
'                <div style="font-size:13px;color:#5f5e5a;margin-top:4px;">{sent_kr}</div>\n'
'            </div>\'\'\', unsafe_allow_html=True)\n'
'            if st.button("🗑 삭제",key=f"del_v_{idx}"):\n'
'                deleted=voca_list.pop(idx)\n'
'                deleted["deleted_at"]=__import__("time").time()\n'
'                deleted["days_kept"]=round((deleted["deleted_at"]-deleted.get("first_saved_at",deleted["deleted_at"]))/86400,1)\n'
'                dl=storage2.get("deleted_expressions",[]); dl.append(deleted)\n'
'                storage2["deleted_expressions"]=dl; storage2["saved_expressions"]=voca_list\n'
'                save_storage(storage2); st.rerun()\n'
'    st.markdown(\'<div style="margin-top:12px;"></div>\', unsafe_allow_html=True)\n'
'    if st.button("↩ 돌아가기",key="vault_back",use_container_width=True):\n'
'        st.session_state.rv_mode=None; st.rerun()\n'
'\n'
)

content = content[:vault_start] + new_vault + content[vault_end:]
with open(r"C:\Users\최정은\Desktop\snapq_toeic_V3\pages\03_오답전장.py", "w", encoding="utf-8") as f:
    f.write(content)
try:
    ast.parse(content)
    print("성공! 문법 OK!")
except SyntaxError as e:
    print(f"에러: {e}")
