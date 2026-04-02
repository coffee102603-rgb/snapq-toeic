"""
FILE: 02_Firepower.py  (구: 02_P5_Arena.py)
ROLE: 화력전 — 문법·어휘 5문제 서바이벌 전장
PHASES: LOBBY → BATTLE → BRIEFING → RESULT
DATA:   storage_data.json → rt_logs(논문D), adp_logs(논문A), word_prison(오답 자동 포획)
LINKS:  main_hub.py (작전사령부 귀환) | 03_POW_HQ.py (포로사령부)
PAPERS: 논문D(rt_logs 반응속도), 논문A(adp_logs 적응형 난이도)
EXTEND: P5 포로수용소 자동저장 재구현 예정 (안전한 옵션A 방식)
EXTEND: Adaptive 난이도 고도화 예정
"""
import streamlit as st
        _css = """<style data-fp>
        /* ── 전장 버튼 래퍼 여백 완전 제거 ── */
        .stMarkdown{margin:0!important;padding:0!important;}
        .element-container{margin:0!important;padding:0!important;}
        div[data-testid="stVerticalBlock"]{gap:3px!important;}
        /* ── 답 버튼 공통 ── */
        div[data-testid="stButton"] button{
            min-height:50px!important;font-size:0.95rem!important;
            font-weight:800!important;border-radius:10px!important;
            text-align:left!important;padding:0.45rem 0.9rem!important;
            margin:0!important;
        }
        div[data-testid="stButton"] button p{font-size:0.95rem!important;font-weight:800!important;}
        """
        if st.session_state.get("ans", False):
         pass
        for _aid, _col, _bg, _sh in _ans_cfg if st.session_state.get("ans", False) else []:
            _css += (
                f'.q-{_qi} #btn-{_aid} div[data-testid="stButton"] button{{' 
                f'border-left:5px solid {_col}!important;background:{_bg}!important;'
                f'border-color:{_col}!important;color:{_col}!important;'
                f'-webkit-appearance:none!important;-webkit-text-fill-color:{_col}!important;}}'
                f'#btn-{_aid}-{_qi} div[data-testid="stButton"] button p{{color:{_col}!important;}}'
                f'#btn-{_aid}-{_qi} div[data-testid="stButton"] button:hover{{box-shadow:0 0 22px {_sh}!important;}}'
            )
        _css += "</style>"
        _style_ph = st.empty()
        _style_ph.markdown(_css, unsafe_allow_html=True)

        _clicked = None
        for _ii, _ch in enumerate(q['ch']):
            _ch_clean = re.sub(r'^\([A-D]\)[:\s]*', '', _ch).strip()
            _display = f"【{_labels[_ii]}】  {_ch_clean}"
            _aid = _ans_cfg[_ii][0]
            st.markdown(f'<div class="q-{_qi}" id="btn-{_aid}">', unsafe_allow_html=True)
            if st.button(_display, key=f"ans_{_rn}_{_qi}_{_ii}_{int(time.time()*1000)%10000}", use_container_width=True):
                _clicked = _ii
            st.markdown('</div>', unsafe_allow_html=True)

        if _clicked is not None:
            if time.time()-st.session_state.qst > st.session_state.tsec:
                st.session_state.phase='lost'; st.rerun()
            i = _clicked
            st.session_state.ans=True; st.session_state.sel=i
            ok=i==q['a']
            st.session_state.round_results.append(ok)
            if ok: st.session_state.sc+=1
            else: st.session_state.wrong+=1
            st.session_state.ta+=1

            # ── 데이터 수집 (rt_logs + zpd_logs + p5_logs) ──
            try:
                _elapsed_now = time.time() - st.session_state.qst
                _tsec_now    = st.session_state.tsec
                _sec_rem     = round(max(0.0, _tsec_now - _elapsed_now), 2)
                _rt_proxy    = round(_tsec_now - _sec_rem, 2)
                _rem_ratio   = _sec_rem / _tsec_now if _tsec_now > 0 else 0
                if ok:
                    _err_type = "correct"
                elif _rem_ratio > 0.8:
                    _err_type = "fast_wrong"
                elif _rem_ratio < 0.2:
                    _err_type = "slow_wrong"
                else:
                    _err_type = "mid_wrong"
                _uid  = st.session_state.get("nickname", "guest")
                _cat  = q.get("cat", "")
                _qid  = q.get("id", "?")
                _today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
                if "p5_session_no" not in st.session_state:
                    st.session_state.p5_session_no = 0
                _sno = st.session_state.p5_session_no
                if "p5_start_date" not in st.session_state:
                    st.session_state.p5_start_date = _today
                try:
                    _dt = __import__("datetime")
                    _days = (_dt.datetime.strptime(_today, "%Y-%m-%d") -
                             _dt.datetime.strptime(st.session_state.p5_start_date, "%Y-%m-%d")).days
                    _week = _days // 7 + 1
                except:
                    _week = 1
                _st_data = load_storage()
                _rt_log = {
                    "user_id":          _uid,
                    "session_date":     _today,
                    "session_no":       _sno,
                    "timer_setting":    _tsec_now,
                    "question_no":      st.session_state.qi + 1,
                    "question_id":      _qid,
                    "seconds_remaining": _sec_rem,
                    "rt_proxy":         _rt_proxy,
                    "correct":          ok,
                    "grammar_type":     _cat,
                    "error_timing_type": _err_type,
                    "difficulty_level": st.session_state.get("adp_level", "normal"),
                    "week":             _week,
                    "timestamp":        __import__("datetime").datetime.now().isoformat(),
                }
                if "rt_logs" not in _st_data:
                    _st_data["rt_logs"] = []
                _st_data["rt_logs"].append(_rt_log)
                if not ok:
                    _st_data.setdefault("_zpd_pending", {})
                    _st_data["_zpd_pending"][_uid] = {
                        "session_date":   _today,
                        "session_no":     _sno,
                        "arena":          "P5",
                        "timer_setting":  _tsec_now,
                        "game_over_q_no": st.session_state.qi + 1,
                        "max_q_reached":  st.session_state.qi + 1,
                        "week":           _week,
                    }
                with open(STORAGE_FILE, "w", encoding="utf-8") as _f:
                    json.dump(_st_data, _f, ensure_ascii=False, indent=2)
            except Exception as _e:
                pass

            try:
                import sys as _sys, os as _os
                _sys.path.insert(0, _os.path.dirname(_os.path.dirname(__file__)))
                from data_collector import DataCollector as _DC
                _DC(st.session_state.get('nickname','guest')).log_activity('P5', q.get('id','?'), i, ok, round(time.time()-st.session_state.qst,2))
            except: pass

            if st.session_state.wrong>=2:
                st.session_state.phase='lost'; st.rerun()
            if st.session_state.qi>=4:
                st.session_state.phase='victory' if st.session_state.sc>=4 else 'lost'
                st.rerun()
            nqi = st.session_state.qi + 1
            if nqi < len(st.session_state.round_qs):
                st.session_state.qi = nqi
                st.session_state.cq = st.session_state.round_qs[nqi]
                st.session_state.ans=False; st.session_state.sel=None
            else:
                st.session_state.phase='victory' if st.session_state.sc>=4 else 'lost'
            st.rerun()

    else:
        # ── 정답/오답 피드백 (답 선택 후) ──
        _sel = st.session_state.sel
        _correct_idx = q['a']
        _ok = (_sel == _correct_idx)
        if _ok:
            components.html("""
            <style>
            *{margin:0;padding:0;box-sizing:border-box;}
            body{background:transparent;display:flex;align-items:center;justify-content:center;height:60px;}
            @keyframes popIn{0%{transform:scale(0.5);opacity:0;}60%{transform:scale(1.15);}100%{transform:scale(1);opacity:1;}}
            .hit{font-family:'Arial Black',sans-serif;font-size:1.6rem;font-weight:900;color:#44FF88;
              text-shadow:0 0 20px #44FF88,0 0 50px #22cc66;letter-spacing:4px;
              animation:popIn 0.4s cubic-bezier(0.34,1.56,0.64,1) forwards;}
            </style>
            <div class="hit">💥 격파!</div>""", height=60)
        else:
            _ans_text = q['ch'][_correct_idx]
            components.html(f"""
            <style>
            *{{margin:0;padding:0;box-sizing:border-box;}}
            body{{background:transparent;display:flex;align-items:center;justify-content:center;height:60px;}}
            @keyframes shk{{0%{{transform:translate(0,0)}}20%{{transform:translate(-5px,0)}}40%{{transform:translate(5px,0)}}60%{{transform:translate(-4px,0)}}80%{{transform:translate(4px,0)}}100%{{transform:translate(0,0)}}}}
            .miss{{font-family:'Arial Black',sans-serif;font-size:1.4rem;font-weight:900;color:#FF2D55;
              text-shadow:0 0 20px #FF2D55,0 0 50px #cc0033;letter-spacing:3px;
              animation:shk 0.4s ease-in-out;}}
            </style>
            <div class="miss">💀 피격! &nbsp;<span style="font-size:1rem;color:#aaa;">정답: {_ans_text}</span></div>""", height=60)

        st.markdown(f'<div style="background:#0a0c14;border-left:4px solid {"#44FF88" if _ok else "#FF2D55"};border-radius:0 10px 10px 0;padding:8px 12px;margin:4px 0;">'
                    f'<span style="font-size:0.85rem;color:{"#44FF88" if _ok else "#FF2D55"};font-weight:700;">💡 {q.get("exk","")}</span></div>', unsafe_allow_html=True)

        if st.button("▶ 다음 문제", key="next_q", use_container_width=True):
            if st.session_state.wrong>=2:
                st.session_state.phase='lost'; st.rerun()
            if st.session_state.qi>=4:
                st.session_state.phase='victory' if st.session_state.sc>=4 else 'lost'; st.rerun()
            nqi = st.session_state.qi + 1
            if nqi < len(st.session_state.round_qs):
                st.session_state.qi = nqi
                st.session_state.cq = st.session_state.round_qs[nqi]
                st.session_state.ans=False; st.session_state.sel=None
            else:
                st.session_state.phase='victory' if st.session_state.sc>=4 else 'lost'
            st.rerun()

# ════════════════════════════════════════
# PHASE: VICTORY
# ════════════════════════════════════════
elif st.session_state.phase=="victory":
    # ── adaptive difficulty 기록 ──
    try:
        _sc_adp = st.session_state.get("sc", 0)
        _rate_adp = _sc_adp / 5.0
        _hist = st.session_state.get("adp_history", [])
        _hist.append(_rate_adp)
        st.session_state.adp_history = _hist
        st.session_state.adp_level = _calc_adp_level()
    except: pass
    # ── zpd_logs + p5_logs ──
    try:
        st.session_state.p5_session_no = st.session_state.get("p5_session_no", 0) + 1
        _st2 = load_storage()
        _uid2 = st.session_state.get("nickname", "guest")
        _today2 = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        _sno2 = st.session_state.p5_session_no
        if "p5_start_date" not in st.session_state:
            st.session_state.p5_start_date = _today2
        try:
            _dt2 = __import__("datetime")
            _days2 = (_dt2.datetime.strptime(_today2, "%Y-%m-%d") -
                      _dt2.datetime.strptime(st.session_state.p5_start_date, "%Y-%m-%d")).days
            _week2 = _days2 // 7 + 1
        except:
            _week2 = 1
        _zpd_entry = {
            "user_id":        _uid2,"session_date":   _today2,"session_no":     _sno2,
            "arena":          "P5","timer_setting":  st.session_state.tsec,
            "game_over_q_no": None,"result":         "VICTORY","max_q_reached":  5,
            "week":           _week2,"timestamp":      __import__("datetime").datetime.now().isoformat(),
        }
        if "zpd_logs" not in _st2: _st2["zpd_logs"] = []
        _st2["zpd_logs"].append(_zpd_entry)
        _p5_entry = {
            "user_id":       _uid2,"session_date":  _today2,"session_no":    _sno2,
            "timer_selected": st.session_state.tsec,"mode":          st.session_state.mode,
            "result":        "VICTORY","correct_count": st.session_state.sc,
            "wrong_count":   st.session_state.wrong,"week":          _week2,
            "timestamp":     __import__("datetime").datetime.now().isoformat(),
        }
        if "p5_logs" not in _st2: _st2["p5_logs"] = []
        if not any(p.get("session_no") == _sno2 and p.get("user_id") == _uid2 and p.get("result") == "VICTORY"
                   for p in _st2["p5_logs"]):
            _st2["p5_logs"].append(_p5_entry)
        with open(STORAGE_FILE, "w", encoding="utf-8") as _f2:
            json.dump(_st2, _f2, ensure_ascii=False, indent=2)
    except: pass

    _sc_v = st.session_state.sc
    _wr_v = st.session_state.wrong
    _rn_v = st.session_state.round_num

    _PERFECT_list = [
        ("👑 PERFECT!", "천재 등장!! 토익 990은 그냥 따놓은 당상이잖아 👑", "#FFD600"),
        ("👑 PERFECT!", "5/5?? 실화냐?? 나도 이제 너한테 배워야겠다 🙇", "#FFD600"),
        ("👑 PERFECT!", "오답이 없어... 이거 혹시 커닝한 거 아니지?? 😏", "#FFD600"),
        ("👑 PERFECT!", "인간 문법 사전 등장!! 토익은 그냥 산책이겠네 🚶", "#FFD600"),
        ("👑 PERFECT!", "이 실력이면 교재 써도 되겠는데?? 진심으로 🏆", "#FFD600"),
        ("👑 PERFECT!", "와... 진짜야? 완벽해!! 토익 만점도 그냥 따놓은 거지? 🔥", "#FFD600"),
        ("👑 PERFECT!", "5개 전부 격파!! 넌 공부하러 온 게 아니라 자랑하러 온 거지?? 💥", "#FFD600"),
        ("👑 PERFECT!", "문법 강사 해도 되는 거 아니야?? 이 정도면 진심 🎓", "#FFD600"),
        ("👑 PERFECT!", "만점이잖아!! 토익 시험장 가면 이름만 써도 되겠는데? 😂", "#FFD600"),
        ("👑 PERFECT!", "완벽 그 자체!! 오늘 이 실력 그대로 시험장 가면 990점 🎯", "#FFD600"),
    ]
    _VICTORY_list = [
        ("⚔️ VICTORY!", "강해!! 이 기세면 토익 900+ 그냥 간다! 💪", "#ff8833"),
        ("⚔️ VICTORY!", "4/5!! 딱 하나 방심한 거지? 다음엔 PERFECT 각이야 🔥", "#ff8833"),
        ("⚔️ VICTORY!", "아깝다 하나!! 그 하나만 잡으면 토익 고득점 확정이야 🎯", "#ff8833"),
        ("⚔️ VICTORY!", "90점짜리 실력!! 조금만 더 갈면 진짜 된다 💥", "#ff8833"),
        ("⚔️ VICTORY!", "거의 다 왔어!! 완벽까지 딱 한 걸음이야 😤", "#ff8833"),
    ]
    _CLEAR_list = [
        ("✅ CLEAR!", "아슬아슬 살아남았어... 겨우겨우지만 그래도 살았잖아 😅", "#ff9944"),
        ("✅ CLEAR!", "3개... 딱 생존선이네. 운이 좋았어 🍀", "#ff9944"),
        ("✅ CLEAR!", "살긴 살았는데, 이게 실력이야? 솔직히 말해봐 😐", "#ff9944"),
        ("✅ CLEAR!", "통과는 했는데... 토익은 이렇게 안 되거든? 알지? 😬", "#ff9944"),
        ("✅ CLEAR!", "3/5... 기초는 됐어. 근데 딱 기초만이야 😑", "#ff9944"),
    ]
    if _sc_v == 5:
        _grade, _praise, _pcol = random.choice(_PERFECT_list)
    elif _sc_v == 4:
        _grade, _praise, _pcol = random.choice(_VICTORY_list)
    else:
        _grade, _praise, _pcol = random.choice(_CLEAR_list)

    _stars_html = "".join([
        f'<div style="position:absolute;left:{random.randint(2,98)}%;top:{random.randint(2,98)}%;'
        f'width:{random.randint(3,12)}px;height:{random.randint(3,12)}px;'
        f'border-radius:50%;background:{"#FFD600" if random.random()>0.4 else "#fff8cc"};'
        f'animation:twinkle {0.3+random.random()*0.8:.1f}s ease-in-out infinite {random.random():.2f}s both;"></div>'
        for _ in range(90)])
    _coins_html = "".join([
        f'<div style="position:absolute;top:-10px;left:{random.randint(2,98)}%;font-size:{1.0+random.random()*0.8:.1f}rem;'
        f'animation:coinFall {0.8+random.random()*1.2:.1f}s ease-in infinite {random.random():.2f}s;">{"💰" if random.random()>0.5 else "⭐" if random.random()>0.5 else "🏆"}</div>'
        for _ in range(22)])
    _lightning_html = "".join([
        f'<div style="position:absolute;left:{random.randint(2,95)}%;top:{random.randint(2,90)}%;'
        f'font-size:{random.randint(18,45)}px;opacity:0.18;'
        f'animation:twinkle {0.2+random.random()*0.4:.1f}s ease-in-out infinite {random.random():.2f}s;">{"⚡" if random.random()>0.5 else "✨"}</div>'
        for _ in range(14)])

    components.html(f"""
    <style>
    *{{margin:0;padding:0;box-sizing:border-box;}}
    body{{background:linear-gradient(180deg,#060400 0%,#1a1000 50%,#060400 100%);
      overflow:hidden;height:100vh;font-family:'Arial Black',sans-serif;
      display:flex;align-items:center;justify-content:center;}}
    @keyframes vi{{0%{{transform:scale(0) rotate(-20deg);opacity:0;}}65%{{transform:scale(1.12) rotate(3deg);}}100%{{transform:scale(1) rotate(0deg);opacity:1;}}}}
    @keyframes goldGlow{{0%,100%{{text-shadow:0 0 20px #FFD600,0 0 60px #ff8800,0 0 120px #ff4400;}}50%{{text-shadow:0 0 60px #FFD600,0 0 120px #ff8800,0 0 200px #ff4400;}}}}
    @keyframes twinkle{{0%,100%{{opacity:1;transform:scale(1) rotate(0deg);}}50%{{opacity:0.1;transform:scale(0.2) rotate(180deg);}}}}
    @keyframes coinFall{{0%{{transform:translateY(-20px) rotate(0deg) scale(1);opacity:1;}}100%{{transform:translateY(160px) rotate(540deg) scale(0.4);opacity:0;}}}}
    @keyframes scoreIn{{0%{{transform:translateY(40px);opacity:0;}}100%{{transform:translateY(0);opacity:1;}}}}
    @keyframes barFill{{0%{{width:0%;}}100%{{width:{int(_sc_v/5*100)}%;}}}}
    @keyframes pulse{{0%,100%{{transform:scale(1);}}50%{{transform:scale(1.05);}}}}
    @keyframes borderPulse{{0%,100%{{box-shadow:0 0 20px rgba(255,214,0,0.4),inset 0 0 20px rgba(255,214,0,0.05);}}50%{{box-shadow:0 0 50px rgba(255,214,0,0.8),inset 0 0 40px rgba(255,214,0,0.1);}}}}
    .wrap{{text-align:center;animation:vi 0.8s cubic-bezier(0.34,1.56,0.64,1) forwards;position:relative;z-index:10;width:90%;}}
    .round-tag{{font-size:0.72rem;color:#886600;font-weight:700;letter-spacing:4px;margin-bottom:8px;}}
    .grade{{font-size:3rem;font-weight:900;color:#FFD600;
      animation:goldGlow 1.5s ease-in-out infinite, pulse 1.5s ease-in-out infinite;
      letter-spacing:3px;line-height:1.1;}}
    .scorebox{{background:rgba(255,214,0,0.08);border:2px solid rgba(255,214,0,0.5);
      border-radius:16px;padding:14px 28px;margin:12px auto;display:inline-block;
      animation:scoreIn 0.6s ease 0.3s both, borderPulse 2s ease-in-out infinite;}}
    .sc-num{{font-size:3.5rem;font-weight:900;color:#FFD600;line-height:1;
      text-shadow:0 0 30px rgba(255,214,0,0.8);}}
    .sc-label{{font-size:0.78rem;color:#aa8800;font-weight:700;letter-spacing:2px;margin-top:4px;}}
    .bar-wrap{{background:#1a1100;border-radius:20px;height:12px;margin:12px auto;width:85%;
      overflow:hidden;border:1px solid #443300;}}
    .bar-fill{{height:100%;border-radius:20px;
      background:linear-gradient(90deg,#886600,#FFD600,#fff8aa);
      box-shadow:0 0 12px #FFD600;animation:barFill 1.2s ease 0.6s both;}}
    .praise{{font-size:1.0rem;color:{_pcol};font-weight:900;margin:10px 0 4px;
      animation:scoreIn 0.5s ease 0.8s both;letter-spacing:1px;}}
    </style>
    <div style="position:absolute;width:100%;height:100%;overflow:hidden;top:0;left:0;">
      {_stars_html}{_coins_html}{_lightning_html}
    </div>
    <div class="wrap">
        <div class="round-tag">💥 WAVE {_rn_v} COMPLETE 💥</div>
        <div class="grade">{_grade}</div>
        <div class="scorebox">
            <div class="sc-num">{_sc_v}<span style="font-size:1.6rem;color:#886600;"> / 5</span></div>
            <div class="sc-label">✅ {_sc_v}격파 &nbsp;·&nbsp; ❌ {_wr_v}개 놓침</div>
        </div>
        <div class="bar-wrap"><div class="bar-fill"></div></div>
        <div class="praise">{_praise}</div>
    </div>
    """, height=320)

    st.markdown("""<style>
    @keyframes zapPulse{
      0%,100%{box-shadow:0 0 18px #00d4ff,0 0 40px rgba(0,212,255,0.5),inset 0 0 18px rgba(0,212,255,0.1);}
      50%{box-shadow:0 0 35px #00d4ff,0 0 80px rgba(0,212,255,0.8),inset 0 0 35px rgba(0,212,255,0.2);}
    }
    /* ① 즉시 재출격 — 전기 파란 불꽃, 최상위 강조 */
    div[data-testid="stButton"]:nth-of-type(1) button{
      background:linear-gradient(135deg,#001a2e,#00121f)!important;
      border:2px solid #00d4ff!important;
      border-left:5px solid #00d4ff!important;
      border-radius:14px!important;
      animation:zapPulse 1.6s ease-in-out infinite!important;
      min-height:62px!important;
    }
    div[data-testid="stButton"]:nth-of-type(1) button p{
      color:#00d4ff!important;font-size:1.25rem!important;font-weight:900!important;
      text-shadow:0 0 12px rgba(0,212,255,0.9)!important;letter-spacing:1px!important;
    }
    div[data-testid="stButton"]:nth-of-type(1) button:hover{
      background:linear-gradient(135deg,#002a40,#001a2e)!important;
      box-shadow:0 0 45px rgba(0,212,255,0.9)!important;
    }
    /* ② 브리핑 보기 — 골드 */
    div[data-testid="stButton"]:nth-of-type(2) button{
      background:#0c0c00!important;border:2px solid #FFD600!important;
      border-left:5px solid #FFD600!important;border-radius:12px!important;
    }
    div[data-testid="stButton"]:nth-of-type(2) button p{color:#FFD600!important;font-size:1.05rem!important;font-weight:900!important;}
    div[data-testid="stButton"]:nth-of-type(2) button:hover{box-shadow:0 0 22px rgba(255,214,0,0.6)!important;}
    /* ③ 홈 — 회색 */
    div[data-testid="stButton"]:nth-of-type(3) button{
      background:#0a0a0a!important;border:1.5px solid rgba(255,255,255,0.2)!important;
    }
    div[data-testid="stButton"]:nth-of-type(3) button p{color:#666!important;font-size:0.95rem!important;}
    </style>""", unsafe_allow_html=True)

    # ── ① 즉시 재출격 (전체 폭, 최우선) ──
    if st.button("⚡ 즉시 재출격!", use_container_width=True, key="btn_relaunch"):
        _keep_mode = st.session_state.get("mode")
        _keep_grp  = st.session_state.get("battle_grp")
        _keep_adp  = st.session_state.get("adp_level", "normal")
        _keep_hist = st.session_state.get("adp_history", [])
        _reset_keys = ["cq","qi","sc","wrong","ta","ans","sel",
                       "round_qs","round_results","round_num","used",
                       "started","qst","sk","msk","tsec"]
        for k in _reset_keys:
            if k in D: st.session_state[k] = D[k]
        st.session_state.mode         = _keep_mode
        st.session_state.battle_grp   = _keep_grp
        st.session_state.adp_level    = _keep_adp
        st.session_state.adp_history  = _keep_hist
        st.session_state.phase = "lobby"
        st.rerun()

    # ── ②③ 브리핑 보기 / 홈 ──
    vc=st.columns(2)
    with vc[0]:
        if st.button("📋 브리핑 보기", use_container_width=True):
            st.session_state.phase="briefing"; st.rerun()
    with vc[1]:
        if st.button("🏠 홈", use_container_width=True):
            st.session_state._p5_just_left = True
            st.session_state.ans = False
            st.session_state["_battle_entry_ans_reset"] = True
            _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
            if _nick:
                st.query_params["nick"] = _nick
                st.query_params["ag"] = "1"
            st.switch_page("main_hub.py")

# ════════════════════════════════════════
# PHASE: YOU LOST
# ════════════════════════════════════════
elif st.session_state.phase=="lost":
    try:
        _sc_adp = st.session_state.get("sc", 0)
        _rate_adp = _sc_adp / 5.0
        _hist = st.session_state.get("adp_history", [])
        _hist.append(_rate_adp)
        st.session_state.adp_history = _hist
        st.session_state.adp_level = _calc_adp_level()
    except: pass
    try:
        st.session_state.p5_session_no = st.session_state.get("p5_session_no", 0) + 1
        _st3 = load_storage()
        _uid3 = st.session_state.get("nickname", "guest")
        _today3 = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        _sno3 = st.session_state.p5_session_no
        if "p5_start_date" not in st.session_state:
            st.session_state.p5_start_date = _today3
        try:
            _dt3 = __import__("datetime")
            _days3 = (_dt3.datetime.strptime(_today3, "%Y-%m-%d") -
                      _dt3.datetime.strptime(st.session_state.p5_start_date, "%Y-%m-%d")).days
            _week3 = _days3 // 7 + 1
        except:
            _week3 = 1
        _pending = _st3.get("_zpd_pending", {}).get(_uid3, {})
        _go_q = _pending.get("game_over_q_no", st.session_state.qi + 1)
        _zpd3 = {
            "user_id":        _uid3,"session_date":   _today3,"session_no":     _sno3,
            "arena":          "P5","timer_setting":  st.session_state.tsec,
            "game_over_q_no": _go_q,"result":         "GAME_OVER",
            "max_q_reached":  st.session_state.qi + 1,"week":           _week3,
            "timestamp":      __import__("datetime").datetime.now().isoformat(),
        }
        if "zpd_logs" not in _st3: _st3["zpd_logs"] = []
        if not any(z.get("session_no") == _sno3 and z.get("user_id") == _uid3
                   for z in _st3["zpd_logs"]):
            _st3["zpd_logs"].append(_zpd3)
        _p5e3 = {
            "user_id":        _uid3,"session_date":   _today3,"session_no":     _sno3,
            "timer_selected": st.session_state.tsec,"mode":           st.session_state.mode,
            "result":         "GAME_OVER","correct_count":  st.session_state.sc,
            "wrong_count":    st.session_state.wrong,"week":           _week3,
            "timestamp":      __import__("datetime").datetime.now().isoformat(),
        }
        if "p5_logs" not in _st3: _st3["p5_logs"] = []
        if not any(p.get("session_no") == _sno3 and p.get("user_id") == _uid3 and p.get("result") == "GAME_OVER"
                   for p in _st3["p5_logs"]):
            _st3["p5_logs"].append(_p5e3)
        with open(STORAGE_FILE, "w", encoding="utf-8") as _f3:
            json.dump(_st3, _f3, ensure_ascii=False, indent=2)
    except: pass

    _sc = st.session_state.sc
    _wrong = st.session_state.wrong
    _pct = int(_sc / 5 * 100)
    _is_timeout = (time.time()-st.session_state.qst > st.session_state.tsec)
    _reason = "시간초과 ⏰" if _is_timeout else f"오답 {_wrong}개 💀"

    _ZERO_list = [
        ("0개?? 이건 운도 안 따라줬네... 그냥 전멸이잖아 💀", "문법책 한 번이라도 펴봐. 딱 한 번만"),
        ("0점이야. 전멸. 진짜 전멸. 할 말이 없다 😶", "수일치도 모르면서 토익 점수 바라지 마"),
        ("하나도 못 맞혔어?? 찍어도 하나는 맞아야 하는데 😂", "랜덤으로 찍는 원숭이도 1개는 맞힌다고"),
        ("이건 실력 문제가 아니라 공부를 안 한 거야 📚", "교재 한 번이라도 펴봤어? 솔직히 말해봐"),
        ("0개 격파... 격파당한 건 본인이잖아 💥", "이 정도면 진짜 기초부터 다시 시작해야 해"),
    ]
    _TIMEOUT_list = [
        ("느려도 너무 느려!! 토익은 스피드도 실력이야 🐢", "시간 관리가 안 되면 토익 절대 못 올려"),
        ("시간이 부족했다고? 그게 실력이야 ⏰", "토익은 느린 사람 기다려주지 않아"),
        ("30초도 모자라?? 50초로 해봐... 그래도 빠듯할 것 같지만 😂", "생각이 느린 게 아니라 감각이 없는 거야"),
        ("시간초과!! 토익 시험장에서도 이럴 거야?? 😱", "실전에선 시간이 2배 빠르게 느껴진다"),
        ("타이머 보이지?? 그게 적이야. 지금 적한테 진 거야 ⏰", "속도 없이 정확도만? 토익엔 통하지 않아"),
    ]
    _LOW_list = [
        (f"찍어서 {_sc}개 맞춘 거 다 알아 😂", "운도 실력이라고? 그건 토익엔 없어"),
        (f"겨우 {_sc}개... 어법이 이 정도면 문장도 못 읽겠다 😤", "접속사? 수일치? 기초부터 다시 해"),
        (f"{_sc}개?? 이러고 토익 점수 올리길 바라는 거야?? 🙃", "기대치를 낮추거나 공부량을 늘려"),
        (f"진짜야? {_sc}개?? 오늘 컨디션 문제인 거 맞지?? 😬", "컨디션 탓은 딱 한 번만 허용해줄게"),
        (f"문법 감각이 없는 게 아니라 없애버린 것 같아 💀", f"{_sc}개로는 토익 600점도 힘들어"),
    ]
    _CLOSE_list = [
        ("딱 한 문제 차이야. 억울하지?? 😭", "그 한 문제가 토익 점수 50점 차이야"),
        ("2개 모자라서 전멸이라니... 진짜 아깝다 😤", "아깝다고 점수 올라가진 않아. 다시 해"),
        ("이 정도 실력이면 왜 졌어?? 집중력 문제야 😡", "실력 있는데 지면 더 억울한 거 알지?"),
        ("아깝다!! 근데 토익은 아까운 거 안 봐줘 😂", "다음엔 이 분한 마음 그대로 시험장 가"),
        ("거의 다 됐는데 왜 무너진 거야!! 😱", "2개 차이면 실력은 있어. 멘탈이 문제야"),
    ]
    if _pct == 0:
        _taunt, _sub = random.choice(_ZERO_list)
    elif _is_timeout:
        _taunt, _sub = random.choice(_TIMEOUT_list)
    elif _pct <= 40:
        _taunt, _sub = random.choice(_LOW_list)
    else:
        _taunt, _sub = random.choice(_CLOSE_list)

    _embers = "".join([
        f'<div style="position:absolute;left:{random.randint(2,98)}%;bottom:{random.randint(0,40)}%;'
        f'width:{random.randint(3,14)}px;height:{random.randint(3,14)}px;border-radius:50%;'
        f'background:{"#ff4400" if random.random()>0.4 else "#ff8800" if random.random()>0.5 else "#ff0000"};'
        f'animation:rise {0.6+random.random():.1f}s ease-in infinite {random.random():.1f}s;"></div>'
        for _ in range(80)])
    _skulls = "".join([
        f'<div style="position:absolute;left:{random.randint(2,95)}%;top:{random.randint(2,85)}%;'
        f'font-size:{random.randint(10,32)}px;opacity:{random.random()*0.2:.2f};'
        f'animation:fadeFloat {0.8+random.random()*1.2:.1f}s ease-in-out infinite {random.random():.1f}s;">{"💀" if random.random()>0.3 else "☠️"}</div>'
        for _ in range(18)])

    components.html(f"""
    <style>
    *{{margin:0;padding:0;box-sizing:border-box;}}
    body{{background:#0a0000;overflow:hidden;display:flex;align-items:center;justify-content:center;
      height:100vh;font-family:'Arial Black',sans-serif;}}
    @keyframes redPulse{{0%,100%{{background:#0a0000;}}50%{{background:#180000;}}}}
    @keyframes crashIn{{0%{{transform:scale(4) rotate(-8deg);opacity:0;}}60%{{transform:scale(0.92) rotate(2deg);}}100%{{transform:scale(1) rotate(0deg);opacity:1;}}}}
    @keyframes shakeX{{0%,100%{{transform:translateX(0);}}20%{{transform:translateX(-10px);}}40%{{transform:translateX(10px);}}60%{{transform:translateX(-7px);}}80%{{transform:translateX(7px);}}}}
    @keyframes rise{{0%{{opacity:1;transform:translateY(0) scale(1);}}100%{{opacity:0;transform:translateY(-350px) scale(0.3);}}}}
    @keyframes flicker{{0%,100%{{opacity:1;}}30%{{opacity:0.6;}}60%{{opacity:0.9;}}}}
    @keyframes fadeFloat{{0%,100%{{opacity:0;transform:translateY(0);}}50%{{opacity:0.15;transform:translateY(-20px);}}}}
    @keyframes scoreIn{{0%{{transform:translateY(30px);opacity:0;}}100%{{transform:translateY(0);opacity:1;}}}}
    body{{animation:redPulse 0.35s ease-in-out infinite;}}
    .wrap{{text-align:center;animation:crashIn 0.6s cubic-bezier(0.34,1.56,0.64,1) forwards;
      z-index:10;position:relative;padding:10px;}}
    .skull{{font-size:2.8rem;animation:shakeX 0.5s ease-in-out infinite;display:inline-block;margin-bottom:6px;}}
    .lost-txt{{font-size:2.2rem;font-weight:900;color:#ff0000;
      text-shadow:0 0 20px #ff0000,0 0 60px #cc0000;
      animation:flicker 0.25s infinite;letter-spacing:4px;}}
    .reason{{font-size:0.9rem;color:#ff6644;font-weight:700;margin:5px 0;letter-spacing:2px;
      background:rgba(255,100,0,0.1);border:1px solid rgba(255,100,0,0.3);
      border-radius:20px;display:inline-block;padding:3px 16px;}}
    .score{{font-size:2.8rem;font-weight:900;color:#ffcc00;
      text-shadow:0 0 30px #ffaa00,0 0 60px #ff8800;margin:8px 0;
      animation:scoreIn 0.5s ease 0.3s both;}}
    .taunt{{font-size:1.05rem;color:#ff8888;font-weight:900;margin:8px 0;
      animation:shakeX 4s ease-in-out infinite;}}
    .sub{{font-size:0.82rem;color:#ff6666;margin-top:4px;font-weight:700;opacity:0.9;}}
    </style>
    <div style="position:absolute;width:100%;height:100%;overflow:hidden;top:0;left:0;">
      {_embers}{_skulls}
    </div>
    <div class="wrap">
        <div class="skull">💀</div>
        <div class="lost-txt">GAME OVER</div>
        <div class="reason">[ {_reason} ]</div>
        <div class="score">{_pct}점</div>
        <div class="taunt">{_taunt}</div>
        <div class="sub">{_sub}</div>
    </div>""", height=300)

    st.markdown("""<style>
    div[data-testid="stButton"]:nth-of-type(1) button{
      background:#0a0000!important;border:2px solid #FF2D55!important;
      border-left:5px solid #FF2D55!important;border-radius:12px!important;
    }
    div[data-testid="stButton"]:nth-of-type(1) button p{color:#FF2D55!important;font-size:1.1rem!important;font-weight:900!important;}
    div[data-testid="stButton"]:nth-of-type(1) button:hover{box-shadow:0 0 25px rgba(255,45,85,0.6)!important;}
    div[data-testid="stButton"]:nth-of-type(2) button{
      background:#0a0a0a!important;border:1.5px solid rgba(255,255,255,0.15)!important;
    }
    div[data-testid="stButton"]:nth-of-type(2) button p{color:#666!important;font-size:0.95rem!important;}
    </style>""", unsafe_allow_html=True)
    bc=st.columns(2)
    with bc[0]:
        if st.button("🔥 설욕전! 다시 싸운다!", use_container_width=True):
            for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","round_num"]:
                if k in D: st.session_state[k]=D[k]
            st.session_state.phase="lobby"; st.rerun()
    with bc[1]:
        if st.button("🏠 홈", use_container_width=True):
            st.session_state._p5_just_left = True
            st.session_state.ans = False
            st.session_state["_battle_entry_ans_reset"] = True
            _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
            if _nick:
                st.query_params["nick"] = _nick
                st.query_params["ag"] = "1"
            st.switch_page("main_hub.py")

# ════════════════════════════════════════
# PHASE: BRIEFING
# ════════════════════════════════════════
elif st.session_state.phase=="briefing":
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
    section[data-testid="stSidebar"]{display:none!important;}
    header[data-testid="stHeader"]{height:0!important;visibility:hidden!important;}
    .block-container{padding-top:0.3rem!important;padding-bottom:1rem!important;margin-top:0!important;}
    .stMarkdown{margin:0!important;padding:0!important;}
    div[data-testid="stVerticalBlock"]{gap:5px!important;}
    .element-container{margin:0!important;padding:0!important;}
    div[data-testid="stHorizontalBlock"]{margin:0!important;padding:0!important;flex-wrap:nowrap!important;gap:5px!important;}
    div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]{min-width:0!important;flex:1!important;padding:0!important;}
    div[data-testid="stButton"] button{width:100%!important;min-height:44px!important;
        font-size:0.88rem!important;padding:6px 4px!important;border-radius:10px!important;}

    /* ── 도트 pill 스타일 ── */
    .br-dots div[data-testid="stButton"] button{
        font-size:0.68rem!important;min-height:28px!important;max-height:28px!important;
        padding:2px!important;border-radius:5px!important;font-weight:900!important;}
    .br-dots div[data-testid="stButton"] button p{font-size:0.68rem!important;font-weight:900!important;}

    /* ── 저장 버튼 ── */
    .br-save-btn div[data-testid="stButton"] button{
        background:#0c1800!important;border:2.5px solid #44ee66!important;
        border-radius:12px!important;color:#44ee66!important;
        font-size:1.0rem!important;font-weight:900!important;min-height:52px!important;
        letter-spacing:1px!important;}
    .br-save-btn div[data-testid="stButton"] button p{color:#44ee66!important;font-size:1.0rem!important;font-weight:900!important;}
    .br-saved-btn div[data-testid="stButton"] button{
        background:#050f05!important;border:1.5px solid #226633!important;
        border-radius:12px!important;color:#336644!important;
        font-size:0.88rem!important;min-height:44px!important;}
    .br-saved-btn div[data-testid="stButton"] button p{color:#336644!important;}

    /* ── POW HQ CTA 버튼 ── */
    .br-pow-btn div[data-testid="stButton"] button{
        background:#0e0020!important;border:2px solid #8833ff!important;
        border-radius:12px!important;color:#ff6644!important;
        font-size:0.92rem!important;font-weight:900!important;min-height:48px!important;
        letter-spacing:0.5px!important;}
    .br-pow-btn div[data-testid="stButton"] button p{color:#aa66ff!important;font-size:0.92rem!important;font-weight:900!important;}

    /* ── 재전투 버튼 ── */
    .br-retry-btn div[data-testid="stButton"] button{
        background:#1a0600!important;border:2px solid #ff6600!important;
        border-radius:12px!important;color:#ff9944!important;
        font-size:0.92rem!important;font-weight:900!important;min-height:48px!important;}
    .br-retry-btn div[data-testid="stButton"] button p{color:#ff9944!important;font-size:0.92rem!important;font-weight:900!important;}

    /* ── 홈 버튼 ── */
    .br-home-btn div[data-testid="stButton"] button{
        background:#05050e!important;border:1px solid #151525!important;
        border-radius:10px!important;color:#3d5066!important;min-height:40px!important;font-size:0.82rem!important;}
    .br-home-btn div[data-testid="stButton"] button p{color:#3d5066!important;}
    </style>""", unsafe_allow_html=True)

    was_victory = st.session_state.sc >= 3
    if "br_idx" not in st.session_state: st.session_state.br_idx = 0

    # ── 새 게임이면 br_saved 초기화 ──
    rqs_temp = st.session_state.get("round_qs", [])
    _br_game_uid = rqs_temp[0].get("id","") if rqs_temp else ""
    if st.session_state.get("_br_game_uid") != _br_game_uid:
        st.session_state.br_saved = set()
        st.session_state.br_idx   = 0
        st.session_state["_br_game_uid"] = _br_game_uid
    elif "br_saved" not in st.session_state:
        st.session_state.br_saved = set()

    bi     = st.session_state.br_idx
    rqs    = st.session_state.round_qs
    rrs    = st.session_state.round_results
    saved  = st.session_state.br_saved
    num_qs = min(len(rqs), len(rrs))
    if bi >= num_qs: bi = num_qs - 1
    if bi < 0: bi = 0
    rn    = st.session_state.round_num
    sc_v  = st.session_state.sc
    wr_v  = st.session_state.wrong

    # ── 상단 배너 (영문) ──
    if was_victory:
        st.markdown(f'''<div style="background:#150800;border:2px solid #ff6600;border-left:5px solid #ff6600;
            border-radius:10px;padding:10px 12px;margin-bottom:2px;">
            <div style="font-family:Orbitron,monospace;font-size:0.85rem;font-weight:900;
              color:#ff8833;letter-spacing:2px;">💥 WAVE {rn} · FIREPOWER COMPLETE</div>
            <div style="font-size:0.75rem;color:#cc6622;font-weight:700;margin-top:3px;letter-spacing:1px;">
              ✅ {sc_v} ELIMINATED &nbsp;·&nbsp; ❌ {wr_v} MISSED</div>
        </div>''', unsafe_allow_html=True)
    else:
        st.markdown(f'''<div style="background:#0c0008;border:2px solid #FF2D55;border-left:5px solid #FF2D55;
            border-radius:10px;padding:10px 12px;margin-bottom:2px;">
            <div style="font-family:Orbitron,monospace;font-size:0.85rem;font-weight:900;
              color:#FF2D55;letter-spacing:2px;">💀 WAVE {rn} · MISSION FAILED</div>
            <div style="font-size:0.75rem;color:#ee4455;font-weight:700;margin-top:3px;letter-spacing:1px;">
              ✅ {sc_v} ELIMINATED &nbsp;·&nbsp; ❌ {wr_v} MISSED</div>
        </div>''', unsafe_allow_html=True)

    # ── 문제 번호 도트 — pill 스타일 ──
    st.markdown('<div class="br-dots">', unsafe_allow_html=True)
    _ncols = st.columns(num_qs)
    for _i in range(num_qs):
        with _ncols[_i]:
            _ok_i  = rrs[_i] if _i < len(rrs) else None
            _col   = "#ff6600" if _ok_i else "#ff2244" if _ok_i is not None else "#2a2a3a"
            _bg    = "#1a0800" if _ok_i else "#1a0008" if _ok_i is not None else "#0a0c18"
            _sym   = "✓" if _ok_i else "✗" if _ok_i is not None else str(_i+1)
            _sel   = f"box-shadow:0 0 0 2px #aaa;outline:2px solid #aaa;" if _i==bi else ""
            st.markdown(f'''<style>
            div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]:nth-child({_i+1}) button{{
                background:{_bg}!important;border:1.5px solid {_col}!important;
                color:{_col}!important;border-radius:5px!important;{_sel}
            }}</style>''', unsafe_allow_html=True)
            if st.button(_sym, key=f"dot_{_i}", use_container_width=True):
                st.session_state.br_idx = _i; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 문제 카드 ──
    q  = rqs[bi]; ok = rrs[bi]
    ans_clean = q["ch"][q["a"]].split(") ",1)[-1] if ") " in q["ch"][q["a"]] else q["ch"][q["a"]]
    if ok:
        sent_html = q["text"].replace("_______", f'<span style="color:#50c878;font-weight:900;border-bottom:2px solid #50c878;">{ans_clean}</span>')
        card_border="#00d4ff"; qnum_color="#50c878"; qnum_sym="✅"
    else:
        sent_html = q["text"].replace("_______",
            f'<span style="color:#ff4466;font-weight:900;text-decoration:line-through;margin-right:4px;">?</span>'
            f'<span style="color:#50c878;font-weight:900;border-bottom:2px solid #50c878;">{ans_clean}</span>')
        card_border="#FF2D55"; qnum_color="#ff4466"; qnum_sym="❌"
    kr=q.get("kr",""); exk=q.get("exk",""); cat=q.get("cat","")

    _is_saved = bi in saved
    _prisoner_badge = '' if ok else (
        '<span style="background:#1a0000;border:1px solid #ff4444;border-radius:6px;'
        'padding:2px 8px;font-size:0.65rem;color:#ff6644;font-weight:900;margin-left:8px;">'
        '💀 포로 등록됨</span>' if _is_saved else
        '<span style="background:#001a00;border:1px solid #44ee66;border-radius:6px;'
        'padding:2px 8px;font-size:0.65rem;color:#44ee66;font-weight:900;margin-left:8px;">'
        '→ 저장하면 포로 등록!</span>'
    )

    st.markdown(f'''<div style="background:#080c1a;border:1.5px solid {card_border};
        border-left:4px solid {card_border};border-radius:14px;padding:12px;margin:3px 0;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="background:#0a0a20;border:1px solid #222;border-radius:8px;
              padding:3px 10px;font-size:0.82rem;font-weight:800;color:{qnum_color};">
              {qnum_sym} Q{bi+1}/{num_qs}</span>
            <span style="font-size:0.65rem;color:#444;letter-spacing:2px;">{cat}{_prisoner_badge}</span>
        </div>
        <div style="font-size:1.05rem;font-weight:700;color:#eeeeff;line-height:1.7;margin-bottom:8px;">{sent_html}</div>
        <div style="font-size:0.82rem;color:#6a7a8a;margin-bottom:7px;">📖 {kr}</div>
        <div style="background:#040d04;border-left:3px solid #50c878;border-radius:0 8px 8px 0;padding:7px 10px;">
            <div style="font-size:0.82rem;color:#50c878;font-weight:700;">💡 {exk}</div>
        </div>
    </div>''', unsafe_allow_html=True)

    # ── 저장 버튼 (최우선 CTA) ──
    if not _is_saved:
        st.markdown('<div class="br-save-btn">', unsafe_allow_html=True)
        if st.button("💾  저장! → 포로사령부 + 단어수용소 자동 등록!", key=f"sv_{q['id']}_{bi}", use_container_width=True):
            item = {"id":q["id"],"text":q["text"],"ch":q["ch"],"a":q["a"],"ex":q.get("ex",""),
                    "exk":q.get("exk",""),"cat":q.get("cat",""),"kr":q.get("kr",""),"tp":q.get("tp","grammar")}
            save_to_storage([item])
            # ── 단어 패밀리 DB 스캔 → word_prison 자동 등록 ──
            try:
                import datetime as _fdt, sys as _sys2, os as _os2
                _sys2.path.insert(0, _os2.path.dirname(__file__))
                from _word_family_db import find_words_in_sentence as _find_words
                _fp_sent = q.get("text","").replace("_______", ans_clean)
                _fp_cat  = q.get("cat","")
                _matched = _find_words(_fp_sent, max_words=3)
                _fp_data = load_storage()
                if "word_prison" not in _fp_data: _fp_data["word_prison"] = []
                _changed = False
                for _m in _matched:
                    _w = _m["word"].strip()
                    if not _w or len(_w) < 3: continue
                    if any(p.get("word","").lower()==_w.lower() for p in _fp_data["word_prison"]): continue
                    _fp_data["word_prison"].append({
                        "word":           _w,
                        "kr":             _m["kr"],
                        "pos":            _m["pos"],
                        "family_root":    _m["family_root"],
                        "source":         "P5",
                        "sentence":       _fp_sent,
                        "captured_date":  _fdt.datetime.now().strftime("%Y-%m-%d"),
                        "correct_streak": 0,
                        "last_reviewed":  None,
                        "cat":            _fp_cat,
                    })
                    _changed = True
                if _changed:
                    import json as _jfp2
                    with open(STORAGE_FILE,"w",encoding="utf-8") as _ffp:
                        _jfp2.dump(_fp_data,_ffp,ensure_ascii=False,indent=2)
            except Exception:
                pass
            st.session_state.br_saved.add(bi)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # 저장됨: 작은 뱃지로 표시 (버튼 제거)
        st.markdown(
            '<div style="text-align:center;padding:4px 0;font-size:0.78rem;color:#336644;'
            'font-weight:700;letter-spacing:1px;">✅ 저장 완료 · 포로사령부 대기중</div>',
            unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:#111122;margin:4px 0;"></div>', unsafe_allow_html=True)

    # ── 하단 버튼 (포로사령부:홈 = 3:1) ──
    def _go_home():
        st.session_state._p5_just_left = True
        st.session_state.ans = False
        st.session_state["_battle_entry_ans_reset"] = True
        _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
        if _nick:
            st.query_params["nick"] = _nick
            st.query_params["ag"] = "1"
        st.switch_page("main_hub.py")

    if was_victory:
        _bc1, _bc2 = st.columns([3, 1])
        with _bc1:
            st.markdown('<div class="br-pow-btn">', unsafe_allow_html=True)
            if st.button("💀  포로사령부!", use_container_width=True):
                st.switch_page("pages/03_POW_HQ.py")
            st.markdown('</div>', unsafe_allow_html=True)
        with _bc2:
            st.markdown('<div class="br-home-btn">', unsafe_allow_html=True)
            if st.button("🏠 홈", use_container_width=True):
                _go_home()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # 게임오버: 설욕전 크게 + 포로사령부·홈 작게
        st.markdown('<div class="br-retry-btn">', unsafe_allow_html=True)
        if st.button("🔥  설욕전!", use_container_width=True):
            for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx","br_saved"]:
                if k in st.session_state: del st.session_state[k]
            for k,v in D.items():
                if k not in st.session_state: st.session_state[k]=v
            qs = pick5(st.session_state.mode)
            st.session_state.round_qs = qs; st.session_state.cq = qs[0]
            st.session_state.qst = time.time(); st.session_state.phase = "battle"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        _rc1, _rc2 = st.columns([3, 1])
        with _rc1:
            st.markdown('<div class="br-pow-btn">', unsafe_allow_html=True)
            if st.button("💀  포로사령부!", use_container_width=True):
                st.switch_page("pages/03_POW_HQ.py")
            st.markdown('</div>', unsafe_allow_html=True)
        with _rc2:
            st.markdown('<div class="br-home-btn">', unsafe_allow_html=True)
            if st.button("🏠 홈", use_container_width=True):
                _go_home()
            st.markdown('</div>', unsafe_allow_html=True)


# PHASE: LOBBY
# ════════════════════════════════════════
else:
    _nav = st.query_params.get('nav', '')
    if _nav == 'hub':
        st.query_params.clear()
        st.session_state._p5_just_left = True
        st.session_state.ans = False
        st.session_state["_battle_entry_ans_reset"] = True
        st.switch_page("main_hub.py")
    elif _nav == 'stg':
        st.query_params.clear()
        st.switch_page("pages/03_POW_HQ.py")
    st.session_state.phase="lobby"
    if "sel_mode" not in st.session_state: st.session_state.sel_mode=None

    tsec      = st.session_state.tsec
    sm        = st.session_state.sel_mode
    rn        = st.session_state.round_num
    _tsec_chosen = st.session_state.get('tsec_chosen', False)
    lbl_map  = {"g1":"⚔️ GRAMMAR","g2":"🔄 FORM","g3":"🔗 LINK","vocab":"📘 VOCAB"}
    mode_map = {"g1":("grammar","g1"),"g2":("grammar","g2"),"g3":("link","g3"),"vocab":("vocab",None)}
    _cur_sm  = st.session_state.get("sel_mode","") or ""
    _cur_tc  = st.session_state.get("tsec_chosen", False)
    _cur_tsec= st.session_state.get("tsec", 30)
    _ready   = _cur_tc and _cur_sm in ["g1","g2","g3","vocab"]
    _adp     = st.session_state.get("adp_level","normal")
    _adp_lbl = {"easy":"🟢 EASY (≤15단어)","normal":"🟡 NORMAL (16-19단어)","hard":"🔴 HARD (20-23단어)"}.get(_adp,"🟡 NORMAL (16-19단어)")
    _hist_len= len(st.session_state.get("adp_history",[]))

    # ══════════════════════════════════════════════════════
    # 로비 CSS + 렌더링 — 암호해독 수준 고급화
    # ══════════════════════════════════════════════════════
    _tlabel_map = {"30":"🔥 BLITZ 30s","40":"⚡ STANDARD 40s","50":"🛡 SNIPER 50s"}

    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');

.stApp { background:#04040c !important; }
section[data-testid="stSidebar"] { display:none !important; }
header[data-testid="stHeader"]   { height:0 !important; overflow:hidden !important; }
.block-container { padding:14px 14px 30px !important; margin:0 !important; }
div[data-testid="stVerticalBlock"] { gap:10px !important; }
.element-container { margin:0 !important; padding:0 !important; }
div[data-testid="stHorizontalBlock"] {
  gap:5px !important; margin:0 !important; flex-wrap:nowrap !important;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"] {
  padding:0 !important; min-width:0 !important; flex:1 !important;
}

@keyframes titleShine {
  0%   { background-position:200% center }
  100% { background-position:-200% center }
}
@keyframes warnBlink {
  0%,100% { opacity:1; color:#ff4466; }
  50%     { opacity:0.65; color:#ff8888; }
}
@keyframes launchGlow {
  0%,100% { box-shadow:0 0 14px rgba(255,70,0,0.7), 0 0 30px rgba(255,50,0,0.3); }
  50%     { box-shadow:0 0 55px rgba(255,210,0,1),  0 0 110px rgba(255,140,0,0.6); }
}
@keyframes selPulse {
  0%,100% { filter:brightness(1); }
  50%     { filter:brightness(1.12); }
}

/* 공통 버튼 */
div[data-testid="stButton"] button {
  background:#070b17 !important;
  border:1.5px solid rgba(0,180,255,0.18) !important;
  border-radius:10px !important;
  font-family:'Rajdhani',sans-serif !important;
  font-size:0.88rem !important; font-weight:700 !important;
  padding:8px 6px !important; color:#4a6688 !important;
  min-height:46px !important; width:100% !important;
  white-space:pre-line !important; line-height:1.3 !important;
  transition:border-color 0.12s, box-shadow 0.12s !important;
}
div[data-testid="stButton"] button p {
  font-size:0.88rem !important; font-weight:700 !important;
  color:#4a6688 !important; white-space:pre-line !important; line-height:1.3 !important;
}

/* 시간: BLITZ 30s 오렌지/불꽃 */
div[data-testid="stButton"] button.fp-t30 {
  background:#0e0700 !important;
  border-color:rgba(200,90,20,0.3) !important; color:#886644 !important;
  min-height:56px !important; font-family:'Orbitron',monospace !important; font-size:0.78rem !important;
}
div[data-testid="stButton"] button.fp-t30 p { color:#886644 !important; }
div[data-testid="stButton"] button.fp-t30.fp-sel {
  background:#220e00 !important;
  border-color:#ff8833 !important; color:#ffaa44 !important;
  box-shadow:0 0 22px rgba(255,130,50,0.55) !important;
  animation:selPulse 1.6s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-t30.fp-sel p { color:#ffaa44 !important; }

/* 시간: STANDARD 40s 파랑 */
div[data-testid="stButton"] button.fp-t40 {
  background:#03091a !important;
  border-color:rgba(40,110,230,0.3) !important; color:#335577 !important;
  min-height:56px !important; font-family:'Orbitron',monospace !important; font-size:0.78rem !important;
}
div[data-testid="stButton"] button.fp-t40 p { color:#335577 !important; }
div[data-testid="stButton"] button.fp-t40.fp-sel {
  background:#07152e !important;
  border-color:#3388ff !important; color:#55aaff !important;
  box-shadow:0 0 22px rgba(60,140,255,0.55) !important;
  animation:selPulse 1.6s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-t40.fp-sel p { color:#55aaff !important; }

/* 시간: SNIPER 50s 보라 */
div[data-testid="stButton"] button.fp-t50 {
  background:#0a051e !important;
  border-color:rgba(130,55,220,0.3) !important; color:#664488 !important;
  min-height:56px !important; font-family:'Orbitron',monospace !important; font-size:0.78rem !important;
}
div[data-testid="stButton"] button.fp-t50 p { color:#664488 !important; }
div[data-testid="stButton"] button.fp-t50.fp-sel {
  background:#180836 !important;
  border-color:#aa44ff !important; color:#cc77ff !important;
  box-shadow:0 0 22px rgba(170,80,255,0.55) !important;
  animation:selPulse 1.6s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-t50.fp-sel p { color:#cc77ff !important; }

/* 작전 카드 공통 — 4열 한 줄 */
div[data-testid="stButton"] button.fp-mode {
  min-height:90px !important;
  text-align:center !important; padding:10px 3px !important;
  font-family:'Rajdhani',sans-serif !important; font-size:0.82rem !important;
}

/* 문법력 파랑 */
div[data-testid="stButton"] button.fp-g1 {
  background:#1a0800 !important; border-color:rgba(255,100,0,0.35) !important; color:#cc5500 !important;
}
div[data-testid="stButton"] button.fp-g1 p { color:#cc5500 !important; }
div[data-testid="stButton"] button.fp-g1.fp-sel {
  background:#2a1000 !important; border-color:#ff6600 !important; color:#ff8833 !important;
  box-shadow:0 0 22px rgba(106,173,255,0.5) !important; border-width:2px !important;
  animation:selPulse 1.8s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-g1.fp-sel p { color:#ff8833 !important; }

/* 구조력 보라 */
div[data-testid="stButton"] button.fp-g2 {
  background:#1a0c00 !important; border-color:rgba(220,140,0,0.35) !important; color:#bb8800 !important;
}
div[data-testid="stButton"] button.fp-g2 p { color:#bb8800 !important; }
div[data-testid="stButton"] button.fp-g2.fp-sel {
  background:#200a3e !important; border-color:#cc88ff !important; color:#ddaaff !important;
  box-shadow:0 0 22px rgba(200,136,255,0.5) !important; border-width:2px !important;
  animation:selPulse 1.8s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-g2.fp-sel p { color:#ddaaff !important; }

/* 연결력 청록 */
div[data-testid="stButton"] button.fp-g3 {
  background:#181000 !important; border-color:rgba(200,160,0,0.35) !important; color:#aa8800 !important;
}
div[data-testid="stButton"] button.fp-g3 p { color:#aa8800 !important; }
div[data-testid="stButton"] button.fp-g3.fp-sel {
  background:#281800 !important; border-color:#ddaa00 !important; color:#ffdd44 !important;
  box-shadow:0 0 22px rgba(0,220,200,0.5) !important; border-width:2px !important;
  animation:selPulse 1.8s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-g3.fp-sel p { color:#ffdd44 !important; }

/* 어휘력 초록 */
div[data-testid="stButton"] button.fp-vc {
  background:#1a0400 !important; border-color:rgba(220,60,0,0.35) !important; color:#cc3300 !important;
}
div[data-testid="stButton"] button.fp-vc p { color:#cc3300 !important; }
div[data-testid="stButton"] button.fp-vc.fp-sel {
  background:#2a0800 !important; border-color:#ff4400 !important; color:#ff6633 !important;
  box-shadow:0 0 22px rgba(85,238,119,0.5) !important; border-width:2px !important;
  animation:selPulse 1.8s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-vc.fp-sel p { color:#ff6633 !important; }

/* 출격 버튼 */
div[data-testid="stButton"] button.fp-launch {
  background:#280800 !important; border:2.5px solid #ff4400 !important;
  border-radius:14px !important; color:#ffcc55 !important;
  font-family:'Orbitron',monospace !important;
  font-weight:900 !important; font-size:0.88rem !important;
  letter-spacing:2px !important; min-height:56px !important;
  transition:none !important; animation:launchGlow 0.55s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-launch p {
  color:#ffcc55 !important; font-family:'Orbitron',monospace !important;
  font-size:0.88rem !important; font-weight:900 !important; letter-spacing:2px !important;
}
div[data-testid="stButton"] button.fp-launch-off {
  background:#06060f !important; border:1px solid #0e0e1c !important;
  border-radius:12px !important; color:#18182a !important;
  font-family:'Orbitron',monospace !important;
  font-size:0.8rem !important; min-height:50px !important;
}
div[data-testid="stButton"] button.fp-launch-off p { color:#18182a !important; }

/* 네비 버튼 */
div[data-testid="stButton"] button.fp-nav {
  background:#05050e !important; border:1px solid #151525 !important;
  border-radius:10px !important; color:#3d5066 !important;
  min-height:40px !important; font-size:0.82rem !important;
}
div[data-testid="stButton"] button.fp-nav p { color:#3d5066 !important; }

@media(max-width:480px) {
  div[data-testid="stButton"] button.fp-t30,
  div[data-testid="stButton"] button.fp-t40,
  div[data-testid="stButton"] button.fp-t50 { min-height:52px !important; }
  div[data-testid="stButton"] button.fp-mode { min-height:82px !important; }
  div[data-testid="stButton"] button.fp-launch { min-height:52px !important; }
}
</style>""", unsafe_allow_html=True)

    # ── 타이틀 ──
    _rb = f'<span style="background:#1a0800;border:1px solid #cc6600;border-radius:20px;padding:1px 10px;font-size:0.68rem;color:#ffaa44;font-weight:900;">🏆 ROUND {rn}</span> ' if rn > 1 else ''
    st.markdown(f"""<div style="text-align:center;padding:10px 0 14px;">
      <div style="font-size:8px;color:#442200;letter-spacing:4px;margin-bottom:4px;font-weight:700;">FIREPOWER BATTLE</div>
      <div style="font-family:Orbitron,monospace;font-size:2rem;font-weight:900;letter-spacing:6px;
        background:linear-gradient(90deg,#00e5ff,#ffffff,#FFD600,#ff3300,#00e5ff);background-size:300%;
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        animation:titleShine 2s linear infinite;line-height:1.2;">{_rb}⚡ 화력전</div>
      <div style="font-size:0.65rem;color:#334455;letter-spacing:2px;margin-top:5px;">
        5문제 · 살아남아라! · 문법어휘 실전 포격전</div>
    </div>""", unsafe_allow_html=True)
