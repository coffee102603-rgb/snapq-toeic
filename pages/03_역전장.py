"""통합 역전장 — P5 학습/시험 + VOCA 학습/시험"""
import streamlit as st
import streamlit.components.v1 as components
import json, os, random, time, re
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="🔥 역전장", page_icon="🔥", layout="wide", initial_sidebar_state="collapsed")

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
.stApp{background:#000000!important;color:#e8e8f0!important;}
@keyframes cardPulse{0%,100%{box-shadow:0 0 20px rgba(var(--glow-rgb),0.1)}50%{box-shadow:0 0 35px rgba(var(--glow-rgb),0.25)}}
@keyframes slideUp{from{opacity:0;transform:translateY(15px)}to{opacity:1;transform:translateY(0)}}
@keyframes choiceFade{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:translateX(0)}}\n@keyframes highlightDraw{from{width:0}to{width:100%}}\n@keyframes hlDraw{from{background-size:0% 4px}to{background-size:100% 4px}}
section[data-testid="stSidebar"]{display:none!important;}
header[data-testid="stHeader"]{background:transparent!important;}
.block-container{padding-top:0.7rem!important;padding-bottom:1rem!important;max-width:100%!important;padding-left:1rem!important;padding-right:1rem!important;}
div[data-testid="stSidebarNav"]{display:none!important;}
div[data-testid="stNavigation"]{display:none!important;}
section[data-testid="stSidebar"]{display:none!important;}
div[data-testid="stVerticalBlock"]>div{gap:0.1rem;}
@keyframes rb{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}

button[kind="primary"]{background:#000000!important;color:#fff!important;border:2px solid #ff4444!important;border-radius:14px!important;font-size:1.0rem!important;font-weight:900!important;padding:0.4rem 0.6rem!important;}
button[kind="primary"] p{font-size:1.0rem!important;font-weight:900!important;text-align:center!important;}
button[kind="secondary"]{background:#000000!important;color:#fff!important;border:2px solid #4488ff!important;border-radius:14px!important;font-size:1.0rem!important;font-weight:900!important;padding:0.4rem 0.6rem!important;}
button[kind="secondary"] p{font-size:1.0rem!important;font-weight:900!important;text-align:center!important;}

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
.sg-rmt{max-width:95vw;margin:0 auto;background:#000000;
    border-radius:32px;padding:24px 16px 16px 16px;border:3px solid #ffd700;
    box-shadow:0 8px 40px rgba(255,215,0,0.2);text-align:center;}
.sg-rmt-t{font-size:1.4rem;font-weight:900;
    background:linear-gradient(90deg,#ffd700,#ffffff,#ffd700);
    background-size:300% 300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
    animation:rb 4s ease infinite;letter-spacing:2px;}
.sg-nag{background:#000000;border:2px solid #ffd700;border-radius:18px;padding:14px;margin:12px 0;text-align:center;}
.sg-nag-t{font-size:1.0rem;font-weight:900;color:#ffd700;text-shadow:0 0 12px rgba(255,215,0,0.4);}
.sg-zn{border-radius:18px;padding:14px;margin:12px 0 6px 0;text-align:center;}
.sg-zl{font-size:1.1rem;font-weight:900;letter-spacing:4px;text-transform:uppercase;}

/* 로비 4개 카드 버튼 공통 */
div[data-testid="column"] button[kind="primary"],
div[data-testid="column"] button[kind="secondary"]{
    min-height:60px!important;
    height:auto!important;
    white-space:pre-line!important;
    font-size:1.0rem!important;
    font-weight:900!important;
    line-height:1.4!important;
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
    padding:0.5rem 0.5rem!important;
    box-sizing:border-box!important;
    word-break:keep-all!important;
}
div[data-testid="column"] button[kind="primary"] p,
div[data-testid="column"] button[kind="secondary"] p{
    white-space:pre-line!important;
    font-size:1.0rem!important;
    font-weight:900!important;
    line-height:1.4!important;
    text-align:center!important;
    word-break:keep-all!important;
    overflow-wrap:break-word!important;
    margin:0!important;
    padding:0 4px!important;
}

/* ══════════════════════════════════
   반응형 — 태블릿 (768px 이하)
══════════════════════════════════ */
@media(max-width:768px){
    .block-container{padding-top:0.5rem!important;padding-bottom:2rem!important;padding-left:0.6rem!important;padding-right:0.6rem!important;}
    button[kind="primary"],button[kind="secondary"]{font-size:1.5rem!important;padding:0.6rem 0.8rem!important;}
    button[kind="primary"] p,button[kind="secondary"] p{font-size:1.5rem!important;}
    div[data-testid="column"] button[kind="primary"],
    div[data-testid="column"] button[kind="secondary"]{min-height:150px!important;font-size:1.3rem!important;}
    div[data-testid="column"] button[kind="primary"] p,
    div[data-testid="column"] button[kind="secondary"] p{font-size:1.3rem!important;}
    .sg-rmt-t{font-size:2rem!important;}
    .sg-nag-t{font-size:1.2rem!important;}
    .sg-zl{font-size:1.3rem!important;}
    .note-sent{font-size:1.4rem!important;line-height:2!important;}
    .note-hl{font-size:1.5rem!important;}
    .note-kr{font-size:1.2rem!important;}
    .note-ex{font-size:1.1rem!important;}
    .exam-q{font-size:1.7rem!important;}
}

/* ══════════════════════════════════
   반응형 — 모바일 (480px 이하)
══════════════════════════════════ */
@media(max-width:480px){
    .block-container{padding-top:0.3rem!important;padding-bottom:1.5rem!important;padding-left:0.4rem!important;padding-right:0.4rem!important;}
    button[kind="primary"],button[kind="secondary"]{font-size:1.2rem!important;padding:0.5rem 0.6rem!important;border-radius:12px!important;}
    button[kind="primary"] p,button[kind="secondary"] p{font-size:1.2rem!important;}
    div[data-testid="column"] button[kind="primary"],
    div[data-testid="column"] button[kind="secondary"]{min-height:60px!important;font-size:1.1rem!important;padding:1rem 0.6rem!important;}
    div[data-testid="column"] button[kind="primary"] p,
    div[data-testid="column"] button[kind="secondary"] p{font-size:1.1rem!important;line-height:1.6!important;}
    .sg-rmt{padding:16px 10px 12px!important;border-radius:22px!important;}
    .sg-rmt-t{font-size:1.6rem!important;letter-spacing:1px!important;}
    .sg-nag-t{font-size:1.1rem!important;}
    .sg-zl{font-size:1.1rem!important;letter-spacing:2px!important;}
    .note{padding:1rem 0.8rem!important;}
    .note-sent{font-size:1.2rem!important;line-height:1.9!important;}
    .note-hl{font-size:1.3rem!important;}
    .note-kr{font-size:1.05rem!important;}
    .note-ex{font-size:0.95rem!important;}
    .exam{padding:1.2rem 1rem!important;}
    .exam-q{font-size:1.4rem!important;line-height:1.7!important;}
}

/* ══════════════════════════════════
   반응형 — 초소형 (360px 이하)
══════════════════════════════════ */
@media(max-width:360px){
    div[data-testid="column"] button[kind="primary"],
    div[data-testid="column"] button[kind="secondary"]{min-height:100px!important;font-size:1rem!important;}
    div[data-testid="column"] button[kind="primary"] p,
    div[data-testid="column"] button[kind="secondary"] p{font-size:1rem!important;}
    .sg-rmt-t{font-size:1.3rem!important;}
    .note-sent{font-size:1.1rem!important;}
    .exam-q{font-size:1.2rem!important;}
}
</style>""", unsafe_allow_html=True)

# ═══ 세션 ═══
for k,v in {"sg_phase":"lobby","sg_idx":0,"sg_mode":None,"rv_battle":None,"rv_mode":None,
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
    combo_best = storage.get("combo_best", 0)
    combo_label = f"⭐{combo_best}" if combo_best > 0 else "—"

    # 뮤지컬 CSS
    st.markdown("""<style>
    @keyframes fireGlow{0%,100%{text-shadow:0 0 20px #ff8800,0 0 40px #ff4400;}50%{text-shadow:0 0 35px #ffd700,0 0 60px #ff8800;}}
    @keyframes stageIn{from{opacity:0;transform:translateY(25px);}to{opacity:1;transform:translateY(0);}}
    @keyframes firePulse{0%,100%{box-shadow:0 0 25px rgba(255,136,0,0.5),0 0 50px rgba(255,68,0,0.2);}50%{box-shadow:0 0 45px rgba(255,215,0,0.9),0 0 80px rgba(255,136,0,0.5);}}
    @keyframes nagFade{0%{opacity:0;transform:translateY(8px)}100%{opacity:1;transform:translateY(0)}}

    .rv-title{text-align:center;padding:16px 8px 6px 8px;}
    .rv-title h1{font-size:2.4rem;font-weight:900;letter-spacing:6px;color:#ffd700;animation:fireGlow 2.5s ease infinite;margin:0;}
    .rv-title p{font-size:0.85rem;color:#664400;letter-spacing:3px;margin:4px 0 0 0;}

    .rv-stage{animation:stageIn 0.5s ease;border-radius:20px;padding:18px 12px;margin:8px 0;}
    .rv-stage-1{background:linear-gradient(145deg,#0a0500,#150900);border:2px solid rgba(255,136,0,0.6);box-shadow:0 0 20px rgba(255,136,0,0.1);}
    .rv-stage-2p5{background:linear-gradient(145deg,#0a0000,#180500);border:2px solid rgba(255,68,0,0.6);box-shadow:0 0 20px rgba(255,68,0,0.1);}
    .rv-stage-2p7{background:linear-gradient(145deg,#080500,#150a00);border:2px solid rgba(255,170,0,0.6);box-shadow:0 0 20px rgba(255,170,0,0.1);}
    .rv-stage-3{background:linear-gradient(145deg,#0a0600,#1a0800);border:2px solid rgba(255,215,0,0.7);box-shadow:0 0 30px rgba(255,215,0,0.15);}

    .rv-act{font-size:0.7rem;font-weight:900;letter-spacing:4px;margin-bottom:8px;text-align:center;}
    .rv-act-1{color:#ff8800;}
    .rv-act-2p5{color:#ff4400;}
    .rv-act-2p7{color:#ffaa00;}
    .rv-act-3{color:#ffd700;}

    .rv-msg{font-size:1.25rem;font-weight:900;color:#fff;text-align:center;line-height:1.5;margin-bottom:12px;}
    .rv-msg .fire{color:#ff8800;}
    .rv-msg .gold{color:#ffd700;}
    .rv-msg .red{color:#ff4444;}
    .rv-msg .cyan{color:#00ffcc;}

    .rv-confirmed{text-align:center;padding:6px;margin-bottom:8px;}
    .rv-confirmed span{font-size:1rem;color:#ffd700;font-weight:900;background:rgba(255,136,0,0.15);padding:5px 14px;border-radius:20px;border:1px solid rgba(255,136,0,0.5);}

    @keyframes rvshake{0%,100%{transform:translateY(0);}20%{transform:translateY(-9px);}50%{transform:translateY(-3px);}75%{transform:translateY(-7px);}90%{transform:translateY(-1px);}}
    @keyframes rvblaze{0%,100%{box-shadow:0 0 15px rgba(255,136,0,0.3);}50%{box-shadow:0 0 60px rgba(255,210,0,1),0 0 120px rgba(255,80,0,0.7);border-color:rgba(255,235,0,1)!important;}}
    button[kind="secondary"]{
        background:#080300!important;border:2px solid rgba(255,136,0,0.7)!important;
        border-radius:14px!important;font-size:1.3rem!important;font-weight:900!important;
        padding:14px 8px!important;color:#e0e0e0!important;min-height:64px!important;
        animation:rvshake 1.6s ease-in-out infinite,rvblaze 1.9s ease-in-out infinite!important;
    }
    button[kind="secondary"] p{font-size:1.3rem!important;font-weight:900!important;white-space:pre-line!important;line-height:1.3!important;text-align:center!important;}

    button[data-testid="stBaseButton-primary"]{
        background:linear-gradient(135deg,#3a1500,#7a2a00,#aa4400)!important;
        border:3px solid #ffd700!important;font-size:1.6rem!important;font-weight:900!important;
        padding:1.2rem!important;color:#ffd700!important;border-radius:16px!important;
        animation:firePulse 1.5s ease infinite!important;
        text-shadow:0 0 10px rgba(255,215,0,0.8)!important;
    }
    #MainMenu{visibility:hidden!important;}header[data-testid="stHeader"]{height:0!important;visibility:hidden!important;}div[data-testid="stToolbar"]{visibility:hidden!important;}.block-container{padding-top:0.2rem!important;}
    </style>""", unsafe_allow_html=True)

    # 타이틀
    st.markdown('''<div class="rv-title">
        <h1>🔥 역 전 장</h1>
        <p>패배는 없다 · 역전만 있을 뿐이다</p>
    </div>''', unsafe_allow_html=True)

    # 나긴 멘트 애니메이션
    nag = random.choice(NAGGING)
    nag_words = nag.split()
    nag_spans = ""
    for i, w in enumerate(nag_words):
        delay = i * 0.4
        nag_spans += f'<span style="opacity:0;animation:nagFade 0.5s ease {delay}s forwards;font-size:1.6rem;font-weight:900;color:#ff8800;">{w} </span>'
    components.html(f"""
    <style>@keyframes nagFade{{0%{{opacity:0;transform:translateY(8px)}}100%{{opacity:1;transform:translateY(0)}}}}</style>
    <div style="text-align:center;padding:8px 0 12px 0;background:transparent;">{nag_spans}</div>
    """, height=60)

    _rv_battle = st.session_state.get("rv_battle", None)   # "p5" or "p7"
    _rv_mode = st.session_state.get("rv_mode", None)       # "p5s","p5e","p7s","p7e"

    # ━━━ 1막: 전장 선택 ━━━
    if not _rv_battle:
        st.markdown('''<div class="rv-stage rv-stage-1">
            <div class="rv-act rv-act-1">🎬 1 막 · 돌아갈 전장을 선택하라!</div>
            <div class="rv-msg">틀린 적이 있다면,<br><span class="fire">아직 끝나지 않았다!</span></div>
        </div>''', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⚔️\nP5 전장\n문법의 전쟁", key="rv_p5", type="secondary", use_container_width=True):
                st.session_state.rv_battle = "p5"; st.rerun()
        with c2:
            if st.button("📖\nP7 전장\n독해의 전쟁", key="rv_p7", type="secondary", use_container_width=True):
                st.session_state.rv_battle = "p7"; st.rerun()

    # ━━━ 2막 P5: 전투 방식 선택 ━━━
    elif _rv_battle == "p5" and not _rv_mode:
        st.markdown('''<div class="rv-confirmed"><span>⚔️ P5 전장 귀환!</span></div>''', unsafe_allow_html=True)
        st.markdown('''<div class="rv-stage rv-stage-2p5">
            <div class="rv-act rv-act-2p5">🎬 2 막 · 전투 방식을 선택하라!</div>
            <div class="rv-msg"><span class="red">새기며 익히느냐</span><br>실전으로 <span class="gold">증명하느냐!</span><br><span style="font-size:1rem;color:#888;">선택이 곧 너의 무기다</span></div>
        </div>''', unsafe_allow_html=True)
        if st.button(f"😤  P5 학습모드\n틀린 문제, 이번엔 완전히 박살! ({len(p5_data)}문제)", key="rv_p5s", type="secondary", use_container_width=True):
            if p5_data:
                st.session_state.rv_mode="p5s"; st.session_state.sg_phase="p5_study"; st.session_state.sg_idx=0; st.rerun()
            else: st.warning("P5 저장 문제 없음!")
        if st.button(f"🔥  P5 시험모드\n이번엔 절대 안 틀린다, 증명하라! 🏆{p5_rate}", key="rv_p5e", type="secondary", use_container_width=True):
            if len(p5_data) >= 5:
                import random as _r
                qs = _r.sample(p5_data, 5)
                st.session_state.sg_exam_qs=qs; st.session_state.sg_exam_idx=0
                st.session_state.sg_exam_results=[]; st.session_state.sg_exam_start=time.time()
                st.session_state.sg_exam_wrong=False; st.session_state.rv_mode="p5e"
                st.session_state.sg_phase="p5_exam"; st.rerun()
            else: st.warning("최소 5문제 필요!")
        if st.button("↩ 전장 다시 선택", key="rv_back1", use_container_width=True):
            st.session_state.rv_battle=None; st.rerun()

    # ━━━ 2막 P7: 전투 방식 선택 ━━━
    elif _rv_battle == "p7" and not _rv_mode:
        st.markdown('''<div class="rv-confirmed"><span>📖 P7 전장 귀환!</span></div>''', unsafe_allow_html=True)
        st.markdown('''<div class="rv-stage rv-stage-2p7">
            <div class="rv-act rv-act-2p7">🎬 2 막 · 전투 방식을 선택하라!</div>
            <div class="rv-msg"><span class="gold">어휘를 새기느냐</span><br>어휘로 <span class="fire">싸우느냐!</span><br><span style="font-size:1rem;color:#888;">단어 하나가 점수 하나다</span></div>
        </div>''', unsafe_allow_html=True)
        if st.button(f"🧠  P7 어휘 학습모드\n단어를 완전히 내 몸에 새겨라! ({len(voca_data)}단어)", key="rv_p7s", type="secondary", use_container_width=True):
            if len(voca_data) >= 3:
                st.session_state.sg_wave=1; st.session_state.sg_wave_idx=0
                st.session_state.sg_wave_results=[]; st.session_state.sg_wave_dead=False
                st.session_state.sg_wave_start=time.time()
                if "sg_sv_pool" in st.session_state: del st.session_state.sg_sv_pool
                if "sg_wave_start" in st.session_state: del st.session_state.sg_wave_start
                st.session_state.rv_mode="p7s"; st.session_state.sg_phase="survival"; st.rerun()
            else: st.warning("최소 3단어 필요!")
        if st.button(f"💪  P7 어휘 시험모드\n진짜 내 것이 됐는지 증명하라! {combo_label}", key="rv_p7e", type="secondary", use_container_width=True):
            if len(voca_data) >= 3:
                st.session_state.sg_combo_score=0; st.session_state.sg_combo_count=0
                st.session_state.sg_combo_idx=0; st.session_state.sg_combo_start=time.time()
                st.session_state.sg_combo_over=False
                if "sg_combo_pool" in st.session_state: del st.session_state.sg_combo_pool
                st.session_state.rv_mode="p7e"; st.session_state.sg_phase="combo_rush"; st.rerun()
            else: st.warning("최소 3단어 필요!")
        if st.button("↩ 전장 다시 선택", key="rv_back2", use_container_width=True):
            st.session_state.rv_battle=None; st.rerun()

    # ━━━ 항상 고정 네비게이션 ━━━
    st.markdown('<div style="font-size:0.7rem;color:#331100;text-align:center;letter-spacing:3px;margin-top:16px;padding-top:12px;border-top:1px solid #1a0800;">N A V I G A T E</div>', unsafe_allow_html=True)
    mn1, mn2, mn3 = st.columns(3)
    with mn1:
        if st.button("⚔️ P5전장", key="sg_nav1", type="secondary", use_container_width=True):
            st.session_state.phase="lobby"; st.session_state._p5_active=False
            st.switch_page("pages/02_P5_Arena.py")
    with mn2:
        if st.button("📖 P7전장", key="sg_nav2", type="secondary", use_container_width=True):
            st.switch_page("pages/04_P7_Reading.py")
    with mn3:
        if st.button("🏠 메인", key="sg_nav3", type="secondary", use_container_width=True):
            st.switch_page("main_hub.py")
    import streamlit.components.v1 as _cmp
    _cmp.html("""<script>
    (function(){
        function styleNavBtns(){
            var doc=window.parent.document;
            var rows=doc.querySelectorAll('[data-testid="stHorizontalBlock"]');
            if(!rows.length) return;
            var lastRow=rows[rows.length-1];
            var btns=lastRow.querySelectorAll('button');
            btns.forEach(function(b){
                b.style.setProperty('animation','none','important');
                b.style.setProperty('transform','none','important');
                b.style.setProperty('border','1.5px solid rgba(255,255,255,0.4)','important');
                b.style.setProperty('background','#030303','important');
                b.style.setProperty('box-shadow','none','important');
                b.style.setProperty('color','#ccc','important');
            });
        }
        setTimeout(styleNavBtns,150);setTimeout(styleNavBtns,500);setTimeout(styleNavBtns,1200);
        var ob=new MutationObserver(function(){setTimeout(styleNavBtns,100);});
        ob.observe(window.parent.document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['style']});
    })();
    </script>""", height=0)

    with st.expander("⚠️ 역전장 관리"):
        if st.button("🗑 P5 전체 삭제", key="del_p5"):
            storage["saved_questions"] = []; save_storage(storage); st.rerun()
        if st.button("🗑 VOCA 전체 삭제", key="del_voca"):
            storage["saved_expressions"] = []; save_storage(storage); st.rerun()
        if st.button("🗑 시험 기록 초기화", key="del_rec"):
            storage["p5_exam_record"] = {"wins":0,"total":0}
            storage["voca_exam_record"] = {"wins":0,"total":0}
            save_storage(storage); st.rerun()


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
        if st.button("🔥 역전장", key="back_exam", type="secondary", use_container_width=True):
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
        1: {"name": "1전 · 뜻, 내가 먼저 안다!", "desc": "영어표현 → 한글뜻", "count": 2},
        2: {"name": "2전 · 표현, 내 입으로 말한다!", "desc": "한글뜻 → 영어표현", "count": 2},
        3: {"name": "3전 · 문장, 눈으로 꿰뚫는다!", "desc": "영어문장 → 한글해석", "count": 2},
        4: {"name": "4전 · 완전정복 · 마지막이다!", "desc": "한글해석 → 영어문장", "count": 2},
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
    wave_icons={1:'🧠',2:'🧠',3:'💥',4:'🏆'}
    wi=wave_icons.get(wave,'🏆')
    sv_header += f'<div style="font-size:2rem;font-weight:900;color:{wc};">{wi} {cfg["name"]}</div>'
    sv_header += f'<div style="font-size:1rem;color:#aaa;font-weight:700;">{cfg["desc"]}</div>'
    
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
        def make_kr_distractors(correct_kr, count=3):
            result = []
            swap_map = {
                "개발": ["판매","구축","운영","폐기","축소"],
                "집중": ["중단","포기","전환","확대","지원"],
                "집중할": ["중단할","포기할","전환할","확대할"],
                "발표": ["철회","수정","취소","연기","검토"],
                "지지": ["반대","비판","거부","철회","검토"],
                "완료": ["중단","취소","연기","실패","포기"],
                "시작": ["중단","완료","취소","연기","포기"],
                "증가": ["감소","유지","하락","축소","정체"],
                "확보": ["상실","반환","포기","실패","축소"],
                "가동": ["중단","폐쇄","축소","매각","정지"],
                "제공": ["철회","중단","거부","취소","제한"],
                "열": ["닫","취소","연기","폐쇄"],
                "지속 가능한": ["재생 가능한","친환경적인","효율적인"],
                "새로운": ["기존의","낡은"],
                "강력히": ["약하게","소극적으로"],
            }
            for orig, replacements in swap_map.items():
                if orig in correct_kr:
                    for rep in replacements:
                        fake = correct_kr.replace(orig, rep, 1)
                        if fake != correct_kr and fake not in result:
                            result.append(fake)
                        if len(result) >= count:
                            break
                if len(result) >= count:
                    break
            if len(result) < count:
                for v in voca_data:
                    if v.get("expr","") != expr_text:
                        vkr = v.get("kr", v.get("meaning",""))
                        vkr_f = vkr.split(". ")[0] + "." if ". " in vkr else vkr
                        if vkr_f != correct_kr and vkr_f not in result:
                            result.append(vkr_f)
                    if len(result) >= count:
                        break
            return result[:count]
        others = make_kr_distractors(correct_ans, 3)
    else:
        # 한글해석 → 영어문장
        q_display = f'<div style="border-radius:20px;padding:1.8rem 1.4rem;margin:10px 0;text-align:center;background:linear-gradient(145deg,#3e1a2a,#4a2235,#3e1a2a);border:2.5px solid rgba(255,68,102,0.7);box-shadow:0 0 40px rgba(255,68,102,0.3);animation:slideUp 0.4s ease-out;"><div style="font-size:1rem;font-weight:800;letter-spacing:3px;text-transform:uppercase;color:rgba(255,68,102,0.75);margin-bottom:10px;">영어 문장은?</div><div style="font-size:2.5rem;font-weight:900;line-height:1.6;color:#ffbbcc;text-align:left;">{kr_first}</div></div>'
        correct_ans = first_en
        # Wave4: 고유명사/날짜/숫자 고정, 핵심 동사만 교체해서 오답 생성
        def make_en_distractors(correct_en, count=3):
            import re as _re5
            result = []
            # 핵심 동사/표현 교체 쌍
            verb_swaps = [
                ("is due by", "must be paid by"),
                ("is due by", "should be submitted by"),
                ("is due by", "needs to be settled by"),
                ("must be paid", "is required by"),
                ("will focus on", "will concentrate on"),
                ("will focus on", "will work toward"),
                ("will focus on", "will shift away from"),
                ("has announced", "has reported"),
                ("has announced", "has canceled"),
                ("has announced", "has delayed"),
                ("announced plans to open", "announced plans to close"),
                ("announced plans to open", "announced plans to expand"),
                ("announced plans to open", "announced plans to relocate"),
                ("is pleased to inform", "regrets to inform"),
                ("is pleased to inform", "would like to confirm"),
                ("approved", "rejected"),
                ("approved", "suspended"),
                ("approved", "under review for"),
                ("will be held", "has been canceled"),
                ("will be held", "has been postponed"),
                ("is eligible for", "is not eligible for"),
                ("is eligible for", "may apply for"),
                ("are required to", "are encouraged to"),
                ("are required to", "are not required to"),
                ("will increase", "will decrease"),
                ("will increase", "is expected to remain"),
                ("has been completed", "has been delayed"),
                ("has been completed", "has been suspended"),
            ]
            words_en = correct_en.lower()
            for orig, rep in verb_swaps:
                if orig.lower() in words_en:
                    # 대소문자 유지하면서 교체
                    import re as _re6
                    fake = _re6.sub(re.escape(orig), rep, correct_en, count=1, flags=re.IGNORECASE)
                    if fake != correct_en and fake not in result:
                        result.append(fake)
                if len(result) >= count:
                    break
            # 부족하면 다른 카드 문장에서 채우기 (fallback)
            if len(result) < count:
                for v in voca_data:
                    if v.get("expr","") != expr_text:
                        vs = v.get("sentences", [])
                        if vs and vs[0] != correct_en and vs[0] not in result:
                            result.append(vs[0])
                    if len(result) >= count:
                        break
            return result[:count]
        others = make_en_distractors(correct_ans, 3)

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
        note += f'<div style="font-size:1.5rem;color:#ff8888;font-weight:800;margin-bottom:8px;">내 선택: <span style="text-decoration:line-through;opacity:0.7;">{wr["my_ans"]}</span></div>'
        
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
            note += '<div style="font-size:1.1rem;font-weight:800;letter-spacing:2px;color:#88bbff;margin-top:12px;margin-bottom:4px;">[정답]</div>'
            if wave == 4:
                note += f'<div style="font-size:2.3rem;color:#ccddff;font-weight:700;line-height:1.6;margin-top:4px;padding:14px;background:rgba(100,140,255,0.08);border-radius:12px;">{_hl_sent}</div>'
            # Wave 3: 영어문장 위에 이미 보임 → 표시 안 함
        if wr.get("kr"):
            if wave == 3:
                note += f'<div style="font-size:2.0rem;color:#aabbcc;font-weight:600;margin-top:4px;padding:0 10px;">→ {wr["kr"]}</div>'
            # Wave 4: 한글문장 위에 이미 보임 → 표시 안 함>'
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
            <div style="font-size:3.5rem;font-weight:900;color:#ffcc00;text-shadow:0 0 30px #ffaa00;">🏆 완전정복! 🏆</div>
            <div style="font-size:1.5rem;color:#ffdd44;font-weight:800;margin-top:8px;">4전 전부 완벽 정답! 진짜 내 것이 됐다!</div>
        </div>''', unsafe_allow_html=True)
    elif cleared:
        st.markdown(f'''<div style="text-align:center;padding:1.5rem;">
            <div style="font-size:3.5rem;font-weight:900;color:#44ff88;text-shadow:0 0 30px #00ff66;">🎉 정복 완료! 🎉</div>
            <div style="font-size:1.5rem;color:#88ffbb;font-weight:800;margin-top:8px;">4전 모두 돌파! 단어가 내 것이 됐다!</div>
        </div>''', unsafe_allow_html=True)
    else:
        st.markdown(f'''<div style="text-align:center;padding:1.5rem;">
            <div style="font-size:3.5rem;font-weight:900;color:#ff8800;text-shadow:0 0 20px #ff6600;">💥 여기까지! 💥</div>
        </div>''', unsafe_allow_html=True)

    st.markdown(f'<div style="text-align:center;font-size:1.5rem;color:#ccc;font-weight:700;">✅ {ok_cnt}/{total_answered} 정답</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🧠 다시 밟고\n완전정복!", key="sv_retry", type="primary", use_container_width=True):
            st.session_state.sg_wave = 1; st.session_state.sg_wave_idx = 0
            st.session_state.sg_wave_results = []; st.session_state.sg_wave_dead = False
            st.session_state.sg_wave_start = time.time()
            if "sg_sv_pool" in st.session_state: del st.session_state.sg_sv_pool
            if "sg_wave_start" in st.session_state: del st.session_state.sg_wave_start
            st.session_state.sg_phase = "survival"; st.rerun()
    with c2:
        if st.button("💪 진짜 됐는지\n덤벼봐!", key="sv_combo", type="secondary", use_container_width=True):
            st.session_state.sg_combo_score = 0; st.session_state.sg_combo_count = 0
            st.session_state.sg_combo_idx = 0; st.session_state.sg_combo_start = time.time()
            st.session_state.sg_combo_over = False
            if "sg_combo_pool" in st.session_state: del st.session_state.sg_combo_pool
            st.session_state.sg_phase = "combo_rush"; st.rerun()
    with c3:
        if st.button("🔥 역전장으로\n귀환", key="sv_back", type="secondary", use_container_width=True):
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
    header += '<div style="font-size:2rem;font-weight:900;color:#ff8800;">💪 P7 단어 · 덤벼봐, 틀리면 끝이다!</div>'
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
            <div style="font-size:3rem;font-weight:900;color:#ffcc00;text-shadow:0 0 30px #ffaa00;">🏆 신기록 달성! 🏆</div>
            <div style="font-size:2.5rem;font-weight:900;color:#fff;margin-top:8px;">⭐ {score}</div>
        </div>''', unsafe_allow_html=True)
    else:
        st.markdown(f'''<div style="text-align:center;padding:1.5rem;">
            <div style="font-size:3rem;font-weight:900;color:#ff8800;text-shadow:0 0 20px #ff6600;">💪 여기까지! 💪</div>
            <div style="font-size:2.5rem;font-weight:900;color:#fff;margin-top:8px;">⭐ {score}</div>
            <div style="font-size:1.2rem;color:#888;font-weight:700;margin-top:4px;">최고기록: ⭐ {max(best, score)}</div>
        </div>''', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💪 다시 덤벼,\n이번엔 안 진다!", key="cb_retry", type="primary", use_container_width=True):
            st.session_state.sg_combo_score = 0; st.session_state.sg_combo_count = 0
            st.session_state.sg_combo_idx = 0; st.session_state.sg_combo_start = time.time()
            st.session_state.sg_combo_over = False
            if "sg_combo_pool" in st.session_state: del st.session_state.sg_combo_pool
            st.session_state.sg_phase = "combo_rush"; st.rerun()
    with c2:
        if st.button("🧠 단계부터\n다시 밟는다!", key="cb_wave", type="secondary", use_container_width=True):
            st.session_state.sg_wave = 1; st.session_state.sg_wave_idx = 0
            st.session_state.sg_wave_results = []; st.session_state.sg_wave_dead = False
            st.session_state.sg_wave_start = time.time()
            if "sg_sv_pool" in st.session_state: del st.session_state.sg_sv_pool
            if "sg_wave_start" in st.session_state: del st.session_state.sg_wave_start
            st.session_state.sg_phase = "survival"; st.rerun()
    with c3:
        if st.button("🔥 역전장으로\n귀환", key="cb_back", type="secondary", use_container_width=True):
            st.session_state.sg_phase = "lobby"; st.rerun()

