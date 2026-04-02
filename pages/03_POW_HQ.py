"""
FILE: 03_POW_HQ.py  (구: 03_오답전장.py)
ROLE: 포로사령부 — 오답 관리 허브 (학습·시험·포로수용소·어휘시험 통합)
PHASES: LOBBY → PUZZLE_BATTLE | EXAM | WORD_PRISON | VOCA_EXAM
DATA:   storage_data.json → saved_questions, saved_expressions, word_prison, forget_logs(논문C)
LINKS:  main_hub.py (작전사령부 귀환) | 02_Firepower.py (화력전) | 04_Decrypt_Op.py (암호해독 작전)
PAPERS: 논문C(forget_logs 망각곡선), 논문A(armory_p5 정복률)
EXTEND: 단어 포로수용소 심문(퀴즈) 기능 추가 예정 — WORD_PRISON phase 하단에 삽입
EXTEND: 슬라이드 제스처 완성 예정
EXTEND: P4 청음전장 연동 예정
"""
import streamlit as st
import streamlit.components.v1 as components
import json, os, random, time, re
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="💀 포로사령부", page_icon="💀", layout="wide", initial_sidebar_state="collapsed")
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

# ★ 포로수용소 — 스마트 단어 1개 추출 함수
_PRISON_STOP = {
    "the","a","an","in","on","at","to","for","of","by","with","is","are","was","were",
    "has","have","had","be","been","that","this","it","its","all","not","and","or","but",
    "as","if","so","no","do","did","can","may","will","shall","would","could","should",
    "must","from","into","upon","than","then","also","very","much","more","most","only",
    "just","even","still","yet","each","every","both","few","many","some","any","other",
    "such","what","which","who","whom","whose","where","when","how","why","its","their",
    "our","your","his","her","my","they","we","he","she","i","you","it","us","him","them",
    "been","being","had","have","next","last","new","first","one","two","three","take",
    "make","said","says","will","was","were","are","is","not","also","than","then","there",
    "these","those","about","after","before","between","during","since","while","within",
    "without","across","against","along","among","around","behind","below","beside",
    "beyond","down","up","off","out","over","past","through","under","until","upon"
}

def _extract_prison_word(text, ex_field="", cat="", ch=None, a_idx=0):
    """P5 문제에서 포로 단어 1개 스마트 추출"""
    # 1순위: ex 필드 "단어=설명" 패턴
    if ex_field:
        m = re.match(r"^([a-zA-Z_\-]+)\s*=", ex_field.strip())
        if m:
            w = m.group(1).strip()
            if len(w) >= 3 and w.lower() not in _PRISON_STOP:
                return w

    # 2순위: 문장에서 5자 이상 핵심 어휘 (6→5로 완화)
    if text:
        words = re.findall(r"[a-zA-Z]{5,}", text)
        cands = [w for w in words if w.lower() not in _PRISON_STOP]
        if cands:
            cands.sort(key=len, reverse=True)
            return cands[0]

    # 3순위: 정답 선택지 단어 (기능어 아니면)
    if ch and a_idx is not None and a_idx < len(ch):
        raw = ch[a_idx]
        ans = raw.split(") ", 1)[-1] if ") " in raw else raw
        ans = ans.strip()
        if len(ans) >= 3 and ans.lower() not in _PRISON_STOP:
            return ans

    # 4순위: 선택지 중 아무 단어라도 (마지막 보루)
    if ch:
        for _c in ch:
            _w = (_c.split(") ", 1)[-1] if ") " in _c else _c).strip()
            if len(_w) >= 3:
                return _w
    return None

def _add_to_prison(word, source, sentence="", kr="", cat=""):
    """포로수용소에 단어 추가 (중복 없이)"""
    if not word or len(word) < 2:
        return
    try:
        # JSONDecodeError 안전 처리
        try:
            st_data = load_storage()
        except Exception:
            st_data = {"saved_questions": [], "saved_expressions": []}
        if "word_prison" not in st_data:
            st_data["word_prison"] = []
        # 중복 체크
        if any(p.get("word","").lower() == word.lower() for p in st_data["word_prison"]):
            return
        import datetime as _pdt
        st_data["word_prison"].append({
            "word":           word,
            "kr":             kr,
            "source":         source,
            "sentence":       sentence,
            "captured_date":  _pdt.datetime.now().strftime("%Y-%m-%d"),
            "correct_streak": 0,
            "last_reviewed":  None,
            "cat":            cat,
        })
        save_storage(st_data)
    except Exception:
        pass

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
button[kind="secondary"]{background:#000000!important;color:#fff!important;border:2px solid #8833ff!important;border-radius:14px!important;font-size:1.0rem!important;font-weight:900!important;padding:0.4rem 0.6rem!important;}
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
    border-radius:32px;padding:24px 16px 16px 16px;border:3px solid #8833ff;
    box-shadow:0 8px 40px rgba(255,215,0,0.2);text-align:center;}
.sg-rmt-t{font-size:1.12rem;font-weight:900;
    background:linear-gradient(90deg,#8833ff,#cc88ff,#8833ff);
    background-size:300% 300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
    animation:rb 4s ease infinite;letter-spacing:2px;}
.sg-nag{background:#000000;border:2px solid #8833ff;border-radius:18px;padding:14px;margin:12px 0;text-align:center;}
.sg-nag-t{font-size:1.0rem;font-weight:900;color:#cc88ff;text-shadow:0 0 12px rgba(136,51,255,0.4);}
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
# ════════════════════════════════════════
# PHASE: LOBBY
# 기능: 포로사령부 메인 - 전장 선택 (P5 전쟁포로 / P7 전쟁포로)
# ════════════════════════════════════════
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
    @keyframes fireGlow{0%,100%{text-shadow:0 0 20px #8833ff,0 0 40px #6600cc;}50%{text-shadow:0 0 35px #aa66ff,0 0 60px #8833ff;}}
    @keyframes stageIn{from{opacity:0;transform:translateY(25px);}to{opacity:1;transform:translateY(0);}}
    @keyframes firePulse{0%,100%{box-shadow:0 0 25px rgba(255,136,0,0.5),0 0 50px rgba(255,68,0,0.2);}50%{box-shadow:0 0 45px rgba(255,215,0,0.9),0 0 80px rgba(255,136,0,0.5);}}
    @keyframes nagFade{0%{opacity:0;transform:translateY(8px)}100%{opacity:1;transform:translateY(0)}}

    .rv-title{text-align:center;padding:16px 8px 6px 8px;}
    .rv-title h1{font-size:1.5rem!important;font-size:3.2rem;font-weight:900;letter-spacing:6px;color:#aa66ff;animation:fireGlow 2.5s ease infinite;margin:0;}
    .rv-title p{font-size:1.0rem;color:#9966ff;font-weight:900;letter-spacing:3px;margin:4px 0 0 0;}

    .rv-stage{animation:stageIn 0.5s ease;border-radius:20px;padding:18px 12px;margin:8px 0;}
    .rv-stage-1{background:linear-gradient(145deg,#0a0500,#150900);border:2px solid rgba(255,136,0,0.6);box-shadow:0 0 20px rgba(255,136,0,0.1);}
    .rv-stage-2p5{background:linear-gradient(145deg,#0a0000,#180500);border:2px solid rgba(255,68,0,0.6);box-shadow:0 0 20px rgba(255,68,0,0.1);}
    .rv-stage-2p7{background:linear-gradient(145deg,#080500,#150a00);border:2px solid rgba(255,170,0,0.6);box-shadow:0 0 20px rgba(255,170,0,0.1);}
    .rv-stage-3{background:linear-gradient(145deg,#0a0600,#1a0800);border:2px solid rgba(255,215,0,0.7);box-shadow:0 0 30px rgba(255,215,0,0.15);}

    .rv-act{font-size:0.7rem;font-weight:900;letter-spacing:4px;margin-bottom:8px;text-align:center;}
    .rv-act-1{color:#aa66ff;}
    .rv-act-2p5{color:#8833ff;}
    .rv-act-2p7{color:#ffaa00;}
    .rv-act-3{color:#aa66ff;}

    .rv-msg{font-size:1.25rem;font-weight:900;color:#fff;text-align:center;line-height:1.5;margin-bottom:12px;}
    .rv-msg .fire{color:#9966ff;}
    .rv-msg .gold{color:#aa66ff;}
    .rv-msg .red{color:#ff4444;}
    .rv-msg .cyan{color:#00ffcc;}

    .rv-confirmed{text-align:center;padding:6px;margin-bottom:8px;}
    .rv-confirmed span{font-size:1rem;color:#aa66ff;font-weight:900;background:rgba(136,51,255,0.15);padding:5px 14px;border-radius:20px;border:1px solid rgba(136,51,255,0.5);}

    button[kind="secondary"]{
        background:#0e0028!important;border:2px solid rgba(136,51,255,0.7)!important;
        border-radius:14px!important;font-size:1.3rem!important;font-weight:900!important;
        padding:14px 8px!important;color:#e0e0e0!important;min-height:64px!important;
    }
    button[kind="secondary"] p{font-size:1.3rem!important;font-weight:900!important;white-space:pre-line!important;line-height:1.3!important;text-align:center!important;}

    button[data-testid="stBaseButton-primary"]{
        background:linear-gradient(135deg,#3a1500,#7a2a00,#aa4400)!important;
        border:2px solid #8833ff!important;font-size:1.1rem!important;font-weight:900!important;
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
        <div style="font-size:1.8rem;font-weight:900;color:#cc88ff;letter-spacing:5px;">💀 포로사령부</div>
        <div style="font-size:0.65rem;color:#9966ff;letter-spacing:3px;margin-top:2px;">POW HQ · FINAL TRAINING</div>
        <div style="display:flex;align-items:center;justify-content:center;gap:8px;margin-top:4px;">
            <div style="height:1px;width:60px;background:linear-gradient(90deg,transparent,#8833ff);"></div>
            <div style="font-size:0.7rem;color:#aa66ff;opacity:0.9;">틀린 문제가 무기가 된다 — 반복이 실력이다</div>
            <div style="height:1px;width:60px;background:linear-gradient(90deg,#8833ff,transparent);"></div>
        </div>
    </div>''', unsafe_allow_html=True)

    _rv_battle = st.session_state.get("rv_battle", None)
    _rv_mode = st.session_state.get("rv_mode", None)

    import streamlit.components.v1 as _nc
    _nc.html("""<div style='background:rgba(10,5,20,0.96);border:1.5px solid #8833ff;border-radius:10px;padding:9px 14px;display:flex;align-items:center;gap:10px;'><span style='font-size:18px;animation:skB 0.9s ease-in-out infinite;display:inline-block;flex-shrink:0;'>💀</span><div style='font-size:12px;font-weight:900;color:#fff;min-height:18px;' id='nt'></div></div><style>@keyframes skB{0%,100%{transform:scale(1)}50%{transform:scale(1.2)}}</style><script>(function(){var KEY='snapq_tour_day';var today=new Date().toISOString().slice(0,10);var raw=localStorage.getItem(KEY);var data=raw?JSON.parse(raw):{first:''};if(!data.first){data.first=today;localStorage.setItem(KEY,JSON.stringify(data));}var diff=(new Date(today)-new Date(data.first))/(1000*60*60*24);var msgs=diff<3?["📊 정답률 낮으면 복습이 답! 숫자 올라야 실력!", "⚔️ 화력전 약점 박살내러 당장 출격해!", "📖 P7문장=P5문제. 결국 토익 만점!", "📊 기록이 쌓이면 성장! P5·P7 80% 목표!"]:["💀 오늘도 포로 심문 준비 됐어?", "⚔️ 틀린 문제 반복이 진짜 실력!", "📖 해독 포로 정복하면 P5도 올라!"];var el=document.getElementById('nt'),mi=0,ci=0;function run(){var txt=msgs[mi%msgs.length];if(ci<txt.length){el.textContent+=txt[ci++];setTimeout(run,50);}else{setTimeout(function(){el.textContent='';ci=0;mi++;run();},3000);}}setTimeout(run,600);})();</script>""", height=52)
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
            <div style="text-align:center;font-size:0.75rem;font-weight:900;color:#cc88ff;letter-spacing:2px;margin-bottom:8px;">📊 나의 전투 기록</div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;text-align:center;gap:4px;border-bottom:1px solid #2a2a3a;padding-bottom:8px;">
                <div style="border-right:1px solid #2a2a3a;">
                    <div style="font-size:0.65rem;color:#aaa;margin-bottom:3px;">P5 정답률</div>
                    <div style="font-size:1.2rem;font-weight:900;color:#ffcc44;">{p5_rate_disp}</div>
                </div>
                <div style="border-right:1px solid #2a2a3a;">
                    <div style="font-size:0.65rem;color:#aaa;margin-bottom:3px;">P5 저장</div>
                    <div style="font-size:1.2rem;font-weight:900;color:#cc88ff;">{p5_save_cnt}개</div>
                </div>
                <div style="border-right:1px solid #2a2a3a;">
                    <div style="font-size:0.65rem;color:#aaa;margin-bottom:3px;">P7 무기</div>
                    <div style="font-size:1.2rem;font-weight:900;color:#cc88ff;">{p7_weapon_cnt}개</div>
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
            st.markdown('''<div style="background:#0e0628;border:2px solid #8833ff;border-radius:14px;overflow:hidden;margin-bottom:6px;">
                <div style="background:#1a0800;padding:6px;text-align:center;font-size:0.85rem;font-weight:900;color:#ff8833;letter-spacing:1px;">🔥⚡ 화력전 포로 ⚡🔥</div>
                <div style="padding:14px 10px 10px 10px;text-align:center;">
                    <div style="font-size:2.2rem;">⚔️</div>
                    <div style="font-size:1.0rem;color:#ffcc99;margin-top:4px;font-weight:700;">문법 · 어휘</div>
                    <div style="font-size:0.8rem;color:#aaa;margin-top:2px;">틀린 문제 박살!</div>
                </div>
            </div>''', unsafe_allow_html=True)
            if st.button("출격!", key="rv_p5", use_container_width=True):
                st.session_state.rv_battle = "p5"; st.rerun()
        with c2:
            st.markdown('''<div style="background:#05080f;border:2px solid #8833ff;border-radius:14px;overflow:hidden;margin-bottom:6px;">
                <div style="background:#001828;padding:6px;text-align:center;font-size:0.85rem;font-weight:900;color:#00ccee;letter-spacing:1px;">📡✨ 해독 포로 ✨📡</div>
                <div style="padding:14px 10px 10px 10px;text-align:center;">
                    <div style="font-size:2.2rem;">📖</div>
                    <div style="font-size:1.0rem;color:#aaddff;margin-top:4px;font-weight:700;">독해 · 무기 획득</div>
                    <div style="font-size:0.8rem;color:#aaa;margin-top:2px;">문장으로 무기 장착!</div>
                </div>
            </div>''', unsafe_allow_html=True)
            if st.button("출격!", key="rv_p7", use_container_width=True):
                st.session_state.rv_battle = "p7"; st.rerun()

    # ━━━ 2막 P5: 전투 방식 선택 ━━━
    elif _rv_battle == "p5" and not _rv_mode:
        st.markdown('''<div style="text-align:center;margin-bottom:8px;">
            <span style="background:#1a0838;border:1.5px solid #8833ff;border-radius:12px;padding:5px 18px;font-size:0.9rem;font-weight:900;color:#cc88ff;">⚡ 화력전 포로</span>
        </div>''', unsafe_allow_html=True)

        # 학습모드 카드
        # 학습모드 — 지붕 라벨 + 카드 + 버튼
        st.markdown('''<div style="display:flex;align-items:flex-end;margin-bottom:0;">
            <div style="background:#150830;border:2px solid #8833ff;border-bottom:none;border-radius:8px 8px 0 0;padding:4px 14px;font-size:0.85rem;font-weight:900;color:#cc88ff;display:inline-block;">📋 정밀 심문</div>
        </div>''', unsafe_allow_html=True)
        _c1, _c2 = st.columns([3, 1])
        with _c1:
            st.markdown(f'''<div style="background:#0e0628;border:2px solid #8833ff;border-top:none;border-radius:0 12px 12px 12px;padding:12px 14px;min-height:82px;">
                <div style="font-size:1.05rem;font-weight:900;color:#ffffff;letter-spacing:1px;">🗡️ 오답 격파</div>
                <div style="font-size:0.9rem;color:#55ffbb;margin-top:5px;font-weight:700;">틀린 문제만 골라<br>완전히 내 것으로!</div>
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
            <div style="background:#0e0025;border:2px solid #6622cc;border-bottom:none;border-radius:8px 8px 0 0;padding:4px 14px;font-size:0.85rem;font-weight:900;color:#aa66ff;display:inline-block;">💥 생존 심문</div>
            <div style="background:#1a0838;border:2px solid #6622cc;border-bottom:none;border-radius:8px 8px 0 0;padding:4px 14px;font-size:0.8rem;font-weight:900;color:#aa66ff;display:inline-block;">💣 33초 시한폭탄</div>
        </div>''', unsafe_allow_html=True)
        _c3, _c4 = st.columns([3, 1])
        with _c3:
            st.markdown(f'''<div style="background:#0e0628;border:2px solid #6622cc;border-top:none;border-radius:0 12px 12px 12px;padding:12px 14px;min-height:82px;">
                <div style="font-size:1.05rem;font-weight:900;color:#ffffff;letter-spacing:1px;">5문제 생존전투!</div>
                <div style="font-size:0.9rem;color:#ffdd66;margin-top:5px;font-weight:700;">못 맞추면 💥 폭파 —<br>살아남아라!</div>
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
            <span style="background:#1a0838;border:1.5px solid #6622cc;border-radius:12px;padding:5px 18px;font-size:0.9rem;font-weight:900;color:#aa88ff;">📡 해독 포로</span>
        </div>''', unsafe_allow_html=True)
        
        # 학습모드 지붕
        st.markdown('''<div style="display:flex;align-items:flex-end;margin-bottom:0;">
            <div style="background:#150830;border:2px solid #8833ff;border-bottom:none;border-radius:8px 8px 0 0;padding:4px 14px;font-size:0.85rem;font-weight:900;color:#cc88ff;display:inline-block;">📋 정밀 심문</div>
        </div>''', unsafe_allow_html=True)
        _p7c1, _p7c2 = st.columns([3, 1])
        with _p7c1:
            st.markdown(f'''<div style="background:#0e0628;border:2px solid #8833ff;border-top:none;border-radius:0 12px 12px 12px;padding:12px 14px;min-height:90px;">
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
            <div style="background:#0e0025;border:2px solid #6622cc;border-bottom:none;border-radius:8px 8px 0 0;padding:4px 14px;font-size:0.85rem;font-weight:900;color:#aa66ff;display:inline-block;">💥 생존 심문</div>
            <div style="background:#1a0838;border:2px solid #6622cc;border-bottom:none;border-radius:8px 8px 0 0;padding:4px 14px;font-size:0.8rem;font-weight:900;color:#aa66ff;display:inline-block;">💣 33초 시한폭탄</div>
        </div>''', unsafe_allow_html=True)
        _p7c3, _p7c4 = st.columns([3, 1])
        with _p7c3:
            st.markdown(f'''<div style="background:#0e0628;border:2px solid #6622cc;border-top:none;border-radius:0 12px 12px 12px;padding:12px 14px;min-height:90px;">
                <div style="font-size:1.05rem;font-weight:900;color:#ffffff;">5문제 생존전투!</div>
                <div style="font-size:0.9rem;color:#ffdd66;margin-top:5px;font-weight:700;">문장 속 빈칸 — 33초 안에 맞춰라!</div>
                <div style="font-size:0.82rem;color:#ffcc88;margin-top:3px;font-weight:600;">못 맞추면 💥 폭파 —<br>살아남아라!</div>
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
            if st.button("⚡ 화력전", key="sg_nav1", use_container_width=True):
                for k in ["phase","cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx","br_saved"]: 
                    if k in st.session_state: del st.session_state[k]
                st.switch_page("pages/02_Firepower.py"); st.rerun()
        with mn2:
            if st.button("🏠 홈", key="sg_nav2", use_container_width=True):
                st.session_state.rv_mode=None; st.session_state.rv_battle=None
                _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
                if _nick:
                    st.query_params["nick"] = _nick
                    st.query_params["ag"] = "1"
                st.switch_page("main_hub.py")
        with mn3:
            if st.button("📡 암호해독", key="sg_nav3", use_container_width=True):
                st.session_state.rv_mode=None; st.session_state.rv_battle=None
                st.switch_page("pages/04_Decrypt_Op.py")
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

    ans = q["ch"][q["a"]]
    clean = ans.split(") ",1)[-1] if ") " in ans else ans
    sent = q["text"].replace("_______", f'<span style="color:#00ffaa;font-weight:900;border-bottom:2px solid #00ffaa;padding:0 3px;text-shadow:0 0 8px rgba(0,255,170,0.6);">{clean}</span>')
    kr   = q.get("kr","")
    exk  = q.get("exk","")
    cat  = q.get("cat","")
    _prog = int((bi / max(len(p5_data),1)) * 100)
    _rem  = len(p5_data) - bi - 1

    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
    div[data-testid="stHorizontalBlock"] button{
        animation:none!important;transform:none!important;
        border:1.5px solid rgba(100,150,200,0.35)!important;
        color:#4a6688!important;background:#07090f!important;
        font-weight:700!important;font-size:0.88rem!important;
        border-radius:10px!important;min-height:44px!important;
    }
    div[data-testid="stHorizontalBlock"] button p{
        color:#4a6688!important;font-weight:700!important;font-size:0.88rem!important;
    }
    div[data-testid="stHorizontalBlock"] button:hover{
        border-color:rgba(100,180,255,0.6)!important;color:#88aacc!important;
    }
    div[data-testid="stHorizontalBlock"] button:disabled{opacity:0.25!important;}
    </style>""", unsafe_allow_html=True)

    st.markdown(f'''<div style="text-align:center;padding:6px 0 4px;">
      <div style="font-size:7px;color:#224433;letter-spacing:4px;margin-bottom:3px;font-weight:700;">POW HEADQUARTERS · INTEL FILE</div>
      <div style="font-family:Orbitron,monospace;font-size:1.1rem;font-weight:900;color:#aa66ff;letter-spacing:3px;">☠️ STUDY MODE · DEBRIEFING</div>
    </div>''', unsafe_allow_html=True)

    st.markdown(f'''<div style="margin:3px 0 6px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
        <span style="font-size:8px;color:#336655;letter-spacing:3px;font-weight:700;">PRISONER {bi+1} / {len(p5_data)}</span>
        <span style="background:#0a1a10;border:1px solid #4400aa;border-radius:20px;
          padding:2px 10px;font-size:8px;color:#aa66ff;font-weight:700;letter-spacing:1px;">
          ⚔ {_rem} 포로 대기중</span>
      </div>
      <div style="background:#0a0c10;border-radius:4px;height:7px;border:1px solid #112211;">
        <div style="background:linear-gradient(90deg,#4400aa,#8833ff);height:5px;margin:1px;
          border-radius:3px;width:{_prog}%;box-shadow:0 0 8px rgba(68,204,136,0.5);"></div>
      </div>
    </div>''', unsafe_allow_html=True)

    st.markdown(f'''<div style="background:#06090f;border:1.5px solid rgba(0,212,150,0.35);
        border-left:4px solid #00cc88;border-radius:14px;padding:14px 14px 12px;margin:3px 0;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
        <span style="font-size:7px;color:#336655;letter-spacing:3px;font-weight:700;">◈ INTEL FILE #{bi+1:03d}</span>
        <span style="background:#0a1808;border:1px solid #4400aa;border-radius:6px;
          padding:2px 10px;font-size:8px;color:#aa66ff;font-weight:900;letter-spacing:1px;">{cat}</span>
      </div>
      <div style="font-size:1.0rem;font-weight:900;color:#ddeeff;line-height:1.75;
        margin-bottom:10px;word-break:keep-all;">{sent}</div>
      <div style="height:1px;background:linear-gradient(90deg,#00cc88,transparent);margin:8px 0;opacity:0.3;"></div>
      <div style="font-size:0.85rem;font-weight:600;color:#7a9a8a;line-height:1.65;margin-bottom:8px;">📖 {kr}</div>
      <div style="background:#0a0420;border-left:3px solid #8833ff;border-radius:0 8px 8px 0;padding:7px 10px;">
        <span style="font-size:0.82rem;font-weight:700;color:#aa66ff;">💡 {exk}</span>
      </div>
    </div>''', unsafe_allow_html=True)

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
    st.markdown("""<style>
    .exam-btn div[data-testid="stButton"] button{
        background:#0e0028!important;border:2px solid #8833ff!important;
        border-radius:12px!important;color:#ff9944!important;
        font-size:0.92rem!important;font-weight:900!important;min-height:50px!important;}
    .exam-btn div[data-testid="stButton"] button p{color:#ff9944!important;font-size:0.92rem!important;font-weight:900!important;}
    .back-btn div[data-testid="stButton"] button{
        background:#05050e!important;border:1px solid #151525!important;
        border-radius:10px!important;color:#3d5066!important;
        font-size:0.82rem!important;min-height:44px!important;}
    .back-btn div[data-testid="stButton"] button p{color:#3d5066!important;}
    </style>""", unsafe_allow_html=True)
    _rb4, _rb5 = st.columns([3, 1])
    with _rb4:
        st.markdown('<div class="exam-btn">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)
    with _rb5:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("↩ 돌아가기", key="back_lobby", use_container_width=True):
            st.session_state.sg_phase = "lobby"; st.session_state.rv_battle = None; st.session_state.rv_mode = None; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

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
        twarn = '<div style="text-align:center;font-size:1.2rem;color:#ff0000;font-weight:900;margin:8px 0 6px;">💀💀 폭발한다!! 💀💀</div>'
    elif rem <= 10:
        bg_css = "background:linear-gradient(135deg,#1e0815,#2e0a25 30%,#1e0818 70%,#1e0815)!important;"
        tcl = "#ff2200"; tsz = "2rem"; tglow = "text-shadow:0 0 25px #ff2200,0 0 50px #ff0000;"
        twarn = '<div style="text-align:center;font-size:1.0rem;color:#ff4444;font-weight:900;margin:8px 0 6px;">💀 서둘러!! 또 틀릴 거야?! 💀</div>'
    elif rem <= 15:
        bg_css = "background:linear-gradient(135deg,#160a1e,#220e30 30%,#160a22 70%,#160a1e)!important;"
        tcl = "#ff6600"; tsz = "1.6rem"; tglow = "text-shadow:0 0 15px #ff6600;"
        twarn = '<div style="text-align:center;font-size:0.9rem;color:#ff8844;font-weight:900;margin:6px 0 4px;">⚡ 서둘러!! ⚡</div>'
    elif rem <= 20:
        bg_css = "background:linear-gradient(135deg,#121530,#1e1845 30%,#121838 70%,#121530)!important;"
        tcl = "#ffaa00"; tsz = "1.4rem"; tglow = "text-shadow:0 0 8px #ffaa00;"
        twarn = ""
    else:
        bg_css = ""
        tcl = "#aa66ff"; tsz = "1.2rem"; tglow = ""; twarn = ""
    tpct = int(rem / 33 * 100)
    q_border = "rgba(255,50,50,0.6)" if rem <= 10 else "rgba(100,140,255,0.4)"
    q_shadow = "0 0 40px rgba(255,0,0,0.2)" if rem <= 10 else "0 0 30px rgba(100,140,255,0.15)"
    _exam_labels = ["A","B","C","D"]
    _exam_cfg = [
        ("ex-ans-a","#ff6633","#160800","rgba(255,102,51,0.55)"),
        ("ex-ans-b","#00E5FF","#001518","rgba(0,229,255,0.55)"),
        ("ex-ans-c","#FF2D55","#140008","rgba(255,45,85,0.55)"),
        ("ex-ans-d","#44FF88","#001408","rgba(68,255,136,0.55)"),
    ]

    if bg_css:
        st.markdown(f'<style>.stApp{{{bg_css}}}</style>', unsafe_allow_html=True)

    # ── CSS: 버튼 공통 + id 래퍼 색상 ──
    _exam_css = """<style>
    .stMarkdown{margin:0!important;padding:0!important;}
    .element-container{margin:0!important;padding:0!important;}
    div[data-testid="stVerticalBlock"]{gap:3px!important;}
    div[data-testid="stButton"] button{
        min-height:46px!important;font-size:0.9rem!important;
        font-weight:800!important;border-radius:12px!important;
        text-align:left!important;padding:0.4rem 0.9rem!important;margin:0!important;
    }
    div[data-testid="stButton"] button p{font-size:0.9rem!important;font-weight:800!important;}
    """
    for _eid,_ecol,_ebg,_esh in _exam_cfg:
        _exam_css += (
            f'#btn-{_eid} div[data-testid="stButton"] button{{'
            f'border-left:5px solid {_ecol}!important;background:{_ebg}!important;'
            f'border-color:{_ecol}!important;color:{_ecol}!important;}}'
            f'#btn-{_eid} div[data-testid="stButton"] button p{{color:{_ecol}!important;}}'
            f'#btn-{_eid} div[data-testid="stButton"] button:hover{{box-shadow:0 0 22px {_esh}!important;}}'
        )
    _exam_css += "</style>"
    st.markdown(_exam_css, unsafe_allow_html=True)

    # ── HUD: 문제 진행 도트 ──
    _dots = '<div style="display:flex;justify-content:center;gap:8px;margin:2px 0 4px;">'
    for _di in range(len(qs)):
        if _di < qi:
            _dc="#aa66ff"; _db="rgba(170,102,255,0.15)"; _ds="0 0 10px #aa66ff"; _dd="✓"
        elif _di == qi:
            _dc=tcl; _db="rgba(100,140,255,0.12)"; _ds=f"0 0 14px {tcl}"; _dd=str(_di+1)
        else:
            _dc="#333"; _db="transparent"; _ds="none"; _dd=str(_di+1)
        _dots += (
            f'<div style="width:26px;height:26px;border-radius:50%;border:2px solid {_dc};'
            f'background:{_db};box-shadow:{_ds};display:flex;align-items:center;'
            f'justify-content:center;font-size:0.7rem;font-weight:900;color:{_dc};">{_dd}</div>'
        )
    _dots += '</div>'

    # ── 타이머 + 도트 + 바 + 경고 ──
    st.markdown(
        f'<div style="text-align:center;margin:2px 0;padding:2px;">'
        f'<span style="font-size:{tsz};font-weight:900;color:{tcl};'
        f'font-family:Impact,Arial Black,sans-serif;{tglow}">{rem}</span>'
        f'<span style="font-size:0.75rem;color:{tcl};opacity:0.7;">s</span></div>',
        unsafe_allow_html=True)
    st.markdown(_dots, unsafe_allow_html=True)
    bar_color = tcl if rem <= 15 else "#aa66ff"
    st.markdown(
        f'<div style="background:rgba(255,255,255,0.06);border-radius:10px;padding:2px;margin:2px 0;">'
        f'<div style="background:linear-gradient(90deg,{bar_color},{tcl});height:10px;'
        f'border-radius:8px;width:{tpct}%;transition:width 0.5s;"></div></div>',
        unsafe_allow_html=True)
    if twarn:
        st.markdown(twarn, unsafe_allow_html=True)

    # ── 문제 카드 (사이즈 축소) ──
    blank_text = q["text"].replace("_______", '<span style="border-bottom:3px solid #cc88ff;padding:0 10px;color:#88bbff;">________</span>')
    st.markdown(
        f'<div style="background:linear-gradient(145deg,#141435,#1c1c4a);'
        f'border:2px solid {q_border};border-radius:14px;padding:0.65rem 0.85rem;'
        f'margin:4px 0;box-shadow:{q_shadow};">'
        f'<div style="font-size:0.95rem;font-weight:900;color:#ffffff;line-height:1.55;">'
        f'{blank_text}</div></div>',
        unsafe_allow_html=True)

    # ── 답 버튼 4개 — div id 래퍼 + 클릭 로직 ──
    _prev_result_len = len(st.session_state.sg_exam_results)
    for i, ch in enumerate(q["ch"]):
        _ch_clean = ch.split(") ",1)[-1] if ") " in ch else ch
        _display  = f"【{_exam_labels[i]}】  {_ch_clean}"
        _eid      = _exam_cfg[i][0]
        st.markdown(f'<div id="btn-{_eid}">', unsafe_allow_html=True)
        if st.button(_display, key=f"ex_{qi}_{i}", use_container_width=True):
            ok = (i == q["a"])
            st.session_state.sg_exam_results.append(ok)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── forget_logs + phase 처리 (div-래퍼 루프에서 ok가 append된 경우) ──
    if len(st.session_state.sg_exam_results) > _prev_result_len:
        ok = st.session_state.sg_exam_results[-1]
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
            _first_wrong = q.get("first_wrong_date", q.get("saved_date", _today))
            try:
                _interval = (_dt.datetime.strptime(_today, "%Y-%m-%d") -
                             _dt.datetime.strptime(_first_wrong, "%Y-%m-%d")).days
            except:
                _interval = 0
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
                "finally_correct":  False,
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
            try:
                _pw = _extract_prison_word(
                    text=q.get("text",""),
                    ex_field=q.get("ex",""),
                    cat=q.get("cat",""),
                    ch=q.get("ch",[]),
                    a_idx=q.get("a",0)
                )
                if _pw:
                    _sent = q.get("text","").replace("_______", _pw)
                    _add_to_prison(
                        word=_pw,
                        source="P5 시험 오답",
                        sentence=_sent,
                        kr=q.get("kr",""),
                        cat=q.get("cat","")
                    )
            except Exception:
                pass
            st.session_state.sg_exam_wrong = True
            st.session_state.sg_phase = "p5_exam_result"; st.rerun()
        else:
            st.session_state.sg_exam_idx += 1
            st.rerun()
    # JS 스타일 주입 제거 — CSS id 래퍼 방식으로 대체

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
            <div style="font-size:0.95rem;color:#aa66ff;font-weight:700;">💀 폭탄이 터졌다... 넌 산산조각!</div>
        </div>''', unsafe_allow_html=True)
        st.markdown(f'''<div style="background:#0e0028;border:1.5px solid #8833ff;border-radius:12px;padding:10px;text-align:center;margin:8px 0;">
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
        if st.button("⚔️ 설욕전! 다시 싸운다!", key="retry_exam", use_container_width=True):
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
            if st.button("💀 포로사령부", key="retry_lobby", use_container_width=True):
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
            <div style="font-size:2.8rem;font-weight:900;color:#cc88ff;margin:6px 0;">🏆 생존!</div>
            <div style="font-size:0.95rem;color:#8833ff;font-weight:700;">폭탄을 이겨냈다! 진짜 전사!</div>
        </div>''', unsafe_allow_html=True)
        st.markdown(f'''<div style="background:#0c0c00;border:1.5px solid #8833ff;border-radius:12px;padding:10px;text-align:center;margin:8px 0;">
            <div style="font-size:1.6rem;font-weight:900;color:#cc88ff;">🏆 {ok_cnt} / 5</div>
        </div>''', unsafe_allow_html=True)
        st.markdown('''<div style="background:#0a0800;border:1px solid #8833ff;border-radius:10px;padding:8px;text-align:center;margin-bottom:8px;">
            <div style="font-size:0.85rem;color:#8833ff;font-weight:700;">⚡ 3번 반복하면 장기기억 전환율 3배!</div>
            <div style="font-size:0.75rem;color:#886600;margin-top:2px;">지금 이 기세로 한 번 더!</div>
        </div>''', unsafe_allow_html=True)
        if st.button("💀 한 번 더! 완전 정복!", key="retry_exam", use_container_width=True):
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
            if st.button("💀 포로사령부", key="retry_lobby", use_container_width=True):
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
            <div style="font-size:0.85rem;color:#888;margin-top:4px;">암호해독 작전 브리핑에서 어려운 문장을 저장하세요</div>
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
            if st.button("⚡ 시험모드!",key="sb_go_exam",use_container_width=True):
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
    st.markdown(f'''<div style="background:#150830;border:1.5px solid #8833ff;border-radius:14px;padding:8px 14px;text-align:center;margin-bottom:8px;">
        <div style="font-size:0.95rem;font-weight:700;color:#aa66ff;">📖 문장 퍼즐 배틀</div>
        <div style="font-size:0.8rem;color:#aaa;margin-top:2px;">{idx+1} / {total} 문장 &nbsp;|&nbsp; {_lv_label}</div>
        <div style="background:#0a0a1a;border-radius:4px;height:5px;margin-top:5px;"><div style="background:linear-gradient(90deg,#8833ff,#cc88ff);height:5px;border-radius:4px;width:{int((idx/max(total,1))*100)}%;"></div></div>
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
            st.markdown(f'''<div style="background:#0a0420;border:2px solid #aa66ff;border-radius:14px;padding:14px;text-align:center;margin-bottom:8px;">
                <div style="font-size:2rem;">🎯</div>
                <div style="font-size:1.3rem;font-weight:900;color:#aa66ff;margin-top:4px;">완벽해! 몸으로 익혔다!</div>
                <div style="font-size:0.9rem;color:#88ddaa;margin-top:4px;">이 문장, 이제 완전히 네 것!</div>
                <div style="font-size:0.8rem;color:#aa66ff;margin-top:6px;opacity:0.8;">현재 난이도: {_level_emoji} ({_level_msg})</div>
            </div>''', unsafe_allow_html=True)
            if st.button("▶ 다음 문장!",key="sb_next",use_container_width=True):
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
                if st.button("🔄 다시 도전!",key="sb_retry",use_container_width=True):
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
                        ans_html+=f'<span style="background:#0a0420;border:2px solid #aa66ff;border-radius:8px;padding:2px 10px;color:#aa66ff;font-weight:900;margin:0 2px;">{_w}</span> '
                    else:
                        ans_html+=f'<span style="color:#ddddff;">{_w}</span> '
                st.markdown(f'''<div style="background:#0a1a0a;border:2px solid #aa66ff;border-radius:14px;padding:12px 14px;margin-bottom:8px;">
                    <div style="font-size:0.7rem;color:#aa66ff;letter-spacing:2px;margin-bottom:6px;">✅ 정답 문장</div>
                    <div style="font-size:1.05rem;font-weight:600;line-height:2.0;">{ans_html}</div>
                </div>''', unsafe_allow_html=True)
                # 잔소리 멘트 (1번만)
                st.markdown(f'''<div style="background:#1a0a00;border:2px solid #ff8844;border-radius:14px;padding:10px 14px;margin-bottom:8px;text-align:center;">
                    <div style="font-size:1.05rem;font-weight:800;color:#ffaa55;">{msg}</div>
                </div>''', unsafe_allow_html=True)
                if st.button("▶ 다음 문장!",key="sb_next2",use_container_width=True):
                    # ★ 2번 틀리면 레벨 DOWN
                    st.session_state.puzzle_streak = 0
                    old_level = st.session_state.get("puzzle_blank_level", 2)
                    st.session_state.puzzle_blank_level = max(1, old_level - 1)
                    # ★ 포로수용소 — 퍼즐 오답: blank_order 중 1개 (가장 긴 단어)
                    try:
                        _pr_sent = item.get("sentences",[""])[0] if item.get("sentences") else item.get("expr","")
                        _pr_kr   = item.get("kr", item.get("meaning",""))
                        _bw_list = [w.strip(".,!?;:()") for w in blank_order if len(w.strip(".,!?;:()")) >= 3]
                        if _bw_list:
                            _best = max(_bw_list, key=len)
                            if _best.lower() not in _PRISON_STOP:
                                _add_to_prison(_best, "퍼즐 오답", _pr_sent, _pr_kr, "vocabulary")
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
                if _i<len(selected): s0_html+=f'<span style="background:#0a0420;border:2px solid #aa66ff;border-radius:8px;padding:2px 10px;color:#aa66ff;font-weight:700;margin:0 3px;">{selected[_i]}</span>'
                else: s0_html+='<span style="background:#0a0a1a;border:2px dashed #8833ff;border-radius:8px;padding:2px 18px;color:#333;margin:0 3px;">_____</span>'
        st.markdown(f'''<div style="background:#150830;border:1.5px solid #8833ff;border-radius:12px;padding:12px 14px;margin-bottom:8px;font-size:1.05rem;font-weight:600;line-height:2.2;">{s0_html}</div>''', unsafe_allow_html=True)
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
            # ★ 포로수용소 — 건너뛴 문장 핵심 단어 1개
            try:
                _sk_sent = item.get("sentences",[""])[0] if item.get("sentences") else item.get("expr","")
                _sk_kr   = item.get("kr", item.get("meaning",""))
                _sk_words = [w.strip(".,!?;:()") for w in st.session_state.get("sb_blank_order",[]) if len(w.strip(".,!?;:()")) >= 3]
                if _sk_words:
                    _sk_best = max(_sk_words, key=len)
                    if _sk_best.lower() not in _PRISON_STOP:
                        _add_to_prison(_sk_best, "퍼즐 건너뜀", _sk_sent, _sk_kr, "vocabulary")
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
            <div style="font-size:3.5rem;font-weight:900;color:#aa66ff;text-shadow:0 0 30px #00ff66;">🎉 정복 완료! 🎉</div>
            <div style="font-size:1.5rem;color:#88ffbb;font-weight:800;margin-top:8px;">4전 모두 돌파! 단어가 내 것이 됐다!</div>
        </div>''', unsafe_allow_html=True)
    else:
        st.markdown(f'''<div style="text-align:center;padding:1.5rem;">
            <div style="font-size:3.5rem;font-weight:900;color:#cc88ff;text-shadow:0 0 20px #8833ff;">💥 여기까지! 💥</div>
        </div>''', unsafe_allow_html=True)

    st.markdown(f'<div style="text-align:center;font-size:1.5rem;color:#ccc;font-weight:700;">✅ {ok_cnt}/{total_answered} 정답</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🧠 다시 밟고\n완전정복!", key="sv_retry", use_container_width=True):
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
        if st.button("🔥 사령부 귀환", key="sv_back", type="secondary", use_container_width=True):
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
    if rem<=5: bg_css="background:linear-gradient(135deg,#2a0808,#3a0a1a)!important;"; tcl="#ff0000"; tsz="2.5rem"; tglow="text-shadow:0 0 40px #ff0000;"; twarn='<div style="text-align:center;font-size:1.2rem;color:#ff0000;font-weight:900;margin:8px 0 6px;">💀 폭발한다!! 💀</div>'
    elif rem<=10: bg_css="background:linear-gradient(135deg,#1e0815,#2e0a25)!important;"; tcl="#ff2200"; tsz="2rem"; tglow="text-shadow:0 0 25px #ff2200;"; twarn='<div style="text-align:center;font-size:1.0rem;color:#ff4444;font-weight:900;margin:8px 0 6px;">💀 서둘러!! 💀</div>'
    elif rem<=15: bg_css=""; tcl="#ff6600"; tsz="1.6rem"; tglow="text-shadow:0 0 15px #ff6600;"; twarn='<div style="text-align:center;font-size:0.9rem;color:#ff8844;font-weight:900;margin:6px 0 4px;">⚡ 서둘러!!</div>'
    else: bg_css=""; tcl="#aa66ff"; tsz="1.2rem"; tglow=""; twarn=""
    tpct=int(rem/30*100)
    if bg_css: st.markdown(f'<style>.stApp{{{bg_css}}}</style>',unsafe_allow_html=True)
    ok_cnt=sum(1 for r in st.session_state.sg_combo_results if r)
    needed=max(0,3-ok_cnt); remain_q=total_qs-cidx
    survive_color="#aa66ff" if ok_cnt>=3 else "#ffcc00" if needed<=remain_q else "#ff4444"
    st.markdown(f'<div style="background:linear-gradient(180deg,#0a0118,#1a0830);border:2.5px solid #8833ff;border-radius:22px;padding:8px;text-align:center;"><div style="font-size:1.0rem;font-weight:900;color:#aa66ff;">⚡ P7 실전 블랭크 · 5문제 중 3개 이상!</div><div style="display:flex;justify-content:space-around;margin-top:6px;"><span style="font-size:0.85rem;font-weight:900;color:#aa66ff;">✅ {ok_cnt}개</span><span style="font-size:0.85rem;font-weight:900;color:#ffcc00;">{cidx+1}/{total_qs}</span><span style="font-size:0.85rem;font-weight:900;color:{survive_color};">필요 {needed}개</span></div></div>',unsafe_allow_html=True)
    st.markdown(f'<div style="text-align:center;margin:4px 0;"><span style="font-size:{tsz};font-weight:900;color:{tcl};{tglow}">{rem}</span><span style="font-size:0.8rem;color:{tcl};opacity:0.7;">s</span></div>',unsafe_allow_html=True)
    st.markdown(f'<div style="background:rgba(255,255,255,0.06);border-radius:12px;padding:3px;margin:4px 0;"><div style="background:linear-gradient(90deg,{tcl},#8833ff);height:12px;border-radius:10px;width:{tpct}%;"></div></div>',unsafe_allow_html=True)
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
    blank_styled=blank_sent.replace("_______",'<span style="border-bottom:3px solid #8833ff;padding:0 8px;color:#cc88ff;font-weight:900;">_______</span>')
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
            if i==correct_idx:
                results.append(True); st.session_state.sg_combo_score=score+100; st.session_state.sg_combo_count=combo+1
            else:
                results.append(False)
                # ★ 포로수용소 — P7 오답 시 key_word 자동 저장
                try:
                    _kw = correct_ans.strip(".,!?;:()")
                    if _kw and len(_kw) >= 3 and _kw.lower() not in _PRISON_STOP:
                        _pr_sent = sentences[0] if sentences else ""
                        _pr_kr = q_item.get("meaning", q_item.get("kr",""))
                        _add_to_prison(
                            word=_kw,
                            source="P7 어휘 오답",
                            sentence=_pr_sent,
                            kr=_pr_kr,
                            cat="vocabulary"
                        )
                except Exception:
                    pass
            st.session_state.sg_combo_results=results; st.session_state.sg_combo_idx=cidx+1
            wrong_cnt=sum(1 for r in results if not r)
            if wrong_cnt>(total_qs-3): st.session_state.sg_combo_over=True
            st.rerun()

# ════════════════════════════════
# 단어 저장고 — 무기 관리 (삭제)
# ════════════════════════════════
if st.session_state.get("rv_mode") == "p7_vault":
    st.markdown('''<div style="text-align:center;padding:1rem 0;">
        <div style="font-size:1.8rem;font-weight:900;color:#cc88ff;">⚔️ 무기 저장고</div>
        <div style="font-size:0.9rem;color:#9966ff;margin-top:4px;font-weight:700;">실전 무기를 점검하고 · 불필요한 건 제거하라!</div>
    </div>''', unsafe_allow_html=True)
    storage2=load_storage()
    voca_list=storage2.get("saved_expressions",[])
    if not voca_list:
        st.markdown('''<div style="text-align:center;background:#0e0628;border-radius:12px;padding:2rem;color:#aa66ff;border:1.5px solid #6622cc;">
            <div style="font-size:2rem;">📭</div>
            <div style="font-size:1rem;margin-top:8px;">저장된 문장이 없어요!</div>
            <div style="font-size:0.85rem;margin-top:4px;">암호해독 작전 브리핑에서 어려운 문장을 저장하세요</div>
        </div>''', unsafe_allow_html=True)
    else:
        for idx,item in enumerate(voca_list):
            sentences=item.get("sentences",[])
            sentence=sentences[0] if sentences else item.get("expr","")
            kr_full=item.get("kr","") or item.get("meaning","")
            kr_sents=[x.strip() for x in kr_full.replace("!","!|").replace("?","?|").replace(".",".|").split("|") if x.strip()]
            sent_kr=kr_sents[0] if kr_sents else kr_full
            st.markdown(f'''<div style="background:#0e0628;border:1.5px solid #4400aa;border-radius:12px;padding:12px 14px;margin-bottom:4px;">
                <div style="font-size:15px;font-weight:700;color:#ddeeff;line-height:1.6;">{sentence}</div>
                <div style="font-size:13px;color:#aa88dd;margin-top:4px;">{sent_kr}</div>
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
            <div style="font-size:2.8rem;font-weight:900;color:#cc88ff;text-shadow:0 0 30px #8833ff,0 0 60px #6600cc;margin:6px 0;">🏆 신기록!</div>
            <div style="font-size:0.9rem;color:#8833ff;font-weight:700;">새로운 최고 기록 달성!</div>
        </div>''', unsafe_allow_html=True)
        st.markdown(f'''<div style="background:#0c0c00;border:2px solid #8833ff;border-radius:14px;padding:14px;text-align:center;margin:8px 0;">
            <div style="font-size:0.75rem;color:#886600;margin-bottom:4px;">🎉 NEW RECORD</div>
            <div style="font-size:2.8rem;font-weight:900;color:#cc88ff;text-shadow:0 0 20px rgba(136,51,255,0.5);">⭐ {score}</div>
        </div>''', unsafe_allow_html=True)
    else:
        st.markdown('<style>.stApp{background:#080000!important;}</style>', unsafe_allow_html=True)
        st.markdown(f'''<div style="text-align:center;padding:1rem 0 0.5rem 0;">
            <div style="font-size:0.9rem;letter-spacing:4px;opacity:0.5;">💣 🔥 💥 ☠️ ⚡ 💣 🔥</div>
            <div style="font-size:2.8rem;font-weight:900;color:#ff2200;text-shadow:0 0 20px #ff0000;margin:6px 0;">💀 전멸!</div>
            <div style="font-size:0.9rem;color:#aa66ff;font-weight:700;">💀 폭탄이 터졌다... 한 번 더 도전!</div>
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
    if st.button("💪 다시 덤벼! 이번엔 안 진다!", key="cb_retry", use_container_width=True):
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
    if st.button("🔥 사령부 귀환", key="cb_back", use_container_width=True):
        st.session_state.sg_phase = "lobby"; st.session_state.rv_battle = None; st.session_state.rv_mode = None; st.rerun()












# ════════════════════════════════════════
# PHASE: WORD_PRISON
# 기능: 포로 목록 표시 + 심문(퀴즈) 3종 — 뜻맞추기/빈칸채우기/타임어택
# EXTEND: 심문 퀴즈 기능 여기에 추가 예정 — 뜻맞추기/빈칸채우기/타임어택
# ════════════════════════════════════════
# ════════════════════════════════════════
# PHASE: WORD_PRISON — 극적인 심문실
# ════════════════════════════════════════
# ════════════════════════════════════════
# PHASE: WORD_PRISON — 극적인 심문실
# ════════════════════════════════════════
# ════════════════════════════════════════
# PHASE: WORD_PRISON — 극적인 심문실
# ════════════════════════════════════════
# ════════════════════════════════════════
# PHASE: WORD_PRISON — 극적인 심문실
# ════════════════════════════════════════
# ════════════════════════════════════════
# PHASE: WORD_PRISON — 극적인 심문실
# ════════════════════════════════════════
# ════════════════════════════════════════
# PHASE: WORD_PRISON — 극적인 심문실
# ════════════════════════════════════════
# ════════════════════════════════════════
# PHASE: WORD_PRISON — 극적인 심문실
# ════════════════════════════════════════
# ════════════════════════════════════════
# PHASE: WORD_PRISON — 극적인 심문실
# ════════════════════════════════════════
# ════════════════════════════════════════
# PHASE: WORD_PRISON — 극적인 심문실
# ════════════════════════════════════════
# ════════════════════════════════════════
# PHASE: WORD_PRISON — 극적인 심문실
# ════════════════════════════════════════
# ════════════════════════════════════════
# PHASE: WORD_PRISON — 극적인 심문실
# ════════════════════════════════════════
# ════════════════════════════════════════
# PHASE: WORD_PRISON — 극적인 심문실
# ════════════════════════════════════════
# ════════════════════════════════════════
# PHASE: WORD_PRISON — 극적인 심문실
# ════════════════════════════════════════
elif st.session_state.sg_phase == "word_prison":
    import datetime as _pr_dt2, random as _pr_random

    _nick = st.session_state.get("nickname","")

    st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
#MainMenu{visibility:hidden!important;}
header[data-testid="stHeader"]{height:0!important;overflow:hidden!important;}
.block-container{padding:8px 12px 20px!important;margin:0!important;}
div[data-testid="stVerticalBlock"]{gap:5px!important;}
.element-container{margin:0!important;padding:0!important;}
div[data-testid="stHorizontalBlock"]{gap:8px!important;margin:0!important;flex-wrap:nowrap!important;}
div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]{padding:0!important;min-width:0!important;flex:1!important;}
div[data-testid="stButton"] button{
  border-radius:14px!important;font-weight:800!important;min-height:44px!important;width:100%!important;
  background:#0e1020!important;border:1.5px solid #2a2d45!important;color:#c0c8e0!important;font-size:0.9rem!important;
}
div[data-testid="stButton"] button p{color:#c0c8e0!important;font-size:0.9rem!important;font-weight:800!important;}
#btn-know div[data-testid="stButton"] button{background:#081a0e!important;border:2.5px solid #22dd55!important;color:#aa66ff!important;min-height:64px!important;font-size:1.05rem!important;}
#btn-know div[data-testid="stButton"] button p{color:#aa66ff!important;font-size:1.05rem!important;font-weight:900!important;}
#btn-no div[data-testid="stButton"] button{background:#1a0808!important;border:2.5px solid #dd3322!important;color:#ff5544!important;min-height:64px!important;font-size:1.05rem!important;}
#btn-no div[data-testid="stButton"] button p{color:#ff5544!important;font-size:1.05rem!important;font-weight:900!important;}
#btn-flip div[data-testid="stButton"] button{background:#10102a!important;border:2.5px solid #6655ee!important;color:#cc99ff!important;min-height:58px!important;font-size:1rem!important;}
#btn-flip div[data-testid="stButton"] button p{color:#cc99ff!important;font-size:1rem!important;font-weight:900!important;}
#btn-start div[data-testid="stButton"] button{background:#0e0028!important;border:2.5px solid #8833ff!important;color:#cc88ff!important;min-height:64px!important;font-size:1.1rem!important;}
#btn-start div[data-testid="stButton"] button p{color:#cc88ff!important;font-size:1.1rem!important;font-weight:900!important;}

#btn-home div[data-testid="stButton"] button{background:#08080f!important;border:1px solid #1a1d2a!important;color:#3a4455!important;min-height:38px!important;font-size:0.8rem!important;}
#btn-home div[data-testid="stButton"] button p{color:#3a4455!important;font-size:0.8rem!important;}
#btn-back div[data-testid="stButton"] button{background:#08080f!important;border:1px solid #1a1d2a!important;color:#3a4455!important;min-height:36px!important;font-size:0.78rem!important;}
#btn-back div[data-testid="stButton"] button p{color:#3a4455!important;font-size:0.78rem!important;}
</style>""", unsafe_allow_html=True)

    _pr_st = load_storage()
    if "word_prison" not in _pr_st: _pr_st["word_prison"] = []
    _prisoners = _pr_st["word_prison"]
    _today_str2 = _pr_dt2.datetime.now().strftime("%Y-%m-%d")

    # 카테고리별 캐릭터 + 영/한 라벨
    # 기본 토익 어휘 사전 (kr 없을 때 fallback)
    _VOCAB_DICT = {
        "submit":"제출하다","submission":"제출","submitted":"제출된",
        "approve":"승인하다","approval":"승인","approved":"승인된",
        "policy":"정책","policies":"정책들",
        "regulation":"규정","regulations":"규정들",
        "comply":"준수하다","compliance":"준수",
        "enhance":"향상시키다","improvement":"개선","improve":"개선하다",
        "efficiency":"효율성","efficient":"효율적인",
        "establish":"설립하다","establishment":"설립",
        "maintain":"유지하다","maintenance":"유지",
        "implement":"시행하다","implementation":"시행",
        "evaluate":"평가하다","evaluation":"평가",
        "facilitate":"촉진하다","facilitate":"용이하게 하다",
        "require":"요구하다","requirement":"요구사항",
        "provide":"제공하다","provision":"제공",
        "ensure":"보장하다","guarantee":"보증하다",
        "announce":"발표하다","announcement":"발표",
        "consider":"고려하다","consideration":"고려",
        "conduct":"수행하다","procedure":"절차",
        "confirm":"확인하다","confirmation":"확인",
        "complete":"완료하다","completion":"완료",
        "notify":"통지하다","notification":"통지",
        "indicate":"나타내다","indication":"표시",
        "significant":"상당한","significantly":"상당히",
        "temporary":"임시의","temporarily":"일시적으로",
        "permanent":"영구적인","permanently":"영구적으로",
        "available":"이용 가능한","availability":"가용성",
        "efficient":"효율적인","effectively":"효과적으로",
        "effective":"효과적인","effectively":"효과적으로",
        "primary":"주요한","primarily":"주로",
        "additional":"추가적인","additionally":"추가로",
        "appropriate":"적절한","appropriately":"적절히",
        "responsible":"책임있는","responsibility":"책임",
        "opportunity":"기회","challenge":"도전",
        "strategy":"전략","strategic":"전략적인",
        "performance":"성과","perform":"수행하다",
        "analysis":"분석","analyze":"분석하다",
        "process":"과정/처리","proceed":"진행하다",
        "schedule":"일정","scheduled":"예정된",
        "deadline":"마감일","extension":"연장",
        "reduction":"감소","reduce":"줄이다",
        "increase":"증가/증가시키다","decrease":"감소/감소하다",
        "receive":"받다","provide":"제공하다",
        "request":"요청","respond":"응답하다",
        "application":"지원/신청","apply":"지원하다/적용하다",
        "candidate":"지원자","applicant":"지원자",
        "participate":"참가하다","participation":"참가",
        "contribute":"기여하다","contribution":"기여",
        "distribute":"배포하다","distribution":"배포",
        "operate":"운영하다","operation":"운영",
        "manage":"관리하다","management":"관리",
        "organize":"조직하다","organization":"조직",
        "promote":"홍보하다/승진시키다","promotion":"홍보/승진",
        "purchase":"구매","acquire":"취득하다",
        "supply":"공급","demand":"수요",
        "negotiate":"협상하다","negotiation":"협상",
        "contract":"계약","agreement":"합의",
        "project":"프로젝트","proposal":"제안",
        "budget":"예산","invest":"투자하다",
        "efficient":"효율적인","productivity":"생산성",
        "retire":"은퇴하다","retirement":"은퇴",
        "relocate":"이전하다","relocation":"이전",
        "renovate":"개조하다","renovation":"개조",
        "suspend":"중단하다","suspension":"중단",
        "transfer":"이전/이동","transport":"운송",
        "launch":"출시/시작","introduce":"소개하다",
        "update":"업데이트","upgrade":"업그레이드",
        "inspect":"검사하다","inspection":"검사",
        "report":"보고하다/보고서","document":"문서",
        "member":"구성원","committee":"위원회",
        "board":"이사회","director":"이사/감독",
        "department":"부서","division":"부문",
        "employee":"직원","staff":"직원",
        "customer":"고객","client":"고객",
        "company":"회사","corporation":"기업",
        "office":"사무실","facility":"시설",
        "meeting":"회의","conference":"회의",
        "training":"교육","workshop":"워크샵",
        "policy":"정책","procedure":"절차",
        "number":"수","amount":"양","total":"합계",
        "endure":"견디다","retain":"유지하다",
        "considerable":"상당한","significant":"중요한",
    }

    def _lemma(w):
        """단어 원형 복원: 안전한 패턴만 처리"""
        w = w.strip()
        if not w or " " in w: return w
        lw = w.lower()
        # ies → y  (policies→policy)
        if lw.endswith('ies') and len(lw) > 4: return lw[:-3] + 'y'
        # s → 단수 (members→member)
        if (lw.endswith('s') and len(lw) > 3
                and not lw.endswith('ss') and not lw.endswith('us')
                and not lw.endswith('ous') and not lw.endswith('ness')):
            return lw[:-1]
        return lw

    def _clean_kr(kr):
        """뜻 정제: exk 찌꺼기 제거, 순수 뜻만 추출"""
        if not kr or kr == "?": return ""
        import re as _re_k
        # → 화살표 패턴 제거 (복수 → were)
        if "→" in kr:
            # 화살표 앞부분이 진짜 뜻인지 확인
            parts = kr.split("→")
            # 영어 단어만 있으면 뜻이 아님
            if _re_k.match(r'^[A-Za-z\s]+$', parts[0].strip()):
                return parts[-1].strip() if len(parts) > 1 else kr
            return parts[0].strip()
        # 괄호 제거
        kr = _re_k.sub(r'\(.*?\)', '', kr).strip()
        # 20자 초과면 앞부분만
        if len(kr) > 25: kr = kr[:22] + "..."
        return kr.strip()

    def _get_char(p):
        src = p.get("source",""); cat = p.get("cat","")
        if "수동태" in cat: return "🤖","#5599ff","PASSIVE · 수동태 포로"
        if "가정법" in cat: return "🧙","#bb66ff","SUBJUNCTIVE · 가정법 포로"
        if "관계" in cat:   return "🕵️","#ffaa33","RELATIVE · 관계사 포로"
        if "수일치" in cat: return "👥","#33ddaa","AGREEMENT · 수일치 포로"
        if "접속사" in cat: return "🔗","#ff7755","CONNECTOR · 접속사 포로"
        if "동명사" in cat or "준동사" in cat: return "🏃","#33ddff","GERUND · 준동사 포로"
        if "도치" in cat:   return "🙃","#ffee44","INVERSION · 도치 포로"
        if "분사" in cat:   return "🎭","#ff88bb","PARTICIPLE · 분사 포로"
        if src == "P7":     return "👽","#00eedd","READING · 독해 포로"
        return "🦁","#ffbb44","VOCAB · 어휘 포로"

    # ═══ 공유 단어 패밀리 DB import ═══
    import sys as _wp_sys, os as _wp_os
    _wp_sys.path.insert(0, _wp_os.path.dirname(__file__))
    try:
        from _word_family_db import get_family as _get_family_db, FAMILY_DB as _FAMILY_DB_EXT, lookup as _wp_lookup
        def _get_family(word, raw_word=""):
            """단어 패밀리 반환 — 공유 DB 사용"""
            for _w in [word, raw_word, _lemma(word)]:
                if not _w: continue
                fam = _get_family_db(_w)
                if fam: return fam
            return {}
    except Exception:
        # fallback: DB import 실패 시 빈 함수
        def _get_family(word, raw_word=""):
            return {}

    # ★ word_prison 진입 감지: _wp_guard=False면 외부에서 새로 진입 → lobby 강제
    # 나갈 때 _wp_guard=False 설정, 들어올 때 True로 잠금 → 재진입시 항상 로비
    # ★ word_prison 진입 감지: _wp_guard=False면 외부에서 새로 진입 → lobby 강제
    # 나갈 때 _wp_guard=False 설정, 들어올 때 True로 잠금 → 재진입시 항상 로비
    if not st.session_state.get("_wp_guard", False):
        import random as _wp_rnd2
        st.session_state.wp_mode    = "lobby"
        st.session_state.wp_idx     = 0
        st.session_state.wp_flipped = False
        st.session_state.wp_freed   = 0
        st.session_state["wp_quiz_trigger"]  = _wp_rnd2.randint(3, 5)
        st.session_state["wp_interrogator"]  = _wp_rnd2.randint(0, 4)
        st.session_state["wp_seen_words"]    = []
        st.session_state["wp_quiz_qs"]       = []
        st.session_state["wp_quiz_idx"]      = 0
        st.session_state["wp_quiz_score"]    = 0
        st.session_state["wp_quiz_feedback"] = None
        st.session_state["_wp_guard"] = True
    for _k,_v in {"wp_mode":"lobby","wp_idx":0,"wp_flipped":False,"wp_freed":0,
                  "wp_seen_words":[],"wp_quiz_qs":[],"wp_quiz_idx":0,
                  "wp_quiz_score":0,"wp_quiz_feedback":None}.items():
        if _k not in st.session_state: st.session_state[_k] = _v

    st.markdown('<div id="btn-home">', unsafe_allow_html=True)
    if st.button("🏠 홈", key="wp_home"):
        st.session_state["_wp_guard"] = False  # ★ 나갈 때 guard 해제 → 다음 진입시 로비 강제
        if _nick: st.query_params["nick"]=_nick; st.query_params["ag"]="1"
        st.switch_page("main_hub.py")
    st.markdown('</div>', unsafe_allow_html=True)

    if not _prisoners:
        components.html("""
        <style>*{margin:0;padding:0;}body{background:transparent;font-family:sans-serif;text-align:center;padding:40px 16px;}</style>
        <div style="font-size:56px;margin-bottom:12px;">🏆</div>
        <div style="font-family:'Orbitron',monospace;font-size:14px;color:#aa66ff;letter-spacing:4px;margin-bottom:6px;">전원 석방 🏆</div>
        <div style="font-size:13px;color:#448866;margin-top:8px;line-height:1.7;">모든 단어를 정복! 진짜 어휘 전사!</div>
        """, height=180)
        if st.button("💀 사령부 귀환", key="wp_back_empty", use_container_width=True):
            st.session_state["_wp_guard"] = False  # ★ guard 해제
            st.session_state.sg_phase="lobby"; st.rerun()

    elif st.session_state.wp_mode == "lobby":
        _total=len(_prisoners); _freed=st.session_state.wp_freed
        _p5=sum(1 for p in _prisoners if p.get("source","")=="P5")
        _p7=sum(1 for p in _prisoners if p.get("source","")=="P7")

        components.html(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
        *{{margin:0;padding:0;box-sizing:border-box;}}body{{background:transparent;}}
        </style>
        <div style="background:radial-gradient(ellipse at top,#1e0a35 0%,#08080f 70%);
             border:2px solid #8833ff;border-radius:16px;padding:14px 16px;text-align:center;
             box-shadow:inset 0 0 40px rgba(136,51,255,0.15);">
          <div style="font-family:'Orbitron',monospace;font-size:11px;font-weight:700;color:#aa66ee;
               letter-spacing:4px;margin-bottom:10px;">☠ INTERROGATION ROOM ☠</div>
          <div style="font-size:38px;margin-bottom:6px;filter:drop-shadow(0 0 12px #8833ff);">🚔</div>
          <div style="font-family:'Orbitron',monospace;font-size:15px;font-weight:900;color:#ddaaff;letter-spacing:3px;margin-bottom:4px;">WORD PRISON</div>
          <div style="font-size:14px;color:#cc99ff;font-weight:700;margin-bottom:2px;">단어 심문실</div>
          <div style="font-size:14px;color:#ffffff;font-weight:800;margin-top:10px;line-height:1.8;letter-spacing:0.3px;
               text-shadow:none;padding:6px 4px;
               border-top:1px solid #ff337744;">
            🚨 기억하면 <span style="color:#ff2244;font-weight:900;">석방</span>, 잊으면 <span style="color:#ff2244;font-weight:900;">재투옥</span>,<br>
            <span style="color:#ff2244;font-weight:900;">방심</span>하면 <span style="color:#ff2244;font-weight:900;">공범</span>까지 소환된다.
          </div>
        </div>
        """, height=210)

        st.markdown(f"""<div style="display:flex;gap:5px;margin:5px 0;">
          <div style="flex:1;background:#110820;border:1.5px solid #6633aa;border-radius:14px;padding:12px;text-align:center;">
            <div style="font-family:Orbitron,monospace;font-size:10px;font-weight:700;color:#aa77dd;letter-spacing:2px;margin-bottom:4px;">PRISONERS</div>
            <div style="font-size:26px;font-weight:900;color:#ddaaff;">{_total}</div>
            <div style="font-size:12px;color:#bb88ee;font-weight:600;margin-top:3px;">수감중</div>
          </div>
          <div style="flex:1;background:#110820;border:1.5px solid #6633aa;border-radius:14px;padding:12px;text-align:center;">
            <div style="font-family:Orbitron,monospace;font-size:10px;font-weight:700;color:#aa66ff;letter-spacing:2px;margin-bottom:4px;">RELEASED</div>
            <div style="font-size:26px;font-weight:900;color:#aa66ff;">{_freed}</div>
            <div style="font-size:12px;color:#cc88ff;font-weight:600;margin-top:3px;">오늘 석방</div>
          </div>
          <div style="flex:1;background:#0c1018;border:1.5px solid #334455;border-radius:14px;padding:10px;text-align:center;">
            <div style="font-size:13px;font-weight:800;color:#ff9944;">⚡ P5 · {_p5}</div>
            <div style="font-size:11px;color:#cc7733;font-weight:600;margin-bottom:8px;">화력전</div>
            <div style="font-size:13px;font-weight:800;color:#00ddee;">📡 P7 · {_p7}</div>
            <div style="font-size:11px;color:#22aabb;font-weight:600;">암호해독</div>
          </div>
        </div>""", unsafe_allow_html=True)

        # ★ Bug 1: 로비 진입 시 sent_kr 없는 단어들 API 일괄 번역 후 저장
        _needs_tr = [p for p in _prisoners if p.get("sentence","") and not p.get("sent_kr","")]
        if _needs_tr:
            try:
                import requests as _rq_bulk
                _api_key_bulk = st.secrets.get("ANTHROPIC_API_KEY","")
                if _api_key_bulk:
                    _bulk_updated = False
                    for _pi_item in _needs_tr:
                        _sent_item = _pi_item.get("sentence","")
                        _tr_resp2 = _rq_bulk.post("https://api.anthropic.com/v1/messages",
                            headers={"Content-Type":"application/json","x-api-key":_api_key_bulk,
                                     "anthropic-version":"2023-06-01"},
                            json={"model":"claude-haiku-4-5-20251001","max_tokens":100,
                                  "messages":[{"role":"user","content":
                                    f"다음 영어 문장을 자연스러운 한국어로만 번역해줘 (설명 없이): {_sent_item}"}]},
                            timeout=5)
                        if _tr_resp2.status_code == 200:
                            _tr_txt2 = _tr_resp2.json().get("content",[{}])[0].get("text","").strip()
                            if _tr_txt2:
                                for _pj, _px2 in enumerate(_pr_st.get("word_prison",[])):
                                    if _px2.get("sentence","") == _sent_item:
                                        _pr_st["word_prison"][_pj]["sent_kr"] = _tr_txt2
                                        _bulk_updated = True
                    if _bulk_updated:
                        save_storage(_pr_st)
                        _prisoners = _pr_st["word_prison"]  # 갱신된 리스트 반영
            except Exception:
                pass

        for _p in _prisoners[:2]:
            _ch,_col,_lbl = _get_char(_p)
            _w_raw = _p.get("word",""); _w = _lemma(_w_raw)
            _raw_kr = _p.get("kr","") or ""
            _kr = _clean_kr(_raw_kr)
            if not _kr or _kr in ("?","뜻 없음",""):
                _kr = _VOCAB_DICT.get(_w.lower(),"") or _VOCAB_DICT.get(_w_raw.lower(),"") or "?"
            _streak = _p.get("correct_streak",0)
            st.markdown(
                f'<div style="background:#0c0e1a;border:1px solid #1e2235;border-left:3px solid {_col};'
                f'border-radius:9px;padding:6px 10px;display:flex;align-items:center;gap:7px;margin-bottom:3px;">'
                f'<span style="font-size:19px;">{_ch}</span>'
                f'<div style="flex:1;">'
                f'<div style="font-size:13px;font-weight:900;color:#ffffff;">{_w}</div>'
                f'<div style="font-size:11px;color:#aabbcc;font-weight:600;">{_kr}</div>'
                f'</div>'
                f'<div style="text-align:right;">'
                f'<div style="font-size:11px;color:{_col};font-weight:700;">{"●"*_streak}{"○"*(3-_streak)}</div>'
                f'</div></div>',
                unsafe_allow_html=True)

        if _total>2:
            st.markdown(f'<div style="text-align:center;font-size:13px;color:#8899bb;font-weight:600;margin-top:4px;">+ {_total-2}명 더 수감중...</div>', unsafe_allow_html=True)

        st.markdown('<div style="height:2px;"></div>', unsafe_allow_html=True)
        st.markdown('<div id="btn-start">', unsafe_allow_html=True)
        if st.button("💥 탕!! 심문실 돌입!!", key="wp_start", use_container_width=True):
            st.session_state.wp_idx=0; st.session_state.wp_flipped=False; st.session_state.wp_mode="card"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div id="btn-back" style="margin-top:4px;">', unsafe_allow_html=True)
        if st.button("↩️ 사령부 귀환", key="wp_back_lobby", use_container_width=True):
            st.session_state["_wp_guard"] = False  # ★ guard 해제 → 다음 진입시 로비 강제
            st.session_state.sg_phase="lobby"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.wp_mode == "card":
        _deck=list(_prisoners); _idx=st.session_state.wp_idx; _freed=st.session_state.wp_freed

        if _idx >= len(_deck):
            components.html(f"""
            <style>@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');
            *{{margin:0;padding:0;}}body{{background:transparent;font-family:sans-serif;text-align:center;padding:28px 16px;}}</style>
            <div style="font-size:52px;margin-bottom:10px;">{'🎉' if _freed>0 else '💪'}</div>
            <div style="font-family:'Orbitron',monospace;font-size:13px;letter-spacing:3px;
                 color:#{'33ff77' if _freed>0 else 'ffcc44'};margin-bottom:6px;">
              심문 완료</div>
            <div style="font-size:14px;color:#7788aa;">석방 {_freed}명 🔓 · 계속 훈련하면 다 풀어줄 수 있어!</div>
            """, height=130)
            _r1,_r2=st.columns(2)
            with _r1:
                if st.button("🔁 다시 심문", key="wp_restart", use_container_width=True):
                    st.session_state.wp_idx=0; st.session_state.wp_flipped=False; st.session_state.wp_freed=0; st.rerun()
            with _r2:
                if st.button("↩️ LOBBY", key="wp_done_back", use_container_width=True):
                    st.session_state.wp_mode="lobby"; st.session_state.wp_freed=0; st.rerun()
        else:
            _p=_deck[_idx]; _raw_word=_p.get("word",""); _word=_lemma(_raw_word)
            _raw_kr=_p.get("kr","") or ""; _kr=_clean_kr(_raw_kr)
            _sent=_p.get("sentence",""); _sent_kr=_p.get("sent_kr","")
            # kr 없으면 사전 fallback 시도
            if not _kr or _kr in ("?","뜻 없음",""):
                _kr = _VOCAB_DICT.get(_word.lower(), "") or _VOCAB_DICT.get(_raw_word.lower(), "")
            _has_meaning = bool(_kr and _kr not in ("뜻 없음","?",""))
            _streak=_p.get("correct_streak",0)
            _src=_p.get("source",""); _ch,_col,_lbl=_get_char(_p)
            # 진입 시 앞면 보장
            if st.session_state.get("_wp_last_idx") != _idx:
                st.session_state.wp_flipped = False
                st.session_state["_wp_last_idx"] = _idx
            _flipped=st.session_state.wp_flipped

            # 재밌는 심문 멘트 (순환)
            _catchphrases=[
                "이 단어 아냐고?? 뒤집어! 👊",
                "알긴 아냐고? 아는척? 뒤집어! 🕵️",
                "어디 쳐다봐! 뒤집어봐봐! 👀",
                "도망 못 간다! 뒤집어! ⛓",
                "눈 똑바로 떠! 뜻 알면 뒤집어! 🔦",
                "솔직히 몰라? 그럼 빨리 뒤집어! 😤",
                "3초 안에 뜻 생각해봐! ⏱ 뒤집어!",
                "이 단어 또 나왔네... 이번엔 뒤집어! 😏",
                "아는척하지 마! 진짜로 뒤집어봐! 😈",
                "심문관이 기다린다! 뒤집어! 🚔",
                "긴장돼? 정상이야. 뒤집어! 💀",
                "이 단어 토익 단골! 뒤집어봐! 📋",
                "모른다고? 일단 뒤집어! 용기내! 💪",
                "뒤집으면 답 나와! 어서! 👇",
            ]
            _catchphrase = _catchphrases[_idx % len(_catchphrases)]

            # HUD
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'background:#08080f;border:1px solid #1e2235;border-radius:10px;padding:7px 14px;margin-bottom:5px;">'
                f'<span style="font-family:Orbitron,monospace;font-size:8px;color:#334455;letter-spacing:4px;">INTERROGATION</span>'
                f'<span style="font-size:13px;color:#8899bb;font-weight:800;">{_idx+1} / {len(_deck)}</span>'
                f'<span style="font-size:13px;font-weight:900;color:#aa66ff;">🔓 {_freed}</span>'
                f'</div>', unsafe_allow_html=True)

            if not _flipped:
                # ── 앞면: 영어 단어 하나만 + 심문 멘트 버튼 ──
                _dots="".join([f'<span style="display:inline-block;width:24px;height:8px;border-radius:4px;margin:0 4px;background:{""+_col+"" if i<_streak else "#1e2235"};"></span>' for i in range(3)])
                components.html(f"""
                <style>
                @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');
                *{{margin:0;padding:0;box-sizing:border-box;}}body{{background:transparent;font-family:sans-serif;text-align:center;}}
                .flicker{{animation:flicker 3s infinite;}}
                @keyframes flicker{{0%,95%,100%{{opacity:1}}96%{{opacity:0.4}}97%{{opacity:1}}98%{{opacity:0.6}}}}
                </style>
                <div style="background:radial-gradient(ellipse at 50% 20%,#1a1040 0%,#06060e 80%);
                     border:2.5px solid {_col};border-radius:18px;padding:18px 16px 16px;
                     box-shadow:inset 0 0 40px {_col}18, 0 0 24px {_col}44;">
                  <div style="font-size:52px;margin-bottom:10px;filter:drop-shadow(0 0 14px {_col}aa);">{_ch}</div>
                  <div style="font-family:'Orbitron',monospace;font-size:28px;font-weight:900;color:#ffffff;
                       letter-spacing:3px;text-shadow:0 0 30px {_col},0 0 12px #fff,0 2px 4px #000;
                       margin-bottom:16px;" class="flicker">{_word}</div>
                  <div style="display:flex;justify-content:center;gap:4px;margin-bottom:10px;">{_dots}</div>
                  <div style="font-size:11px;color:#8899aa;font-style:italic;line-height:1.5;margin-top:4px;padding:0 4px;">{_sent[:80]+'...' if _sent and len(_sent)>80 else _sent if _sent else ('🔓 석방 완료!' if _streak>=3 else '⛓ 첫 번째 도전!' if _streak==0 else '🔑 '+str(3-_streak)+'번 더 맞히면 석방!')}</div>
                </div>
                """, height=260)

                # 심문 멘트 = 클릭 버튼
                st.markdown('<div id="btn-flip">', unsafe_allow_html=True)
                if st.button(f"{_catchphrase}", key=f"wp_flip_{_idx}", use_container_width=True):
                    # sent_kr 없으면 API로 번역 시도 후 저장
                    if _sent and not _sent_kr:
                        try:
                            import streamlit as _st3, requests as _rtr, json as _jtr
                            _api_key = _st3.secrets.get("ANTHROPIC_API_KEY","")
                            if _api_key:
                                _tr_resp = _rtr.post("https://api.anthropic.com/v1/messages",
                                    headers={"Content-Type":"application/json","x-api-key":_api_key,
                                             "anthropic-version":"2023-06-01"},
                                    json={"model":"claude-haiku-4-5-20251001","max_tokens":100,
                                          "messages":[{"role":"user","content":
                                            f"다음 영어 문장을 자연스러운 한국어로만 번역해줘 (설명 없이): {_sent}"}]},
                                    timeout=5)
                                if _tr_resp.status_code == 200:
                                    _tr_txt = _tr_resp.json().get("content",[{}])[0].get("text","").strip()
                                    if _tr_txt:
                                        _pr_st2 = load_storage()
                                        for _pi2, _px in enumerate(_pr_st2.get("word_prison",[])):
                                            if _px.get("sentence","") == _sent:
                                                _pr_st2["word_prison"][_pi2]["sent_kr"] = _tr_txt
                                        save_storage(_pr_st2)
                                        # 현재 포로에도 즉시 반영
                                        _p["sent_kr"] = _tr_txt
                        except Exception:
                            pass
                    st.session_state.wp_flipped=True; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            else:
                # ── 뒷면: 뜻 + 예문(compact) + 공범 단어 패밀리 ──
                import re as _re_hl

                # 예문 (한글 해석 제거, 영어만 compact)
                _sent_short = _sent[:95]+"..." if len(_sent)>95 else _sent
                _sent_block = ""
                if _sent:
                    _hl_sent = _re_hl.sub(
                        f"(?i)({_re_hl.escape(_raw_word)}|{_re_hl.escape(_word)})",
                        f'<span style="color:#ffee44;font-weight:900;border-bottom:2px solid #ffee44;padding:0 1px;">\\1</span>',
                        _sent_short
                    )
                    _sent_block = (
                        f'<div style="background:#08100a;border:1.5px solid #1a3020;border-radius:12px;'
                        f'padding:9px 12px;margin:8px 0 4px;text-align:left;">'
                        f'<div style="font-size:11px;font-weight:700;color:#66aa88;letter-spacing:2px;margin-bottom:5px;text-align:center;">📝 예문</div>'
                        f'<div style="font-size:13px;color:#c8d8e0;line-height:1.65;font-style:italic;">&ldquo;{_hl_sent}&rdquo;</div>'
                        f'</div>'
                    )

                # ⛓ 공범 단어 패밀리 블록
                _family = _get_family(_word, _raw_word)
                _family_block = ""
                _shown = 0
                if _family:
                    _POS_STYLE = {
                        "V":   ("동사",   "#331a00","#ff8833"),
                        "N":   ("명사",   "#332a00","#ffcc44"),
                        "ADJ": ("형용사", "#001a2a","#44ccee"),
                        "ADV": ("부사",   "#1a0033","#bb88ff"),
                    }
                    _rows_html = ""
                    for _pk, (_pkr, _pbg, _pcol) in _POS_STYLE.items():
                        for _mw, _mkr in _family.get(_pk, []):
                            if _shown >= 7: break
                            _is_cur = _mw.lower() in [_word.lower(), _raw_word.lower(), _lemma(_raw_word).lower()]
                            _rbg = "#1a1030" if _is_cur else "#110e1a"
                            _wc  = "#ffee44" if _is_cur else "#c8d0e0"
                            _krc = "#ffdd66" if _is_cur else "#99aabb"
                            _fw  = "900"     if _is_cur else "600"
                            _star = "★ "    if _is_cur else ""
                            _rows_html += (
                                f'<div style="display:flex;align-items:center;margin-bottom:3px;border-radius:7px;overflow:hidden;">'
                                f'<div style="width:40px;flex-shrink:0;font-size:8px;font-weight:900;letter-spacing:1px;'
                                f'padding:5px 3px;text-align:center;background:{_pbg};color:{_pcol};">{_pkr}</div>'
                                f'<div style="flex:1;font-size:13px;font-weight:{_fw};padding:5px 8px;background:{_rbg};color:{_wc};">{_star}{_mw}</div>'
                                f'<div style="font-size:13px;font-weight:600;color:{_krc};padding:5px 7px;background:{_rbg};text-align:right;white-space:nowrap;">{_mkr}</div>'
                                f'</div>'
                            )
                            _shown += 1
                    if _rows_html:
                        _family_block = (
                            f'<div style="background:#0c0818;border:1.5px solid #3a1a66;border-radius:12px;'
                            f'padding:10px 12px;margin:5px 0 4px;text-align:left;">'
                            f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:8px;'
                            f'padding-bottom:6px;border-bottom:1px solid #2a1544;">'
                            f'<span style="font-family:Orbitron,monospace;font-size:10px;font-weight:700;color:#aa55ff;letter-spacing:3px;">⛓ 공범 소환</span>'
                            f'<span style="font-size:10px;font-weight:700;background:#3a1a66;color:#cc99ff;padding:2px 8px;border-radius:6px;">WORD FAMILY</span>'
                            f'</div>'
                            f'{_rows_html}'
                            f'</div>'
                        )

                _dots2 = "".join([
                    f'<span style="display:inline-block;width:24px;height:8px;border-radius:4px;margin:0 4px;'
                    f'background:{"#33cc55" if i<_streak else "#1e2a1e"};"></span>'
                    for i in range(3)
                ])
                # 동적 높이: base + 예문 + 패밀리행
                _card_h = 150 + (90 if _sent else 0) + (55 + _shown*35 if _family_block else 0) + 50
                components.html(f"""
                <style>
                @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');
                *{{margin:0;padding:0;box-sizing:border-box;}}body{{background:transparent;font-family:sans-serif;overflow-y:auto;}}
                </style>
                <div style="background:radial-gradient(ellipse at 50% 20%,#0a2016 0%,#08080f 75%);
                     border:2.5px solid #22cc55;border-radius:20px;padding:18px 14px;text-align:center;
                     box-shadow:inset 0 0 30px rgba(34,204,85,0.08);">
                  <div style="font-size:36px;margin-bottom:4px;">{_ch}</div>
                  <div style="font-family:'Orbitron',monospace;font-size:15px;color:#ccffdd;
                       letter-spacing:3px;margin-bottom:8px;font-weight:900;">{_word}</div>
                  <div style="font-size:{'29' if _has_meaning else '16'}px;font-weight:900;
                       color:#{'ffffff' if _has_meaning else '668877'};
                       margin-bottom:2px;">{''+_kr+'' if _has_meaning else '아래 예문에서 뜻을 찾아봐! 💡'}</div>
                  {_sent_block}
                  {_family_block}
                  <div style="display:flex;justify-content:center;gap:4px;margin-top:8px;">{_dots2}</div>
                  <div style="font-size:13px;font-weight:700;color:#66aa88;margin-top:4px;">
                    {'🔓 석방 완료!' if _streak>=3 else '💀 솔직하게 말해 · 알아? 몰라?'}</div>
                </div>
                """, height=_card_h)

                _c1,_c2=st.columns(2)
                with _c1:
                    st.markdown('<div id="btn-know">', unsafe_allow_html=True)
                    if st.button("✅  I KNOW!  석방 +1", key=f"wp_know_{_idx}", use_container_width=True):
                        _ri=next((i for i,x in enumerate(_pr_st["word_prison"]) if x.get("word","").lower()==_word.lower()),None)
                        if _ri is not None:
                            _ns=_streak+1
                            _pr_st["word_prison"][_ri]["correct_streak"]=_ns
                            _pr_st["word_prison"][_ri]["last_reviewed"]=_today_str2
                            if _ns>=3: _pr_st["word_prison"].pop(_ri); st.session_state.wp_freed+=1
                            save_storage(_pr_st)
                        # 본 단어 기록
                        _sw = st.session_state.get("wp_seen_words",[])
                        if not any(s["word"]==_word for s in _sw):
                            _sw.append({"word":_word,"kr":_kr if _has_meaning else ""})
                            st.session_state.wp_seen_words = _sw
                        st.session_state.wp_idx+=1; st.session_state.wp_flipped=False
                        # 긴급 소환 트리거 체크
                        if len(st.session_state.wp_seen_words) >= st.session_state.get("wp_quiz_trigger",4):
                            import random as _rnd_trig2; st.session_state.wp_quiz_trigger = _rnd_trig2.randint(3,6); st.session_state.wp_seen_words = []; st.session_state.wp_mode = "flash_intro"
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with _c2:
                    st.markdown('<div id="btn-no">', unsafe_allow_html=True)
                    if st.button("❌  NO IDEA!  재투옥!", key=f"wp_no_{_idx}", use_container_width=True):
                        _ri=next((i for i,x in enumerate(_pr_st["word_prison"]) if x.get("word","").lower()==_word.lower()),None)
                        if _ri is not None:
                            _pr_st["word_prison"][_ri]["correct_streak"]=0
                            _pr_st["word_prison"][_ri]["last_reviewed"]=_today_str2
                            save_storage(_pr_st)
                        # 본 단어 기록
                        _sw = st.session_state.get("wp_seen_words",[])
                        if not any(s["word"]==_word for s in _sw):
                            _sw.append({"word":_word,"kr":_kr if _has_meaning else ""})
                            st.session_state.wp_seen_words = _sw
                        st.session_state.wp_idx+=1; st.session_state.wp_flipped=False
                        # 긴급 소환 트리거 체크
                        if len(st.session_state.wp_seen_words) >= st.session_state.get("wp_quiz_trigger",4):
                            import random as _rnd_trig2; st.session_state.wp_quiz_trigger = _rnd_trig2.randint(3,6); st.session_state.wp_seen_words = []; st.session_state.wp_mode = "flash_intro"
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div id="btn-back" style="margin-top:4px;">', unsafe_allow_html=True)
            if st.button("↩️ LOBBY", key=f"wp_back_{_idx}", use_container_width=True):
                st.session_state.wp_mode="lobby"; st.session_state.wp_flipped=False; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════
    # PHASE: FLASH_INTRO — 🚨 긴급 소환 전환 화면
    # ════════════════════════════════════════
    elif st.session_state.wp_mode == "flash_intro":
        import random as _fi_rnd

        # 수사관 5종
        _INTERROGATORS = [
            {"name":"박형사","emoji":"👮","color":"#ff6633","title":"강력계 형사",
             "enter":"야!! 책상 탁!!! 솔직하게 말해!!",
             "correct":"좋아, 인정한다! 다음!!","wrong":"딱 걸렸어!! 거짓말하지 마!!",
             "done":"이번엔 봐준다... 다음엔 없어."},
            {"name":"Agent K","emoji":"🕵️","color":"#00ccff","title":"CIA 냉철 요원",
             "enter":"우리는... 이미 알고 있어.",
             "correct":"예상대로군.","wrong":"거짓말은 데이터가 증명한다.",
             "done":"임무 완료. 철수."},
            {"name":"여우씨","emoji":"🦊","color":"#ffaa33","title":"교활한 탐정",
             "enter":"어머~ 방심했지? 이건 함정이야~ 🦊",
             "correct":"흠... 맞추다니. 예상 밖인걸?","wrong":"역시~ 내 함정에 딱 걸렸네~",
             "done":"오늘은 봐줄게. 다음엔 더 교활해질 거야."},
            {"name":"UNIT-7","emoji":"🤖","color":"#44ffcc","title":"AI 수사관",
             "enter":"분석 완료. 즉시 응답하라.",
             "correct":"정답 확인됨. 다음 항목.","wrong":"오답 감지. 재투옥 처리 중...",
             "done":"오늘 정확도 분석 완료. 데이터 저장."},
            {"name":"대부","emoji":"👹","color":"#ff3366","title":"보스",
             "enter":"내가... 직접 나왔어.",
             "correct":"...이번만 봐준다.","wrong":"내 앞에서 틀려?! 각오해!!",
             "done":"살아남았군. 오늘은."},
        ]
        st.session_state.setdefault("_fi_interrogators", _INTERROGATORS)

        _inq_idx = st.session_state.get("wp_interrogator", 0)
        _inq = _INTERROGATORS[_inq_idx % len(_INTERROGATORS)]
        _ic = _inq["color"]

        # 문제 아직 생성 안 됐으면 생성
        if not st.session_state.get("wp_quiz_qs"):
            _seen = st.session_state.get("wp_seen_words", [])
            _pool = [s for s in _seen if s.get("kr") and s["kr"] not in ("?","뜻 없음","")]
            if len(_pool) < 2:
                # seen words가 부족하면 word_prison 전체에서 보충
                for _pp in _prisoners:
                    _pw = _pp.get("word",""); _pk = _pp.get("kr","")
                    if _pk and _pk not in ("?","뜻 없음","") and not any(s["word"]==_pw for s in _pool):
                        _pool.append({"word":_pw,"kr":_pk})
                    if len(_pool) >= 5: break
            _q_words = _fi_rnd.sample(_pool, min(5, len(_pool)))
            _qs = []
            for _qi, _qw in enumerate(_q_words):
                _qtype = "ox" if _qi % 2 == 0 else "choice4"
                if _qtype == "ox":
                    _is_cor = _fi_rnd.choice([True, False])
                    if _is_cor:
                        _show_kr = _qw["kr"]
                    else:
                        _wrongs = [s["kr"] for s in _pool if s["word"]!=_qw["word"] and s.get("kr")]
                        _show_kr = _fi_rnd.choice(_wrongs) if _wrongs else _qw["kr"]
                        if _show_kr == _qw["kr"]: _is_cor = True
                    _qs.append({"type":"ox","word":_qw["word"],"kr":_qw["kr"],
                                "show_kr":_show_kr,"correct":_is_cor})
                else:
                    _dists = list({s["kr"] for s in _pool if s["word"]!=_qw["word"] and s.get("kr")
                                   and s["kr"] not in ("?","뜻 없음","")})
                    _fb = ["고용하다","제출하다","준수하다","평가하다","승인하다","관리하다","연장하다","참가하다","발표하다","검토하다"]
                    for _fk in _fb:
                        if _fk not in _dists and _fk != _qw["kr"]: _dists.append(_fk)
                    _dists = [d for d in _dists if d != _qw["kr"]]
                    _fi_rnd.shuffle(_dists)
                    _ch4 = _dists[:3] + [_qw["kr"]]
                    _fi_rnd.shuffle(_ch4)
                    _qs.append({"type":"choice4","word":_qw["word"],"kr":_qw["kr"],
                                "choices":_ch4,"answer_idx":_ch4.index(_qw["kr"])})
            st.session_state.wp_quiz_qs = _qs
            st.session_state.wp_quiz_idx = 0
            st.session_state.wp_quiz_score = 0
            st.session_state.wp_quiz_feedback = None

        components.html(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');
        *{{margin:0;padding:0;box-sizing:border-box;}}body{{background:transparent;font-family:sans-serif;text-align:center;overflow:hidden;}}
        @keyframes redFlash{{0%{{opacity:1}}30%{{opacity:0.3}}60%{{opacity:1}}80%{{opacity:0.6}}100%{{opacity:1}}}}
        @keyframes slideUp{{from{{transform:translateY(80px);opacity:0}}to{{transform:translateY(0);opacity:1}}}}
        @keyframes thud{{0%{{transform:scale(1)}}20%{{transform:scale(1.4)}}40%{{transform:scale(0.9)}}60%{{transform:scale(1.15)}}100%{{transform:scale(1)}}}}
        @keyframes alarmPulse{{0%,100%{{box-shadow:0 0 30px {_ic},0 0 60px {_ic}44}}50%{{box-shadow:0 0 60px {_ic},0 0 120px {_ic}88}}}}
        @keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}
        .container{{background:radial-gradient(ellipse at 50% 30%,#2a0010 0%,#06080f 70%);
            border:3px solid {_ic};border-radius:20px;padding:24px 16px;
            animation:alarmPulse 1.2s ease infinite;}}
        .alarm{{font-family:'Orbitron',monospace;font-size:13px;font-weight:900;
            color:{_ic};letter-spacing:4px;animation:blink 0.8s ease infinite;margin-bottom:12px;}}
        .emoji{{font-size:64px;animation:slideUp 0.6s ease;display:block;margin-bottom:10px;filter:drop-shadow(0 0 20px {_ic});}}
        .title{{font-family:'Orbitron',monospace;font-size:11px;color:{_ic};letter-spacing:3px;margin-bottom:4px;}}
        .name{{font-family:'Orbitron',monospace;font-size:20px;font-weight:900;color:#ffffff;margin-bottom:14px;}}
        .enter{{font-size:18px;font-weight:900;color:#ffffff;line-height:1.6;animation:slideUp 0.8s ease;margin-bottom:8px;}}
        .sub{{font-size:13px;color:{_ic};font-weight:700;animation:blink 1.5s ease infinite;}}
        </style>
        <div class="container">
          <div class="alarm">🚨 EMERGENCY RECALL 🚨</div>
          <span class="emoji">{_inq["emoji"]}</span>
          <div class="title">{_inq["title"]}</div>
          <div class="name">{_inq["name"]}</div>
          <div class="enter">"{_inq["enter"]}"</div>
          <div class="sub">방금 본 단어들... 진짜 알아?</div>
        </div>
        """, height=330)

        st.markdown(f'<div id="btn-start" style="margin-top:8px;">', unsafe_allow_html=True)
        if st.button(f"⚡ 긴급 심문 돌입!", key="flash_go", use_container_width=True):
            st.session_state.wp_mode = "flash_quiz"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════
    # PHASE: FLASH_QUIZ — ⚡ 긴급 소환 퀴즈
    # ════════════════════════════════════════
    elif st.session_state.wp_mode == "flash_quiz":
        _INTERROGATORS = st.session_state.get("_fi_interrogators", [
            {"name":"박형사","emoji":"👮","color":"#ff6633","title":"강력계 형사",
             "enter":"야!!","correct":"좋아!","wrong":"딱 걸렸어!!","done":"이번엔 봐준다."},
        ])
        _inq_idx = st.session_state.get("wp_interrogator", 0)
        _inq = _INTERROGATORS[_inq_idx % len(_INTERROGATORS)]
        _ic = _inq["color"]
        _qs = st.session_state.get("wp_quiz_qs", [])
        _qi = st.session_state.get("wp_quiz_idx", 0)
        _score = st.session_state.get("wp_quiz_score", 0)
        _fb = st.session_state.get("wp_quiz_feedback", None)

        if _qi >= len(_qs):
            st.session_state.wp_mode = "flash_result"; st.rerun()
        else:
            _q = _qs[_qi]
            _qword = _q["word"]; _qkr = _q["kr"]
            _total_q = len(_qs)

            # HUD
            components.html(f"""
            <style>@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');
            *{{margin:0;padding:0;box-sizing:border-box;}}body{{background:transparent;font-family:sans-serif;}}
            @keyframes shake{{0%,100%{{transform:translateX(0)}}20%{{transform:translateX(-8px)}}40%{{transform:translateX(8px)}}60%{{transform:translateX(-5px)}}80%{{transform:translateX(5px)}}}}
            @keyframes popIn{{from{{transform:scale(0.7);opacity:0}}to{{transform:scale(1);opacity:1}}}}
            .hud{{background:#06080f;border:2px solid {_ic};border-radius:14px;padding:10px 14px;
                display:flex;justify-content:space-between;align-items:center;margin-bottom:2px;}}
            .inq{{font-size:22px;}} .inq-name{{font-family:'Orbitron',monospace;font-size:10px;color:{_ic};font-weight:900;}}
            .prog{{font-family:'Orbitron',monospace;font-size:14px;font-weight:900;color:#ffffff;}}
            .star{{font-size:16px;}}
            .card{{background:radial-gradient(ellipse at top,#1a0820 0%,#06080f 70%);
                border:2.5px solid {_ic};border-radius:18px;padding:20px 16px;text-align:center;
                {'animation:shake 0.5s ease;' if _fb and not _fb["correct"] else 'animation:popIn 0.4s ease;'}}}
            .qtype{{font-family:'Orbitron',monospace;font-size:9px;color:{_ic};letter-spacing:3px;margin-bottom:10px;}}
            .word{{font-family:'Orbitron',monospace;font-size:24px;font-weight:900;color:#ffffff;
                text-shadow:0 0 20px {_ic};margin-bottom:4px;}}
            .kr-show{{font-size:22px;font-weight:900;color:#ffee44;margin:8px 0;}}
            .fb-ok{{font-size:28px;font-weight:900;color:#aa66ff;animation:popIn 0.3s ease;}}
            .fb-ng{{font-size:22px;font-weight:900;color:#ff4444;}}
            .fb-ans{{font-size:14px;color:#aabbcc;margin-top:4px;}}
            .inq-msg{{font-size:15px;font-weight:800;color:#ffffff;margin-top:8px;line-height:1.5;}}
            </style>
            <div class="hud">
              <div><div class="inq">{_inq["emoji"]}</div><div class="inq-name">{_inq["name"]}</div></div>
              <div class="prog">Q{_qi+1} / {_total_q}</div>
              <div class="star">{"⭐"*_score}{"☆"*(_qi-_score)}</div>
            </div>
            <div class="card">
              {'<div class="fb-ok">✅ 탁!!</div><div class="inq-msg">' + _inq["correct"] + '</div>' if _fb and _fb["correct"]
               else '<div class="fb-ng">❌ 딱 걸렸어!</div><div class="fb-ans">정답: ' + _qkr + '</div><div class="inq-msg">' + _inq["wrong"] + '</div>' if _fb and not _fb["correct"]
               else ('<div class="qtype">' + ('🔎 OX 심문' if _q["type"]=="ox" else '🎯 4지선다') + '</div>'
               + ('<div class="word">' + _qword + '</div><div class="kr-show">' + _q.get("show_kr","") + '</div>'
                  if _q["type"]=="ox" else '<div style="font-size:14px;color:#aabbcc;margin-bottom:6px;">아래 중 맞는 한국어 뜻은?</div><div class="word">' + _qword + '</div>'))}
            </div>
            """, height=210 if _fb else 190)

            if _fb:
                st.markdown('<div id="btn-start">', unsafe_allow_html=True)
                _next_label = "🏁 결과 보기!" if _qi+1 >= _total_q else "다음 → "
                if st.button(_next_label, key=f"fq_next_{_qi}", use_container_width=True):
                    st.session_state.wp_quiz_idx += 1
                    st.session_state.wp_quiz_feedback = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            elif _q["type"] == "ox":
                _ox1, _ox2 = st.columns(2)
                with _ox1:
                    st.markdown('<div id="btn-know">', unsafe_allow_html=True)
                    if st.button("⭕ 맞아!", key=f"fq_ox_y_{_qi}", use_container_width=True):
                        _ok = _q["correct"]
                        if _ok: st.session_state.wp_quiz_score += 1
                        st.session_state.wp_quiz_feedback = {"correct": _ok}; st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with _ox2:
                    st.markdown('<div id="btn-no">', unsafe_allow_html=True)
                    if st.button("❌ 아니야!", key=f"fq_ox_n_{_qi}", use_container_width=True):
                        _ok = not _q["correct"]
                        if _ok: st.session_state.wp_quiz_score += 1
                        st.session_state.wp_quiz_feedback = {"correct": _ok}; st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                _choices = _q["choices"]
                for _ci, _ch in enumerate(_choices):
                    if st.button(f"{chr(9312+_ci)} {_ch}", key=f"fq_ch_{_qi}_{_ci}", use_container_width=True):
                        _ok = (_ci == _q["answer_idx"])
                        if _ok: st.session_state.wp_quiz_score += 1
                        st.session_state.wp_quiz_feedback = {"correct": _ok}; st.rerun()

    # ════════════════════════════════════════
    # PHASE: FLASH_RESULT — 🏆 긴급 소환 결과
    # ════════════════════════════════════════
    elif st.session_state.wp_mode == "flash_result":
        _INTERROGATORS = st.session_state.get("_fi_interrogators", [
            {"name":"박형사","emoji":"👮","color":"#ff6633",
             "done":"이번엔 봐준다."},
        ])
        _inq_idx = st.session_state.get("wp_interrogator", 0)
        _inq = _INTERROGATORS[_inq_idx % len(_INTERROGATORS)]
        _ic = _inq["color"]
        _score = st.session_state.get("wp_quiz_score", 0)
        _total = len(st.session_state.get("wp_quiz_qs", [1,2,3,4,5]))

        _done_msg = _inq["done"].replace("{score}", str(_score))
        if _score == _total:
            _grade_emoji, _grade_msg, _grade_color = "🏆", "완전 석방 확정! 넌 자유야!", "#ffdd00"
        elif _score >= _total * 0.8:
            _grade_emoji, _grade_msg, _grade_color = "⭐", "거의 다! 한 놈만 더 잡자!", "#aa66ff"
        elif _score >= _total * 0.6:
            _grade_emoji, _grade_msg, _grade_color = "💪", "절반 인정. 나머지 재심문!", "#ffaa33"
        else:
            _grade_emoji, _grade_msg, _grade_color = "💀", "전원 재투옥! 다시 시작해!", "#ff4444"

        components.html(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');
        *{{margin:0;padding:0;box-sizing:border-box;}}body{{background:transparent;font-family:sans-serif;text-align:center;}}
        @keyframes popIn{{from{{transform:scale(0.5);opacity:0}}to{{transform:scale(1);opacity:1}}}}
        @keyframes pulse{{0%,100%{{box-shadow:0 0 20px {_ic}44}}50%{{box-shadow:0 0 50px {_ic}99}}}}
        .card{{background:radial-gradient(ellipse at top,#150a25 0%,#06080f 70%);
            border:2.5px solid {_ic};border-radius:20px;padding:22px 16px;animation:pulse 2s ease infinite;}}
        .inq-big{{font-size:52px;margin-bottom:6px;filter:drop-shadow(0 0 16px {_ic});animation:popIn 0.6s ease;}}
        .inq-msg{{font-size:15px;font-weight:800;color:#cccccc;margin-bottom:14px;line-height:1.5;font-style:italic;}}
        .grade{{font-size:48px;animation:popIn 0.5s 0.2s both ease;}}
        .score{{font-family:'Orbitron',monospace;font-size:32px;font-weight:900;color:{_grade_color};
            text-shadow:0 0 20px {_grade_color};margin:6px 0;}}
        .grade-msg{{font-size:16px;font-weight:900;color:{_grade_color};margin-top:4px;}}
        .stars{{font-size:20px;letter-spacing:4px;margin-top:8px;}}
        </style>
        <div class="card">
          <div class="inq-big">{_inq["emoji"]}</div>
          <div class="inq-msg">"{_done_msg}"</div>
          <div class="grade">{_grade_emoji}</div>
          <div class="score">{_score} / {_total}</div>
          <div class="grade-msg">{_grade_msg}</div>
          <div class="stars">{"⭐"*_score}{"☆"*(_total-_score)}</div>
        </div>
        """, height=320)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        _r1, _r2 = st.columns(2)
        with _r1:
            if st.button("🔁 심문 계속!", key="fl_resume", use_container_width=True):
                import random as _fr_rnd
                st.session_state.wp_mode = "card"
                st.session_state.wp_quiz_trigger = 9999  # 다시 발동 안 함
                st.session_state.wp_quiz_feedback = None
                st.rerun()
        with _r2:
            if st.button("↩️ 로비", key="fl_lobby", use_container_width=True):
                st.session_state["_wp_guard"] = False
                st.session_state.wp_mode = "lobby"; st.rerun()


