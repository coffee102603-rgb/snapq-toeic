"""통합 저장고 — P5 학습/시험 + VOCA 학습/시험"""
import streamlit as st
import streamlit.components.v1 as components
import json, os, random, time, re
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="📦 저장고", page_icon="📦", layout="wide", initial_sidebar_state="collapsed")

STORAGE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage_data.json")

def load_storage():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE,"r",encoding="utf-8") as f:
            d = json.load(f)
            if isinstance(d, list): return {"saved_questions":d,"saved_expressions":[]}
            if "saved_questions" not in d: d["saved_questions"]=[]
            if "saved_expressions" not in d: d["saved_expressions"]=[]
            return d
    return {"saved_questions":[],"saved_expressions":[]}

def save_storage(data):
    with open(STORAGE_FILE,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2)

def make_alt_question(q):
    ans = q["ch"][q["a"]]
    clean_ans = ans.split(") ",1)[-1] if ") " in ans else ans
    full = q["text"].replace("_______", clean_ans)
    words = full.replace(",", " ,").replace(".", " .").split()
    skip = {"the","a","an","in","on","at","to","for","of","by","with","is","are","was","were","has","have","had","be","been","that","this","it","its","all","not","and","or","but","as","if","so","no","do","did","can","may","will","shall","would","could","should","must","from","into","upon","than","then","also","very","much","more","most","only","just","even","still","yet","each","every","both","few","many","some","any","other","such","what","which","who","whom","whose","where","when","how","why"}
    candidates = []
    for i, w in enumerate(words):
        cw = w.strip(".,;:!?'\"").lower()
        if len(cw) >= 3 and cw not in skip and cw != clean_ans.lower():
            candidates.append((i, w))
    if not candidates: return None
    idx, target_word = random.choice(candidates)
    target_clean = target_word.strip(".,;:!?'\"")
    new_words = words.copy()
    new_words[idx] = words[idx].replace(target_clean, "_______")
    new_text = " ".join(new_words).replace(" ,", ",").replace(" .", ".")
    distractors_pool = ["provide","maintain","require","consider","establish","develop","address","achieve","indicate","determine","implement","evaluate","facilitate","demonstrate","acknowledge","contribute","participate","collaborate","recommend","negotiate","relevant","significant","appropriate","essential","available","potential","sufficient","additional","comprehensive","preliminary"]
    distractors = random.sample([d for d in distractors_pool if d.lower() != target_clean.lower()], min(3, len(distractors_pool)))
    choices = distractors + [target_clean]
    random.shuffle(choices)
    correct_idx = choices.index(target_clean)
    labeled = [f"({chr(65+i)}) {c}" for i, c in enumerate(choices)]
    return {"text": new_text, "ch": labeled, "a": correct_idx, "type": "alt_vocab"}

# ═══ 잔소리 풀 ═══
NAGGING = [
    "💀 인간은 틀린 문제를 또 틀릴 확률 72%",
    "🔥 복습 안 하면 24시간 내 80% 망각",
    "⚡ 3번 반복하면 장기기억 전환율 3배",
    "💣 토익 고수는 오답노트를 3번 본다",
    "🧠 에빙하우스: 1일 후 기억 잔존율 33%",
    "🎯 반복학습 없이 고득점? 꿈 깨세요",
    "📖 단어는 문장 속에서 외워야 진짜다",
    "⏰ 하루 10분 복습 > 주말 2시간 벼락치기",
]

# ═══ CSS ═══
st.markdown("""<style>
.stApp{background:linear-gradient(135deg,#121538,#241a50 30%,#142248 70%,#121538)!important;color:#e8e8f0!important;}
@keyframes cardPulse{0%,100%{box-shadow:0 0 20px rgba(var(--glow-rgb),0.1)}50%{box-shadow:0 0 35px rgba(var(--glow-rgb),0.25)}}
@keyframes slideUp{from{opacity:0;transform:translateY(15px)}to{opacity:1;transform:translateY(0)}}
@keyframes choiceFade{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:translateX(0)}}\n@keyframes highlightDraw{from{width:0}to{width:100%}}\n@keyframes hlDraw{from{background-size:0% 4px}to{background-size:100% 4px}}
section[data-testid="stSidebar"]{display:none!important;}
header[data-testid="stHeader"]{background:transparent!important;}
.block-container{padding-top:0.7rem!important;padding-bottom:1rem!important;max-width:100%!important;padding-left:1rem!important;padding-right:1rem!important;}
div[data-testid="stVerticalBlock"]>div{gap:0.1rem;}
@keyframes rb{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}

button[kind="primary"]{background:linear-gradient(135deg,#cc2200,#ff4422,#ff6644)!important;color:#fff!important;border:2px solid #ff5533!important;border-radius:14px!important;font-size:2rem!important;font-weight:900!important;padding:0.8rem 1rem!important;}
button[kind="primary"] p{font-size:2rem!important;font-weight:900!important;text-align:center!important;}
button[kind="secondary"]{background:linear-gradient(135deg,#0044cc,#0066ff,#2288ff)!important;color:#fff!important;border:2px solid #3399ff!important;border-radius:14px!important;font-size:2rem!important;font-weight:900!important;padding:0.8rem 1rem!important;}
button[kind="secondary"] p{font-size:2rem!important;font-weight:900!important;text-align:center!important;}

/* 줄노트 */
.note{background:#fffef5;border-radius:12px;padding:1.5rem 1.2rem;margin:0.5rem 0;
    background-image:repeating-linear-gradient(transparent,transparent 39px,#e8e0c8 39px,#e8e0c8 40px);
    background-position:0 1.5rem;box-shadow:0 3px 15px rgba(0,0,0,0.2);border:1px solid #d8d0b8;min-height:200px;}
.note-sent{font-size:1.7rem;font-weight:700;color:#1a1a1a;line-height:2.2;margin:0.8rem 0;}
.note-hl{color:#008844;font-weight:900;font-size:1.8rem;text-decoration:underline;text-underline-offset:5px;text-decoration-thickness:3px;background:rgba(0,180,80,0.08);padding:0 4px;border-radius:4px;}
.note-kr{font-size:1.5rem;font-weight:600;color:#333;line-height:1.8;margin-bottom:0.5rem;}
.note-ex{font-size:1.3rem;color:#555;line-height:1.6;padding:0.5rem 0.8rem;background:rgba(255,180,0,0.1);border-left:4px solid #ffaa00;border-radius:0 8px 8px 0;}

/* 시험 */
.exam{background:#fff;border-radius:4px;padding:1.8rem 1.5rem;margin:0.4rem 0;box-shadow:0 2px 10px rgba(0,0,0,0.15);border:1px solid #ccc;font-family:'Times New Roman',serif;}
.exam-q{font-size:2rem;font-weight:900;color:#e8e8ff;line-height:1.9;margin:0.8rem 0;word-break:keep-all;}

/* 리모컨 */
.sg-rmt{max-width:95vw;margin:0 auto;background:linear-gradient(180deg,#0a0e1a,#121830);
    border-radius:32px;padding:24px 16px 16px 16px;border:3px solid #8844cc;
    box-shadow:0 8px 40px rgba(136,68,204,0.15);text-align:center;}
.sg-rmt-t{font-size:2.6rem;font-weight:900;
    background:linear-gradient(90deg,#cc66ff,#ff66aa,#ffaa44,#cc66ff);
    background-size:300% 300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
    animation:rb 4s ease infinite;letter-spacing:2px;}
.sg-nag{background:linear-gradient(135deg,#1a0520,#2a0a30);border:2px solid #aa44cc;border-radius:18px;padding:14px;margin:12px 0;text-align:center;}
.sg-nag-t{font-size:1.4rem;font-weight:900;color:#ffcc00;text-shadow:0 0 10px rgba(255,204,0,0.3);}
.sg-zn{border-radius:18px;padding:14px;margin:12px 0 6px 0;text-align:center;}
.sg-zl{font-size:1.6rem;font-weight:900;letter-spacing:4px;text-transform:uppercase;}
</style>""", unsafe_allow_html=True)

# ═══ 세션 ═══
for k,v in {"sg_phase":"lobby","sg_idx":0,"sg_mode":None,
    "sg_exam_qs":[],"sg_exam_idx":0,"sg_exam_results":[],"sg_exam_start":None,"sg_exam_wrong":False,
    "p5_exam_recorded":False,
    "sg_wave":1,"sg_wave_idx":0,"sg_wave_results":[],"sg_wave_start":None,"sg_wave_dead":False,
    "sg_combo_score":0,"sg_combo_count":0,"sg_combo_idx":0,"sg_combo_start":None,"sg_combo_over":False}.items():
    if k not in st.session_state: st.session_state[k]=v

storage = load_storage()
p5_data = storage.get("saved_questions",[])
voca_data = storage.get("saved_expressions",[])

# ════════════════════════════════
# PHASE: LOBBY (리모컨)
# ════════════════════════════════
if st.session_state.sg_phase == "lobby":
    # 승률 계산
    p5_rec = storage.get("p5_exam_record", {"wins":0,"total":0})
    voca_rec = storage.get("voca_exam_record", {"wins":0,"total":0})
    p5_rate = f'{int(p5_rec["wins"]/p5_rec["total"]*100)}%' if p5_rec["total"] > 0 else "—"
    voca_rate = f'{int(voca_rec["wins"]/voca_rec["total"]*100)}%' if voca_rec["total"] > 0 else "—"

    # ═══ 상단 ═══
    st.markdown("""<div style="background:linear-gradient(135deg,#101828,#182238);border:2px solid #3a5068;border-radius:22px;padding:16px;text-align:center;margin-bottom:12px;">
        <div style="font-size:2.4rem;font-weight:900;letter-spacing:6px;color:#99bbdd;">📦 저 장 고</div>
    </div>""", unsafe_allow_html=True)

    nag = random.choice(NAGGING)
    nag_words = nag.split()
    nag_spans = ""
    for i, w in enumerate(nag_words):
        delay = i * 0.4
        nag_spans += f'<span style="opacity:0;animation:nagFade 0.5s ease {delay}s forwards;font-size:1.8rem;font-weight:900;color:#ffcc00;">{w} </span>'
    components.html(f"""
    <style>
    @keyframes nagFade{{0%{{opacity:0;transform:translateY(8px)}}100%{{opacity:1;transform:translateY(0)}}}}
    </style>
    <div style="text-align:center;padding:10px 0 16px 0;background:transparent;">{nag_spans}</div>
    """, height=70)

    # ═══ 학습 줄 ═══
    r1c1, r1c2 = st.columns([1,1], gap="medium")
    with r1c1:
        if st.button(f"📖  P5 학습\n{len(p5_data)}문제", key="sg_p5s", type="secondary", use_container_width=True):
            if p5_data:
                st.session_state.sg_phase = "p5_study"; st.session_state.sg_idx = 0; st.rerun()
            else: st.warning("P5 저장 문제 없음!")
    with r1c2:
        if st.button(f"🌊  웨이브\n{len(voca_data)}단어", key="sg_vs", type="secondary", use_container_width=True):
            if len(voca_data) >= 3:
                st.session_state.sg_wave = 1; st.session_state.sg_wave_idx = 0
                st.session_state.sg_wave_results = []; st.session_state.sg_wave_dead = False
                st.session_state.sg_wave_start = time.time()
                if "sg_sv_pool" in st.session_state: del st.session_state.sg_sv_pool
                if "sg_wave_start" in st.session_state: del st.session_state.sg_wave_start
                st.session_state.sg_phase = "survival"; st.rerun()
            else: st.warning("최소 3단어 필요!")

    # 간격
    st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

    # ═══ 시험 줄 ═══
    r2c1, r2c2 = st.columns([1,1], gap="medium")
    with r2c1:
        if st.button(f"📝  P5 시험\n🏆 {p5_rate}", key="sg_p5e", type="primary", use_container_width=True):
            if len(p5_data) >= 5:
                qs = random.sample(p5_data, 5)
                st.session_state.sg_exam_qs = qs; st.session_state.sg_exam_idx = 0
                st.session_state.sg_exam_results = []; st.session_state.sg_exam_start = time.time()
                st.session_state.sg_exam_wrong = False; st.session_state.sg_phase = "p5_exam"; st.rerun()
            else: st.warning("최소 5문제 필요!")
    with r2c2:
        combo_best = storage.get("combo_best", 0)
        combo_label = f"⭐{combo_best}" if combo_best > 0 else "—"
        if st.button(f"🔥  콤보러시\n⭐ {combo_label}", key="sg_ve", type="primary", use_container_width=True):
            if len(voca_data) >= 3:
                st.session_state.sg_combo_score = 0; st.session_state.sg_combo_count = 0
                st.session_state.sg_combo_idx = 0; st.session_state.sg_combo_start = time.time()
                st.session_state.sg_combo_over = False
                if "sg_combo_pool" in st.session_state: del st.session_state.sg_combo_pool
                st.session_state.sg_phase = "combo_rush"; st.rerun()
            else: st.warning("최소 3단어 필요!")

    # 간격
    st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)

    # ═══ 하단 ═══
    st.markdown("""<div style="background:linear-gradient(135deg,#101828,#182238);border:2px solid #3a5068;border-radius:22px;padding:10px;text-align:center;">
        <div style="font-size:1.1rem;font-weight:900;color:#7799bb;letter-spacing:4px;">🧭 N A V I G A T E</div>
    </div>""", unsafe_allow_html=True)
    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
    mn1, mn2, mn3 = st.columns(3, gap="medium")
    with mn1:
        if st.button("⚔️ P5전장", key="sg_nav1", type="secondary", use_container_width=True):
            st.session_state.phase = "lobby"
            st.session_state._p5_active = False
            st.switch_page("pages/02_P5_Arena.py")
    with mn2:
        if st.button("📖 P7전장", key="sg_nav2", type="secondary", use_container_width=True):
            st.switch_page("pages/04_P7_Reading.py")
    with mn3:
        if st.button("🏠 메인", key="sg_nav3", type="secondary", use_container_width=True):
            st.switch_page("main_hub.py")

    with st.expander("⚠️ 저장고 관리"):
        if st.button("🗑 P5 전체 삭제", key="del_p5"):
            storage["saved_questions"] = []; save_storage(storage); st.rerun()
        if st.button("🗑 VOCA 전체 삭제", key="del_voca"):
            storage["saved_expressions"] = []; save_storage(storage); st.rerun()
        if st.button("🗑 시험 기록 초기화", key="del_rec"):
            storage["p5_exam_record"] = {"wins":0,"total":0}
            storage["voca_exam_record"] = {"wins":0,"total":0}
            save_storage(storage); st.rerun()

    # JS — 밝고 세련된 색상
    components.html("""
    <script>
    function sgC(){
        const d=window.parent.document;
        d.querySelectorAll('button[kind="secondary"]').forEach(b=>{
            const t=b.textContent||'';
            if(t.includes('P5 학습')){b.style.cssText='background:linear-gradient(145deg,#3d1530,#5a2045)!important;border:2.5px solid #ee5599!important;border-radius:22px!important;min-height:120px!important;color:#fff!important;font-size:1.6rem!important;font-weight:900!important;box-shadow:0 4px 20px rgba(238,85,153,0.15)!important;';}
            if(t.includes('VOCA 학습')||t.includes('웨이브')){b.style.cssText='background:linear-gradient(145deg,#0a2a4a,#153858)!important;border:2.5px solid #4488ff!important;border-radius:22px!important;min-height:120px!important;color:#fff!important;font-size:1.6rem!important;font-weight:900!important;box-shadow:0 4px 20px rgba(68,136,255,0.15)!important;';}
            if(t.includes('P5전장')||t.includes('P7전장')||t.includes('메인')){b.style.cssText='background:linear-gradient(145deg,#1a2545,#253560)!important;border:1.5px solid #5577aa!important;border-radius:16px!important;color:#aaccee!important;font-size:1.3rem!important;font-weight:900!important;';}
        });
        d.querySelectorAll('button[kind="primary"]').forEach(b=>{
            const t=b.textContent||'';
            if(t.includes('P5 시험')){b.style.cssText='background:linear-gradient(145deg,#4a1525,#6a2035)!important;border:2.5px solid #ff4477!important;border-radius:22px!important;min-height:120px!important;color:#fff!important;font-size:1.6rem!important;font-weight:900!important;box-shadow:0 4px 20px rgba(255,68,119,0.2)!important;';}
            if(t.includes('VOCA 시험')||t.includes('콤보러시')){b.style.cssText='background:linear-gradient(145deg,#3a1a00,#5a2a0a)!important;border:2.5px solid #ff8800!important;border-radius:22px!important;min-height:120px!important;color:#fff!important;font-size:1.6rem!important;font-weight:900!important;box-shadow:0 4px 20px rgba(255,136,0,0.2)!important;';}
        });
    }
    setTimeout(sgC,200);setTimeout(sgC,800);
    const o=new MutationObserver(sgC);o.observe(window.parent.document.body,{childList:true,subtree:true});
    </script>
    """, height=0)


elif st.session_state.sg_phase == "p5_study":
    if not p5_data:
        st.warning("저장된 문제가 없습니다!")
        st.session_state.sg_phase = "lobby"; st.rerun()

    bi = st.session_state.sg_idx
    if bi >= len(p5_data): bi = len(p5_data)-1
    if bi < 0: bi = 0
    q = p5_data[bi]

    st.markdown('<div style="text-align:center;"><span style="font-size:1.5rem;font-weight:900;color:#44cc88;">📖 P5 학습모드</span></div>', unsafe_allow_html=True)

    nc1, nc2, nc3 = st.columns([1, 6, 1])
    with nc1:
        if st.button("◀", key="st_p", disabled=bi<=0, use_container_width=True):
            st.session_state.sg_idx = bi-1; st.rerun()
    with nc3:
        if st.button("▶", key="st_n", disabled=bi>=len(p5_data)-1, use_container_width=True):
            st.session_state.sg_idx = bi+1; st.rerun()

    ans = q["ch"][q["a"]]
    clean = ans.split(") ",1)[-1] if ") " in ans else ans
    sent = q["text"].replace("_______", f'<span class="note-hl">{clean}</span>')
    kr = q.get("kr","")
    exk = q.get("exk","")
    cat = q.get("cat","")

    st.markdown(f'''<div class="note">
        <div style="display:flex;justify-content:space-between;">
            <div style="font-size:1rem;font-weight:800;color:#cc6600;">✏️ {bi+1} / {len(p5_data)}</div>
            <div style="font-size:1rem;font-weight:900;color:#cc0000;border:2px solid #cc0000;border-radius:50px;padding:0.1rem 0.6rem;">{cat}</div>
        </div>
        <div class="note-sent">{sent}</div>
        <div style="border-top:2px dashed #ccc;margin:0.6rem 0;"></div>
        <div class="note-kr">📖 {kr}</div>
        <div class="note-ex">💡 {exk}</div>
    </div>''', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🗑 삭제", key="del_q", type="secondary", use_container_width=True):
            p5_data.pop(bi)
            storage["saved_questions"] = p5_data
            save_storage(storage)
            if bi >= len(p5_data): st.session_state.sg_idx = max(0, len(p5_data)-1)
            st.rerun()
    with c2:
        if st.button("📝 시험", key="go_exam", type="primary", use_container_width=True):
            if len(p5_data) >= 5:
                qs = random.sample(p5_data, 5)
                st.session_state.sg_exam_qs = qs
                st.session_state.sg_exam_idx = 0
                st.session_state.sg_exam_results = []
                st.session_state.sg_exam_start = time.time()
                st.session_state.sg_exam_wrong = False
                st.session_state.sg_phase = "p5_exam"; st.rerun()
            else: st.warning("최소 5문제 필요!")
    with c3:
        if st.button("📦 로비", key="back_lobby", type="secondary", use_container_width=True):
            st.session_state.sg_phase = "lobby"; st.rerun()
    with c4:
        if st.button("🏠 메인", key="go_main_p5s", type="secondary", use_container_width=True):
            st.switch_page("main_hub.py")

# ════════════════════════════════
# P5 시험모드 — 33초 타임폭탄
# ════════════════════════════════
elif st.session_state.sg_phase == "p5_exam":
    st_autorefresh(interval=1000, limit=40, key="p5_exam_timer")
    qs = st.session_state.sg_exam_qs
    qi = st.session_state.sg_exam_idx
    if qi >= len(qs):
        st.session_state.sg_phase = "p5_exam_result"; st.rerun()
    q = qs[qi]
    elapsed = time.time() - st.session_state.sg_exam_start
    rem = max(0, 33 - int(elapsed))
    left = 5 - qi
    if rem <= 0:
        st.session_state.sg_exam_results.append(False)
        st.session_state.sg_exam_wrong = True
        st.session_state.sg_phase = "p5_exam_result"; st.rerun()

    # 배경색 점차 붉어짐 (움직임 없음!)
    if rem <= 5:
        bg_css = "background:linear-gradient(135deg,#2a0808,#3a0a1a 30%,#2a0510 70%,#2a0808)!important;"
        tcl = "#ff0000"; tsz = "5rem"; tglow = "text-shadow:0 0 40px #ff0000,0 0 80px #cc0000;"
        twarn = '<div style="text-align:center;font-size:1.4rem;color:#ff0000;font-weight:900;margin-top:4px;">💀💀 폭발한다!! 💀💀</div>'
    elif rem <= 10:
        bg_css = "background:linear-gradient(135deg,#1e0815,#2e0a25 30%,#1e0818 70%,#1e0815)!important;"
        tcl = "#ff2200"; tsz = "4rem"; tglow = "text-shadow:0 0 25px #ff2200,0 0 50px #ff0000;"
        twarn = '<div style="text-align:center;font-size:1.1rem;color:#ff4444;font-weight:900;">💀 서둘러!! 또 틀릴 거야?! 💀</div>'
    elif rem <= 15:
        bg_css = "background:linear-gradient(135deg,#160a1e,#220e30 30%,#160a22 70%,#160a1e)!important;"
        tcl = "#ff6600"; tsz = "3.2rem"; tglow = "text-shadow:0 0 15px #ff6600;"
        twarn = '<div style="text-align:center;font-size:1rem;color:#ff8844;font-weight:900;">⚡ 서둘러!! ⚡</div>'
    elif rem <= 20:
        bg_css = "background:linear-gradient(135deg,#121530,#1e1845 30%,#121838 70%,#121530)!important;"
        tcl = "#ffaa00"; tsz = "2.8rem"; tglow = "text-shadow:0 0 8px #ffaa00;"
        twarn = ""
    else:
        bg_css = ""
        tcl = "#44ff88"; tsz = "2.4rem"; tglow = ""; twarn = ""
    tpct = int(rem / 33 * 100)
    q_border = "rgba(255,50,50,0.6)" if rem <= 10 else "rgba(100,140,255,0.4)"
    q_shadow = "0 0 40px rgba(255,0,0,0.2)" if rem <= 10 else "0 0 30px rgba(100,140,255,0.15)"
    if bg_css:
        st.markdown(f'<style>.stApp{{{bg_css}}}</style>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;margin:8px 0;padding:10px;"><span style="font-size:{tsz};font-weight:900;color:{tcl};font-family:Impact,Arial Black,sans-serif;{tglow}">{rem}</span><span style="font-size:1.5rem;color:{tcl};opacity:0.7;">s</span><div style="font-size:1rem;color:#888;font-weight:700;margin-top:4px;">Q{qi+1} / 5 · 남은 {left}문제</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:rgba(255,255,255,0.06);border-radius:12px;padding:3px;margin:4px 0;"><div style="background:linear-gradient(90deg,{tcl},#4488ff);height:12px;border-radius:10px;width:{tpct}%;"></div></div>', unsafe_allow_html=True)
    if twarn:
        st.markdown(twarn, unsafe_allow_html=True)
    blank_text = q["text"].replace("_______", '<span style="border-bottom:3px solid #66aaff;padding:0 16px;color:#88bbff;">________</span>')
    st.markdown(f'<div style="background:linear-gradient(145deg,#141435,#1c1c4a);border:2.5px solid {q_border};border-radius:20px;padding:1.8rem 1.4rem;margin:10px 0;box-shadow:{q_shadow};"><div style="font-size:2.4rem;font-weight:900;color:#e8e8ff;line-height:1.7;font-family:Georgia,serif;">{blank_text}</div></div>', unsafe_allow_html=True)
    for i, ch in enumerate(q["ch"]):
        if st.button(ch, key=f"ex_{qi}_{i}", type="secondary", use_container_width=True):
            ok = (i == q["a"])
            st.session_state.sg_exam_results.append(ok)
            if not ok:
                st.session_state.sg_exam_wrong = True
                st.session_state.sg_phase = "p5_exam_result"; st.rerun()
            else:
                st.session_state.sg_exam_idx += 1
                st.rerun()
    components.html("""<script>
    function stP(){const d=window.parent.document;d.querySelectorAll('button[kind="secondary"]').forEach(b=>{const t=(b.textContent||'').trim();if(/^\([A-D]\)/.test(t)){b.style.cssText='background:linear-gradient(135deg,rgba(100,140,200,0.25),rgba(100,140,200,0.12))!important;color:#ffffff!important;border:2px solid rgba(100,140,200,0.5)!important;border-radius:16px!important;font-size:1.9rem!important;font-weight:900!important;padding:0.9rem 1rem!important;min-height:auto!important;box-shadow:0 3px 15px rgba(100,140,200,0.15)!important;font-family:Georgia,serif!important;';b.querySelectorAll('p').forEach(p=>p.style.cssText='font-size:1.9rem!important;font-weight:900!important;font-family:Georgia,serif!important;');}});};setTimeout(stP,80);setTimeout(stP,300);setTimeout(stP,700);new MutationObserver(stP).observe(window.parent.document.body,{childList:true,subtree:true});
    </script>""", height=0)

# ════════════════════════════════
# P5 시험 결과
# ════════════════════════════════
elif st.session_state.sg_phase == "p5_exam_result":
    results = st.session_state.sg_exam_results
    ok_cnt = sum(results)
    passed = not st.session_state.sg_exam_wrong and ok_cnt == 5
    # 승률 저장
    if "p5_exam_recorded" not in st.session_state:
        rec = storage.get("p5_exam_record", {"wins":0,"total":0})
        rec["total"] += 1
        if passed: rec["wins"] += 1
        storage["p5_exam_record"] = rec; save_storage(storage)
        st.session_state.p5_exam_recorded = True
    if not passed:
        st.markdown('<div style="text-align:center;font-size:3rem;font-weight:900;color:#ff4444;text-shadow:0 0 20px #ff0000;">💀 FAIL! 💀</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align:center;font-size:3rem;font-weight:900;color:#44ff88;text-shadow:0 0 20px #00ff66;">🎉 PASS! 🎉</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;font-size:1.5rem;color:#ccc;font-weight:700;">✅ {ok_cnt} / 5</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 다시!", key="retry_exam", type="primary", use_container_width=True):
            st.session_state.p5_exam_recorded = False
            st.session_state.sg_phase = "lobby"; st.rerun()
    with c2:
        if st.button("📦 저장고", key="back_exam", type="secondary", use_container_width=True):
            st.session_state.p5_exam_recorded = False
            st.session_state.sg_phase = "lobby"; st.rerun()
# ════════════════════════════════
# VOCA 서바이벌 웨이브 (순수 학습모드 - 타이머 없음)
# ════════════════════════════════
elif st.session_state.sg_phase == "survival":

    wave = st.session_state.get("sg_wave", 1)
    widx = st.session_state.get("sg_wave_idx", 0)
    results = st.session_state.get("sg_wave_results", [])
    dead = st.session_state.get("sg_wave_dead", False)

    # 웨이브 설정 (시간 제한 없음 - 학습모드)
    WAVE_CFG = {
        1: {"name": "Wave 1", "desc": "영어표현 → 한글뜻", "count": 2},
        2: {"name": "Wave 2", "desc": "한글뜻 → 영어표현", "count": 2},
        3: {"name": "Wave 3", "desc": "영어문장 → 한글해석", "count": 2},
        4: {"name": "Wave 4 FINAL", "desc": "한글해석 → 영어문장", "count": 2},
    }
    cfg = WAVE_CFG.get(wave, WAVE_CFG[4])
    q_per_wave = cfg["count"]

    # 전체 진행 인덱스
    global_idx = (wave - 1) * 2 + widx
    total_qs = 8  # 4웨이브 × 2문제

    # 문제 풀 준비
    if "sg_sv_pool" not in st.session_state:
        pool = voca_data.copy()
        random.shuffle(pool)
        while len(pool) < 8:
            pool += voca_data.copy()
        st.session_state.sg_sv_pool = pool[:8]

    sv_pool = st.session_state.sg_sv_pool

    # 클리어 / 사망 판정
    if dead:
        st.session_state.sg_phase = "survival_result"; st.rerun()
    if wave > 4:
        st.session_state.sg_phase = "survival_result"; st.rerun()

    q_item = sv_pool[global_idx] if global_idx < len(sv_pool) else sv_pool[-1]

    # ── UI ──
    wave_colors = {1: "#44cc88", 2: "#ffcc00", 3: "#ff8844", 4: "#ff4466"}
    wc = wave_colors.get(wave, "#ff4466")

    sv_header = f'<div style="background:linear-gradient(180deg,#181850,#2c2068);border:2.5px solid {wc};border-radius:22px;padding:14px;text-align:center;">'
    sv_header += f'<div style="font-size:2rem;font-weight:900;color:{wc};">🌊 {cfg["name"]}</div>'
    sv_header += f'<div style="font-size:1rem;color:#aaa;font-weight:700;">{cfg["desc"]}</div>'
    sv_header += '<div style="font-size:0.7rem;color:#555;">v8</div>'
    sv_header += '</div>'
    st.markdown(sv_header, unsafe_allow_html=True)

    # 진행 바
    prog_pct = int(global_idx / total_qs * 100)
    st.markdown(f'<div style="background:#2a2a50;border-radius:10px;padding:3px;margin:6px 0;"><div style="background:linear-gradient(90deg,#44cc88,{wc});height:10px;border-radius:8px;width:{prog_pct}%;"></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;font-size:1rem;color:#888;font-weight:700;">{global_idx}/{total_qs}</div>', unsafe_allow_html=True)

    # ── 문제 출제 (웨이브별) ──
    expr_text = q_item.get("expr", "")
    meaning = q_item.get("meaning", "")
    sentences = q_item.get("sentences", [])
    kr_text = q_item.get("kr", meaning)
    first_en = sentences[0] if sentences else expr_text
    kr_first = kr_text.split(". ")[0] + "." if ". " in kr_text else kr_text

    if wave == 1:
        # 영어표현 → 한글뜻
        q_display = f'<div style="border-radius:20px;padding:1.8rem 1.4rem;margin:10px 0;text-align:center;background:linear-gradient(145deg,#124028,#185535,#124028);border:2.5px solid rgba(68,204,136,0.7);box-shadow:0 0 40px rgba(68,204,136,0.3);animation:slideUp 0.4s ease-out;"><div style="font-size:1rem;font-weight:800;letter-spacing:3px;text-transform:uppercase;color:rgba(68,204,136,0.75);margin-bottom:8px;">what does this mean?</div><div style="font-size:3.5rem;font-weight:900;line-height:1.3;color:#88ffbb;">{expr_text}</div></div>'
        correct_ans = meaning
        others = [v.get("meaning","") for v in voca_data if v.get("meaning","") != meaning]
    elif wave == 2:
        # 한글뜻 → 영어표현
        q_display = f'<div style="border-radius:20px;padding:1.8rem 1.4rem;margin:10px 0;text-align:center;background:linear-gradient(145deg,#3e3210,#4a3c15,#3e3210);border:2.5px solid rgba(255,204,0,0.7);box-shadow:0 0 40px rgba(255,204,0,0.3);animation:slideUp 0.4s ease-out;"><div style="font-size:1rem;font-weight:800;letter-spacing:3px;text-transform:uppercase;color:rgba(255,204,0,0.75);margin-bottom:8px;">영어 표현은?</div><div style="font-size:3.5rem;font-weight:900;line-height:1.3;color:#ffee88;">{meaning}</div></div>'
        correct_ans = expr_text
        others = [v.get("expr","") for v in voca_data if v.get("expr","") != expr_text]
    elif wave == 3:
        # 영어문장 → 한글해석
        q_display = f'<div style="border-radius:20px;padding:1.8rem 1.4rem;margin:10px 0;text-align:center;background:linear-gradient(145deg,#3e2810,#4a3215,#3e2810);border:2.5px solid rgba(255,136,68,0.7);box-shadow:0 0 40px rgba(255,136,68,0.3);animation:slideUp 0.4s ease-out;"><div style="font-size:1rem;font-weight:800;letter-spacing:3px;text-transform:uppercase;color:rgba(255,136,68,0.75);margin-bottom:10px;">translate this sentence</div><div style="font-size:2.5rem;font-weight:900;line-height:1.6;color:#ffddaa;text-align:left;">{first_en}</div></div>'
        correct_ans = kr_first
        others = []
        for v in voca_data:
            if v.get("expr","") != expr_text:
                vkr = v.get("kr", v.get("meaning",""))
                vkr_first = vkr.split(". ")[0] + "." if ". " in vkr else vkr
                if vkr_first != correct_ans:
                    others.append(vkr_first)
    else:
        # 한글해석 → 영어문장
        q_display = f'<div style="border-radius:20px;padding:1.8rem 1.4rem;margin:10px 0;text-align:center;background:linear-gradient(145deg,#3e1a2a,#4a2235,#3e1a2a);border:2.5px solid rgba(255,68,102,0.7);box-shadow:0 0 40px rgba(255,68,102,0.3);animation:slideUp 0.4s ease-out;"><div style="font-size:1rem;font-weight:800;letter-spacing:3px;text-transform:uppercase;color:rgba(255,68,102,0.75);margin-bottom:10px;">영어 문장은?</div><div style="font-size:2.5rem;font-weight:900;line-height:1.6;color:#ffbbcc;text-align:left;">{kr_first}</div></div>'
        correct_ans = first_en
        others = []
        for v in voca_data:
            if v.get("expr","") != expr_text:
                vs = v.get("sentences", [])
                if vs and vs[0] != correct_ans:
                    others.append(vs[0])

    st.markdown(q_display, unsafe_allow_html=True)

    # ── 비슷한 첫 글자 오답 생성 (Wave 1,2) ──
    def similar_distractors(ans, pool, count=3):
        """같은 첫 글자 → 같은 길이 순으로 비슷한 오답 선택"""
        if not ans:
            return pool[:count]
        first_ch = ans[0].lower()
        ans_len = len(ans)
        # 같은 첫 글자 우선
        same_first = [w for w in pool if w and w[0].lower() == first_ch and w != ans]
        # 길이 비슷한 순 정렬
        same_first.sort(key=lambda w: abs(len(w) - ans_len))
        result = same_first[:count]
        # 부족하면 길이 비슷한 다른 단어로 채움
        if len(result) < count:
            rest = [w for w in pool if w != ans and w not in result]
            rest.sort(key=lambda w: abs(len(w) - ans_len))
            result += rest[:count - len(result)]
        return result[:count]

    if wave in (1, 2):
        distractors = similar_distractors(correct_ans, others, 3)
    else:
        # Wave 3,4: 정답 문장 끝부분만 바꿔서 비슷한 오답
        def make_similar_sentences(correct, others_pool, count=3):
            import random as _rnd2
            result = []
            words = correct.split()
            is_korean = any('\uac00' <= ch <= '\ud7a3' for ch in correct)
            if len(words) >= 4:
                for o in others_pool:
                    ow = o.split()
                    if len(ow) >= 3:
                        # 정답 앞부분 + 다른 문장 뒷부분
                        cut = max(2, len(words) - 2)
                        fake = ' '.join(words[:cut]) + ' ' + ' '.join(ow[-2:])
                        if fake != correct and fake not in result:
                            result.append(fake)
                    if len(result) >= count:
                        break
            # 부족하면 기존 others
            for o in others_pool:
                if o != correct and o not in result:
                    result.append(o)
                if len(result) >= count:
                    break
            return result[:count]
        distractors = make_similar_sentences(correct_ans, others, 3)

    fallback_pool = ["implement","approximately","eligible","comprehensive","완전히 가동되다","자금을 확보하다","~에 집중하다","추가 비용 없이"]
    while len(distractors) < 3:
        for fb in fallback_pool:
            if fb != correct_ans and fb not in distractors:
                distractors.append(fb)
                break
        else:
            break

    rng = random.Random(hash(f"sv_{wave}_{widx}_{correct_ans}"))
    choices = distractors[:3] + [correct_ans]
    rng.shuffle(choices)
    correct_idx = choices.index(correct_ans)
    labeled = [f"({chr(65+i)}) {c}" for i, c in enumerate(choices)]

    # ── 틀렸을 때 브리핑 모드 체크 ──
    wave_wrong = st.session_state.get("sg_wave_wrong_review", None)

    if wave_wrong and wave_wrong.get("wave") == wave and wave_wrong.get("widx") == widx:
        # 브리핑 노트 표시 (선택지 대신!)
        wr = wave_wrong
        st.markdown(f'<div style="text-align:center;font-size:2rem;font-weight:900;color:#ff5555;margin:8px 0;">❌ 오답!</div>', unsafe_allow_html=True)

        # 브리핑 노트
        note_border = "rgba(255,100,100,0.6)"
        note_bg = "linear-gradient(145deg,#1a1235,#221540,#1a1235)"
        note = f'<div style="background:{note_bg};border:2.5px solid {note_border};border-radius:20px;padding:1.5rem;margin:10px 0;box-shadow:0 0 25px rgba(255,100,100,0.15);">'
        note += f'<div style="font-size:1.5rem;font-weight:800;letter-spacing:3px;color:rgba(255,150,150,0.8);margin-bottom:10px;">📝 REVIEW NOTE</div>'
        note += f'<div style="font-size:1.9rem;color:#ff8888;font-weight:800;margin-bottom:8px;">내 선택: <span style="text-decoration:line-through;opacity:0.7;">{wr["my_ans"]}</span></div>'
        note += f'<div style="font-size:2.2rem;color:#55ffaa;font-weight:900;margin-bottom:12px;">✅ 정답: {wr["correct_ans"]}</div>'
        note += f'<div style="border-top:1px solid rgba(255,255,255,0.1);padding-top:12px;margin-top:8px;">'
        note += f'<div style="font-size:2.5rem;font-weight:900;color:#88bbff;margin-bottom:6px;">📖 {wr["expr"]}</div>'
        note += f'<div style="font-size:2rem;color:#aaa;font-weight:700;margin-bottom:6px;">뜻: {wr["meaning"]}</div>'
        if wr.get("sentence"):
            import re as _re2
            _hl_sent = wr["sentence"]
            _hl_expr = wr["expr"]
            _matched = False
            if _hl_expr:
                # 1차: 정확한 매칭
                if _hl_expr.lower() in _hl_sent.lower():
                    try:
                        _hl_sent = _re2.sub(f"(?i)({_re2.escape(_hl_expr)})", '<mark style="background:none;color:#ffffff;font-weight:900;padding:0 2px;border-bottom:4px solid #ffe066;text-decoration:none;position:relative;display:inline;background-image:linear-gradient(#ffe066,#ffe066);background-size:0% 4px;background-position:left bottom;background-repeat:no-repeat;animation:hlDraw 0.8s ease-out 0.3s forwards;border-bottom:none;">\\1</mark>', _hl_sent)
                        _matched = True
                    except: pass
                # 2차: 어근 매칭 (첫 4글자 이상 공통)
                if not _matched:
                    _words = _hl_expr.split()
                    for _w in _words:
                        if len(_w) >= 4:
                            _stem = _w[:min(len(_w)-1, 5)]
                            try:
                                _hl_sent = _re2.sub(f"(?i)(\\b{_re2.escape(_stem)}\\w*)", '<mark style="background:none;color:#ffffff;font-weight:900;padding:0 2px;border-bottom:4px solid #ffe066;text-decoration:none;position:relative;display:inline;background-image:linear-gradient(#ffe066,#ffe066);background-size:0% 4px;background-position:left bottom;background-repeat:no-repeat;animation:hlDraw 0.8s ease-out 0.3s forwards;border-bottom:none;">\\1</mark>', _hl_sent, count=1)
                            except: pass
            note += f'<div style="font-size:1.9rem;color:#ccddff;font-weight:600;line-height:1.6;margin-top:8px;padding:14px;background:rgba(100,140,255,0.08);border-radius:12px;">💬 {_hl_sent}</div>'
        if wr.get("kr"):
            note += f'<div style="font-size:1.7rem;color:#aabbcc;font-weight:600;margin-top:4px;padding:0 10px;">→ {wr["kr"]}</div>'
        note += '</div></div>'
        st.markdown(note, unsafe_allow_html=True)

        # 다음 문제 버튼
        if st.button("▶ 다음 문제", key=f"wave_next_{wave}_{widx}", type="primary", use_container_width=True):
            st.session_state.sg_wave_wrong_review = None
            new_widx = widx + 1
            if new_widx >= q_per_wave:
                st.session_state.sg_wave = wave + 1
                st.session_state.sg_wave_idx = 0
            else:
                st.session_state.sg_wave_idx = new_widx
            st.rerun()
    else:
        # 일반 선택지 표시
        for i, ch in enumerate(labeled):
            if st.button(ch, key=f"sv_{wave}_{widx}_{i}", type="secondary", use_container_width=True):
                if i == correct_idx:
                    results.append(True)
                    st.session_state.sg_wave_results = results
                    # 맞추면 바로 다음 문제!
                    st.session_state.sg_wave_wrong_review = None
                    new_widx = widx + 1
                    if new_widx >= q_per_wave:
                        st.session_state.sg_wave = wave + 1
                        st.session_state.sg_wave_idx = 0
                    else:
                        st.session_state.sg_wave_idx = new_widx
                    st.rerun()
                else:
                    results.append(False)
                    st.session_state.sg_wave_results = results
                    # 틀리면 브리핑 노트 표시! (다음 문제로 안 넘어감)
                    st.session_state.sg_wave_wrong_review = {
                        "wave": wave, "widx": widx,
                        "my_ans": choices[i], "correct_ans": correct_ans,
                        "expr": expr_text, "meaning": meaning,
                        "sentence": first_en if sentences else "",
                        "kr": kr_first if kr_text else ""
                    }
                    st.rerun()

    _wc_map = {1:"68,204,136", 2:"255,204,0", 3:"255,136,68", 4:"255,68,102"}
    _rgb = _wc_map.get(wave, "255,68,102")
    components.html(f"""<script>
    function stW(){{const d=window.parent.document;d.querySelectorAll('button[kind="secondary"]').forEach(b=>{{const t=(b.textContent||'').trim();if(/^\([A-D]\)/.test(t)){{b.style.cssText='background:linear-gradient(135deg,rgba({_rgb},0.25),rgba({_rgb},0.12))!important;color:#ffffff!important;border:2px solid rgba({_rgb},0.5)!important;border-radius:16px!important;font-size:1.8rem!important;font-weight:900!important;padding:0.85rem 1rem!important;min-height:auto!important;box-shadow:0 3px 15px rgba('+'{_rgb}'+',0.15)!important;';b.querySelectorAll('p').forEach(p=>p.style.cssText='font-size:1.8rem!important;font-weight:900!important;');}}}});}};setTimeout(stW,80);setTimeout(stW,300);setTimeout(stW,700);new MutationObserver(stW).observe(window.parent.document.body,{{childList:true,subtree:true}});
    </script>""", height=0)

# ════════════════════════════════
# 서바이벌 결과
# ════════════════════════════════
elif st.session_state.sg_phase == "survival_result":
    wave = st.session_state.get("sg_wave", 1)
    results = st.session_state.get("sg_wave_results", [])
    ok_cnt = sum(results)
    total_answered = len(results)
    cleared = wave > 4

    if cleared and ok_cnt == total_answered:
        st.markdown('''<div style="text-align:center;padding:1.5rem;">
            <div style="font-size:3.5rem;font-weight:900;color:#ffcc00;text-shadow:0 0 30px #ffaa00;">🏆 PERFECT! 🏆</div>
            <div style="font-size:1.5rem;color:#ffdd44;font-weight:800;margin-top:8px;">4 웨이브 전부 정답!</div>
        </div>''', unsafe_allow_html=True)
    elif cleared:
        st.markdown(f'''<div style="text-align:center;padding:1.5rem;">
            <div style="font-size:3.5rem;font-weight:900;color:#44ff88;text-shadow:0 0 30px #00ff66;">🎉 CLEAR! 🎉</div>
            <div style="font-size:1.5rem;color:#88ffbb;font-weight:800;margin-top:8px;">4 웨이브 클리어!</div>
        </div>''', unsafe_allow_html=True)
    else:
        st.markdown(f'''<div style="text-align:center;padding:1.5rem;">
            <div style="font-size:3.5rem;font-weight:900;color:#ff8800;text-shadow:0 0 20px #ff6600;">🌊 FINISH 🌊</div>
        </div>''', unsafe_allow_html=True)

    st.markdown(f'<div style="text-align:center;font-size:1.5rem;color:#ccc;font-weight:700;">✅ {ok_cnt}/{total_answered} 정답</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🌊 재도전", key="sv_retry", type="primary", use_container_width=True):
            st.session_state.sg_wave = 1; st.session_state.sg_wave_idx = 0
            st.session_state.sg_wave_results = []; st.session_state.sg_wave_dead = False
            st.session_state.sg_wave_start = time.time()
            if "sg_sv_pool" in st.session_state: del st.session_state.sg_sv_pool
            if "sg_wave_start" in st.session_state: del st.session_state.sg_wave_start
            st.session_state.sg_phase = "survival"; st.rerun()
    with c2:
        if st.button("🔥 콤보러시", key="sv_combo", type="secondary", use_container_width=True):
            st.session_state.sg_combo_score = 0; st.session_state.sg_combo_count = 0
            st.session_state.sg_combo_idx = 0; st.session_state.sg_combo_start = time.time()
            st.session_state.sg_combo_over = False
            if "sg_combo_pool" in st.session_state: del st.session_state.sg_combo_pool
            st.session_state.sg_phase = "combo_rush"; st.rerun()
    with c3:
        if st.button("📦 저장고", key="sv_back", type="secondary", use_container_width=True):
            st.session_state.sg_phase = "lobby"; st.rerun()

# ════════════════════════════════
# VOCA 콤보 러시 — 33초 타임폭탄 시험!
# ════════════════════════════════
elif st.session_state.sg_phase == "combo_rush":
    st_autorefresh(interval=1000, limit=40, key="combo_timer")

    if "sg_combo_score" not in st.session_state: st.session_state.sg_combo_score = 0
    if "sg_combo_count" not in st.session_state: st.session_state.sg_combo_count = 0
    if "sg_combo_idx" not in st.session_state: st.session_state.sg_combo_idx = 0
    if "sg_combo_over" not in st.session_state: st.session_state.sg_combo_over = False

    score = st.session_state.sg_combo_score
    combo = st.session_state.sg_combo_count
    cidx = st.session_state.sg_combo_idx
    total_qs = min(10, len(voca_data))

    # 문제 풀 준비
    if "sg_combo_pool" not in st.session_state:
        pool = voca_data.copy()
        random.shuffle(pool)
        while len(pool) < 10:
            pool += voca_data.copy()
        st.session_state.sg_combo_pool = pool[:10]
    c_pool = st.session_state.sg_combo_pool

    # 종료 판정
    if cidx >= total_qs or st.session_state.sg_combo_over:
        st.session_state.sg_phase = "combo_result"; st.rerun()

    q_item = c_pool[cidx]

    # 통합 33초 타이머
    elapsed = time.time() - st.session_state.sg_combo_start
    rem = max(0, 33 - int(elapsed))
    left = total_qs - cidx
    if rem <= 0:
        st.session_state.sg_combo_over = True
        st.session_state.sg_phase = "combo_result"; st.rerun()

    # 배경 붉어짐 (움직임 없음!)
    if rem <= 5:
        bg_css = "background:linear-gradient(135deg,#2a0808,#3a0a1a 30%,#2a0510 70%,#2a0808)!important;"
        tcl = "#ff0000"; tsz = "5rem"; tglow = "text-shadow:0 0 40px #ff0000,0 0 80px #cc0000;"
        twarn = '<div style="text-align:center;font-size:1.4rem;color:#ff0000;font-weight:900;margin-top:4px;">💀💀 폭발한다!! 💀💀</div>'
    elif rem <= 10:
        bg_css = "background:linear-gradient(135deg,#1e0815,#2e0a25 30%,#1e0818 70%,#1e0815)!important;"
        tcl = "#ff2200"; tsz = "4rem"; tglow = "text-shadow:0 0 25px #ff2200,0 0 50px #ff0000;"
        twarn = '<div style="text-align:center;font-size:1.1rem;color:#ff4444;font-weight:900;">💀 서둘러!! 💀</div>'
    elif rem <= 15:
        bg_css = "background:linear-gradient(135deg,#160a1e,#220e30 30%,#160a22 70%,#160a1e)!important;"
        tcl = "#ff6600"; tsz = "3.2rem"; tglow = "text-shadow:0 0 15px #ff6600;"
        twarn = '<div style="text-align:center;font-size:1rem;color:#ff8844;font-weight:900;">⚡ 서둘러!! ⚡</div>'
    elif rem <= 20:
        bg_css = "background:linear-gradient(135deg,#121530,#1e1845 30%,#121838 70%,#121530)!important;"
        tcl = "#ffaa00"; tsz = "2.8rem"; tglow = "text-shadow:0 0 8px #ffaa00;"
        twarn = ""
    else:
        bg_css = ""; tcl = "#44ff88"; tsz = "2.4rem"; tglow = ""; twarn = ""
    tpct = int(rem / 33 * 100)
    q_border = "rgba(255,50,50,0.6)" if rem <= 10 else "rgba(255,136,0,0.7)"
    if bg_css:
        st.markdown(f'<style>.stApp{{{bg_css}}}</style>', unsafe_allow_html=True)

    # ── 헤더 ──
    combo_color = "#44ff88" if combo < 3 else "#ffcc00" if combo < 6 else "#ff4444"
    if combo >= 8:
        combo_color = "#ff00ff"
    combo_text = f"{combo}x" if combo > 0 else "0x"

    header = '<div style="background:linear-gradient(180deg,#0a0a1a,#1a1030);border:2.5px solid #ff8800;border-radius:22px;padding:12px;text-align:center;">'
    header += '<div style="font-size:2rem;font-weight:900;color:#ff8800;">🔥 COMBO RUSH</div>'
    header += f'<div style="display:flex;justify-content:space-around;margin-top:6px;">'
    header += f'<span style="font-size:1.3rem;font-weight:900;color:{combo_color};">🔥 {combo_text}</span>'
    header += f'<span style="font-size:1.3rem;font-weight:900;color:#ffcc00;">⭐ {score}</span>'
    header += f'<span style="font-size:1.3rem;font-weight:900;color:#aaa;">{cidx+1}/{total_qs}</span>'
    header += '</div></div>'
    st.markdown(header, unsafe_allow_html=True)

    # 타이머 UI
    st.markdown(f'<div style="text-align:center;margin:8px 0;padding:10px;"><span style="font-size:{tsz};font-weight:900;color:{tcl};font-family:Impact,Arial Black,sans-serif;{tglow}">{rem}</span><span style="font-size:1.5rem;color:{tcl};opacity:0.7;">s</span><div style="font-size:1rem;color:#888;font-weight:700;margin-top:4px;">Q{cidx+1}/{total_qs} · 남은 {left}문제</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background:rgba(255,255,255,0.06);border-radius:12px;padding:3px;margin:4px 0;"><div style="background:linear-gradient(90deg,{tcl},#ff8800);height:12px;border-radius:10px;width:{tpct}%;"></div></div>', unsafe_allow_html=True)
    if twarn:
        st.markdown(twarn, unsafe_allow_html=True)

    # ── 문제 유형 랜덤 ──
    expr_text = q_item.get("expr", "")
    meaning = q_item.get("meaning", "")
    sentences = q_item.get("sentences", [])
    kr_text = q_item.get("kr", meaning)
    first_en = sentences[0] if sentences else expr_text
    kr_first = kr_text.split(". ")[0] + "." if ". " in kr_text else kr_text

    q_types = ["expr2meaning", "meaning2expr"]
    if sentences:
        q_types.append("blank_fill")
    qtype_rng = random.Random(hash(f"qt_{cidx}"))
    qtype = qtype_rng.choice(q_types)

    if qtype == "expr2meaning":
        # 영어표현 → 한글뜻
        st.markdown(f'<div style="border-radius:20px;padding:1.8rem 1.4rem;margin:10px 0;text-align:center;background:linear-gradient(145deg,#3e2810,#4a3415,#3e2810);border:2.5px solid rgba(255,136,0,0.7);box-shadow:0 0 40px rgba(255,136,0,0.35);animation:slideUp 0.4s ease-out;"><div style="font-size:1rem;font-weight:800;letter-spacing:3px;text-transform:uppercase;color:rgba(255,136,0,0.75);margin-bottom:8px;">what does this mean?</div><div style="font-size:3.5rem;font-weight:900;line-height:1.3;color:#ffcc88;">{expr_text}</div></div>', unsafe_allow_html=True)
        correct_ans = meaning
        others = [v.get("meaning","") for v in voca_data if v.get("meaning","") != meaning]

    elif qtype == "meaning2expr":
        # 한글뜻 → 영어표현
        st.markdown(f'<div style="border-radius:20px;padding:1.8rem 1.4rem;margin:10px 0;text-align:center;background:linear-gradient(145deg,#3e2810,#4a3415,#3e2810);border:2.5px solid rgba(255,136,0,0.7);box-shadow:0 0 40px rgba(255,136,0,0.35);animation:slideUp 0.4s ease-out;"><div style="font-size:1rem;font-weight:800;letter-spacing:3px;text-transform:uppercase;color:rgba(255,136,0,0.75);margin-bottom:8px;">영어 표현은?</div><div style="font-size:3.5rem;font-weight:900;line-height:1.3;color:#ffcc88;">{meaning}</div></div>', unsafe_allow_html=True)
        correct_ans = expr_text
        others = [v.get("expr","") for v in voca_data if v.get("expr","") != expr_text]

    else:
        # 빈칸 채우기
        import re as _re
        expr_words = expr_text.split()
        key_word = max(expr_words, key=len) if expr_words else expr_text
        blank_sent = _re.sub(r'(?i)\b' + _re.escape(key_word) + r'\b', "_______", first_en, count=1)
        if "_______" not in blank_sent:
            blank_sent = first_en.replace(expr_text, "_______", 1)
        if "_______" not in blank_sent:
            blank_sent = f"The company will _______ by next quarter."

        blank_styled = blank_sent.replace("_______", '<span style="border-bottom:3px solid #ff8800;padding:0 8px;color:#ffaa44;">_______</span>')
        st.markdown(f'<div style="border-radius:20px;padding:1.8rem 1.4rem;margin:10px 0;text-align:center;background:linear-gradient(145deg,#3e2810,#4a3415,#3e2810);border:2.5px solid rgba(255,136,0,0.7);box-shadow:0 0 40px rgba(255,136,0,0.35);animation:slideUp 0.4s ease-out;"><div style="font-size:1rem;font-weight:800;letter-spacing:3px;text-transform:uppercase;color:rgba(255,136,0,0.75);margin-bottom:10px;">fill in the blank</div><div style="font-size:2.5rem;font-weight:900;line-height:1.6;color:#ffddaa;text-align:left;">{blank_styled}</div></div>', unsafe_allow_html=True)
        correct_ans = key_word
        fallback_words = ["implement","approximately","eligible","comprehensive","facilitate","preliminary","mandatory","subsequent","operational","sustainable"]
        others = [w for w in fallback_words if w.lower() != key_word.lower()]

    # 선택지
    rng2 = random.Random(hash(f"cb_{cidx}_{correct_ans}"))
    rng2.shuffle(others)
    distractors = others[:3]
    while len(distractors) < 3:
        distractors.append("N/A")
    choices = distractors + [correct_ans]
    rng2.shuffle(choices)
    correct_idx = choices.index(correct_ans)
    labeled = [f"({chr(65+i)}) {c}" for i, c in enumerate(choices)]

    for i, ch in enumerate(labeled):
        if st.button(ch, key=f"cb_{cidx}_{i}", type="secondary", use_container_width=True):
            if i == correct_idx:
                new_combo = combo + 1
                bonus = 100 * new_combo
                st.session_state.sg_combo_count = new_combo
                st.session_state.sg_combo_score = score + bonus
                st.session_state.sg_combo_idx = cidx + 1
                st.rerun()
            else:
                # 틀리면 즉사! YOU LOST!
                st.session_state.sg_combo_over = True
                st.session_state.sg_phase = "combo_result"; st.rerun()

    components.html("""<script>
    function stC(){const d=window.parent.document;d.querySelectorAll('button[kind="secondary"]').forEach(b=>{const t=(b.textContent||'').trim();if(/^\([A-D]\)/.test(t)){b.style.cssText='background:linear-gradient(135deg,rgba(255,136,0,0.22),rgba(255,136,0,0.10))!important;color:#ffffff!important;border:1.5px solid rgba(255,136,0,0.5)!important;border-radius:16px!important;font-size:1.8rem!important;font-weight:900!important;padding:0.85rem 1rem!important;min-height:auto!important;box-shadow:0 3px 15px rgba('+'{_rgb}'+',0.15)!important;';b.querySelectorAll('p').forEach(p=>p.style.cssText='font-size:1.8rem!important;font-weight:900!important;');}});};setTimeout(stC,80);setTimeout(stC,300);setTimeout(stC,700);new MutationObserver(stC).observe(window.parent.document.body,{childList:true,subtree:true});
    </script>""", height=0)

# ════════════════════════════════
# 콤보 러시 결과
# ════════════════════════════════
elif st.session_state.sg_phase == "combo_result":
    score = st.session_state.get("sg_combo_score", 0)
    combo = st.session_state.get("sg_combo_count", 0)
    cidx = st.session_state.get("sg_combo_idx", 0)

    # 최고점수 저장
    best = storage.get("combo_best", 0)
    new_record = score > best
    if new_record:
        storage["combo_best"] = score
        save_storage(storage)

    if new_record:
        st.markdown(f'''<div style="text-align:center;padding:1.5rem;">
            <div style="font-size:3rem;font-weight:900;color:#ffcc00;text-shadow:0 0 30px #ffaa00;">🏆 NEW RECORD! 🏆</div>
            <div style="font-size:2.5rem;font-weight:900;color:#fff;margin-top:8px;">⭐ {score}</div>
        </div>''', unsafe_allow_html=True)
    else:
        st.markdown(f'''<div style="text-align:center;padding:1.5rem;">
            <div style="font-size:3rem;font-weight:900;color:#ff8800;text-shadow:0 0 20px #ff6600;">🔥 FINISH! 🔥</div>
            <div style="font-size:2.5rem;font-weight:900;color:#fff;margin-top:8px;">⭐ {score}</div>
            <div style="font-size:1.2rem;color:#888;font-weight:700;margin-top:4px;">최고기록: ⭐ {max(best, score)}</div>
        </div>''', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔥 재도전", key="cb_retry", type="primary", use_container_width=True):
            st.session_state.sg_combo_score = 0; st.session_state.sg_combo_count = 0
            st.session_state.sg_combo_idx = 0; st.session_state.sg_combo_start = time.time()
            st.session_state.sg_combo_over = False
            if "sg_combo_pool" in st.session_state: del st.session_state.sg_combo_pool
            st.session_state.sg_phase = "combo_rush"; st.rerun()
    with c2:
        if st.button("🌊 웨이브", key="cb_wave", type="secondary", use_container_width=True):
            st.session_state.sg_wave = 1; st.session_state.sg_wave_idx = 0
            st.session_state.sg_wave_results = []; st.session_state.sg_wave_dead = False
            st.session_state.sg_wave_start = time.time()
            if "sg_sv_pool" in st.session_state: del st.session_state.sg_sv_pool
            if "sg_wave_start" in st.session_state: del st.session_state.sg_wave_start
            st.session_state.sg_phase = "survival"; st.rerun()
    with c3:
        if st.button("📦 저장고", key="cb_back", type="secondary", use_container_width=True):
            st.session_state.sg_phase = "lobby"; st.rerun()

