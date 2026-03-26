"""통합 오답전장 — P5 학습/시험 + VOCA 학습/시험"""
import streamlit as st
import streamlit.components.v1 as components
import json, os, random, time, re
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="🔥 오답전장", page_icon="🔥", layout="wide", initial_sidebar_state="collapsed")
# ★★★ iOS Safari 세션 가드 — WebSocket 끊겨도 세션 자동 복원 ★★★
_qs_nick = st.query_params.get("nick", "")
_qs_ag   = st.query_params.get("ag", "")
if _qs_nick and _qs_ag == "1":
    if not st.session_state.get("access_granted"):
        st.session_state["battle_nickname"] = _qs_nick
        st.session_state["nickname"]        = _qs_nick
        st.session_state["access_granted"]  = True
        st.session_state["_code_verified"]  = True
        st.session_state["_id_verified"]    = True
    st.query_params.clear()


# ★ 공유 반응형 CSS (iOS Safari 수정 + PC 글씨 확대)
import sys as _sys
_sys.path.insert(0, os.path.dirname(__file__))
from _responsive_css import inject_css as _inject_css
_inject_css()

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
    # voca_data 단어만 빈칸 후보로 사용 (정답 보장)
    voca_words = set()
    for v in voca_data:
        for w in v.get("expr","").split():
            voca_words.add(w.strip(".,;:!?\'\"").lower())
    candidates = [(i,w) for i,w in candidates if w.strip(".,;:!?\'\"").lower() in voca_words]
    if not candidates: return None
    idx, target_word = random.choice(candidates)
    target_clean = target_word.strip(".,;:!?\'\"")
    new_words = words.copy()
    new_words[idx] = words[idx].replace(target_clean, "_______")
    new_text = " ".join(new_words).replace(" ,", ",").replace(" .", ".")
    # 오답도 voca_data 단어에서
    all_voca = []
    for v in voca_data:
        for w in v.get("expr","").split():
            cw = w.strip(".,;:!?\'\"")
            if len(cw) > 2 and cw.lower() != target_clean.lower() and cw not in all_voca:
                all_voca.append(cw)
    fallback = ["provide","maintain","require","consider","establish","develop","relevant","significant","appropriate","essential","available","potential"]
    for d in fallback:
        if d not in all_voca:
            all_voca.append(d)
    distractors = random.sample([d for d in all_voca if d.lower() != target_clean.lower()], min(3, len(all_voca)))
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
div[data-testid="stSidebarNav"] a span{font-weight:300!important;opacity:0.4!important;font-size:0.8rem!important;}
div[data-testid="stSidebarNav"] svg{display:none!important;}
header[data-testid="stHeader"]{background:transparent!important;}
.block-container{padding-top:0.2rem!important;padding-bottom:1rem!important;max-width:100%!important;padding-left:1rem!important;padding-right:1rem!important;}
div[data-testid="stSidebarNav"]{display:none!important;}
div[data-testid="stNavigation"]{display:none!important;}
section[data-testid="stSidebar"]{display:none!important;}
div[data-testid="stSidebarNav"] a span{font-weight:300!important;opacity:0.4!important;font-size:0.8rem!important;}
div[data-testid="stSidebarNav"] svg{display:none!important;}
div[data-testid="stVerticalBlock"]>div{gap:0rem;}
@keyframes rb{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}

button[kind="primary"]{background:#000000!important;color:#fff!important;border:2px solid #ff4444!important;border-radius:14px!important;font-size:1.0rem!important;font-weight:900!important;padding:0.4rem 0.6rem!important;}
button[kind="primary"] p{font-size:1.0rem!important;font-weight:900!important;text-align:center!important;}
button[kind="secondary"]{background:#000000!important;color:#fff!important;border:2px solid #4488ff!important;border-radius:14px!important;font-size:1.0rem!important;font-weight:900!important;padding:0.4rem 0.6rem!important;}
button[kind="secondary"] p{font-size:1.0rem!important;font-weight:900!important;text-align:center!important;}

/* 줄노트 */
.note{background:#fffef5;border-radius:12px;padding:1.5rem 1.2rem;margin:0.5rem 0;
    background-image:repeating-linear-gradient(transparent,transparent 39px,#e8e0c8 39px,#e8e0c8 40px);
    background-position:0 1.5rem;box-shadow:0 3px 15px rgba(0,0,0,0.2);border:1px solid #d8d0b8;min-height:200px;}
.note-sent{font-size:1.0rem;font-weight:700;color:#1a1a1a;line-height:1.6;margin:0.4rem 0;}
.note-hl{color:#008844;font-weight:900;font-size:1.0rem;text-decoration:underline;text-underline-offset:5px;text-decoration-thickness:3px;background:rgba(0,180,80,0.08);padding:0 4px;border-radius:4px;}
.note-kr{font-size:1.5rem;font-weight:600;color:#333;line-height:1.8;margin-bottom:0.5rem;}
.note-ex{font-size:1.3rem;color:#555;line-height:1.6;padding:0.5rem 0.8rem;background:rgba(255,180,0,0.1);border-left:4px solid #ffaa00;border-radius:0 8px 8px 0;}

/* 시험 */
.exam{background:#fff;border-radius:4px;padding:0.8rem 0.8rem;margin:0.2rem 0;box-shadow:0 2px 10px rgba(0,0,0,0.15);border:1px solid #ccc;font-family:'Times New Roman',serif;}
.exam-q{font-size:1.0rem;font-weight:900;color:#e8e8ff;line-height:1.5;margin:0.4rem 0;word-break:keep-all;}

/* 리모컨 */
.sg-rmt{max-width:95vw;margin:0 auto;background:#000000;
    border-radius:32px;padding:24px 16px 16px 16px;border:3px solid #ffd700;
    box-shadow:0 8px 40px rgba(255,215,0,0.2);text-align:center;}
.sg-rmt-t{font-size:1.12rem;font-weight:900;
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
    min-height:50px!important;
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
    button[kind="primary"],button[kind="secondary"]{font-size:1.0rem!important;padding:0.4rem 0.6rem!important;}
    button[kind="primary"] p,button[kind="secondary"] p{font-size:1.0rem!important;}
    div[data-testid="column"] button[kind="primary"],
    div[data-testid="column"] button[kind="secondary"]{min-height:50px!important;font-size:1.3rem!important;}
    div[data-testid="column"] button[kind="primary"] p,
    div[data-testid="column"] button[kind="secondary"] p{font-size:1.3rem!important;}
    .sg-rmt-t{font-size:1.6rem!important;}
    .sg-nag-t{font-size:1.2rem!important;}
    .sg-zl{font-size:1.3rem!important;}
    .note-sent{font-size:1.4rem!important;line-height:2!important;}
    .note-hl{font-size:1.5rem!important;}
    .note-kr{font-size:1.2rem!important;}
    .note-ex{font-size:1.1rem!important;}
    .exam-q{font-size:1.0rem!important;line-height:1.5!important;}
}

/* ══════════════════════════════════
   반응형 — 모바일 (480px 이하)
══════════════════════════════════ */
@media(max-width:480px){
    .block-container{padding-top:0.3rem!important;padding-bottom:1.5rem!important;padding-left:0.4rem!important;padding-right:0.4rem!important;}
    button[kind="primary"],button[kind="secondary"]{font-size:0.9rem!important;padding:0.3rem 0.4rem!important;border-radius:12px!important;}
    button[kind="primary"] p,button[kind="secondary"] p{font-size:0.9rem!important;}
    div[data-testid="column"] button[kind="primary"],
    div[data-testid="column"] button[kind="secondary"]{min-height:50px!important;font-size:1.1rem!important;padding:0.3rem 0.4rem!important;}
    div[data-testid="column"] button[kind="primary"] p,
    div[data-testid="column"] button[kind="secondary"] p{font-size:1.1rem!important;line-height:1.6!important;}
    .sg-rmt{padding:16px 10px 12px!important;border-radius:22px!important;}
    .sg-rmt-t{font-size:1.28rem!important;letter-spacing:1px!important;}
    .sg-nag-t{font-size:1.1rem!important;}
    .sg-zl{font-size:1.1rem!important;letter-spacing:2px!important;}
    .note{padding:1rem 0.8rem!important;}
    .note-sent{font-size:1.2rem!important;line-height:1.9!important;}
    .note-hl{font-size:1.3rem!important;}
    .note-kr{font-size:1.05rem!important;}
    .note-ex{font-size:0.95rem!important;}
    .exam{padding:1.2rem 1rem!important;}
    .exam-q{font-size:0.95rem!important;line-height:1.5!important;}
}

/* ══════════════════════════════════
   반응형 — 초소형 (360px 이하)
══════════════════════════════════ */
@media(max-width:360px){
    div[data-testid="column"] button[kind="primary"],
    div[data-testid="column"] button[kind="secondary"]{min-height:50px!important;font-size:1rem!important;}
    div[data-testid="column"] button[kind="primary"] p,
    div[data-testid="column"] button[kind="secondary"] p{font-size:1rem!important;}
    .sg-rmt-t{font-size:1.04rem!important;}
    .note-sent{font-size:1.1rem!important;}
    .exam-q{font-size:0.85rem!important;}
}

/* P5학습 버튼 강제 가로배치 */
@media (max-width: 768px) {
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        flex-direction: row !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        min-width: 0 !important;
        flex: 1 !important;
    }
}
</style>""", unsafe_allow_html=True)

# ═══ 세션 ═══
for k,v in {"sg_phase":"lobby","sg_idx":0,"sg_mode":None,"rv_battle":None,"rv_mode":None,
    "sg_exam_qs":[],"sg_exam_idx":0,"sg_exam_results":[],"sg_exam_start":None,"sg_exam_wrong":False,
    "sg_wave":1,"sg_wave_idx":0,"sg_wave_results":[],"sg_wave_start":None,"sg_wave_dead":False,
    "sg_combo_score":0,"sg_combo_count":0,"sg_combo_idx":0,"sg_combo_start":None,"sg_combo_over":False,
    "puzzle_blank_level":2,"puzzle_streak":0}.items():  # ★ 적응형 빈칸: level 1=1개 2=2개 3=3개
    if k not in st.session_state: st.session_state[k]=v

storage = load_storage()
p5_data = storage.get("saved_questions",[])
# session_state 우선, 없으면 파일에서
if "saved_expressions" in st.session_state:
    voca_data = st.session_state["saved_expressions"]
else:
    voca_data = storage.get("saved_expressions",[])
hall_of_fame = storage.get("hall_of_fame", [])

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
    .rv-title h1{font-size:1.5rem!important;font-size:3.2rem;font-weight:900;letter-spacing:6px;color:#ffd700;animation:fireGlow 2.5s ease infinite;margin:0;}
    .rv-title p{font-size:1.0rem;color:#ff8800;font-weight:900;letter-spacing:3px;margin:4px 0 0 0;}

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
        border:2px solid #ffd700!important;font-size:1.1rem!important;font-weight:900!important;
        padding:0.5rem!important;color:#ffffff!important;border-radius:12px!important;
        min-height:44px!important;max-height:44px!important;
        animation:none!important;
        text-shadow:none!important;
    }
    button[data-testid="stBaseButton-primary"] p{
        font-size:1.1rem!important;font-weight:900!important;color:#ffffff!important;
    }
    #MainMenu{visibility:hidden!important;}header[data-testid="stHeader"]{height:0!important;visibility:hidden!important;}div[data-testid="stToolbar"]{visibility:hidden!important;}.block-container{padding-top:0.1rem!important;margin-top:0!important;}div[data-testid="stAppViewBlockContainer"]{padding-top:0!important;}
    </style>""", unsafe_allow_html=True)

    # 타이틀 강화
    st.markdown('''<div style="text-align:center;padding:8px 0 4px 0;">
        <div style="font-size:1.8rem;font-weight:900;color:#ff9900;letter-spacing:5px;">🔥 오답전장</div>
        <div style="font-size:0.65rem;color:#ff8800;letter-spacing:3px;margin-top:2px;">TOEIC WRONG ANSWER ARENA</div>
        <div style="display:flex;align-items:center;justify-content:center;gap:8px;margin-top:4px;">
            <div style="height:1px;width:60px;background:linear-gradient(90deg,transparent,#ff6600);"></div>
            <div style="font-size:0.7rem;color:#ff6600;opacity:0.8;">틀린 문제가 무기가 된다 — 반복이 실력이다</div>
            <div style="height:1px;width:60px;background:linear-gradient(90deg,#ff6600,transparent);"></div>
        </div>
    </div>''', unsafe_allow_html=True)

    _rv_battle = st.session_state.get("rv_battle", None)
    _rv_mode = st.session_state.get("rv_mode", None)

    # ━━━ 1막: 전장 선택 ━━━
    if not _rv_battle:
        p5_save_cnt = len(p5_data)
        p7_weapon_cnt = len(voca_data)
        p5_rate_val = int(p5_rec["wins"]/p5_rec["total"]*100) if p5_rec["total"] > 0 else 0
        p5_rate_disp = f"{p5_rate_val}%" if p5_rec["total"] > 0 else "—"
        voca_rec = storage.get("voca_exam_record", {"wins":0,"total":0})
        p7_rate_val = int(voca_rec["wins"]/voca_rec["total"]*100) if voca_rec["total"] > 0 else 0
        p7_rate_disp = f"{p7_rate_val}%" if voca_rec["total"] > 0 else "—"
        avg_rate = int((p5_rate_val + p7_rate_val) / 2) if (p5_rec["total"] > 0 or voca_rec["total"] > 0) else 0

        st.markdown(f'''<div style="background:#12101a;border:1.5px solid #7766ff;border-radius:14px;padding:12px 10px 10px 10px;margin-bottom:10px;">
            <div style="text-align:center;font-size:0.75rem;font-weight:900;color:#aa99ff;letter-spacing:2px;margin-bottom:8px;">📊 나의 전투 기록</div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;text-align:center;gap:4px;border-bottom:1px solid #2a2a3a;padding-bottom:8px;">
                <div style="border-right:1px solid #2a2a3a;">
                    <div style="font-size:0.65rem;color:#aaa;margin-bottom:3px;">P5 정답률</div>
                    <div style="font-size:1.2rem;font-weight:900;color:#ffcc44;">{p5_rate_disp}</div>
                </div>
                <div style="border-right:1px solid #2a2a3a;">
                    <div style="font-size:0.65rem;color:#aaa;margin-bottom:3px;">P5 저장</div>
                    <div style="font-size:1.2rem;font-weight:900;color:#44aaff;">{p5_save_cnt}개</div>
                </div>
                <div style="border-right:1px solid #2a2a3a;">
                    <div style="font-size:0.65rem;color:#aaa;margin-bottom:3px;">P7 무기</div>
                    <div style="font-size:1.2rem;font-weight:900;color:#44aaff;">{p7_weapon_cnt}개</div>
                </div>
                <div>
                    <div style="font-size:0.65rem;color:#aaa;margin-bottom:3px;">P7 정답률</div>
                    <div style="font-size:1.2rem;font-weight:900;color:#ff8844;">{p7_rate_disp}</div>
                </div>
            </div>
            <div style="margin-top:8px;">
                <div style="background:#1a1a2a;border-radius:4px;height:6px;">
                    <div style="background:#7766ff;height:6px;border-radius:4px;width:{avg_rate}%;opacity:0.8;"></div>
                </div>
                <div style="text-align:right;font-size:0.65rem;color:#888;margin-top:2px;">총 전투력 {avg_rate}%</div>
            </div>
        </div>''', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('''<div style="background:#150505;border:2px solid #ff5533;border-radius:14px;overflow:hidden;margin-bottom:6px;">
                <div style="background:#2a0808;padding:6px;text-align:center;font-size:0.8rem;font-weight:900;color:#ff8866;letter-spacing:1px;">P5 오답전장</div>
                <div style="padding:14px 10px 10px 10px;text-align:center;">
                    <div style="font-size:2.2rem;">⚔️</div>
                    <div style="font-size:1.0rem;color:#ffcc99;margin-top:4px;font-weight:700;">문법 · 어휘</div>
                    <div style="font-size:0.8rem;color:#aaa;margin-top:2px;">틀린 문제 박살!</div>
                </div>
            </div>''', unsafe_allow_html=True)
            if st.button("출격!", key="rv_p5", type="primary", use_container_width=True):
                st.session_state.rv_battle = "p5"; st.rerun()
        with c2:
            st.markdown('''<div style="background:#05080f;border:2px solid #3388ff;border-radius:14px;overflow:hidden;margin-bottom:6px;">
                <div style="background:#081428;padding:6px;text-align:center;font-size:0.8rem;font-weight:900;color:#66aaff;letter-spacing:1px;">P7 오답전장</div>
                <div style="padding:14px 10px 10px 10px;text-align:center;">
                    <div style="font-size:2.2rem;">📖</div>
                    <div style="font-size:1.0rem;color:#aaddff;margin-top:4px;font-weight:700;">독해 · 무기 획득</div>
                    <div style="font-size:0.8rem;color:#aaa;margin-top:2px;">문장으로 무기 장착!</div>
                </div>
            </div>''', unsafe_allow_html=True)
            if st.button("출격!", key="rv_p7", type="primary", use_container_width=True):
                st.session_state.rv_battle = "p7"; st.rerun()

    # ━━━ 2막 P5: 전투 방식 선택 ━━━
    elif _rv_battle == "p5" and not _rv_mode:
        st.markdown('''<div style="text-align:center;margin-bottom:8px;">
            <span style="background:#2a1000;border:1.5px solid #ff6600;border-radius:12px;padding:5px 18px;font-size:0.9rem;font-weight:900;color:#ffaa44;">⚔️ P5 오답전장</span>
        </div>''', unsafe_allow_html=True)

        # 학습모드 카드
        # 학습모드 — 지붕 라벨 + 카드 + 버튼
        st.markdown('''<div style="display:flex;align-items:flex-end;margin-bottom:0;">
            <div style="background:#081a14;border:2px solid #22cc88;border-bottom:none;border-radius:8px 8px 0 0;padding:4px 14px;font-size:0.85rem;font-weight:900;color:#44ffaa;display:inline-block;">📖 학습모드</div>
        </div>''', unsafe_allow_html=True)
        _c1, _c2 = st.columns([3, 1])
        with _c1:
            st.markdown(f'''<div style="background:#081a14;border:2px solid #22cc88;border-top:none;border-radius:0 12px 12px 12px;padding:12px 14px;min-height:82px;">
                <div style="font-size:1.05rem;font-weight:900;color:#ffffff;letter-spacing:1px;">🗡️ 오답 격파</div>
                <div style="font-size:0.9rem;color:#55ffbb;margin-top:5px;font-weight:700;">틀린 문제만 골라 완전히 내 것으로!</div>
                <div style="font-size:0.78rem;color:#aaa;margin-top:3px;">{len(p5_data)}문제 · 해설 · 정답 확인</div>
            </div>''', unsafe_allow_html=True)
        with _c2:
            st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
            if st.button("▶\n시작", key="rv_p5s", use_container_width=True):
                if p5_data:
                    st.session_state.rv_mode="p5s"; st.session_state.sg_phase="p5_study"; st.session_state.sg_idx=0; st.rerun()
                else: st.warning("P5 저장 문제 없음!")

        # 시험모드 — 지붕 라벨 + 시한폭탄 배지 + 카드 + 버튼
        st.markdown('''<div style="display:flex;align-items:flex-end;margin-top:10px;margin-bottom:0;gap:4px;">
            <div style="background:#1a0800;border:2px solid #ff8800;border-bottom:none;border-radius:8px 8px 0 0;padding:4px 14px;font-size:0.85rem;font-weight:900;color:#ffaa44;display:inline-block;">⚡ 시험모드</div>
            <div style="background:#2a1000;border:2px solid #ff6600;border-bottom:none;border-radius:8px 8px 0 0;padding:4px 14px;font-size:0.8rem;font-weight:900;color:#ff8844;display:inline-block;">💣 33초 시한폭탄</div>
        </div>''', unsafe_allow_html=True)
        _c3, _c4 = st.columns([3, 1])
        with _c3:
            st.markdown(f'''<div style="background:#1a0800;border:2px solid #ff8800;border-top:none;border-radius:0 12px 12px 12px;padding:12px 14px;min-height:82px;">
                <div style="font-size:1.05rem;font-weight:900;color:#ffffff;letter-spacing:1px;">5문제 생존전투!</div>
                <div style="font-size:0.9rem;color:#ffdd66;margin-top:5px;font-weight:700;">못 맞추면 💥 폭파 — 살아남아라!</div>
                <div style="font-size:0.78rem;color:#aaa;margin-top:3px;">3개 이상 → 생존 · 최고 {p5_rate}</div>
            </div>''', unsafe_allow_html=True)
        with _c4:
            st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
            if st.button("💣\n도전", key="rv_p5e", use_container_width=True):
                if len(p5_data) >= 5:
                    import random as _r
                    qs = _r.sample(p5_data, 5)
                    st.session_state.sg_exam_qs=qs; st.session_state.sg_exam_idx=0
                    st.session_state.sg_exam_results=[]; st.session_state.sg_exam_start=time.time()
                    st.session_state.sg_exam_wrong=False; st.session_state.rv_mode="p5e"
                    st.session_state.sg_phase="p5_exam"; st.rerun()
                else: st.warning("최소 5문제 필요!")

        st.markdown('''<style>
        button[data-testid="stBaseButton-secondary"]{
            animation:none!important;transform:none!important;
            box-shadow:none!important;
            font-size:0.8rem!important;font-weight:500!important;
            min-height:32px!important;padding:4px!important;
            border:1px solid #444!important;color:#777!important;
        }
        button[data-testid="stBaseButton-secondary"] p{
            font-size:0.8rem!important;color:#777!important;
        }
        </style>''', unsafe_allow_html=True)
        st.markdown('<div style="margin-top:4px;"></div>', unsafe_allow_html=True)
        if st.button("↩ 돌아가기", key="rv_back1", use_container_width=True):
            st.session_state.rv_battle=None; st.rerun()

    # ━━━ 2막 P7: 전투 방식 선택 ━━━
    elif _rv_battle == "p7" and not _rv_mode:
        total_words = len(voca_data)
        st.markdown(f'''<div style="text-align:center;margin-bottom:8px;">
            <span style="background:#0a1428;border:1.5px solid #3388ff;border-radius:12px;padding:5px 18px;font-size:0.9rem;font-weight:900;color:#66aaff;">📖 P7 오답전장</span>
        </div>''', unsafe_allow_html=True)
        
        # 학습모드 지붕
        st.markdown('''<div style="display:flex;align-items:flex-end;margin-bottom:0;">
            <div style="background:#081a14;border:2px solid #22cc88;border-bottom:none;border-radius:8px 8px 0 0;padding:4px 14px;font-size:0.85rem;font-weight:900;color:#44ffaa;display:inline-block;">📖 학습모드</div>
        </div>''', unsafe_allow_html=True)
        _p7c1, _p7c2 = st.columns([3, 1])
        with _p7c1:
            st.markdown(f'''<div style="background:#081a14;border:2px solid #22cc88;border-top:none;border-radius:0 12px 12px 12px;padding:12px 14px;min-height:90px;">
                <div style="font-size:1.05rem;font-weight:900;color:#ffffff;">🗡️ 문장 격파</div>
                <div style="font-size:0.9rem;color:#55ffbb;margin-top:5px;font-weight:700;">한글 보고 → 영어 빈칸 채워라!</div>
                <div style="font-size:0.82rem;color:#cceecc;margin-top:3px;font-weight:600;">문장을 몸으로 익혀라!</div>
                <div style="font-size:0.72rem;color:#888;margin-top:2px;">{len(voca_data)}문장 · 퍼즐 배틀 · 3번 기회</div>
            </div>''', unsafe_allow_html=True)
        with _p7c2:
            st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
            if st.button("▶\n시작", key="rv_p7s", use_container_width=True):
                if len(voca_data) >= 3:
                    st.session_state.sg_wave=1; st.session_state.sg_wave_idx=0
                    st.session_state.sg_wave_results=[]; st.session_state.sg_wave_dead=False
                    st.session_state.sg_wave_start=time.time()
                    if "sg_sv_pool" in st.session_state: del st.session_state.sg_sv_pool
                    if "sg_wave_start" in st.session_state: del st.session_state.sg_wave_start
                    st.session_state.rv_mode="p7s"; st.session_state.sg_phase="survival"; st.rerun()
                else: st.warning("최소 3문장 필요!")

        # 시험모드 지붕
        st.markdown('''<div style="display:flex;align-items:flex-end;margin-top:10px;margin-bottom:0;gap:4px;">
            <div style="background:#1a0800;border:2px solid #ff8800;border-bottom:none;border-radius:8px 8px 0 0;padding:4px 14px;font-size:0.85rem;font-weight:900;color:#ffaa44;display:inline-block;">⚡ 시험모드</div>
            <div style="background:#2a1000;border:2px solid #ff6600;border-bottom:none;border-radius:8px 8px 0 0;padding:4px 14px;font-size:0.8rem;font-weight:900;color:#ff8844;display:inline-block;">💣 33초 시한폭탄</div>
        </div>''', unsafe_allow_html=True)
        _p7c3, _p7c4 = st.columns([3, 1])
        with _p7c3:
            st.markdown(f'''<div style="background:#1a0800;border:2px solid #ff8800;border-top:none;border-radius:0 12px 12px 12px;padding:12px 14px;min-height:90px;">
                <div style="font-size:1.05rem;font-weight:900;color:#ffffff;">5문제 생존전투!</div>
                <div style="font-size:0.9rem;color:#ffdd66;margin-top:5px;font-weight:700;">문장 속 빈칸 — 33초 안에 맞춰라!</div>
                <div style="font-size:0.82rem;color:#ffcc88;margin-top:3px;font-weight:600;">못 맞추면 💥 폭파 — 살아남아라!</div>
                <div style="font-size:0.72rem;color:#888;margin-top:2px;">3개 이상 → 생존 · 최고 {combo_label}</div>
            </div>''', unsafe_allow_html=True)
        with _p7c4:
            st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
            if st.button("💣\n도전", key="rv_p7e", use_container_width=True):
                if len(voca_data) >= 3:
                    st.session_state.sg_combo_score=0; st.session_state.sg_combo_count=0
                    st.session_state.sg_combo_idx=0; st.session_state.sg_combo_start=time.time()
                    st.session_state.sg_combo_over=False; st.session_state.sg_combo_results=[]
                    if "sg_combo_pool" in st.session_state: del st.session_state.sg_combo_pool
                    st.session_state.rv_mode="p7e"; st.session_state.sg_phase="combo_rush"; st.rerun()
                else: st.warning("최소 3문장 필요!")

        # 문장 무기고 — 오른쪽 버튼
        st.markdown('<div style="margin-top:10px;"></div>', unsafe_allow_html=True)
        _p7c5, _p7c6 = st.columns([3, 1])
        with _p7c5:
            st.markdown(f'''<div style="background:#0a0814;border:2px solid #7766ff;border-radius:12px;padding:12px 14px;min-height:64px;">
                <div style="font-size:1.05rem;font-weight:900;color:#ccbbff;">📦 문장 무기고</div>
                <div style="font-size:0.82rem;color:#aaa;margin-top:4px;font-weight:600;">보유 {total_words}개 · 불필요한 무기 제거</div>
            </div>''', unsafe_allow_html=True)
        with _p7c6:
            st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
            if st.button("📦 관리", key="rv_vault", use_container_width=True):
                st.session_state.rv_mode="p7_vault"; st.rerun()

    # ━━━ 항상 고정 네비게이션 ━━━
    if st.session_state.get("rv_mode") != "p7_vault":
        st.markdown('<div style="height:1px;background:#2a2a2a;margin:14px 0 10px 0;"></div>', unsafe_allow_html=True)
        st.markdown('''<style>
        div[data-testid="stHorizontalBlock"]:last-of-type button{
            font-size:0.8rem!important;
            font-weight:600!important;
            border:1.5px solid #666!important;
            background:#111!important;
            color:#aaa!important;
            min-height:36px!important;
            padding:4px!important;
        }
        div[data-testid="stHorizontalBlock"]:last-of-type button p{
            font-size:0.8rem!important;
            font-weight:600!important;
            color:#aaa!important;
        }
        </style>''', unsafe_allow_html=True)
        mn1, mn2, mn3 = st.columns(3)
        with mn1:
            if st.button("⚔️ P5전장", key="sg_nav1", use_container_width=True):
                for k in ["phase","cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx","br_saved"]: 
                    if k in st.session_state: del st.session_state[k]
                st.switch_page("pages/02_P5_Arena.py"); st.rerun()
        with mn2:
            if st.button("🏠 홈", key="sg_nav2", use_container_width=True):
                st.session_state.rv_mode=None; st.session_state.rv_battle=None
                _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
                if _nick:
                    st.query_params["nick"] = _nick
                    st.query_params["ag"] = "1"
                st.switch_page("main_hub.py")
        with mn3:
            if st.button("📖 P7전장", key="sg_nav3", use_container_width=True):
                st.session_state.rv_mode=None; st.session_state.rv_battle=None
                st.switch_page("pages/04_P7_Reading.py")
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



elif st.session_state.sg_phase == "p5_study":
    if not p5_data:
        st.warning("저장된 문제가 없습니다!")
        st.session_state.sg_phase = "lobby"; st.session_state.rv_battle = None; st.session_state.rv_mode = None; st.rerun()

    bi = st.session_state.sg_idx
    if bi >= len(p5_data): bi = len(p5_data)-1
    if bi < 0: bi = 0
    q = p5_data[bi]

    st.markdown('<div style="text-align:center;"><span style="font-size:1.5rem;font-weight:900;color:#44cc88;">📖 P5 학습모드</span></div>', unsafe_allow_html=True)

    ans = q["ch"][q["a"]]
    clean = ans.split(") ",1)[-1] if ") " in ans else ans
    sent = q["text"].replace("_______", f'<span class="note-hl">{clean}</span>')
    kr = q.get("kr","")
    exk = q.get("exk","")
    cat = q.get("cat","")

    # 진행바
    _prog = int((bi / max(len(p5_data),1)) * 100)
    st.markdown(f'''<div style="margin-bottom:6px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;">
            <span style="font-size:0.75rem;color:#4488ff;font-weight:700;">📖 P5 학습모드</span>
            <span style="font-size:0.75rem;color:#4488ff;font-weight:700;">{bi+1}/{len(p5_data)}</span>
        </div>
        <div style="background:#1a1a2a;border-radius:3px;height:4px;">
            <div style="background:#4488ff;height:4px;border-radius:3px;width:{_prog}%;"></div>
        </div>
    </div>''', unsafe_allow_html=True)

    # 카테고리 배지
    st.markdown(f'<div style="text-align:right;margin-bottom:4px;"><span style="background:#1a0808;border:1.5px solid #cc3333;border-radius:20px;padding:3px 12px;font-size:0.75rem;font-weight:900;color:#ff8866;">{cat}</span></div>', unsafe_allow_html=True)

    # 메인 카드 — 세련된 노트
    st.markdown(f'''<div style="background:#fafaf2;border-radius:16px;padding:1.2rem 1rem 1rem 1.4rem;border:1.5px solid #d4d0b8;
        background-image:repeating-linear-gradient(transparent,transparent 31px,#e8e4d0 31px,#e8e4d0 32px);
        background-position:0 1.2rem;
        border-left:4px solid #ffaaaa;
        min-height:200px;">
        <div style="font-size:1.1rem;font-weight:900;color:#111111;line-height:1.8;">{sent}</div>
        <div style="border-top:1.5px dashed #ccc;margin:0.7rem 0;"></div>
        <div style="font-size:0.95rem;font-weight:800;color:#222222;line-height:1.7;">📖 {kr}</div>
        <div style="background:#fffbe8;border-left:4px solid #ccaa00;border-radius:0 8px 8px 0;padding:0.4rem 0.8rem;margin-top:0.5rem;">
            <span style="font-size:0.88rem;font-weight:800;color:#664400;">💡 {exk}</span>
        </div>
    </div>''', unsafe_allow_html=True)

    st.markdown('''<style>
    div[data-testid="stHorizontalBlock"] button{
        animation:none!important;transform:none!important;box-shadow:none!important;
        border:1.5px solid rgba(255,255,255,0.5)!important;
        color:rgba(255,255,255,0.7)!important;
        background:#111!important;
        font-weight:400!important;
        font-size:0.9rem!important;
    }
    div[data-testid="stHorizontalBlock"] button p{
        color:rgba(255,255,255,0.7)!important;
        font-weight:400!important;
        font-size:0.9rem!important;
    }
    </style>''', unsafe_allow_html=True)

    # 이전/삭제/다음 — 한 줄 (이전/다음 좁게)
    _rb1, _rb2, _rb3 = st.columns([0.85, 1, 0.85])
    with _rb1:
        if st.button("◀ 이전", key="st_p", disabled=bi<=0, use_container_width=True):
            st.session_state.sg_idx = bi-1; st.rerun()
    with _rb2:
        if st.button("🗑 삭제", key="del_q", use_container_width=True):
            # ★ 극복 기록 (forget_logs finally_correct=True)
            try:
                _dt2 = __import__("datetime")
                _today2 = _dt2.datetime.now().strftime("%Y-%m-%d")
                _uid2   = st.session_state.get("nickname", "guest")
                _qid2   = q.get("id", "?")
                _first2 = q.get("first_wrong_date", q.get("saved_date", _today2))
                try:
                    _days2 = (_dt2.datetime.strptime(_today2, "%Y-%m-%d") -
                              _dt2.datetime.strptime(_first2, "%Y-%m-%d")).days
                except:
                    _days2 = 0
                _st2 = load_storage()
                # 최근 forget_log 중 이 문제를 finally_correct=True로 업데이트
                _updated = False
                for _lg in reversed(_st2.get("forget_logs", [])):
                    if _lg.get("problem_id") == _qid2 and _lg.get("user_id") == _uid2:
                        _lg["finally_correct"]  = True
                        _lg["days_to_overcome"] = _days2
                        _updated = True
                        break
                # 업데이트된 항목 없으면 새로 추가
                if not _updated:
                    _st2.setdefault("forget_logs", []).append({
                        "user_id":          _uid2,
                        "problem_id":       _qid2,
                        "grammar_type":     q.get("cat", ""),
                        "source":           "P5",
                        "first_wrong_date": _first2,
                        "revisit_date":     _today2,
                        "interval_days":    _days2,
                        "re_wrong":         False,
                        "revisit_count":    st.session_state.get(f"revisit_{_qid2}", 0),
                        "finally_correct":  True,
                        "days_to_overcome": _days2,
                        "timestamp":        _dt2.datetime.now().isoformat(),
                    })
                with open(STORAGE_FILE, "w", encoding="utf-8") as _ff2:
                    json.dump(_st2, _ff2, ensure_ascii=False, indent=2)
            except:
                pass

            p5_data.pop(bi)
            storage["saved_questions"] = p5_data
            save_storage(storage)
            if bi >= len(p5_data): st.session_state.sg_idx = max(0, len(p5_data)-1)
            st.rerun()
    with _rb3:
        if st.button("다음 ▶", key="st_n", disabled=bi>=len(p5_data)-1, use_container_width=True):
            st.session_state.sg_idx = bi+1; st.rerun()

    # 시험 + 돌아가기
    st.markdown('''<style>
    div[data-testid="stHorizontalBlock"]:last-of-type button{
        min-height:46px!important;
        height:46px!important;
    }
    </style>''', unsafe_allow_html=True)
    _rb4, _rb5 = st.columns([2, 1])
    with _rb4:
        st.markdown('''<style>
        div[data-testid="column"]:first-child button[data-testid="stBaseButton-secondary"]{
            background:linear-gradient(135deg,#5a0800,#cc2200,#ff4400)!important;
            border:3px solid #ff6600!important;
            color:#ffffff!important;
            font-size:1.05rem!important;
            font-weight:900!important;
            min-height:52px!important;
            text-shadow:0 0 8px rgba(255,200,0,0.8)!important;
            box-shadow:0 0 18px rgba(255,80,0,0.7),inset 0 0 10px rgba(255,150,0,0.2)!important;
        }
        div[data-testid="column"]:first-child button[data-testid="stBaseButton-secondary"] p{
            color:#ffffff!important;font-size:1.05rem!important;font-weight:900!important;
        }
        </style>''', unsafe_allow_html=True)
        if st.button("🔥 시험 당장 도전!", key="go_exam", use_container_width=True):
            if len(p5_data) >= 5:
                qs = random.sample(p5_data, 5)
                st.session_state.sg_exam_qs = qs
                st.session_state.sg_exam_idx = 0
                st.session_state.sg_exam_results = []
                st.session_state.sg_exam_start = time.time()
                st.session_state.sg_exam_wrong = False
                st.session_state.sg_phase = "p5_exam"; st.rerun()
            else: st.warning("최소 5문제 필요!")
    with _rb5:
        st.markdown('<div style="height:2px;"></div>', unsafe_allow_html=True)
        if st.button("↩ 돌아가기", key="back_lobby", use_container_width=True):
            st.session_state.sg_phase = "lobby"; st.session_state.rv_battle = None; st.session_state.rv_mode = None; st.rerun()

# ════════════════════════════════
# P5 시험모드 — 33초 타임폭탄
# ════════════════════════════════
elif st.session_state.sg_phase == "p5_exam":
    st_autorefresh(interval=1000, limit=36, key="p5_exam_timer")
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
        tcl = "#ff0000"; tsz = "2.5rem"; tglow = "text-shadow:0 0 40px #ff0000,0 0 80px #cc0000;"
        twarn = '<div style="text-align:center;font-size:1.4rem;color:#ff0000;font-weight:900;margin-top:4px;">💀💀 폭발한다!! 💀💀</div>'
    elif rem <= 10:
        bg_css = "background:linear-gradient(135deg,#1e0815,#2e0a25 30%,#1e0818 70%,#1e0815)!important;"
        tcl = "#ff2200"; tsz = "2rem"; tglow = "text-shadow:0 0 25px #ff2200,0 0 50px #ff0000;"
        twarn = '<div style="text-align:center;font-size:1.1rem;color:#ff4444;font-weight:900;">💀 서둘러!! 또 틀릴 거야?! 💀</div>'
    elif rem <= 15:
        bg_css = "background:linear-gradient(135deg,#160a1e,#220e30 30%,#160a22 70%,#160a1e)!important;"
        tcl = "#ff6600"; tsz = "1.6rem"; tglow = "text-shadow:0 0 15px #ff6600;"
        twarn = '<div style="text-align:center;font-size:1rem;color:#ff8844;font-weight:900;">⚡ 서둘러!! ⚡</div>'
    elif rem <= 20:
        bg_css = "background:linear-gradient(135deg,#121530,#1e1845 30%,#121838 70%,#121530)!important;"
        tcl = "#ffaa00"; tsz = "1.4rem"; tglow = "text-shadow:0 0 8px #ffaa00;"
        twarn = ""
    else:
        bg_css = ""
        tcl = "#44ff88"; tsz = "1.2rem"; tglow = ""; twarn = ""
    tpct = int(rem / 33 * 100)
    q_border = "rgba(255,50,50,0.6)" if rem <= 10 else "rgba(100,140,255,0.4)"
    q_shadow = "0 0 40px rgba(255,0,0,0.2)" if rem <= 10 else "0 0 30px rgba(100,140,255,0.15)"
    if bg_css:
        st.markdown(f'<style>.stApp{{{bg_css}}}</style>', unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;margin:2px 0;padding:4px;"><span style="font-size:{tsz};font-weight:900;color:{tcl};font-family:Impact,Arial Black,sans-serif;{tglow}">{rem}</span><span style="font-size:0.8rem;color:{tcl};opacity:0.7;">s</span><div style="font-size:1rem;color:#888;font-weight:700;margin-top:4px;">Q{qi+1} / 5 · 남은 {left}문제</div></div>', unsafe_allow_html=True)
    bar_color = tcl if rem <= 15 else "#44ff88"
    st.markdown(f'<div style="background:rgba(255,255,255,0.06);border-radius:12px;padding:3px;margin:4px 0;"><div style="background:linear-gradient(90deg,{bar_color},{tcl});height:12px;border-radius:10px;width:{tpct}%;transition:width 0.5s;"></div></div>', unsafe_allow_html=True)
    if twarn:
        st.markdown(twarn, unsafe_allow_html=True)
    blank_text = q["text"].replace("_______", '<span style="border-bottom:3px solid #66aaff;padding:0 16px;color:#88bbff;">________</span>')
    st.markdown(f'<div style="background:linear-gradient(145deg,#141435,#1c1c4a);border:2.5px solid {q_border};border-radius:20px;padding:1.4rem 1.2rem;margin:8px 0;box-shadow:{q_shadow};"><div style="font-size:1.15rem;font-weight:900;color:#ffffff;line-height:1.7;">{blank_text}</div></div>', unsafe_allow_html=True)
    for i, ch in enumerate(q["ch"]):
        if st.button(ch, key=f"ex_{qi}_{i}", type="secondary", use_container_width=True):
            ok = (i == q["a"])
            st.session_state.sg_exam_results.append(ok)

            # ══════════════════════════════════════════
            # ★ forget_logs 저장 (논문 02 SSCI 핵심)
            # ══════════════════════════════════════════
            try:
                _dt = __import__("datetime")
                _today = _dt.datetime.now().strftime("%Y-%m-%d")
                _uid  = st.session_state.get("nickname", "guest")
                _qid  = q.get("id", "?")
                _cat  = q.get("cat", "")
                _src  = "P5"

                # first_wrong_date: 문제에 저장된 날짜 사용, 없으면 오늘
                _first_wrong = q.get("first_wrong_date", q.get("saved_date", _today))

                # interval_days 계산
                try:
                    _interval = (_dt.datetime.strptime(_today, "%Y-%m-%d") -
                                 _dt.datetime.strptime(_first_wrong, "%Y-%m-%d")).days
                except:
                    _interval = 0

                # revisit_count 증가
                _rv_key = f"revisit_{_qid}"
                _rv_cnt = st.session_state.get(_rv_key, 0) + 1
                st.session_state[_rv_key] = _rv_cnt

                _st_f = load_storage()
                _fl = {
                    "user_id":          _uid,
                    "problem_id":       _qid,
                    "grammar_type":     _cat,
                    "source":           _src,
                    "first_wrong_date": _first_wrong,
                    "revisit_date":     _today,
                    "interval_days":    _interval,
                    "re_wrong":         not ok,
                    "revisit_count":    _rv_cnt,
                    "finally_correct":  False,  # 삭제 시 True로 업데이트
                    "days_to_overcome": None,
                    "timestamp":        _dt.datetime.now().isoformat(),
                }
                if "forget_logs" not in _st_f:
                    _st_f["forget_logs"] = []
                _st_f["forget_logs"].append(_fl)

                with open(STORAGE_FILE, "w", encoding="utf-8") as _ff:
                    json.dump(_st_f, _ff, ensure_ascii=False, indent=2)
            except:
                pass

            if not ok:
                st.session_state.sg_exam_wrong = True
                st.session_state.sg_phase = "p5_exam_result"; st.rerun()
            else:
                st.session_state.sg_exam_idx += 1
                st.rerun()
    components.html("""<script>
    function stP(){const d=window.parent.document;d.querySelectorAll('button[kind="secondary"]').forEach(b=>{const t=(b.textContent||'').trim();if(/^\([A-D]\)/.test(t)){b.style.cssText='background:linear-gradient(135deg,rgba(100,140,200,0.25),rgba(100,140,200,0.12))!important;color:#ffffff!important;border:2px solid rgba(100,140,200,0.5)!important;border-radius:16px!important;font-size:1.0rem!important;font-weight:900!important;padding:0.45rem 0.5rem!important;min-height:auto!important;box-shadow:0 3px 15px rgba(100,140,200,0.15)!important;font-family:Georgia,serif!important;';b.querySelectorAll('p').forEach(p=>p.style.cssText='font-size:1.0rem!important;font-weight:900!important;font-family:Georgia,serif!important;');}});};setTimeout(stP,80);setTimeout(stP,300);setTimeout(stP,700);new MutationObserver(stP).observe(window.parent.document.body,{childList:true,subtree:true});
    </script>""", height=0)

# ════════════════════════════════
# P5 시험 결과
# ════════════════════════════════
elif st.session_state.sg_phase == "p5_exam_result":
    results = st.session_state.sg_exam_results
    ok_cnt = sum(results)
    passed = not st.session_state.sg_exam_wrong and ok_cnt == 5
    import random as _rnd3
    if not passed:
        st.markdown('''<style>.stApp{background:#080000!important;}</style>''', unsafe_allow_html=True)
        st.markdown('''<div style="text-align:center;padding:1rem 0 0.5rem 0;">
            <div style="font-size:1rem;letter-spacing:4px;opacity:0.6;">💣 🔥 💥 ☠️ ⚡ 💣 🔥</div>
            <div style="font-size:2.8rem;font-weight:900;color:#ff2200;margin:6px 0;">☠️ 전멸!</div>
            <div style="font-size:0.95rem;color:#ff6600;font-weight:700;">폭탄이 터졌다... 넌 산산조각!</div>
        </div>''', unsafe_allow_html=True)
        st.markdown(f'''<div style="background:#1a0000;border:1.5px solid #ff4400;border-radius:12px;padding:10px;text-align:center;margin:8px 0;">
            <div style="font-size:1.6rem;font-weight:900;color:#ff8888;">💀 {ok_cnt} / 5</div>
        </div>''', unsafe_allow_html=True)
        _nag = _rnd3.choice([
            "🧠 에빙하우스: 복습 없이 24시간 후 80% 망각!",
            "💀 인간은 틀린 문제를 또 틀릴 확률 72%",
            "🔥 토익 990은 오답노트를 3번 본다...",
            "⚡ 3번 반복하면 장기기억 전환율 3배!",
            "💣 폭탄보다 무서운 건 복습 안 하는 것!",
        ])
        st.markdown(f'''<div style="background:#120000;border:1px solid #661100;border-radius:10px;padding:8px;text-align:center;margin-bottom:8px;">
            <div style="font-size:0.85rem;color:#ff6644;font-weight:700;">{_nag}</div>
        </div>''', unsafe_allow_html=True)
        if st.button("⚔️ 설욕전! 다시 싸운다!", key="retry_exam", type="primary", use_container_width=True):
            st.session_state.sg_phase = "lobby"; st.session_state.rv_battle = None; st.session_state.rv_mode = None; st.rerun()
        st.markdown('''<style>
        div[data-testid="stHorizontalBlock"]:last-of-type button{
            border:1.5px solid rgba(255,255,255,0.5)!important;
            background:#0a0a0a!important;
            color:rgba(255,255,255,0.6)!important;
            font-weight:400!important;font-size:0.85rem!important;
        }
        div[data-testid="stHorizontalBlock"]:last-of-type button p{
            color:rgba(255,255,255,0.6)!important;
            font-weight:400!important;font-size:0.85rem!important;
        }
        </style>''', unsafe_allow_html=True)
        _c1, _c2 = st.columns(2)
        with _c1:
            if st.button("🔥 오답전장", key="retry_lobby", use_container_width=True):
                st.session_state.sg_phase = "lobby"; st.session_state.rv_battle = None; st.session_state.rv_mode = None; st.rerun()
        with _c2:
            if st.button("🏠 홈", key="retry_main", use_container_width=True):
                _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
                if _nick:
                    st.query_params["nick"] = _nick
                    st.query_params["ag"] = "1"
                st.switch_page("main_hub.py")
    else:
        st.markdown('''<style>.stApp{background:#080600!important;}</style>''', unsafe_allow_html=True)
        st.markdown('''<div style="text-align:center;padding:1rem 0 0.5rem 0;">
            <div style="font-size:1rem;letter-spacing:4px;opacity:0.6;">🏆 💰 ✨ 👑 ⭐ 🏆 💛</div>
            <div style="font-size:2.8rem;font-weight:900;color:#ffd700;margin:6px 0;">🏆 생존!</div>
            <div style="font-size:0.95rem;color:#d4af37;font-weight:700;">폭탄을 이겨냈다! 진짜 전사!</div>
        </div>''', unsafe_allow_html=True)
        st.markdown(f'''<div style="background:#0c0c00;border:1.5px solid #d4af37;border-radius:12px;padding:10px;text-align:center;margin:8px 0;">
            <div style="font-size:1.6rem;font-weight:900;color:#ffd700;">🏆 {ok_cnt} / 5</div>
        </div>''', unsafe_allow_html=True)
        st.markdown('''<div style="background:#0a0800;border:1px solid #d4af37;border-radius:10px;padding:8px;text-align:center;margin-bottom:8px;">
            <div style="font-size:0.85rem;color:#d4af37;font-weight:700;">⚡ 3번 반복하면 장기기억 전환율 3배!</div>
            <div style="font-size:0.75rem;color:#886600;margin-top:2px;">지금 이 기세로 한 번 더!</div>
        </div>''', unsafe_allow_html=True)
        if st.button("⚡ 한 번 더! 완전 정복!", key="retry_exam", type="primary", use_container_width=True):
            st.session_state.sg_phase = "lobby"; st.session_state.rv_battle = None; st.session_state.rv_mode = None; st.rerun()
        st.markdown('''<style>
        div[data-testid="stHorizontalBlock"]:last-of-type button{
            border:1.5px solid rgba(255,255,255,0.5)!important;
            background:#0a0a0a!important;
            color:rgba(255,255,255,0.6)!important;
            font-weight:400!important;font-size:0.85rem!important;
        }
        div[data-testid="stHorizontalBlock"]:last-of-type button p{
            color:rgba(255,255,255,0.6)!important;
            font-weight:400!important;font-size:0.85rem!important;
        }
        </style>''', unsafe_allow_html=True)
        _c1, _c2 = st.columns(2)
        with _c1:
            if st.button("🔥 오답전장", key="retry_lobby", use_container_width=True):
                st.session_state.sg_phase = "lobby"; st.session_state.rv_battle = None; st.session_state.rv_mode = None; st.rerun()
        with _c2:
            if st.button("🏠 홈", key="retry_main", use_container_width=True):
                _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
                if _nick:
                    st.query_params["nick"] = _nick
                    st.query_params["ag"] = "1"
                st.switch_page("main_hub.py")


# ════════════════════════════════
# VOCA 서바이벌 웨이브 (순수 학습모드 - 타이머 없음)
# ════════════════════════════════
elif st.session_state.sg_phase == "survival":
    # ════════ 문장 퍼즐 배틀 ════════
    import re as _re5
    if not voca_data:
        st.markdown('''<div style="text-align:center;background:#f8f8f8;border-radius:12px;padding:2rem;">
            <div style="font-size:2rem;">📭</div>
            <div style="font-size:1rem;font-weight:600;color:#333;margin-top:8px;">저장된 문장이 없어요!</div>
            <div style="font-size:0.85rem;color:#888;margin-top:4px;">P7전장 브리핑에서 어려운 문장을 저장하세요</div>
        </div>''', unsafe_allow_html=True)
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
        st.markdown('''<div style="text-align:center;padding:2rem;background:#eaf3de;border-radius:16px;border:1px solid #c0dd97;">
            <div style="font-size:2.5rem;">🎉</div>
            <div style="font-size:1.3rem;font-weight:700;color:#27500a;margin-top:8px;">모든 문장 완료!</div>
            <div style="font-size:0.95rem;color:#639922;margin-top:4px;">이제 시험모드에서 증명하라!</div>
        </div>''', unsafe_allow_html=True)
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
        # ★ 적응형 빈칸 개수 — 레벨에 따라 1~3개
        _blank_level = st.session_state.get("puzzle_blank_level", 2)
        _blank_count = max(1, min(3, _blank_level))  # 1~3 범위 보장
        words=sentence.split()
        stopwords={"the","a","an","in","on","at","to","for","of","by","with","is","are","was","were","has","have","had","be","been","that","this","it","its","and","or","but","as","if","so","not","do","did","will","shall","would","could","should","must","from","into","upon","than","then","also"}
        candidates=[w.strip(".,!?;:()") for w in words if w.strip(".,!?;:()").lower() not in stopwords and len(w.strip(".,!?;:()"))>=3]
        rng=random.Random(hash(sentence))
        rng.shuffle(candidates)
        blank_words=candidates[:_blank_count] if len(candidates)>=_blank_count else candidates
        if not blank_words:
            blank_words=[w.strip(".,!?;:()") for w in words if len(w.strip(".,!?;:()"))>=3][:_blank_count]
        blanked=sentence
        border=[]
        for bw in blank_words:
            pat=r"(?i)\b"+_re5.escape(bw)+r"\b"
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
        while len(distractors)<1:
            distractors.append(["process","indicate","establish","provide","conduct"][len(distractors)])
        distractors=list(dict.fromkeys(distractors))[:1]
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
    _cur_lv = st.session_state.get("puzzle_blank_level", 2)
    _lv_label = ["", "🟢 기초(빈칸 1개)", "🟡 표준(빈칸 2개)", "🔴 심화(빈칸 3개)"][_cur_lv]
    st.markdown(f'''<div style="background:#1a1a2e;border:1.5px solid #4488ff;border-radius:14px;padding:8px 14px;text-align:center;margin-bottom:8px;">
        <div style="font-size:0.95rem;font-weight:700;color:#4488ff;">📖 문장 퍼즐 배틀</div>
        <div style="font-size:0.8rem;color:#aaa;margin-top:2px;">{idx+1} / {total} 문장 &nbsp;|&nbsp; {_lv_label}</div>
        <div style="background:#0a0a1a;border-radius:4px;height:5px;margin-top:5px;"><div style="background:linear-gradient(90deg,#4488ff,#44ccff);height:5px;border-radius:4px;width:{int((idx/max(total,1))*100)}%;"></div></div>
    </div>''', unsafe_allow_html=True)

    # ── 한글 해석 (위) ──
    st.markdown(f'''<div style="background:#fffff5;border:1.5px solid #e8e0c8;border-radius:12px;padding:12px 14px;margin-bottom:6px;">
        <div style="font-size:0.65rem;color:#aaa;letter-spacing:2px;margin-bottom:5px;">KOREAN</div>
        <div style="font-size:1.05rem;color:#222;line-height:1.8;font-weight:500;">{sent_kr}</div>
    </div>''', unsafe_allow_html=True)

    st.markdown('<div style="text-align:center;color:#888;font-size:0.8rem;margin:3px 0;">↓ 영어 문장 빈칸을 채워라!</div>', unsafe_allow_html=True)
    if "sb_wrong_cnt" not in st.session_state: st.session_state.sb_wrong_cnt=0
    if "sb_wrong_counted" not in st.session_state: st.session_state.sb_wrong_counted=False
    if done:
        sel_sorted=sorted([s.lower() for s in selected])
        ord_sorted=sorted([b.lower() for b in blank_order])
        correct=(sel_sorted==ord_sorted)
        if not correct and not st.session_state.sb_wrong_counted:
            st.session_state.sb_wrong_cnt+=1
            st.session_state.sb_wrong_counted=True
            st.rerun()
        wrong_cnt=st.session_state.sb_wrong_cnt
        if correct:
            # ★ 적응형 레벨 UP — 연속 2회 정답 시 빈칸 증가
            st.session_state.puzzle_streak = st.session_state.get("puzzle_streak", 0) + 1
            if st.session_state.puzzle_streak >= 2:
                old_level = st.session_state.get("puzzle_blank_level", 2)
                st.session_state.puzzle_blank_level = min(3, old_level + 1)
                st.session_state.puzzle_streak = 0
            _cur_level = st.session_state.get("puzzle_blank_level", 2)
            _level_emoji = ["", "🟢 기초", "🟡 표준", "🔴 심화"][_cur_level]
            _level_msg = ["", "빈칸 1개", "빈칸 2개", "빈칸 3개!"][_cur_level]
            st.markdown(f'''<div style="background:#0a2a0a;border:2px solid #44ff88;border-radius:14px;padding:14px;text-align:center;margin-bottom:8px;">
                <div style="font-size:2rem;">🎯</div>
                <div style="font-size:1.3rem;font-weight:900;color:#44ff88;margin-top:4px;">완벽해! 몸으로 익혔다!</div>
                <div style="font-size:0.9rem;color:#88ddaa;margin-top:4px;">이 문장, 이제 완전히 네 것!</div>
                <div style="font-size:0.8rem;color:#44ff88;margin-top:6px;opacity:0.8;">현재 난이도: {_level_emoji} ({_level_msg})</div>
            </div>''', unsafe_allow_html=True)
            if st.button("▶ 다음 문장!",key="sb_next",type="primary",use_container_width=True):
                st.session_state.sb_idx=idx+1; st.session_state.sb_wrong_cnt=0
                for k in ["sb_selected","sb_done","sb_blanked","sb_blank_order","sb_blank_words"]:
                    if k in st.session_state: del st.session_state[k]
                st.rerun()
        else:
            if wrong_cnt==1:
                st.markdown('''<div style="background:#1a0808;border:2px solid #ff6644;border-radius:14px;padding:12px;text-align:center;margin-bottom:8px;">
                    <div style="font-size:1.5rem;">😤</div>
                    <div style="font-size:1.1rem;font-weight:800;color:#ff8866;margin-top:4px;">한 번 더! 할 수 있어!</div>
                    <div style="font-size:0.85rem;color:#ffaa88;margin-top:3px;">다시 한글 보고 순서대로!</div>
                </div>''', unsafe_allow_html=True)
                if st.button("🔄 다시 도전!",key="sb_retry",type="primary",use_container_width=True):
                    st.session_state.sb_selected=[]
                    st.session_state.sb_done=False
                    st.session_state.sb_wrong_counted=False
                    st.rerun()
            else:
                import random as _rnd2
                funny_msgs=[
                    "😤 이걸 틀려?! 다음엔 눈 크게 뜨고!!",
                    "🧠 뇌야 일해라! 저장 안 됐냐?!",
                    "💀 틀렸다고 죽진 않아. 근데 990은 죽었어.",
                    "📚 이 문장 모르면 토익도 몰라. 외워!",
                    "⚡ 틀린 게 부끄럽진 않아. 또 틀리는 게 문제지!",
                    "🔥 괜찮아! 오늘 틀린 게 시험장에서 맞는 거야!",
                    "😂 이 문장이 웃겨? 외우면 더 웃길 거야!",
                ]
                msg=_rnd2.choice(funny_msgs)
                # 정답으로 채워진 문장 표시
                correct_sent=sentence
                ans_parts=correct_sent.split()
                ans_html=""
                for _w in ans_parts:
                    _clean=_w.strip(".,!?;:()")
                    if any(_clean.lower()==_b.lower() for _b in blank_order):
                        ans_html+=f'<span style="background:#0a2a0a;border:2px solid #44ff88;border-radius:8px;padding:2px 10px;color:#44ff88;font-weight:900;margin:0 2px;">{_w}</span> '
                    else:
                        ans_html+=f'<span style="color:#ddddff;">{_w}</span> '
                st.markdown(f'''<div style="background:#0a1a0a;border:2px solid #44ff88;border-radius:14px;padding:12px 14px;margin-bottom:8px;">
                    <div style="font-size:0.7rem;color:#44ff88;letter-spacing:2px;margin-bottom:6px;">✅ 정답 문장</div>
                    <div style="font-size:1.05rem;font-weight:600;line-height:2.0;">{ans_html}</div>
                </div>''', unsafe_allow_html=True)
                # 잔소리 멘트 (1번만)
                st.markdown(f'''<div style="background:#1a0a00;border:2px solid #ff8844;border-radius:14px;padding:10px 14px;margin-bottom:8px;text-align:center;">
                    <div style="font-size:1.05rem;font-weight:800;color:#ffaa55;">{msg}</div>
                </div>''', unsafe_allow_html=True)
                if st.button("▶ 다음 문장!",key="sb_next2",type="primary",use_container_width=True):
                    # ★ 2번 틀리면 레벨 DOWN
                    st.session_state.puzzle_streak = 0
                    old_level = st.session_state.get("puzzle_blank_level", 2)
                    st.session_state.puzzle_blank_level = max(1, old_level - 1)
                    # ★ 포로수용소 자동 저장 — 틀린 빈칸 단어들
                    try:
                        _pr_storage = load_storage()
                        if "word_prison" not in _pr_storage:
                            _pr_storage["word_prison"] = []
                        import datetime as _dt2
                        _pr_today = _dt2.datetime.now().strftime("%Y-%m-%d")
                        _pr_sent = item.get("sentences", [""])[0] if item.get("sentences") else item.get("expr", "")
                        _pr_kr   = item.get("kr", item.get("meaning", ""))
                        for _bw in blank_order:
                            _bw_clean = _bw.strip(".,!?;:()")
                            if not _bw_clean or len(_bw_clean) < 2:
                                continue
                            _exists = any(p.get("word","").lower() == _bw_clean.lower()
                                          for p in _pr_storage["word_prison"])
                            if not _exists:
                                _pr_storage["word_prison"].append({
                                    "word":           _bw_clean,
                                    "kr":             _pr_kr,
                                    "source":         "퍼즐 오답",
                                    "sentence":       _pr_sent,
                                    "captured_date":  _pr_today,
                                    "correct_streak": 0,
                                    "last_reviewed":  None,
                                    "cat":            "vocabulary",
                                })
                        save_storage(_pr_storage)
                    except Exception:
                        pass
                    st.session_state.sb_idx=idx+1; st.session_state.sb_wrong_cnt=0
                    for k in ["sb_selected","sb_done","sb_blanked","sb_blank_order","sb_blank_words","sb_wrong_counted"]:
                        if k in st.session_state: del st.session_state[k]
                    st.rerun()
    else:
        fp0=blanked.split("[___]"); s0_html=""
        for _i,_p in enumerate(fp0):
            s0_html+=f'<span style="color:#ddddff;">{_p}</span>'
            if _i<len(fp0)-1:
                if _i<len(selected): s0_html+=f'<span style="background:#0a2a0a;border:2px solid #44ff88;border-radius:8px;padding:2px 10px;color:#44ff88;font-weight:700;margin:0 3px;">{selected[_i]}</span>'
                else: s0_html+='<span style="background:#0a0a1a;border:2px dashed #4488ff;border-radius:8px;padding:2px 18px;color:#333;margin:0 3px;">_____</span>'
        st.markdown(f'''<div style="background:#1a1a2e;border:1.5px solid #4488ff;border-radius:12px;padding:12px 14px;margin-bottom:8px;font-size:1.05rem;font-weight:600;line-height:2.2;">{s0_html}</div>''', unsafe_allow_html=True)
        # ── 단어 카드 5개 ──
        st.markdown('<div style="font-size:0.8rem;color:#888;text-align:center;margin-bottom:5px;">👇 단어를 터치해서 빈칸에 넣어라!</div>', unsafe_allow_html=True)
        used=[s.lower() for s in selected]
        cols=st.columns(len(blank_words))
        for ci,bw in enumerate(blank_words):
            with cols[ci]:
                if bw.lower() in used:
                    st.markdown(f'<div style="background:#111;border:1px solid #333;border-radius:10px;padding:10px 4px;text-align:center;color:#333;font-weight:700;font-size:0.9rem;">{bw}</div>', unsafe_allow_html=True)
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
            # ★ 건너뛴 문장 단어도 포로 수감
            try:
                _sk_storage = load_storage()
                if "word_prison" not in _sk_storage:
                    _sk_storage["word_prison"] = []
                import datetime as _dt3
                _sk_today = _dt3.datetime.now().strftime("%Y-%m-%d")
                _sk_sent = item.get("sentences", [""])[0] if item.get("sentences") else item.get("expr","")
                _sk_kr   = item.get("kr", item.get("meaning",""))
                _sk_words = st.session_state.get("sb_blank_order", [])
                for _sw in _sk_words:
                    _sw_c = _sw.strip(".,!?;:()")
                    if not _sw_c or len(_sw_c) < 2: continue
                    if not any(p.get("word","").lower() == _sw_c.lower()
                               for p in _sk_storage["word_prison"]):
                        _sk_storage["word_prison"].append({
                            "word":           _sw_c,
                            "kr":             _sk_kr,
                            "source":         "퍼즐 건너뜀",
                            "sentence":       _sk_sent,
                            "captured_date":  _sk_today,
                            "correct_streak": 0,
                            "last_reviewed":  None,
                            "cat":            "vocabulary",
                        })
                save_storage(_sk_storage)
            except Exception:
                pass
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

elif st.session_state.sg_phase == "survival_result":
    wave = st.session_state.get("sg_wave", 1)
    results = st.session_state.get("sg_wave_results", [])
    ok_cnt = sum(results)
    total_answered = len(results)
    cleared = wave > 4

    if cleared and ok_cnt == total_answered:
        st.markdown(f'''<div style="text-align:center;padding:1.5rem;">
            <div style="font-size:3.5rem;font-weight:900;color:#ffcc00;text-shadow:0 0 30px #ffaa00;">🏆 완전정복! 🏆</div>
            <div style="font-size:1.5rem;color:#ffdd44;font-weight:800;margin-top:8px;">4전 전부 완벽 정답! 숙련도 +1 상승!</div>
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
        if st.button("🔥 오답전장 귀환", key="sv_back", type="secondary", use_container_width=True):
            st.session_state.sg_phase = "lobby"; st.session_state.rv_battle = None; st.session_state.rv_mode = None; st.rerun()

# ════════════════════════════════
# VOCA 콤보 러시 — 33초 타임폭탄 시험!
# ════════════════════════════════
elif st.session_state.sg_phase == "combo_rush":
    if not voca_data:
        st.warning("저장된 P7 단어/표현이 없습니다!")
        if st.button("돌아가기"): st.session_state.sg_phase="lobby"; st.session_state.rv_battle=None; st.session_state.rv_mode=None; st.rerun()
        st.stop()
    st_autorefresh(interval=1000, limit=40, key="combo_timer")
    if "sg_combo_score" not in st.session_state: st.session_state.sg_combo_score=0
    if "sg_combo_count" not in st.session_state: st.session_state.sg_combo_count=0
    if "sg_combo_idx" not in st.session_state: st.session_state.sg_combo_idx=0
    if "sg_combo_over" not in st.session_state: st.session_state.sg_combo_over=False
    if "sg_combo_results" not in st.session_state: st.session_state.sg_combo_results=[]
    score=st.session_state.sg_combo_score; combo=st.session_state.sg_combo_count
    cidx=st.session_state.sg_combo_idx
    if "sg_combo_pool" not in st.session_state:
        has_sent=[v for v in voca_data if v.get("sentences")]
        if not has_sent: has_sent=voca_data[:]
        pool=has_sent[:]; random.shuffle(pool)
        while len(pool)<5: pool+=has_sent.copy(); random.shuffle(pool)
        st.session_state.sg_combo_pool=pool[:5]
    c_pool=st.session_state.sg_combo_pool
    total_qs=min(5,len(c_pool))
    if cidx>=total_qs or st.session_state.sg_combo_over:
        st.session_state.sg_phase="combo_result"; st.rerun()
    q_item=c_pool[cidx]
    elapsed=time.time()-st.session_state.sg_combo_start
    rem=max(0,30-int(elapsed))
    if rem<=0: st.session_state.sg_combo_over=True; st.session_state.sg_phase="combo_result"; st.rerun()
    if rem<=5: bg_css="background:linear-gradient(135deg,#2a0808,#3a0a1a)!important;"; tcl="#ff0000"; tsz="2.5rem"; tglow="text-shadow:0 0 40px #ff0000;"; twarn='<div style="text-align:center;font-size:1.4rem;color:#ff0000;font-weight:900;">💀 폭발한다!! 💀</div>'
    elif rem<=10: bg_css="background:linear-gradient(135deg,#1e0815,#2e0a25)!important;"; tcl="#ff2200"; tsz="2rem"; tglow="text-shadow:0 0 25px #ff2200;"; twarn='<div style="text-align:center;font-size:1.1rem;color:#ff4444;font-weight:900;">💀 서둘러!! 💀</div>'
    elif rem<=15: bg_css=""; tcl="#ff6600"; tsz="1.6rem"; tglow="text-shadow:0 0 15px #ff6600;"; twarn='<div style="text-align:center;font-size:1rem;color:#ff8844;font-weight:900;">⚡ 서둘러!!</div>'
    else: bg_css=""; tcl="#44ff88"; tsz="1.2rem"; tglow=""; twarn=""
    tpct=int(rem/30*100)
    if bg_css: st.markdown(f'<style>.stApp{{{bg_css}}}</style>',unsafe_allow_html=True)
    ok_cnt=sum(1 for r in st.session_state.sg_combo_results if r)
    needed=max(0,3-ok_cnt); remain_q=total_qs-cidx
    survive_color="#44ff88" if ok_cnt>=3 else "#ffcc00" if needed<=remain_q else "#ff4444"
    st.markdown(f'<div style="background:linear-gradient(180deg,#0a0a1a,#1a1030);border:2.5px solid #4488ff;border-radius:22px;padding:8px;text-align:center;"><div style="font-size:1.0rem;font-weight:900;color:#4488ff;">⚡ P7 실전 블랭크 · 5문제 중 3개 이상!</div><div style="display:flex;justify-content:space-around;margin-top:6px;"><span style="font-size:0.85rem;font-weight:900;color:#44ff88;">✅ {ok_cnt}개</span><span style="font-size:0.85rem;font-weight:900;color:#ffcc00;">{cidx+1}/{total_qs}</span><span style="font-size:0.85rem;font-weight:900;color:{survive_color};">필요 {needed}개</span></div></div>',unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;margin:4px 0;"><span style="font-size:{tsz};font-weight:900;color:{tcl};{tglow}">{rem}</span><span style="font-size:0.8rem;color:{tcl};opacity:0.7;">s</span></div>',unsafe_allow_html=True)
    st.markdown(f'<div style="background:rgba(255,255,255,0.06);border-radius:12px;padding:3px;margin:4px 0;"><div style="background:linear-gradient(90deg,{tcl},#4488ff);height:12px;border-radius:10px;width:{tpct}%;"></div></div>',unsafe_allow_html=True)
    if twarn: st.markdown(twarn,unsafe_allow_html=True)
    import re as _re2
    expr_text=q_item.get("expr",""); meaning=q_item.get("meaning",""); sentences=q_item.get("sentences",[])
    expr_words=expr_text.split(); key_word=max(expr_words,key=len) if expr_words else expr_text
    if not sentences:
        st.session_state.sg_combo_idx=cidx+1
        if not st.session_state.sg_combo_results: st.session_state.sg_combo_results=[]
        st.session_state.sg_combo_results.append(True); st.rerun()
    first_en=sentences[0]
    blank_sent=_re2.sub(r"(?i)\b"+_re2.escape(key_word)+r"\b","_______",first_en,count=1)
    if "_______" not in blank_sent: blank_sent=first_en.replace(expr_text,"_______",1)
    if "_______" not in blank_sent:
        words=[w for w in first_en.split() if len(w.strip(".,!?;:()"))>=3]
        if words:
            chosen=words[len(words)//2]
            blank_sent=first_en.replace(chosen,"_______",1)
            key_word=chosen.strip(".,!?;:()")
    if "_______" not in blank_sent: blank_sent=first_en.replace(first_en.split()[0],"_______",1)
    blank_styled=blank_sent.replace("_______",'<span style="border-bottom:3px solid #4488ff;padding:0 8px;color:#88aaff;font-weight:900;">_______</span>')
    st.markdown(f'<div style="border-radius:20px;padding:1rem;margin:6px 0;background:linear-gradient(145deg,#1a1a2e,#2a2040);border:2.5px solid rgba(100,150,255,0.6);"><div style="font-size:0.85rem;font-weight:800;letter-spacing:3px;color:rgba(150,200,255,0.8);margin-bottom:10px;">📖 FILL IN THE BLANK</div><div style="font-size:1.1rem;font-weight:700;line-height:1.6;color:#eeeeff;">{blank_styled}</div></div>',unsafe_allow_html=True)
    WORD_DB={"a":["address","adjust","advance","achieve","allocate","approve","assess","assist","announce"],"b":["balance","benefit","build","boost","brief","bring","budget"],"c":["comply","conduct","confirm","consider","complete","calculate","cancel","coordinate","clarify"],"d":["deliver","determine","develop","distribute","demonstrate","decline","delay","discuss"],"e":["establish","evaluate","examine","execute","expand","ensure","enforce","engage","enhance"],"f":["facilitate","finalize","follow","forecast","fulfill","focus","forward"],"g":["generate","grant","guide","gather","guarantee"],"h":["handle","highlight","hire","hold","head"],"i":["implement","improve","increase","indicate","inspect","install","integrate","introduce"],"j":["justify","join"],"l":["launch","limit","list","locate","lead","leverage"],"m":["maintain","manage","measure","monitor","modify","meet","mention"],"n":["notify","negotiate","note"],"o":["obtain","operate","optimize","organize","outline","oversee"],"p":["prepare","process","produce","provide","publish","perform","present","prevent","promote"],"q":["qualify","question"],"r":["receive","record","reduce","renew","replace","report","require","resolve","review"],"s":["submit","supply","support","suspend","sustain","schedule","secure","select","specify","streamline"],"t":["terminate","transfer","transform","transmit","track","test","target"],"u":["update","upgrade","utilize","undergo"],"v":["verify","validate","volunteer"],"w":["withdraw","work","warrant"]}
    def get_distractors(correct_word,n=3):
        first=correct_word[0].lower() if correct_word else "s"
        candidates=WORD_DB.get(first,WORD_DB["s"])
        filtered=[w for w in candidates if w.lower()!=correct_word.lower()]
        filtered.sort(key=lambda w:abs(len(w)-len(correct_word)))
        rng=random.Random(hash(f"dist_{correct_word}")); rng.shuffle(filtered[:8])
        result=filtered[:n]
        fallback=["implement","facilitate","demonstrate","establish","coordinate"]
        for fb in fallback:
            if len(result)>=n: break
            if fb not in result and fb!=correct_word: result.append(fb)
        return result[:n]
    correct_ans=key_word; distractors=get_distractors(correct_ans,3)
    choices=distractors+[correct_ans]; rng2=random.Random(hash(f"cb_{cidx}_{correct_ans}")); rng2.shuffle(choices)
    correct_idx=choices.index(correct_ans); labeled=[f"({chr(65+i)}) {c}" for i,c in enumerate(choices)]
    for i,ch in enumerate(labeled):
        if st.button(ch,key=f"cb_{cidx}_{i}",type="secondary",use_container_width=True):
            results=st.session_state.sg_combo_results
            if i==correct_idx: results.append(True); st.session_state.sg_combo_score=score+100; st.session_state.sg_combo_count=combo+1
            else: results.append(False)
            st.session_state.sg_combo_results=results; st.session_state.sg_combo_idx=cidx+1
            wrong_cnt=sum(1 for r in results if not r)
            if wrong_cnt>(total_qs-3): st.session_state.sg_combo_over=True
            st.rerun()

# ════════════════════════════════
# 단어 저장고 — 무기 관리 (삭제)
# ════════════════════════════════
if st.session_state.get("rv_mode") == "p7_vault":
    st.markdown('''<div style="text-align:center;padding:1rem 0;">
        <div style="font-size:1.8rem;font-weight:900;color:#185FA5;">📦 문장 저장고</div>
        <div style="font-size:0.9rem;color:#888;margin-top:4px;">저장한 문장으로 학습하고 시험 준비하세요</div>
    </div>''', unsafe_allow_html=True)
    storage2=load_storage()
    voca_list=storage2.get("saved_expressions",[])
    if not voca_list:
        st.markdown('''<div style="text-align:center;background:#f8f8f8;border-radius:12px;padding:2rem;color:#888;">
            <div style="font-size:2rem;">📭</div>
            <div style="font-size:1rem;margin-top:8px;">저장된 문장이 없어요!</div>
            <div style="font-size:0.85rem;margin-top:4px;">P7전장 브리핑에서 어려운 문장을 저장하세요</div>
        </div>''', unsafe_allow_html=True)
    else:
        for idx,item in enumerate(voca_list):
            sentences=item.get("sentences",[])
            sentence=sentences[0] if sentences else item.get("expr","")
            kr_full=item.get("kr","") or item.get("meaning","")
            kr_sents=[x.strip() for x in kr_full.replace("!","!|").replace("?","?|").replace(".",".|").split("|") if x.strip()]
            sent_kr=kr_sents[0] if kr_sents else kr_full
            st.markdown(f'''<div style="background:#ffffff;border:0.5px solid #d3d1c7;border-radius:12px;padding:12px 14px;margin-bottom:4px;">
                <div style="font-size:15px;font-weight:700;color:#1a1a2e;line-height:1.6;">{sentence}</div>
                <div style="font-size:13px;color:#5f5e5a;margin-top:4px;">{sent_kr}</div>
            </div>''', unsafe_allow_html=True)
            if st.button("🗑 삭제",key=f"del_v_{idx}"):
                deleted=voca_list.pop(idx)
                deleted["deleted_at"]=__import__("time").time()
                deleted["days_kept"]=round((deleted["deleted_at"]-deleted.get("first_saved_at",deleted["deleted_at"]))/86400,1)
                dl=storage2.get("deleted_expressions",[]); dl.append(deleted)
                storage2["deleted_expressions"]=dl; storage2["saved_expressions"]=voca_list
                save_storage(storage2); st.rerun()
    st.markdown('<div style="margin-top:12px;"></div>', unsafe_allow_html=True)
    if st.button("↩ 돌아가기",key="vault_back",use_container_width=True):
        st.session_state.rv_mode=None; st.rerun()

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
    combo_pool = st.session_state.get("sg_combo_pool", [])

    if new_record:
        st.markdown('<style>.stApp{background:#080600!important;}</style>', unsafe_allow_html=True)
        st.markdown(f'''<div style="text-align:center;padding:1rem 0 0.5rem 0;">
            <div style="font-size:0.9rem;letter-spacing:4px;opacity:0.7;">🏆 💰 ✨ 👑 ⭐ 🏆 💛</div>
            <div style="font-size:2.8rem;font-weight:900;color:#ffd700;text-shadow:0 0 30px #ffd700,0 0 60px #ff8800;margin:6px 0;">🏆 신기록!</div>
            <div style="font-size:0.9rem;color:#d4af37;font-weight:700;">새로운 최고 기록 달성!</div>
        </div>''', unsafe_allow_html=True)
        st.markdown(f'''<div style="background:#0c0c00;border:2px solid #d4af37;border-radius:14px;padding:14px;text-align:center;margin:8px 0;">
            <div style="font-size:0.75rem;color:#886600;margin-bottom:4px;">🎉 NEW RECORD</div>
            <div style="font-size:2.8rem;font-weight:900;color:#ffd700;text-shadow:0 0 20px rgba(255,215,0,0.5);">⭐ {score}</div>
        </div>''', unsafe_allow_html=True)
    else:
        st.markdown('<style>.stApp{background:#080000!important;}</style>', unsafe_allow_html=True)
        st.markdown(f'''<div style="text-align:center;padding:1rem 0 0.5rem 0;">
            <div style="font-size:0.9rem;letter-spacing:4px;opacity:0.5;">💣 🔥 💥 ☠️ ⚡ 💣 🔥</div>
            <div style="font-size:2.8rem;font-weight:900;color:#ff2200;text-shadow:0 0 20px #ff0000;margin:6px 0;">💀 전멸!</div>
            <div style="font-size:0.9rem;color:#ff6600;font-weight:700;">폭탄이 터졌다... 한 번 더 도전!</div>
        </div>''', unsafe_allow_html=True)
        st.markdown(f'''<div style="background:#1a0000;border:1.5px solid #cc2244;border-radius:12px;padding:10px;text-align:center;margin:8px 0;">
            <div style="font-size:0.75rem;color:#884433;margin-bottom:2px;">이번 결과</div>
            <div style="font-size:2rem;font-weight:900;color:#ff4466;">💀 {score}점 &nbsp;·&nbsp; 최고 {max(best,score)}점</div>
        </div>''', unsafe_allow_html=True)

    st.markdown("""<style>
    button[data-testid="stBaseButton-primary"]{background:#0a0000!important;border:2px solid #cc2244!important;border-radius:12px!important;}
    button[data-testid="stBaseButton-primary"] p{color:#ff4466!important;font-size:1.1rem!important;font-weight:900!important;}
    button[data-testid="stBaseButton-secondary"]{background:#0a0a0a!important;border:1.5px solid rgba(255,255,255,0.2)!important;border-radius:12px!important;}
    button[data-testid="stBaseButton-secondary"] p{color:#aaa!important;font-size:1.0rem!important;}
    </style>""", unsafe_allow_html=True)
    if st.button("💪 다시 덤벼! 이번엔 안 진다!", key="cb_retry", type="primary", use_container_width=True):
        st.session_state.sg_combo_score = 0; st.session_state.sg_combo_count = 0
        st.session_state.sg_combo_idx = 0; st.session_state.sg_combo_start = time.time()
        st.session_state.sg_combo_over = False
        if "sg_combo_pool" in st.session_state: del st.session_state.sg_combo_pool
        st.session_state.sg_phase = "combo_rush"; st.rerun()
    if st.button("🧠 단계부터 다시 밟는다!", key="cb_wave", use_container_width=True):
        st.session_state.sg_wave = 1; st.session_state.sg_wave_idx = 0
        st.session_state.sg_wave_results = []; st.session_state.sg_wave_dead = False
        st.session_state.sg_wave_start = time.time()
        if "sg_sv_pool" in st.session_state: del st.session_state.sg_sv_pool
        if "sg_wave_start" in st.session_state: del st.session_state.sg_wave_start
        st.session_state.sg_phase = "survival"; st.rerun()
    if st.button("🔥 오답전장 귀환", key="cb_back", use_container_width=True):
        st.session_state.sg_phase = "lobby"; st.session_state.rv_battle = None; st.session_state.rv_mode = None; st.rerun()












# ══════════════════════════════════════════════════════════════
# 💀 단어 포로수용소 페이지
# ══════════════════════════════════════════════════════════════
elif st.session_state.sg_phase == "word_prison":
    import datetime as _pr_dt2

    # 홈 버튼
    _nick = st.session_state.get("nickname", "")
    if st.button("🏠 홈", key="prison_home", use_container_width=False):
        if _nick:
            st.query_params["nick"] = _nick
            st.query_params["ag"] = "1"
        st.switch_page("main_hub.py")

    # 저장소 로드
    _pr_st = load_storage()
    if "word_prison" not in _pr_st:
        _pr_st["word_prison"] = []
    _prisoners = _pr_st["word_prison"]

    # 헤더
    st.markdown("""
<div style="background:linear-gradient(135deg,#1a0a2e,#2d1060);
     border:2px solid #7040c0;border-radius:18px;
     padding:16px;text-align:center;margin-bottom:12px;">
  <div style="font-size:2rem;margin-bottom:4px;">💀</div>
  <div style="font-size:1.6rem;font-weight:900;color:#e8d0ff;letter-spacing:2px;">단어 포로수용소</div>
  <div style="font-size:0.85rem;color:#9070c0;margin-top:4px;">틀린 단어들이 갇혀 있다 — 심문하고 석방하라!</div>
</div>""", unsafe_allow_html=True)

    if not _prisoners:
        st.markdown("""
<div style="background:#0a1a0a;border:2px solid #44ff88;border-radius:16px;
     padding:24px;text-align:center;margin:20px 0;">
  <div style="font-size:3rem;">🏆</div>
  <div style="font-size:1.3rem;font-weight:900;color:#44ff88;margin-top:8px;">포로 전원 석방!</div>
  <div style="font-size:0.9rem;color:#88ddaa;margin-top:6px;">모든 단어를 정복했다. 진짜 전사!</div>
</div>""", unsafe_allow_html=True)
        if st.button("🔥 오답전장으로", key="pr_back_empty", use_container_width=True):
            st.session_state.sg_phase = "lobby"
            st.session_state.rv_battle = None
            st.session_state.rv_mode = None
            st.rerun()
    else:
        _today_str2 = _pr_dt2.datetime.now().strftime("%Y-%m-%d")

        def _days_since(d):
            try:
                return (_pr_dt2.datetime.now() - _pr_dt2.datetime.strptime(d, "%Y-%m-%d")).days
            except Exception:
                return 0

        def _danger_level(p):
            d = _days_since(p.get("captured_date", _today_str2))
            if d >= 7: return 3
            if d >= 3: return 2
            return 1

        # 위험도 순 정렬
        _prisoners_sorted = sorted(_prisoners, key=lambda p: -_danger_level(p))

        _total = len(_prisoners_sorted)
        _d3 = sum(1 for p in _prisoners_sorted if _danger_level(p) == 3)
        _d2 = sum(1 for p in _prisoners_sorted if _danger_level(p) == 2)
        _d1 = sum(1 for p in _prisoners_sorted if _danger_level(p) == 1)

        # 통계 배지
        st.markdown(f"""
<div style="display:flex;gap:8px;margin-bottom:10px;">
  <div style="flex:1;background:#1a0505;border:1px solid #ff4040;border-radius:10px;padding:8px;text-align:center;">
    <div style="font-size:1.3rem;font-weight:900;color:#ff4040;">{_d3}</div>
    <div style="font-size:0.7rem;color:#ff8080;">🚨 탈출직전</div>
  </div>
  <div style="flex:1;background:#1a0a00;border:1px solid #ff9040;border-radius:10px;padding:8px;text-align:center;">
    <div style="font-size:1.3rem;font-weight:900;color:#ff9040;">{_d2}</div>
    <div style="font-size:0.7rem;color:#ffbb80;">⚠️ 위험</div>
  </div>
  <div style="flex:1;background:#1a1a00;border:1px solid #c0a030;border-radius:10px;padding:8px;text-align:center;">
    <div style="font-size:1.3rem;font-weight:900;color:#c0a030;">{_d1}</div>
    <div style="font-size:0.7rem;color:#e0c060;">🆕 신입</div>
  </div>
  <div style="flex:1;background:#0a0a1a;border:1px solid #7040c0;border-radius:10px;padding:8px;text-align:center;">
    <div style="font-size:1.3rem;font-weight:900;color:#c080ff;">{_total}</div>
    <div style="font-size:0.7rem;color:#9060c0;">총 포로</div>
  </div>
</div>""", unsafe_allow_html=True)

        # 포로 카드 (최대 10개씩 표시)
        _show_n = min(_total, 10)
        st.markdown(f'<div style="font-size:0.8rem;color:#888;margin-bottom:6px;">📋 포로 현황 (상위 {_show_n}명)</div>', unsafe_allow_html=True)

        _freed_indices = []

        for _pi, _p in enumerate(_prisoners_sorted[:_show_n]):
            _dl = _danger_level(_p)
            _dc = "#ff4040" if _dl == 3 else ("#ff9040" if _dl == 2 else "#c0a030")
            _dlabel = "🚨 탈출 직전" if _dl == 3 else ("⚠️ 위험" if _dl == 2 else "🆕 신입")
            _days = _days_since(_p.get("captured_date", _today_str2))
            _day_txt = f"{_days}일째" if _days > 0 else "오늘"
            _src = _p.get("source", "")
            _sent = _p.get("sentence", "")
            _word = _p.get("word", "")
            _kr = _p.get("kr", "")

            st.markdown(f"""
<div style="background:#1a1a2e;border:1.5px solid {_dc};border-radius:14px;
     padding:12px 14px;margin-bottom:8px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
    <span style="background:{_dc}22;border:1px solid {_dc};color:{_dc};
                 font-size:0.75rem;font-weight:700;padding:2px 8px;border-radius:8px;">{_dlabel}</span>
    <span style="color:#666;font-size:0.75rem;">📌 {_src} · {_day_txt}</span>
  </div>
  <div style="font-size:1.5rem;font-weight:900;color:#ffffff;margin-bottom:4px;">{_word}</div>
  <div style="font-size:0.85rem;color:#9090b0;margin-bottom:6px;">🔑 {_kr}</div>
  {f'<div style="font-size:0.8rem;color:#6060a0;font-style:italic;line-height:1.5;">{_sent[:80]}{"..." if len(_sent) > 80 else ""}</div>' if _sent else ""}
</div>""", unsafe_allow_html=True)

            _c1, _c2 = st.columns(2)
            with _c1:
                if st.button(f"✅ 알았다! 석방!", key=f"pr_free_{_pi}", use_container_width=True):
                    # 석방 → word_prison에서 제거
                    _real_idx = next((i for i, x in enumerate(_pr_st["word_prison"])
                                      if x.get("word","").lower() == _word.lower()), None)
                    if _real_idx is not None:
                        _pr_st["word_prison"].pop(_real_idx)
                        save_storage(_pr_st)
                    st.success(f"🎉 '{_word}' 석방! 완전 정복!")
                    st.rerun()
            with _c2:
                if st.button(f"❌ 아직 몰라", key=f"pr_jail_{_pi}", use_container_width=True):
                    # 복역 연장 — correct_streak 리셋
                    _real_idx2 = next((i for i, x in enumerate(_pr_st["word_prison"])
                                       if x.get("word","").lower() == _word.lower()), None)
                    if _real_idx2 is not None:
                        _pr_st["word_prison"][_real_idx2]["correct_streak"] = 0
                        _pr_st["word_prison"][_real_idx2]["last_reviewed"] = _today_str2
                        save_storage(_pr_st)
                    st.info(f"🔒 '{_word}' 다시 수감. 다음에 또 심문!")
                    st.rerun()

        if _total > _show_n:
            st.markdown(f'<div style="text-align:center;color:#666;font-size:0.8rem;margin-top:4px;">외 {_total - _show_n}명 더 있음...</div>',
                        unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🔥 오답전장으로 돌아가기", key="pr_back", use_container_width=True):
            st.session_state.sg_phase = "lobby"
            st.session_state.rv_battle = None
            st.session_state.rv_mode = None
            st.rerun()
