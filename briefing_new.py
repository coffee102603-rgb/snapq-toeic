elif st.session_state.phase=="briefing":
    st.markdown("""<style>
    section[data-testid="stSidebar"]{display:none!important;}
    header[data-testid="stHeader"]{height:0!important;visibility:hidden!important;}
    .block-container{padding-top:0.2rem!important;padding-bottom:0!important;}
    </style>""", unsafe_allow_html=True)

    was_victory = st.session_state.sc >= 3
    if "br_idx" not in st.session_state: st.session_state.br_idx = 0
    if "br_saved" not in st.session_state: st.session_state.br_saved = set()

    _action = st.query_params.get("br_action", "")
    _aval   = st.query_params.get("br_val", "")
    if _action == "nav" and _aval.isdigit():
        st.session_state.br_idx = int(_aval)
        st.query_params.clear(); st.rerun()
    elif _action == "save":
        bi2 = st.session_state.br_idx
        rqs2 = st.session_state.round_qs
        if 0 <= bi2 < len(rqs2):
            q2 = rqs2[bi2]
            item = {"id":q2["id"],"text":q2["text"],"ch":q2["ch"],"a":q2["a"],
                    "ex":q2.get("ex",""),"exk":q2.get("exk",""),"cat":q2.get("cat",""),
                    "kr":q2.get("kr",""),"tp":q2.get("tp","grammar")}
            save_to_storage([item])
            st.session_state.br_saved.add(bi2)
        st.query_params.clear(); st.rerun()
    elif _action == "next_round":
        st.session_state.round_num += 1
        for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx","br_saved"]:
            if k in st.session_state: del st.session_state[k]
        for k,v in D.items():
            if k not in st.session_state: st.session_state[k]=v
        qs = pick5(st.session_state.mode)
        st.session_state.round_qs = qs; st.session_state.cq = qs[0]
        st.session_state.qst = time.time(); st.session_state.phase = "battle"
        st.query_params.clear(); st.rerun()
    elif _action == "retry":
        for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx","br_saved"]:
            if k in st.session_state: del st.session_state[k]
        for k,v in D.items():
            if k not in st.session_state: st.session_state[k]=v
        qs = pick5(st.session_state.mode)
        st.session_state.round_qs = qs; st.session_state.cq = qs[0]
        st.session_state.qst = time.time(); st.session_state.phase = "battle"
        st.query_params.clear(); st.rerun()
    elif _action == "home":
        st.session_state._p5_just_left = True
        st.session_state.ans = False
        st.session_state["_battle_entry_ans_reset"] = True
        st.query_params.clear()
        st.switch_page("main_hub.py")

    bi    = st.session_state.br_idx
    rqs   = st.session_state.round_qs
    rrs   = st.session_state.round_results
    saved = st.session_state.br_saved
    num_qs = min(len(rqs), len(rrs))
    if bi >= num_qs: bi = num_qs - 1
    if bi < 0: bi = 0
    rn    = st.session_state.round_num
    sc_v  = st.session_state.sc
    wr_v  = st.session_state.wrong

    q  = rqs[bi]; ok = rrs[bi]
    ans_clean = q["ch"][q["a"]].split(") ",1)[-1] if ") " in q["ch"][q["a"]] else q["ch"][q["a"]]
    if ok:
        sent_html = q["text"].replace("_______", '<span style="color:#50c878;font-weight:900;border-bottom:2px solid #50c878;">'+ans_clean+'</span>')
        card_border="#00d4ff"; qnum_color="#50c878"; qnum_sym="V"
    else:
        sent_html = q["text"].replace("_______", '<span style="color:#ff4466;font-weight:900;text-decoration:line-through;margin-right:4px;">?</span><span style="color:#50c878;font-weight:900;border-bottom:2px solid #50c878;">'+ans_clean+'</span>')
        card_border="#cc2244"; qnum_color="#ff4466"; qnum_sym="X"
    kr=q.get("kr",""); exk=q.get("exk",""); cat=q.get("cat","")
    is_saved = bi in saved

    dots = "".join([
        '<a href="?br_action=nav&br_val='+str(_i)+'" style="display:inline-flex;align-items:center;justify-content:center;width:38px;height:38px;border-radius:50%;font-size:0.95rem;font-weight:900;text-decoration:none;background:'+("#0d2010" if rrs[_i] else "#200810")+';border:2px solid '+("#50c878" if rrs[_i] else "#cc2244")+';color:'+("#50c878" if rrs[_i] else "#cc2244")+';box-shadow:0 0 8px '+("rgba(80,200,120,0.5)" if rrs[_i] else "rgba(204,34,68,0.5)")+';'+("outline:3px solid #00d4ff;outline-offset:3px;" if _i==bi else "")+'">'+str(_i+1)+'</a>'
        for _i in range(num_qs)
    ])
    prev_href = "?br_action=nav&br_val="+str(bi-1) if bi > 0 else "#"
    next_href = "?br_action=nav&br_val="+str(bi+1) if bi < num_qs-1 else "#"
    prev_op = "1" if bi > 0 else "0.3"
    next_op = "1" if bi < num_qs-1 else "0.3"

    if was_victory:
        banner_bg="#0c0c00"; banner_bc="#d4af37"
        banner_title="🏆 라운드 "+str(rn)+" — VICTORY!"
        banner_sub="✅"+str(sc_v)+"문제 격파! ❌"+str(wr_v)+"개 놓침"
        banner_tc="#d4af37"; banner_sc="#886600"
    else:
        banner_bg="#0c0008"; banner_bc="#cc2244"
        banner_title="💀 라운드 "+str(rn)+" — GAME OVER"
        banner_sub="✅"+str(sc_v)+"문제 / ❌"+str(wr_v)+"개 틀림"
        banner_tc="#cc2244"; banner_sc="#661122"

    save_label = "✅ 저장됨" if is_saved else "⚔️ 오답전장 저장"
    save_style = "background:#0a1a0a;border:1px solid #50c878;color:#50c878;" if is_saved else "background:#0c0c14;border:1px solid #4488cc;color:#4488cc;"

    if was_victory:
        nrd = rn + 1
        btn1_href = "?br_action=next_round"
        btn1_label = "⚔️ 라운드 "+str(nrd)+"! 완전 정복!"
        btn1_style = "background:#0c0c00;border:2px solid #d4af37;color:#d4af37;font-weight:900;"
    else:
        btn1_href = "?br_action=retry"
        btn1_label = "🔥 설욕전! 다시 싸운다!"
        btn1_style = "background:#0a0008;border:2px solid #cc2244;color:#ff4466;font-weight:900;"

    components.html("""
    <style>
    *{margin:0;padding:0;box-sizing:border-box;}
    body{background:#06060e;font-family:'Rajdhani','Arial',sans-serif;padding:8px;color:#eeeeff;}
    .banner{background:"""+banner_bg+""";border:2px solid """+banner_bc+""";border-left:5px solid """+banner_bc+""";border-radius:10px;padding:8px 12px;margin-bottom:8px;}
    .banner-title{font-size:1rem;font-weight:900;color:"""+banner_tc+""";}
    .banner-sub{font-size:0.75rem;color:"""+banner_sc+""";margin-top:2px;}
    .nav-row{display:flex;align-items:center;justify-content:center;gap:10px;padding:6px 0 8px;}
    .nav-arr{font-size:1.2rem;text-decoration:none;padding:0 4px;}
    .card{background:#0c0c18;border:1.5px solid """+card_border+""";border-left:4px solid """+card_border+""";border-radius:12px;padding:10px 12px;margin:4px 0;}
    .card-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;}
    .qnum{background:#0a0a20;border:1px solid #222;border-radius:10px;padding:2px 10px;font-size:0.78rem;font-weight:700;color:"""+qnum_color+""";}
    .qcat{font-size:0.7rem;color:#444;}
    .qtext{font-size:1rem;font-weight:700;color:#eeeeff;line-height:1.7;margin-bottom:8px;}
    .qkr{font-size:0.8rem;color:#9aa5b4;margin-bottom:6px;}
    .hint{background:#081008;border-left:3px solid #50c878;border-radius:0 8px 8px 0;padding:6px 10px;margin-bottom:8px;}
    .hint-txt{font-size:0.8rem;color:#50c878;font-weight:700;}
    .save-row{display:flex;justify-content:flex-end;}
    .save-btn{padding:5px 12px;border-radius:8px;font-size:0.8rem;font-weight:700;cursor:pointer;text-decoration:none;"""+save_style+"""}
    .divider{height:1px;background:#1a1a2a;margin:10px 0;}
    .btn-row{display:flex;gap:8px;}
    .btn1{flex:2;padding:12px;border-radius:10px;font-size:0.95rem;text-align:center;text-decoration:none;display:block;"""+btn1_style+"""}
    .btn2{flex:1;padding:12px;border-radius:10px;font-size:0.95rem;text-align:center;text-decoration:none;display:block;background:transparent;border:1px solid rgba(255,255,255,0.3);color:rgba(255,255,255,0.5);}
    </style>
    <div class="banner">
        <div class="banner-title">"""+banner_title+"""</div>
        <div class="banner-sub">"""+banner_sub+"""</div>
    </div>
    <div class="nav-row">
        <a class="nav-arr" href=\""""+prev_href+"""\" style="color:rgba(255,255,255,"""+prev_op+""")">&#9664;</a>
        """+dots+"""
        <a class="nav-arr" href=\""""+next_href+"""\" style="color:rgba(255,255,255,"""+next_op+""")">&#9654;</a>
    </div>
    <div class="card">
        <div class="card-top">
            <span class="qnum">"""+qnum_sym+""" Q"""+str(bi+1)+"""/"""+str(num_qs)+"""</span>
            <span class="qcat">"""+cat+"""</span>
        </div>
        <div class="qtext">"""+sent_html+"""</div>
        <div class="qkr">📖 """+kr+"""</div>
        <div class="hint"><div class="hint-txt">💡 """+exk+"""</div></div>
        <div class="save-row">
            <a href="?br_action=save" class="save-btn">"""+save_label+"""</a>
        </div>
    </div>
    <div class="divider"></div>
    <div class="btn-row">
        <a href=\""""+btn1_href+"""\" class="btn1">"""+btn1_label+"""</a>
        <a href="?br_action=home" class="btn2">🏠 홈</a>
    </div>
    """, height=600, scrolling=True)

