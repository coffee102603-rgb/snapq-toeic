import sys, ast
sys.stdout.reconfigure(encoding="utf-8")

with open(r"C:\Users\최정은\Desktop\snapq_toeic_V3\pages\03_오답전장.py", "r", encoding="utf-8-sig") as f:
    lines = f.readlines()

start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if 'elif st.session_state.sg_phase == "survival":' in line and start_idx is None:
        start_idx = i
    if 'elif st.session_state.sg_phase == "survival_result":' in line:
        end_idx = i
        break

print(f"start={start_idx}, end={end_idx}")

new_survival = '''elif st.session_state.sg_phase == "survival":
    # ════════ 문장 퍼즐 배틀 ════════
    import re as _re5
    if not voca_data:
        st.markdown(\'\'\'<div style="text-align:center;background:#f8f8f8;border-radius:12px;padding:2rem;">
            <div style="font-size:2rem;">📭</div>
            <div style="font-size:1rem;font-weight:600;color:#333;margin-top:8px;">저장된 문장이 없어요!</div>
            <div style="font-size:0.85rem;color:#888;margin-top:4px;">P7전장 브리핑에서 어려운 문장을 저장하세요</div>
        </div>\'\'\', unsafe_allow_html=True)
        if st.button("↩ 돌아가기", key="sv_no_data"):
            st.session_state.sg_phase="lobby"; st.session_state.rv_battle=None; st.session_state.rv_mode=None; st.rerun()
        st.stop()

    # 세션 초기화
    if "sb_idx" not in st.session_state: st.session_state.sb_idx=0
    if "sb_pool" not in st.session_state:
        pool=[v for v in voca_data if v.get("sentences")]
        if not pool: pool=voca_data[:]
        random.shuffle(pool)
        st.session_state.sb_pool=pool
    if "sb_selected" not in st.session_state: st.session_state.sb_selected=[]
    if "sb_done" not in st.session_state: st.session_state.sb_done=False
    if "sb_blanked" not in st.session_state: st.session_state.sb_blanked=""
    if "sb_blank_words" not in st.session_state: st.session_state.sb_blank_words=[]
    if "sb_blank_order" not in st.session_state: st.session_state.sb_blank_order=[]
    if "sb_last_idx" not in st.session_state: st.session_state.sb_last_idx=-1

    pool=st.session_state.sb_pool
    idx=st.session_state.sb_idx
    total=len(pool)

    # 모든 문장 완료
    if idx>=total:
        st.markdown(\'\'\'<div style="text-align:center;padding:2rem;background:#eaf3de;border-radius:16px;border:1px solid #c0dd97;">
            <div style="font-size:2.5rem;">🎉</div>
            <div style="font-size:1.3rem;font-weight:700;color:#27500a;margin-top:8px;">모든 문장 완료!</div>
            <div style="font-size:0.95rem;color:#639922;margin-top:4px;">이제 시험모드에서 증명하라!</div>
        </div>\'\'\', unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            if st.button("⚡ 시험모드!",key="sb_go_exam",type="primary",use_container_width=True):
                st.session_state.sg_combo_score=0; st.session_state.sg_combo_count=0
                st.session_state.sg_combo_idx=0; st.session_state.sg_combo_start=time.time()
                st.session_state.sg_combo_over=False; st.session_state.sg_combo_results=[]
                if "sg_combo_pool" in st.session_state: del st.session_state.sg_combo_pool
                st.session_state.rv_mode="p7e"; st.session_state.sg_phase="combo_rush"; st.rerun()
        with c2:
            if st.button("🔄 처음부터",key="sb_restart",use_container_width=True):
                for k in ["sb_idx","sb_pool","sb_selected","sb_done","sb_blanked","sb_blank_words","sb_blank_order","sb_last_idx"]:
                    if k in st.session_state: del st.session_state[k]
                st.rerun()
        st.stop()

    # 새 문장 진입시 초기화
    if st.session_state.sb_last_idx != idx:
        st.session_state.sb_selected=[]
        st.session_state.sb_done=False
        st.session_state.sb_blanked=""
        st.session_state.sb_blank_words=[]
        st.session_state.sb_blank_order=[]
        st.session_state.sb_last_idx=idx

    item=pool[idx]
    sentences=item.get("sentences",[])
    sentence=sentences[0] if sentences else ""
    if not sentence:
        st.session_state.sb_idx=idx+1; st.rerun()

    kr_full=item.get("kr","") or item.get("meaning","")
    kr_sents=[x.strip() for x in kr_full.replace("!","!|").replace("?","?|").replace(".",".|").split("|") if x.strip()]
    sent_kr=kr_sents[0] if kr_sents else kr_full

    # 블랭크 준비 (한 번만)
    if not st.session_state.sb_blanked:
        words=sentence.split()
        stopwords={"the","a","an","in","on","at","to","for","of","by","with","is","are","was","were","has","have","had","be","been","that","this","it","its","and","or","but","as","if","so","not","do","did","will","shall","would","could","should","must","from","into","upon","than","then","also"}
        candidates=[w.strip(".,!?;:()") for w in words if w.strip(".,!?;:()").lower() not in stopwords and len(w.strip(".,!?;:()"))>=3]
        rng=random.Random(hash(sentence))
        rng.shuffle(candidates)
        blank_words=candidates[:3] if len(candidates)>=3 else candidates
        if len(blank_words)<2:
            blank_words=[w.strip(".,!?;:()") for w in words if len(w.strip(".,!?;:()"))>=3][:3]
        blanked=sentence
        border=[]
        for bw in blank_words:
            pat=r"(?i)\\b"+_re5.escape(bw)+r"\\b"
            if _re5.search(pat,blanked):
                blanked=_re5.sub(pat,"[___]",blanked,count=1)
                border.append(bw)
        # 오답 2개 생성
        WORD_DB={"a":["analyze","assess","address","achieve"],"b":["balance","benefit","boost"],"c":["comply","conduct","confirm","consider","complete"],"d":["deliver","determine","develop","decline"],"e":["establish","evaluate","expand","ensure"],"f":["facilitate","finalize","fulfill","focus"],"g":["generate","grant","guide"],"h":["handle","highlight","hire"],"i":["implement","improve","indicate","inspect"],"l":["launch","limit","locate","leverage"],"m":["maintain","manage","measure","monitor"],"n":["notify","negotiate"],"o":["obtain","operate","optimize","organize"],"p":["prepare","process","provide","publish","perform"],"r":["receive","record","reduce","renew","report"],"s":["submit","supply","support","suspend","schedule"],"t":["terminate","transfer","transform","track"],"u":["update","upgrade","utilize","undergo"],"v":["verify","validate"],"w":["withdraw","work"]}
        distractors=[]
        for bw in border:
            first=bw[0].lower() if bw else "s"
            cands=WORD_DB.get(first,WORD_DB.get("s",[]))
            filtered=[w for w in cands if w.lower()!=bw.lower() and w.lower() not in [b.lower() for b in border]]
            filtered.sort(key=lambda w:abs(len(w)-len(bw)))
            if filtered: distractors.append(filtered[0])
        while len(distractors)<2:
            distractors.append(["process","indicate","establish","provide","conduct"][len(distractors)])
        distractors=list(dict.fromkeys(distractors))[:2]
        all_choices=border+distractors
        rng.shuffle(all_choices)
        st.session_state.sb_blanked=blanked
        st.session_state.sb_blank_order=border
        st.session_state.sb_blank_words=all_choices

    blanked=st.session_state.sb_blanked
    blank_order=st.session_state.sb_blank_order
    blank_words=st.session_state.sb_blank_words
    selected=st.session_state.sb_selected
    done=st.session_state.sb_done

    # ── 헤더 ──
    st.markdown(f\'\'\'<div style="background:#1a1a2e;border:1.5px solid #4488ff;border-radius:14px;padding:8px 14px;text-align:center;margin-bottom:8px;">
        <div style="font-size:0.95rem;font-weight:700;color:#4488ff;">📖 문장 퍼즐 배틀</div>
        <div style="font-size:0.8rem;color:#aaa;margin-top:2px;">{idx+1} / {total} 문장</div>
        <div style="background:#0a0a1a;border-radius:4px;height:5px;margin-top:5px;"><div style="background:linear-gradient(90deg,#4488ff,#44ccff);height:5px;border-radius:4px;width:{int((idx/max(total,1))*100)}%;"></div></div>
    </div>\'\'\', unsafe_allow_html=True)

    # ── 한글 해석 (위) ──
    st.markdown(f\'\'\'<div style="background:#fffff5;border:1.5px solid #e8e0c8;border-radius:12px;padding:12px 14px;margin-bottom:6px;">
        <div style="font-size:0.65rem;color:#aaa;letter-spacing:2px;margin-bottom:5px;">KOREAN</div>
        <div style="font-size:1.05rem;color:#222;line-height:1.8;font-weight:500;">{sent_kr}</div>
    </div>\'\'\', unsafe_allow_html=True)

    st.markdown(\'<div style="text-align:center;color:#888;font-size:0.8rem;margin:3px 0;">↓ 영어 문장 빈칸을 채워라!</div>\', unsafe_allow_html=True)

    # ── 영어 빈칸 문장 (아래) ──
    filled_parts=blanked.split("[___]")
    sentence_html=""
    for i,part in enumerate(filled_parts):
        sentence_html+=f\'<span style="color:#ddddff;">{part}</span>\'
        if i<len(filled_parts)-1:
            if i<len(selected):
                sentence_html+=f\'<span style="background:#0a2a0a;border:2px solid #44ff88;border-radius:8px;padding:2px 10px;color:#44ff88;font-weight:700;margin:0 3px;">{selected[i]}</span>\'
            else:
                sentence_html+=\'<span style="background:#0a0a1a;border:2px dashed #4488ff;border-radius:8px;padding:2px 18px;color:#333;margin:0 3px;">_____</span>\'
    st.markdown(f\'\'\'<div style="background:#1a1a2e;border:1.5px solid #4488ff;border-radius:12px;padding:12px 14px;margin-bottom:8px;font-size:1.05rem;font-weight:600;line-height:2.2;">{sentence_html}</div>\'\'\', unsafe_allow_html=True)

    if done:
        sel_lower=[s.lower() for s in selected]
        ord_lower=[b.lower() for b in blank_order]
        correct=(sel_lower==ord_lower)
        if correct:
            st.markdown(\'\'\'<div style="background:#0a2a0a;border:1.5px solid #44ff88;border-radius:12px;padding:10px;text-align:center;">
                <div style="font-size:1.2rem;font-weight:800;color:#44ff88;">✅ 완벽해!</div>
            </div>\'\'\', unsafe_allow_html=True)
        else:
            result_sent=blanked
            for bw in blank_order:
                result_sent=result_sent.replace("[___]",f\'<span style="background:#0a2a0a;border:2px solid #44ff88;border-radius:6px;padding:2px 8px;color:#44ff88;font-weight:700;">{bw}</span>\',1)
            st.markdown(f\'\'\'<div style="background:#1a0808;border:1.5px solid #ff4444;border-radius:12px;padding:10px 12px;margin-bottom:6px;">
                <div style="font-size:0.85rem;font-weight:700;color:#ff6666;margin-bottom:6px;">❌ 정답은 이거야!</div>
                <div style="font-size:1.0rem;font-weight:600;line-height:2.0;">{result_sent}</div>
            </div>\'\'\', unsafe_allow_html=True)
        if st.button("▶ 다음 문장!",key="sb_next",type="primary",use_container_width=True):
            st.session_state.sb_idx=idx+1
            for k in ["sb_selected","sb_done","sb_blanked","sb_blank_order","sb_blank_words"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()
    else:
        # ── 단어 카드 5개 ──
        st.markdown(\'<div style="font-size:0.8rem;color:#888;text-align:center;margin-bottom:5px;">👇 단어를 터치해서 빈칸에 넣어라!</div>\', unsafe_allow_html=True)
        used=[s.lower() for s in selected]
        cols=st.columns(len(blank_words))
        for ci,bw in enumerate(blank_words):
            with cols[ci]:
                if bw.lower() in used:
                    st.markdown(f\'<div style="background:#111;border:1px solid #333;border-radius:10px;padding:10px 4px;text-align:center;color:#333;font-weight:700;font-size:0.9rem;">{bw}</div>\', unsafe_allow_html=True)
                else:
                    if st.button(bw,key=f"sv_w_{idx}_{ci}",use_container_width=True):
                        new_sel=selected+[bw]
                        st.session_state.sb_selected=new_sel
                        if len(new_sel)>=len(blank_order): st.session_state.sb_done=True
                        st.rerun()
        if selected:
            if st.button("↩ 다시 선택",key="sv_clear",use_container_width=False):
                st.session_state.sb_selected=[]; st.session_state.sb_done=False; st.rerun()

    c1,c2=st.columns(2)
    with c1:
        if st.button("⏭ 건너뛰기",key=f"sv_skip_{idx}",use_container_width=True):
            st.session_state.sb_idx=idx+1
            for k in ["sb_selected","sb_done","sb_blanked","sb_blank_order","sb_blank_words"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()
    with c2:
        if st.button("⚡ 시험 바로가기",key="sv_exam",use_container_width=True):
            st.session_state.sg_combo_score=0; st.session_state.sg_combo_count=0
            st.session_state.sg_combo_idx=0; st.session_state.sg_combo_start=time.time()
            st.session_state.sg_combo_over=False; st.session_state.sg_combo_results=[]
            if "sg_combo_pool" in st.session_state: del st.session_state.sg_combo_pool
            st.session_state.rv_mode="p7e"; st.session_state.sg_phase="combo_rush"; st.rerun()

'''

new_lines = lines[:start_idx] + [new_survival] + lines[end_idx:]
with open(r"C:\Users\최정은\Desktop\snapq_toeic_V3\pages\03_오답전장.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

with open(r"C:\Users\최정은\Desktop\snapq_toeic_V3\pages\03_오답전장.py", "r", encoding="utf-8") as f:
    src = f.read()
try:
    ast.parse(src)
    print("성공! 문법 OK!")
except SyntaxError as e:
    print(f"에러: {e}")
