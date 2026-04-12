"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     02_Firepower.py
ROLE:     화력전 — 문법·어휘 5문제 서바이벌 전장 (P5)
VERSION:  SnapQ TOEIC V3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASES:   LOBBY → BATTLE → BRIEFING → RESULT
DATA IN:  storage_data.json (rt_logs, word_prison, saved_expressions)
DATA OUT: rt_logs (반응속도·정답여부), word_prison (오답 포획), adp_logs
LINKS:    main_hub.py → 02_Firepower.py → 03_POW_HQ.py
PAPERS:   논문D (rt_logs 반응속도 프록시)
          논문A (adp_logs 적응형 난이도, word_prison DB 교집합)
          논문B (오답 타이밍 3분류: fast/mid/slow_wrong)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AI-AGENT NOTES:
  [핵심 로직]
  - 오답 타이밍 3분류: round_timings[] 배열로 fast/mid/slow 분류
    → slow_wrong만 강제 저장 (논문B 청구항3)
  - find_words_in_sentence(): _word_family_db.py DB와 교집합 추출
    → 플랫폼 DB에 있는 단어만 word_prison 저장 (논문A 청구항1)
  - GAME OVER 화면에도 브리핑 버튼 존재 (_sc > 0 조건)

  [수정 주의사항]
  - 'answer' 필드 경고는 false positive — 'a' 필드명이 정상, 수정 불필요
  - round_results[], round_timings[] 반드시 함께 리셋할 것
  - HTML은 문자열 연결(+)로 처리 — f-string 멀티라인 금지 (</div> 렌더 오류)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import random, time, json, os, re

st.set_page_config(page_title="화력전 ⚡", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")
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
# ── 활동 기록 (논문A 참여율, 논문B 정복률) ──
try:
    import sys as _sys_path
    import os as _os_path
    _sys_path.path.insert(0, _os_path.path.join(_os_path.path.dirname(_os_path.path.dirname(__file__)), "app", "core"))
    from attendance_engine import record_activity as _record_activity
except Exception:
    def __record_activity(*a, **kw): pass
_inject_css()

# ═══ _storage.py 공통 모듈 연동 ═══════════════════════════════
# PURPOSE: user_id 통일 (get_uid), rt_logs 저장 함수 통일
# PAPER:   논문A(adp_logs), 논문D(rt_logs), 특허 청구항3(error_timing_type)
import _storage

# ═══ STORAGE PATH ═══
STORAGE_FILE = _storage.STORAGE_FILE  # 단일 경로 통일

def load_storage() -> dict:
    """storage_data.json 로드 → dict 반환."""
    return _storage.load()

def save_to_storage(items: list) -> None:
    data = _storage.load()
    existing = data.get("saved_questions", [])
    ids = {x["id"] for x in existing if isinstance(x, dict) and "id" in x}
    for it in items:
        if it["id"] not in ids:
            existing.append(it)
            ids.add(it["id"])
    data["saved_questions"] = existing
    _storage.save(data)

# ═══ 연구 데이터 — rt_logs 저장 ═══════════════════════════════
# 논문 01·02·04 핵심 데이터 / 특허 3순위 (오답타이밍 자동분류)
# IRB 승인 전: _storage.RESEARCH_PHASE = "pre_irb"
# IRB 승인 후: _storage.py 에서 "post_irb" 로 한 번만 변경하면 전 파일 동시 적용

def _classify_error_timing(seconds_remaining: float, timer_setting: float) -> str:
    """타이머 잔여시간 비율 → fast/mid/slow 자동 분류 (특허 B-3 핵심).

    Args:
        seconds_remaining: 남은 시간(초)
        timer_setting: 총 제한시간(초)
    Returns:
        "fast_wrong" | "mid_wrong" | "slow_wrong" | "unknown"
    """
    if timer_setting <= 0:
        return "unknown"
    ratio = seconds_remaining / timer_setting
    if ratio > 0.667:
        return "fast_wrong"   # 충동형 오답 (잔여 > 2/3)
    elif ratio > 0.333:
        return "mid_wrong"    # 표준형 오답 (1/3 ~ 2/3)
    else:
        return "slow_wrong"   # 인지과부하형 오답 (잔여 < 1/3)

# ═══ 전역 CSS — 화력전 전용 폰게임 스타일 ═══
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');

/* ── 기반 ── */
.stApp{background:#06060e!important;color:#eeeeff!important;}
section[data-testid="stSidebar"]{display:none!important;}
header[data-testid="stHeader"]{background:transparent!important;height:0!important;min-height:0!important;overflow:hidden!important;}
.block-container{padding-top:0!important;padding-bottom:0!important;margin-top:-8px!important;}

/* ── iframe 클릭 차단 방지 — components.html이 버튼을 덮지 않도록 ── */
iframe[height="0"]{pointer-events:none!important;position:absolute!important;}
div[data-testid="stButton"]{position:relative;z-index:10!important;}

/* ── 타이틀 헤더 ── */
.ah{text-align:center;padding:0;margin:0 0 2px 0;line-height:1;}
.ah h1{font-family:'Orbitron',monospace!important;font-size:0.85rem;font-weight:900;margin:0;
  background:linear-gradient(90deg,#00d4ff,#ffffff,#FFD600,#00d4ff);background-size:300%;
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  animation:titleShine 2s linear infinite;letter-spacing:4px;}

/* ── 키프레임 ── */
@keyframes titleShine{0%{background-position:200% center}100%{background-position:-200% center}}
@keyframes warningPulse{0%,100%{color:#ff4466;text-shadow:0 0 8px rgba(255,68,102,0.8);}50%{color:#ff8888;text-shadow:0 0 20px rgba(255,68,102,1),0 0 40px rgba(255,0,50,0.6);}}
@keyframes neonPulse{0%,100%{box-shadow:0 0 5px #00d4ff,0 0 15px rgba(0,212,255,0.4);}50%{box-shadow:0 0 15px #00d4ff,0 0 40px rgba(0,212,255,0.7),0 0 60px rgba(0,212,255,0.3);}}
@keyframes answerGlow{0%,100%{opacity:1;}50%{opacity:0.85;}}
@keyframes shake{0%{transform:translate(0,0)}20%{transform:translate(-4px,2px)}40%{transform:translate(4px,-2px)}60%{transform:translate(-3px,3px)}80%{transform:translate(3px,-3px)}100%{transform:translate(0,0)}}

/* ── HUD 배틀바 ── */
.bt{display:flex;align-items:center;justify-content:space-between;
  padding:0.15rem 0.8rem;border-radius:8px;margin-bottom:2px;
  background:#0a0c18;border:1px solid rgba(0,212,255,0.4);
  box-shadow:0 0 15px rgba(0,212,255,0.1);}
.bt-g,.bt-v{background:#080c14;border:1px solid rgba(0,212,255,0.5);}
.bq{font-family:'Orbitron',monospace;font-size:1.5rem;font-weight:900;}
.bq-g,.bq-v{color:#00d4ff;text-shadow:0 0 12px rgba(0,212,255,0.9);}
.bs{font-family:'Orbitron',monospace;font-size:1.0rem;font-weight:800;color:#fff;}

/* ── 라운드 도트 → 전투 프로그레스 pill ── */
.rd-dots{display:flex;justify-content:center;gap:0.3rem;}
.rd-dot{width:38px;height:22px;border-radius:5px;border:1.5px solid #1e2030;
  display:flex;align-items:center;justify-content:center;
  font-size:0.62rem;font-weight:900;letter-spacing:0.5px;}
.rd-cur{border-color:#00d4ff!important;color:#00d4ff!important;
  box-shadow:0 0 10px rgba(0,212,255,0.6)!important;
  background:rgba(0,212,255,0.08)!important;animation:neonPulse 1s infinite;}
.rd-ok{background:#ff6600;border-color:#ff8800;color:#fff;}
.rd-no{background:#ff2244;border-color:#ff2244;color:#fff;}
.rd-wait{background:#0a0c18;border-color:#1e2030;color:#2a2a3a;}

/* ── 문제 카드 ── */
.qb{border-radius:14px;padding:0.55rem 0.75rem;margin:0.05rem 0;background:#080c1a;}
.qb-g{background:#07091a!important;
  border:1.5px solid rgba(0,212,255,0.35)!important;
  border-left:4px solid rgba(0,212,255,0.75)!important;
  border-radius:14px!important;
  box-shadow:0 0 24px rgba(0,212,255,0.07);}
.qb-v{background:#07100a!important;
  border:1.5px solid rgba(0,190,100,0.35)!important;
  border-left:4px solid rgba(0,190,100,0.75)!important;
  border-radius:14px!important;
  box-shadow:0 0 24px rgba(0,190,100,0.07);}
.qc{font-family:'Orbitron',monospace;font-size:0.6rem;font-weight:700;margin-bottom:3px;
  letter-spacing:3px;}
.qc-g{color:#2288bb;}
.qc-v{color:#228855;}
.qt{font-family:'Rajdhani',sans-serif;color:#eeeeff;font-size:0.81rem;font-weight:700;line-height:1.6;word-break:keep-all;}
.qk{color:#00d4ff;font-weight:900;font-size:0.85rem;border-bottom:2px solid #00d4ff;
  text-shadow:0 0 12px rgba(0,212,255,0.9);padding:0 2px;}

/* ── 답 버튼 — 게임 스타일 ── */
div[data-testid="stButton"] button{
  background:#0a0c18!important;
  border:2px solid rgba(0,212,255,0.35)!important;
  border-radius:10px!important;
  font-family:'Rajdhani',sans-serif!important;
  font-size:1.05rem!important;font-weight:700!important;
  padding:0.55rem 0.9rem!important;
  text-align:left!important;
  min-height:52px!important;
  width:100%!important;
  transition:box-shadow 0.15s ease,border-color 0.15s ease!important;
  transform:none!important;
  color:#ddd8c8!important;
}
div[data-testid="stButton"] button p{
  font-size:1.05rem!important;font-weight:700!important;
  color:#ddd8c8!important;text-align:left!important;
}
div[data-testid="stButton"] button:hover{
  background:rgba(0,212,255,0.07)!important;
  border-color:#00d4ff!important;
  box-shadow:0 0 20px rgba(0,212,255,0.35)!important;
}
div[data-testid="stButton"] button:active{
  transform:scale(0.98)!important;
}

/* ── 브리핑 카드 ── */
.wb{background:#0a0c18;border-radius:16px;padding:1.2rem 1.2rem;margin:0.4rem 0;
  border:1px solid rgba(0,212,255,0.3);}
.wb-qn-ok{color:#00d4ff;}.wb-qn-no{color:#ff2244;}
.wb-s{font-size:1.8rem;font-weight:700;color:#f0f0f0;line-height:2;margin-bottom:0.8rem;word-break:keep-all;}
.wb-h{color:#00d4ff;font-weight:900;font-size:2rem;text-decoration:underline;text-decoration-color:#00d4ff;}
.wb-hn{color:#ff2244;font-weight:900;font-size:2rem;text-decoration:underline;text-decoration-color:#ff2244;}
.wb-k{font-size:1.4rem;font-weight:600;color:#ccc;line-height:1.7;}
.wb-e{font-size:1.3rem;color:#aaa;padding:0.5rem 0.8rem;background:rgba(0,212,255,0.06);
  border-left:4px solid #00d4ff;border-radius:0 10px 10px 0;}
.zl{color:#00d4ff!important;font-family:'Orbitron',monospace!important;letter-spacing:4px!important;}
details{background:rgba(0,212,255,0.03)!important;border-radius:12px!important;}
summary{color:#aaa!important;font-weight:700!important;}

/* ── 스크롤바 ── */
::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-track{background:#0a0a0a;}
::-webkit-scrollbar-thumb{background:rgba(0,212,255,0.4);border-radius:2px;}

/* ── 모바일 반응형 ── */
@media(max-width:768px){
  .block-container{padding-top:0.5rem!important;padding-bottom:2rem!important;padding-left:0.6rem!important;padding-right:0.6rem!important;}
  .ah h1{font-size:1.4rem!important;letter-spacing:2px!important;}
  div[data-testid="stButton"] button{font-size:1.5rem!important;padding:0.8rem 1rem!important;min-height:64px!important;}
  div[data-testid="stButton"] button p{font-size:1.5rem!important;}
  .qt{font-size:1.49rem!important;}.qk{font-size:1.6rem!important;}
  .wb-s{font-size:1.6rem!important;}.wb-h,.wb-hn{font-size:1.75rem!important;}
  .wb-k{font-size:1.25rem!important;}.wb-e{font-size:1.15rem!important;}
  .bq{font-size:1.2rem!important;}
}
@media(max-width:480px){
  .block-container{padding-top:0.3rem!important;padding-bottom:1.5rem!important;padding-left:0.3rem!important;padding-right:0.3rem!important;}
  .ah h1{font-size:0.95rem!important;letter-spacing:1px!important;}
  div[data-testid="stButton"] button{font-size:0.98rem!important;padding:0.5rem 0.6rem!important;min-height:52px!important;border-radius:8px!important;}
  div[data-testid="stButton"] button p{font-size:0.98rem!important;}
  .qt{font-size:0.98rem!important;line-height:1.6!important;}.qk{font-size:1.06rem!important;}
  .qb{padding:0.7rem!important;border-radius:10px!important;}
  .bq{font-size:0.95rem!important;}.bs{font-size:0.82rem!important;}
  .rd-dot{width:20px!important;height:20px!important;}
}
@media(max-width:360px){
  .ah h1{font-size:0.9rem!important;}
  div[data-testid="stButton"] button{font-size:1.0rem!important;}
  div[data-testid="stButton"] button p{font-size:1.0rem!important;}
  .qt{font-size:1.02rem!important;}.qk{font-size:1.1rem!important;}
}
</style>
""", unsafe_allow_html=True)

# ═══ 문제 ═══
GQ=[]

# ═══ GRAMMAR BATCH JSON 자동 로드 ═══
import glob as _glob

def _load_grammar_batches() -> list:
    """data/ 폴더의 firepower_grammar_batch*.json 전부 읽어서 GQ 포맷으로 변환"""
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "firepower")
    batch_files = sorted(_glob.glob(os.path.join(DATA_DIR, "firepower_grammar_batch*.json")))
    loaded = []
    existing_ids = {q["id"] for q in GQ}
    for fpath in batch_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                items = json.load(f)
            for q in items:
                if q.get("id") in existing_ids:
                    continue  # 중복 방지
                # 배치 포맷 → GQ 포맷 변환
                converted = {
                    "id":       q.get("id", ""),
                    "word_count": q.get("word_count", 10),
                    "diff":     q.get("diff", "easy"),
                    "text":     q.get("sentence", q.get("text", "")),
                    "ch":       q.get("choices",  q.get("ch", [])),
                    "a":        q.get("answer",   q.get("a", 0)),
                    "ex":       q.get("explanation",    q.get("ex", "")),
                    "exk":      q.get("explanation_kr", q.get("exk", "")),
                    "cat":      q.get("cat", "GRAMMAR"),
                    "kr":       q.get("kr", ""),
                    "tp":       "grammar",
                }
                loaded.append(converted)
                existing_ids.add(converted["id"])
        except Exception:
            pass
    return loaded

GQ.extend(_load_grammar_batches())

# ═══ FORM BATCH JSON 자동 로드 ═══
FQ = []  # Form Questions

def _load_form_batches() -> list:
    """data/ 폴더의 firepower_form_batch*.json 전부 읽어서 FQ 포맷으로 변환"""
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "firepower")
    batch_files = sorted(_glob.glob(os.path.join(DATA_DIR, "firepower_form_batch*.json")))
    loaded = []
    existing_ids = set()
    for fpath in batch_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                items = json.load(f)
            for q in items:
                if q.get("id") in existing_ids:
                    continue
                converted = {
                    "id":        q.get("id", ""),
                    "word_count": q.get("word_count", 10),
                    "diff":      q.get("diff", "easy"),
                    "text":      q.get("sentence", q.get("text", "")),
                    "ch":        q.get("choices",  q.get("ch", [])),
                    "a":         q.get("answer",   q.get("a", 0)),
                    "ex":        q.get("explanation",    q.get("ex", "")),
                    "exk":       q.get("explanation_kr", q.get("exk", "")),
                    "cat":       q.get("cat", "FORM"),
                    "kr":        q.get("kr", ""),
                    "tp":        "form",
                }
                loaded.append(converted)
                existing_ids.add(converted["id"])
        except Exception:
            pass
    return loaded

FQ.extend(_load_form_batches())
# ═══ LINK BATCH JSON 로딩 ═══
LQ = []

def _load_link_batches() -> list:
    """data/ 폴더의 firepower_link_batch*.json 읽어서 LQ 로 변환"""
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "firepower")
    batch_files = sorted(_glob.glob(os.path.join(DATA_DIR, "firepower_link_batch*.json")))
    loaded = []
    seen = set()
    for fp in batch_files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                items = json.load(f)
            for q in items:
                if q.get("id") in seen:
                    continue
                converted = {
                    "id":        q.get("id", ""),
                    "word_count": q.get("word_count", 10),
                    "diff":      q.get("diff", "easy"),
                    "text":      q.get("sentence", q.get("text", "")),
                    "ch":        q.get("choices",  q.get("ch", [])),
                    "a":         q.get("answer",   q.get("a", 0)),
                    "ex":        q.get("explanation",    q.get("ex", "")),
                    "exk":       q.get("explanation_kr", q.get("exk", "")),
                    "cat":       q.get("cat", "LINK"),
                    "kr":        q.get("kr", ""),
                    "tp":        "link",
                }
                loaded.append(converted)
                seen.add(converted["id"])
        except Exception:
            pass
    return loaded

LQ.extend(_load_link_batches())


# ═══ VOCAB BATCH JSON 로딩 ═══
VQ = []

def _load_vocab_batches() -> list:
    """data/ 폴더의 firepower_vocab_batch*.json 읽어서 VQ 로 변환"""
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "firepower")
    batch_files = sorted(_glob.glob(os.path.join(DATA_DIR, "firepower_vocab_batch*.json")))
    loaded = []
    seen = set()
    for fp in batch_files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                items = json.load(f)
            for q in items:
                if q.get("id") in seen:
                    continue
                converted = {
                    "id":        q.get("id", ""),
                    "word_count": q.get("word_count", 10),
                    "diff":      q.get("diff", "easy"),
                    "text":      q.get("sentence", q.get("text", "")),
                    "ch":        q.get("choices",  q.get("ch", [])),
                    "a":         q.get("answer",   q.get("a", 0)),
                    "ex":        q.get("explanation",    q.get("ex", "")),
                    "exk":       q.get("explanation_kr", q.get("exk", "")),
                    "cat":       q.get("cat", "VOCAB"),
                    "kr":        q.get("kr", ""),
                    "tp":        "vocab",
                }
                loaded.append(converted)
                seen.add(converted["id"])
        except Exception:
            pass
    return loaded

VQ.extend(_load_vocab_batches())

# ═══ 세션 ═══
D={"started":False,"cq":None,"qi":0,"sc":0,"wrong":0,"ta":0,"sk":0,"msk":0,
    "ans":False,"sel":None,"tsec":30,"qst":None,"round_qs":[],"round_results":[],"round_timings":[],
    "round_num":1,"phase":"lobby","mode":None,"used":[],
    "adp_level":"normal",
    "adp_history":[],
}
for k,v in D.items():
    if k not in st.session_state: st.session_state[k]=v

if st.session_state.get("_p5_just_left", False):
    st.session_state._p5_just_left = False
    for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","round_timings","round_num","mode"]:
        if k in D: st.session_state[k] = D[k]
    st.session_state.phase = "lobby"
    st.session_state.sel_mode = None
    st.session_state.tsec = 30
    st.session_state.tsec_chosen = False

def pool(m: str) -> list:
    """모드별 문제 풀 반환 (grammar/form/link/vocab)."""
    return GQ if m=="grammar" else FQ if m=="form" else LQ if m=="link" else VQ if m=="vocab" else LQ+VQ
FORM_CATS=["명사형","형용사형","부사형","동사형","분사형","FORM"]
GRP={
    # g1 = GRAMMAR
    "g1":[
        "수동태","수일치","시제","가정법","도치",
        "수동태/수일치","가정법/당위","분사구문",
        "관계대명사","접속사","동명사/준동사","GRAMMAR"
    ],
    # g2 = FORM (품사전환)
    "g2": FORM_CATS,
    # g3 = LINK (미래)
    "g3":["접속사","동명사/준동사","분사구문","관계대명사"]
}
GRP["g3"] = ["전치사","접속사","접속부사","LINK"]

VGRP={"v1":"easy","v2":"hard"}

def _calc_adp_level() -> str:
    """
    즉시 전환 방식: 1문제 결과로 바로 난이도 변경
    word_count 기준 — easy:≤15 / normal:16-19 / hard:20-23
    맞으면 한 단계 UP, 틀리면 한 단계 DOWN
    """
    hist = st.session_state.get("adp_history", [])
    if len(hist) < 1:
        return st.session_state.get("adp_level", "normal")
    last = hist[-1]  # 가장 최근 1문제만 반영
    cur  = st.session_state.get("adp_level", "normal")
    if last == 1:   # 정답 → 한 단계 UP
        if cur == "easy":   return "normal"
        if cur == "normal": return "hard"
        return "hard"
    else:           # 오답 → 한 단계 DOWN
        if cur == "hard":   return "normal"
        if cur == "normal": return "easy"
        return "easy"

def pick5(m: str, grp: str | None = None) -> list:
    """적응형 난이도 적용하여 5문제 선택 (특허 A-3 핵심).

    Args:
        m: 모드 ("grammar" | "form" | "link" | "vocab")
        grp: 그룹 코드 ("g1"~"g4", "v1"~"v4" 등)
    Returns:
        선택된 5문제 리스트
    """
    # ── FORM 모드(g2): FQ 풀 사용 ──
    if grp == "g2":
        p = FQ if FQ else pool(m)
        adp = _calc_adp_level()
        st.session_state.adp_level = adp
        diff_p = [q for q in p if q.get("diff","easy") == adp]
        if len(diff_p) >= 5: p = diff_p
        cat_p = [q for q in p if q.get("cat","") in FORM_CATS]
        if len(cat_p) >= 5: p = cat_p
        avail = [q for q in p if q["id"] not in st.session_state.used]
        if len(avail) < 5: st.session_state.used = []; avail = p.copy()
        chosen = random.sample(avail, min(5, len(avail)))
        for q in chosen: st.session_state.used.append(q["id"]); q["tp"] = "form"
        return chosen
    p=pool(m)
    if grp and grp in GRP:
        cats=GRP[grp]
        p=[q for q in p if q.get("cat","") in cats]
        adp = _calc_adp_level()
        st.session_state.adp_level = adp
        # ── word_count 기반 diff 필터 (문제 충분할 때만 적용) ──
        diff_p = [q for q in p if q.get("diff","easy") == adp]
        if len(diff_p) >= 5:
            p = diff_p
        # ── 기존 cat 기반 적응형 (fallback) ──
        if adp == "hard" and len(p) >= 5:
            hard_cats = ["가정법","가정법/당위","도치","분사구문"]
            hard_p = [q for q in p if q.get("cat","") in hard_cats]
            easy_p = [q for q in p if q.get("cat","") not in hard_cats]
            if len(hard_p) >= 3 and len(easy_p) >= 2:
                avail_h = [q for q in hard_p if q["id"] not in st.session_state.used]
                avail_e = [q for q in easy_p if q["id"] not in st.session_state.used]
                if len(avail_h) < 3: avail_h = hard_p.copy()
                if len(avail_e) < 2: avail_e = easy_p.copy()
                chosen = random.sample(avail_h, min(3,len(avail_h))) + random.sample(avail_e, min(2,len(avail_e)))
                random.shuffle(chosen)
                for q in chosen: st.session_state.used.append(q["id"]); q["tp"]=grp or "grammar"
                return chosen
        elif adp == "easy" and len(p) >= 5:
            easy_cats = ["수일치","수동태/수일치","접속사","관계대명사"]
            easy_p = [q for q in p if q.get("cat","") in easy_cats]
            hard_p = [q for q in p if q.get("cat","") not in easy_cats]
            if len(easy_p) >= 4 and len(hard_p) >= 1:
                avail_e = [q for q in easy_p if q["id"] not in st.session_state.used]
                avail_h = [q for q in hard_p if q["id"] not in st.session_state.used]
                if len(avail_e) < 4: avail_e = easy_p.copy()
                if len(avail_h) < 1: avail_h = hard_p.copy()
                chosen = random.sample(avail_e, min(4,len(avail_e))) + random.sample(avail_h, min(1,len(avail_h)))
                random.shuffle(chosen)
                for q in chosen: st.session_state.used.append(q["id"]); q["tp"]=grp or "grammar"
                return chosen
    elif grp and grp in VGRP:
        adp = _calc_adp_level()
        st.session_state.adp_level = adp
        if adp == "hard":
            diff_p = [q for q in p if q.get("diff","") == "hard"]
            if len(diff_p) >= 5: p = diff_p
        elif adp == "easy":
            diff_p = [q for q in p if q.get("diff","") == "easy"]
            if len(diff_p) >= 5: p = diff_p
        else:
            diff = VGRP[grp]
            p = [q for q in p if q.get("diff","") == diff]
        if len(p) < 5: p = pool(m)
    avail=[q for q in p if q["id"] not in st.session_state.used]
    if len(avail)<5: st.session_state.used=[]; avail=p.copy()
    chosen=random.sample(avail,min(5,len(avail)))
    for q in chosen: st.session_state.used.append(q["id"]); q["tp"]=q.get("tp","grammar") if q.get("tp") in ("grammar","form","link","vocab") else (grp or ("grammar" if q["id"].startswith("G") else "vocab"))
    return chosen

def fq(t: str) -> str:
    """문제 문장의 빈칸을 HTML 하이라이트로 교체."""
    return t.replace("_______",'<span class="qk">________</span>')

def tcls(r: int, t: int) -> str:
    """정답률 기반 CSS 클래스 반환 (safe/warn/danger/critical)."""
    x=r/t if t>0 else 0
    return "safe" if x>0.6 else "warn" if x>0.35 else "danger" if x>0.15 else "critical"

# ════════════════════════════════════════
# PHASE: BATTLE
# ════════════════════════════════════════
if st.session_state.phase=="battle":
    if st.session_state.get("_battle_entry_ans_reset", False):
        st.session_state.ans = False
        st.session_state["_battle_entry_ans_reset"] = False
    q=st.session_state.cq
    if not q: st.session_state.phase="lobby"; st.rerun()
    _tp = q.get("tp","grammar")
    ig = _tp in ("grammar","g1","g2","g3","form","link"); th="g" if ig else "v"; bt="primary" if ig else "secondary"
    ej={"grammar":"🔴","g1":"🔴","form":"🔵","g2":"🔵","link":"🔴","g3":"🔴","vocab":"🔵"}.get(_tp,"🔵")
    tn={"grammar":"문법","g1":"문법","form":"품사","g2":"품사","link":"연결","g3":"연결","vocab":"어휘"}.get(_tp,"어휘")

    _en_mode = {"grammar":"GRM · 문법 사격","g1":"GRM · 문법 사격","form":"FORM · 형태 변환","g2":"FORM · 형태 변환","link":"LINK · 연결 작전","g3":"LINK · 연결 작전","vocab":"VOCAB · 어휘 폭격"}.get(_tp,"VOCAB · 어휘 폭격")
    _rn_str  = f"WAVE {st.session_state.round_num}" if st.session_state.round_num > 1 else "WAVE 1"
    st.markdown(f'<div class="ah"><h1>⚡ {_en_mode} FIREPOWER · {_rn_str}</h1></div>', unsafe_allow_html=True)

    # ── HUD 배틀바 ──
    qi=st.session_state.qi; results=st.session_state.round_results
    dots=""
    for i in range(5):
        if i<len(results):
            cls="rd-ok" if results[i] else "rd-no"
            sym="✓" if results[i] else "✗"
        elif i==qi:
            cls="rd-cur"; sym=str(i+1)
        else:
            cls="rd-wait"; sym=str(i+1)
        dots+=f'<div class="rd-dot {cls}">{sym}</div>'

    st.markdown(f'''<div class="bt bt-{th}">
        <span class="bq bq-{th}">{ej} {qi+1}/5</span>
        <div class="rd-dots">{dots}</div>
        <span class="bs">✅{st.session_state.sc} ❌{st.session_state.wrong}</span>
    </div>''', unsafe_allow_html=True)

    # ── 타이머 ──
    if not st.session_state.ans:
        elapsed=time.time()-st.session_state.qst
        total=st.session_state.tsec; rem=max(0,total-int(elapsed))
        tcl=tcls(rem,total); pct=rem/total*100 if total>0 else 0

        components.html(f"""
        <style>
        *{{margin:0;padding:0;box-sizing:border-box;}}
        body{{background:transparent;overflow:hidden;font-family:'Arial Black',monospace;margin:0;padding:0;}}
        #w{{text-align:center;padding:0 4px;margin:0;line-height:1;}}
        #n{{font-size:2.4rem;font-weight:900;animation:pulse 1s ease-in-out infinite;letter-spacing:2px;}}
        #bw{{background:#111;border-radius:10px;height:12px;margin:3px 4px 0;overflow:hidden;border:1px solid #222;}}
        #b{{height:100%;border-radius:10px;transition:width 1s linear;}}
        .safe{{color:#ff8833;text-shadow:0 0 20px #ff8833,0 0 40px #ff6600;}}
        .warn{{color:#FFD600;text-shadow:0 0 25px #FFD600,0 0 50px #ff8800;}}
        .danger{{color:#ff4444;text-shadow:0 0 35px #ff4444,0 0 70px #ff0000;animation:shakeNum 0.3s infinite!important;}}
        .critical{{color:#ff0000;text-shadow:0 0 50px #ff0000,0 0 100px #ff0000;font-size:2.8rem!important;animation:shakeNum 0.15s infinite!important;}}
        .bs{{background:linear-gradient(90deg,#cc4400,#ff8833);box-shadow:0 0 10px #ff6600;}}
        .bw{{background:linear-gradient(90deg,#cc8800,#FFD600);box-shadow:0 0 10px #FFD600;}}
        .bd{{background:linear-gradient(90deg,#cc2200,#ff4444);box-shadow:0 0 15px #ff4444;animation:bpulse 0.5s infinite;}}
        .bc{{background:linear-gradient(90deg,#ff0000,#ff4444);box-shadow:0 0 25px #ff0000;animation:bpulse 0.2s infinite;}}
        @keyframes pulse{{0%,100%{{transform:scale(1);opacity:1}}50%{{transform:scale(1.08);opacity:0.85}}}}
        @keyframes shakeNum{{0%{{transform:translate(0,0)}}25%{{transform:translate(-4px,0)}}75%{{transform:translate(4px,0)}}100%{{transform:translate(0,0)}}}}
        @keyframes bpulse{{0%,100%{{opacity:1}}50%{{opacity:0.5}}}}
        </style>
        <div id="w">
          <div id="n" class="{tcl}">{rem}</div>
          <div id="bw"><div id="b" class="b{'s' if tcl=='safe' else 'w' if tcl=='warn' else 'd' if tcl=='danger' else 'c'}" style="width:{pct}%"></div></div>
        </div>
        <script>
        var l={rem},t={total},fired=false;
        var e=document.getElementById("n"),b=document.getElementById("b");
        setInterval(function(){{
            l--;if(l<0)l=0;
            e.textContent=l;
            var r=l/t;
            var c=r>0.6?"safe":r>0.35?"warn":r>0.15?"danger":"critical";
            e.className=c;
            b.className="b"+(r>0.6?"s":r>0.35?"w":r>0.15?"d":"c");
            b.style.width=(r*100)+"%";
            if(l<=0 && !fired){{fired=true;
              var btns=window.parent.document.querySelectorAll('button');
              btns.forEach(function(btn){{if((btn.innerText||'').indexOf('TIMEOUT')>-1)btn.click();}});
            }}
        }},1000);
        </script>""", height=52)

        if rem<=0:
            st.session_state.phase="lost"; st.rerun()
        # 숨겨진 타임아웃 버튼 (JS 타이머가 0이 되면 자동 클릭)
        st.markdown('<div style="height:0;overflow:hidden;">', unsafe_allow_html=True)
        if st.button("TIMEOUT", key="timeout_btn"):
            st.session_state.phase="lost"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── 문제 카드 ──
    st.markdown(f'<div class="qb qb-{th}"><div class="qc qc-{th}">{ej} {tn} · {q.get("cat","")}</div><div class="qt">{fq(q["text"])}</div></div>', unsafe_allow_html=True)

    # ── 답 버튼 4개 — A/B/C/D 네온 스타일 ──
    # iOS 2-phase rerun fix
    if st.session_state.get("_fp_processing"):
        st.session_state.pop("_fp_processing")
        if st.session_state.wrong>=2:
            st.session_state.phase='lost'; st.rerun()
        if st.session_state.qi>=4:
            st.session_state.phase='victory' if st.session_state.sc>=4 else 'lost'
            # ── 게임 결과 기록 (activity.jsonl + Google Sheets) ──
            # PAPER: 논문A(정복률), 논문B(참여율)
            try:
                _acc = round(st.session_state.sc / max(st.session_state.ta, 1) * 100, 1)
                _record_activity(
                    nickname=st.session_state.get("battle_nickname", "guest"),
                    arena="P5",
                    acc=_acc,
                    completed=(st.session_state.sc >= 4),
                )
            except Exception:
                pass
            st.rerun()
        _nqi2=st.session_state.qi+1
        if _nqi2<len(st.session_state.round_qs):
            st.session_state.qi=_nqi2
            st.session_state.cq=st.session_state.round_qs[_nqi2]
            st.session_state.ans=False; st.session_state.sel=None
        else:
            st.session_state.phase='victory' if st.session_state.sc>=4 else 'lost'
            # ── 게임 결과 기록 (activity.jsonl + Google Sheets) ──
            # PAPER: 논문A(정복률), 논문B(참여율)
            try:
                _acc = round(st.session_state.sc / max(st.session_state.ta, 1) * 100, 1)
                _record_activity(
                    nickname=st.session_state.get("battle_nickname", "guest"),
                    arena="P5",
                    acc=_acc,
                    completed=(st.session_state.sc >= 4),
                )
            except Exception:
                pass
        st.rerun()

    if not st.session_state.ans:
        _qi = st.session_state.get('qi', 0)
        _rn = st.session_state.get('round_num', 0)

        _labels = ["A", "B", "C", "D"]
        # ★ div id 래퍼로 버튼 색상 확실히 고정
        # ★ .stMarkdown/.element-container 여백 0으로 → 버튼 간격 밀림 방지
        _ans_cfg = [
            ("fp-ans-a", "#ff6633", "#160800", "rgba(255,102,51,0.55)"),
            ("fp-ans-b", "#00E5FF", "#001518", "rgba(0,229,255,0.55)"),
            ("fp-ans-c", "#FF2D55", "#140008", "rgba(255,45,85,0.55)"),
            ("fp-ans-d", "#44FF88", "#001408", "rgba(68,255,136,0.55)"),
        ]
        _css = """<style>
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
        for _aid, _col, _bg, _sh in _ans_cfg:
            _css += (
                f'#btn-{_aid} div[data-testid="stButton"] button{{'
                f'border-left:5px solid {_col}!important;background:{_bg}!important;'
                f'border-color:{_col}!important;color:{_col}!important;}}'
                f'#btn-{_aid} div[data-testid="stButton"] button p{{color:{_col}!important;}}'
                f'#btn-{_aid} div[data-testid="stButton"] button:hover{{box-shadow:0 0 22px {_sh}!important;}}'
            )
        _css += "</style>"
        st.markdown(_css, unsafe_allow_html=True)
        import streamlit.components.v1 as _fp_js
        _fp_js.html("""<script>
        function fpColors(){
            var doc=window.parent.document;
            var btns=doc.querySelectorAll('button');
            var colors=[
                {bg:'#160800',bl:'5px solid #ff6633',co:'#ff6633'},
                {bg:'#001518',bl:'5px solid #00E5FF',co:'#00E5FF'},
                {bg:'#140008',bl:'5px solid #FF2D55',co:'#FF2D55'},
                {bg:'#001408',bl:'5px solid #44FF88',co:'#44FF88'}
            ];
            var ci=0;
            btns.forEach(function(btn){
                var t=btn.innerText||btn.textContent||'';
                if(t.match(/[【]A[】]|[【]B[】]|[【]C[】]|[【]D[】]/)){
                    var clr=colors[ci%4];
                    btn.style.setProperty('background',clr.bg,'important');
                    btn.style.setProperty('border-left',clr.bl,'important');
                    btn.style.setProperty('border-color',clr.co,'important');
                    btn.style.setProperty('color',clr.co,'important');
                    btn.style.setProperty('-webkit-text-fill-color',clr.co,'important');
                    btn.style.setProperty('-webkit-tap-highlight-color','rgba(0,0,0,0)','important');
                    btn.blur();
                    ci++;
                }
            });
        }
        setTimeout(fpColors,100);setTimeout(fpColors,300);setTimeout(fpColors,600);setInterval(fpColors,500);
        </script>""", height=0)

        _btn_slot = st.empty()
        _clicked = None
        with _btn_slot.container():
            for _ii, _ch in enumerate(q['ch']):
                _ch_clean = re.sub(r'^\([A-D]\)[:\s]*', '', _ch).strip()
                _display = f"【{_labels[_ii]}】  {_ch_clean}"
                _aid = _ans_cfg[_ii][0]
                if st.button(_display, key=f"ans_{_rn}_{_qi}_{_ii}", use_container_width=True):
                    _clicked = _ii
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
            # ── ★ rt_log 저장 (논문 01·02·04 / 특허 3순위) ──────────
            # user_id: _storage.get_uid() 로 통일 (POW HQ·Decrypt Op 동일)
            _elapsed_rt = time.time() - st.session_state.qst
            _rem_rt     = max(0, st.session_state.tsec - _elapsed_rt)
            # ── ★ 오답 타이밍 3분류 → 브리핑 저장 로직 연동 (논문B 청구항3) ──
            _timing_type = _classify_error_timing(_rem_rt, st.session_state.tsec) if not ok else None
            if "round_timings" not in st.session_state: st.session_state.round_timings = []
            st.session_state.round_timings.append(_timing_type)
            _storage.save_rt_log(
                q                 = q,
                is_correct        = ok,
                seconds_remaining = _rem_rt,
                timer_setting     = st.session_state.tsec,
                session_no        = st.session_state.get("p5_session_no", 0),
                adp_level         = st.session_state.get("adp_level", "normal"),
                error_timing_type = _timing_type,
            )
            # ────────────────────────────────────────────────────────
            # iOS 2-phase: 버튼 제거 후 다음 문제
            st.session_state["_fp_processing"] = True
            st.rerun()
            nqi = st.session_state.qi + 1
            if nqi < len(st.session_state.round_qs):
                st.session_state.qi = nqi
                st.session_state.cq = st.session_state.round_qs[nqi]
                st.session_state.ans=False; st.session_state.sel=None
            else:
                st.session_state.phase='victory' if st.session_state.sc>=4 else 'lost'
            # ── 게임 결과 기록 (activity.jsonl + Google Sheets) ──
            # PAPER: 논문A(정복률), 논문B(참여율)
            try:
                _acc = round(st.session_state.sc / max(st.session_state.ta, 1) * 100, 1)
                _record_activity(
                    nickname=st.session_state.get("battle_nickname", "guest"),
                    arena="P5",
                    acc=_acc,
                    completed=(st.session_state.sc >= 4),
                )
            except Exception:
                pass
            st.rerun()

    else:
        # ── 정답/오답 피드백 (답 선택 후) ──
        _sel = st.session_state.sel
        _correct_idx = q['a']
        _ok = (_sel == _correct_idx)
        if _ok:
            st.markdown(
                '<div style="text-align:center;padding:12px 0;">'
                '<span style="font-family:Arial Black,sans-serif;font-size:1.6rem;font-weight:900;'
                'color:#44FF88;text-shadow:0 0 20px #44FF88,0 0 50px #22cc66;letter-spacing:4px;">'
                '💥 격파!</span></div>', unsafe_allow_html=True)
        else:
            _ans_text = q['ch'][_correct_idx]
            st.markdown(
                '<div style="text-align:center;padding:12px 0;">'
                '<span style="font-family:Arial Black,sans-serif;font-size:1.4rem;font-weight:900;'
                'color:#FF2D55;text-shadow:0 0 20px #FF2D55,0 0 50px #cc0033;letter-spacing:3px;">'
                '💀 피격!</span>'
                + f' <span style="font-size:1rem;color:#aaa;">정답: {_ans_text}</span>'
                + '</div>', unsafe_allow_html=True)

        st.markdown(f'<div style="background:#0a0c14;border-left:4px solid {"#44FF88" if _ok else "#FF2D55"};border-radius:0 10px 10px 0;padding:8px 12px;margin:4px 0;">'
                    f'<span style="font-size:0.85rem;color:{"#44FF88" if _ok else "#FF2D55"};font-weight:700;">💡 {q.get("exk","")}</span></div>', unsafe_allow_html=True)

        if st.button("▶ 다음 문제", key="next_q", use_container_width=True):
            if st.session_state.wrong>=2:
                st.session_state.phase='lost'; st.rerun()
            if st.session_state.qi>=4:
                st.session_state.phase='victory' if st.session_state.sc>=4 else 'lost'
            # ── 게임 결과 기록 (activity.jsonl + Google Sheets) ──
            # PAPER: 논문A(정복률), 논문B(참여율)
            try:
                _acc = round(st.session_state.sc / max(st.session_state.ta, 1) * 100, 1)
                _record_activity(
                    nickname=st.session_state.get("battle_nickname", "guest"),
                    arena="P5",
                    acc=_acc,
                    completed=(st.session_state.sc >= 4),
                )
            except Exception:
                pass
            nqi = st.session_state.qi + 1
            if nqi < len(st.session_state.round_qs):
                st.session_state.qi = nqi
                st.session_state.cq = st.session_state.round_qs[nqi]
                st.session_state.ans=False; st.session_state.sel=None
            else:
                st.session_state.phase='victory' if st.session_state.sc>=4 else 'lost'
            # ── 게임 결과 기록 (activity.jsonl + Google Sheets) ──
            # PAPER: 논문A(정복률), 논문B(참여율)
            try:
                _acc = round(st.session_state.sc / max(st.session_state.ta, 1) * 100, 1)
                _record_activity(
                    nickname=st.session_state.get("battle_nickname", "guest"),
                    arena="P5",
                    acc=_acc,
                    completed=(st.session_state.sc >= 4),
                )
            except Exception:
                pass
            st.rerun()

# ════════════════════════════════════════
# PHASE: VICTORY
# ════════════════════════════════════════
elif st.session_state.phase=="victory":
    # ── adaptive difficulty 기록 + adp_logs 영속화 ──
    try:
        _sc_adp = st.session_state.get("sc", 0)
        _rate_adp = _sc_adp / 5.0
        _hist = st.session_state.get("adp_history", [])
        _hist.append(_rate_adp)
        st.session_state.adp_history = _hist
        st.session_state.adp_level = _calc_adp_level()
        # ★ adp_logs 영속화 — 세션 종료해도 성장 이력 유지 (논문A 핵심)
        _storage.append_log("adp_logs", {
            "timestamp":   __import__("datetime").datetime.now().isoformat(),
            "user_id":     _storage.get_uid(),
            "adp_level":   st.session_state.adp_level,
            "score":       _sc_adp,
            "rate":        _rate_adp,
            "history_len": len(_hist),
            "week":        _storage.get_week(_storage.get_uid()),
            "research_phase": _storage.RESEARCH_PHASE,
        })
    except: pass
    # ── zpd_logs + p5_logs ──
    try:
        st.session_state.p5_session_no = st.session_state.get("p5_session_no", 0) + 1
        _st2 = _storage.load()
        _uid2 = _storage.get_uid()
        _today2 = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        _sno2 = st.session_state.p5_session_no
        _week2 = _storage.get_week(_uid2)
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
        _storage.save(_st2)
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

    # ── 토리 Victory 메인 이미지 ──
    _ASSETS_V = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    _tori_v_path = os.path.join(_ASSETS_V, "tori_victory.png")
    _cv1, _cv2, _cv3 = st.columns([1, 2, 1])
    with _cv2:
        if os.path.exists(_tori_v_path): st.image(_tori_v_path, width=180)

    _stars_html = "".join([
        f'<div style="position:absolute;left:{random.randint(2,98)}%;top:{random.randint(2,98)}%;'
        f'width:{random.randint(3,12)}px;height:{random.randint(3,12)}px;'
        f'border-radius:50%;background:{"#FFD600" if random.random()>0.4 else "#fff8cc"};'
        f'animation:twinkle {0.3+random.random()*0.8:.1f}s ease-in-out infinite {random.random():.2f}s both;"></div>'
        for _ in range(50)])

    components.html(f"""
    <style>
    *{{margin:0;padding:0;box-sizing:border-box;}}
    body{{background:transparent;overflow:hidden;height:100vh;font-family:'Arial Black',sans-serif;
      display:flex;align-items:center;justify-content:center;}}
    @keyframes vi{{0%{{transform:scale(0) rotate(-20deg);opacity:0;}}65%{{transform:scale(1.12) rotate(3deg);}}100%{{transform:scale(1) rotate(0deg);opacity:1;}}}}
    @keyframes goldGlow{{0%,100%{{text-shadow:0 0 20px #FFD600,0 0 60px #ff8800;}}50%{{text-shadow:0 0 60px #FFD600,0 0 120px #ff8800;}}}}
    @keyframes twinkle{{0%,100%{{opacity:1;transform:scale(1);}}50%{{opacity:0.1;transform:scale(0.2);}}}}
    @keyframes scoreIn{{0%{{transform:translateY(40px);opacity:0;}}100%{{transform:translateY(0);opacity:1;}}}}
    @keyframes barFill{{0%{{width:0%;}}100%{{width:{int(_sc_v/5*100)}%;}}}}
    .wrap{{text-align:center;animation:vi 0.8s cubic-bezier(0.34,1.56,0.64,1) forwards;position:relative;z-index:10;width:90%;}}
    .round-tag{{font-size:0.72rem;color:#886600;font-weight:700;letter-spacing:4px;margin-bottom:4px;}}
    .grade{{font-size:2.2rem;font-weight:900;color:#FFD600;animation:goldGlow 1.5s ease-in-out infinite;letter-spacing:3px;}}
    .scorebox{{background:rgba(255,214,0,0.08);border:2px solid rgba(255,214,0,0.5);
      border-radius:16px;padding:10px 24px;margin:8px auto;display:inline-block;}}
    .sc-num{{font-size:2.8rem;font-weight:900;color:#FFD600;line-height:1;}}
    .sc-label{{font-size:0.72rem;color:#aa8800;font-weight:700;letter-spacing:2px;margin-top:4px;}}
    .bar-wrap{{background:#1a1100;border-radius:20px;height:10px;margin:8px auto;width:85%;overflow:hidden;border:1px solid #443300;}}
    .bar-fill{{height:100%;border-radius:20px;background:linear-gradient(90deg,#886600,#FFD600);animation:barFill 1.2s ease 0.6s both;}}
    .praise{{font-size:0.88rem;color:{_pcol};font-weight:900;margin:6px 0 0;animation:scoreIn 0.5s ease 0.8s both;}}
    </style>
    <div style="position:absolute;width:100%;height:100%;overflow:hidden;top:0;left:0;">{_stars_html}</div>
    <div class="wrap">
        <div class="round-tag">WAVE {_rn_v} COMPLETE</div>
        <div class="grade">{_grade}</div>
        <div class="scorebox">
            <div class="sc-num">{_sc_v}<span style="font-size:1.4rem;color:#886600;"> / 5</span></div>
            <div class="sc-label">✅ {_sc_v}격파 &nbsp;·&nbsp; ❌ {_wr_v}개 놓침</div>
        </div>
        <div class="bar-wrap"><div class="bar-fill"></div></div>
        <div class="praise">{_praise}</div>
    </div>
    """, height=220)

    # ── 토리 한 줄 ──
    _nick_v = st.session_state.get("battle_nickname") or st.session_state.get("nickname","전사")
    _tori_v = f"⛓ 포획 대기 중" if _wr_v > 0 else "전원 격파!"
    _TB = '<span style="background:#331100;border:1px solid #ff6600;border-radius:5px;padding:1px 8px;color:#ff8833;font-weight:900;font-size:11px;letter-spacing:2px;">TORI</span>'
    st.markdown(f'<div style="text-align:center;padding:6px 0;"><div style="margin-bottom:4px;">{_TB}</div><div style="font-size:13px;font-weight:900;color:#ffaa44;">{_nick_v}! {_tori_v} 사령부에 보고하라.</div></div>', unsafe_allow_html=True)

    # ── Adaptive Difficulty 변화 알림 ─────────────────────────
    _adp_v = st.session_state.get("adp_level", "normal")
    _adp_v_color = {"easy": "#44cc66", "normal": "#FFD600", "hard": "#ff3344"}
    _adp_v_next = {
        "easy":   ("🟢 EASY", "계속 틀리면 여기 머문다. 집중해!"),
        "normal": ("🟡 NORMAL", "잘 하면 HARD, 틀리면 EASY — 네 선택이야."),
        "hard":   ("🔴 HARD", "최고 난이도 유지 중. 이게 진짜 실력이야."),
    }
    _v_tag, _v_msg = _adp_v_next[_adp_v]
    _vc = _adp_v_color[_adp_v]
    st.markdown(
        f'<div style="text-align:center;background:#07091a;border:1px solid {_vc}33;'
        f'border-radius:8px;padding:5px 10px;margin:4px 0;">'
        f'<span style="font-family:Orbitron,monospace;font-size:0.75rem;font-weight:900;color:{_vc};">'
        f'{_v_tag}</span>'
        f'<span style="font-size:0.72rem;color:#888;"> · {_v_msg}</span>'
        f'</div>',
        unsafe_allow_html=True
    )
    # ─────────────────────────────────────────────────────────

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
        # ★ adp_logs 영속화 — GAME OVER도 성장 이력 기록 (논문A)
        _storage.append_log("adp_logs", {
            "timestamp":   __import__("datetime").datetime.now().isoformat(),
            "user_id":     _storage.get_uid(),
            "adp_level":   st.session_state.adp_level,
            "score":       _sc_adp,
            "rate":        _rate_adp,
            "history_len": len(_hist),
            "result":      "GAME_OVER",
            "week":        _storage.get_week(_storage.get_uid()),
            "research_phase": _storage.RESEARCH_PHASE,
        })
    except: pass
    try:
        st.session_state.p5_session_no = st.session_state.get("p5_session_no", 0) + 1
        _st3 = _storage.load()
        _uid3 = _storage.get_uid()
        _today3 = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        _sno3 = st.session_state.p5_session_no
        _week3 = _storage.get_week(_uid3)
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
        _storage.save(_st3)
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

    # ── 토리 Warning 메인 이미지 ──
    _ASSETS_GO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    _tori_w_path = os.path.join(_ASSETS_GO, "tori_warning.png")
    _cg1, _cg2, _cg3 = st.columns([1, 2, 1])
    with _cg2:
        if os.path.exists(_tori_w_path): st.image(_tori_w_path, width=200)

    components.html(f"""
    <style>
    *{{margin:0;padding:0;box-sizing:border-box;}}
    body{{background:transparent;overflow:hidden;display:flex;align-items:center;justify-content:center;
      height:100vh;font-family:'Arial Black',sans-serif;}}
    @keyframes crashIn{{0%{{transform:scale(4);opacity:0;}}60%{{transform:scale(0.92);}}100%{{transform:scale(1);opacity:1;}}}}
    @keyframes shakeX{{0%,100%{{transform:translateX(0);}}20%{{transform:translateX(-8px);}}40%{{transform:translateX(8px);}}60%{{transform:translateX(-5px);}}80%{{transform:translateX(5px);}}}}
    @keyframes flicker{{0%,100%{{opacity:1;}}30%{{opacity:0.6;}}60%{{opacity:0.9;}}}}
    @keyframes scoreIn{{0%{{transform:translateY(30px);opacity:0;}}100%{{transform:translateY(0);opacity:1;}}}}
    .wrap{{text-align:center;animation:crashIn 0.6s cubic-bezier(0.34,1.56,0.64,1) forwards;z-index:10;position:relative;}}
    .lost-txt{{font-size:1.8rem;font-weight:900;color:#ff0000;text-shadow:0 0 20px #ff0000;animation:flicker 0.25s infinite;letter-spacing:4px;}}
    .reason{{font-size:0.82rem;color:#ff6644;font-weight:700;margin:4px 0;letter-spacing:2px;background:rgba(255,100,0,0.1);border:1px solid rgba(255,100,0,0.3);border-radius:20px;display:inline-block;padding:2px 14px;}}
    .score{{font-size:2.2rem;font-weight:900;color:#ffcc00;text-shadow:0 0 30px #ffaa00;margin:6px 0;animation:scoreIn 0.5s ease 0.3s both;}}
    .taunt{{font-size:0.92rem;color:#ff8888;font-weight:900;margin:4px 0;animation:shakeX 4s ease-in-out infinite;}}
    .sub{{font-size:0.75rem;color:#ff6666;font-weight:700;opacity:0.9;}}
    </style>
    <div class="wrap">
        <div class="lost-txt">GAME OVER</div>
        <div class="reason">[ {_reason} ]</div>
        <div class="score">{_pct}점</div>
        <div class="taunt">{_taunt}</div>
        <div class="sub">{_sub}</div>
    </div>""", height=200)

    _nick_go = st.session_state.get("battle_nickname") or st.session_state.get("nickname","전사")
    _TB = '<span style="background:#331100;border:1px solid #ff6600;border-radius:5px;padding:1px 8px;color:#ff8833;font-weight:900;font-size:11px;letter-spacing:2px;">TORI</span>'
    st.markdown(f'<div style="text-align:center;padding:6px 0;"><div style="margin-bottom:4px;">{_TB}</div><div style="font-size:13px;font-weight:900;color:#ff6644;">{_nick_go}! 후퇴! 재정비 후 재출격!</div></div>', unsafe_allow_html=True)

    # ── Adaptive Difficulty 하락 경고 ─────────────────────────
    _adp_go = st.session_state.get("adp_level", "normal")
    _go_color = {"easy": "#44cc66", "normal": "#FFD600", "hard": "#ff8833"}
    _go_msgs = {
        "easy":   ("🟢 EASY", "더 내려갈 곳 없다. 여기서 반드시 올라와라."),
        "normal": ("🟡 NORMAL", "틀리면 EASY로 내려간다. 정신 차려."),
        "hard":   ("🔴→🟡 HARD→NORMAL", "한 번 졌다. NORMAL로 내려갈 수도 있다."),
    }
    _go_tag, _go_hint = _go_msgs[_adp_go]
    _gc = _go_color[_adp_go]
    st.markdown(
        f'<div style="text-align:center;background:#0d0005;border:1px solid {_gc}33;'
        f'border-radius:8px;padding:5px 10px;margin:4px 0;">'
        f'<span style="font-family:Orbitron,monospace;font-size:0.75rem;font-weight:900;color:{_gc};">'
        f'{_go_tag}</span>'
        f'<span style="font-size:0.72rem;color:#888;"> · {_go_hint}</span>'
        f'</div>',
        unsafe_allow_html=True
    )
    # ─────────────────────────────────────────────────────────

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
    # ── 브리핑 버튼: 1문제라도 풀었으면 표시 ──
    if _sc > 0:
        st.markdown("""<style>
        div[data-testid="stButton"]:nth-of-type(1) button{
          background:#0a0800!important;border:2px solid #FFD600!important;
          border-left:5px solid #FFD600!important;border-radius:12px!important;
        }
        div[data-testid="stButton"]:nth-of-type(1) button p{color:#FFD600!important;font-size:1.05rem!important;font-weight:900!important;}
        div[data-testid="stButton"]:nth-of-type(1) button:hover{box-shadow:0 0 20px rgba(255,214,0,0.5)!important;}
        </style>""", unsafe_allow_html=True)
        if st.button(f"📋 브리핑 보기  ({_sc}문제 복기)", use_container_width=True):
            st.session_state.phase="briefing"; st.rerun()

    bc=st.columns(2)
    with bc[0]:
        if st.button("🔥 설욕전! 다시 싸운다!", use_container_width=True):
            for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","round_timings","round_num"]:
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

    /* ── 다음 심문 버튼 ── */
    .br-next-btn div[data-testid="stButton"] button{
        background:#0a0a20!important;border:2px solid #00ccff!important;
        border-radius:12px!important;color:#00ddff!important;
        font-size:1.0rem!important;font-weight:900!important;min-height:50px!important;}
    .br-next-btn div[data-testid="stButton"] button p{color:#00ddff!important;font-size:1.0rem!important;font-weight:900!important;}

    /* ── 포획 버튼 ── */
    .br-jail-btn div[data-testid="stButton"] button{
        background:#0c1800!important;border:2.5px solid #44ee66!important;
        border-radius:12px!important;color:#44ee66!important;
        font-size:0.92rem!important;font-weight:900!important;min-height:46px!important;}
    .br-jail-btn div[data-testid="stButton"] button p{color:#44ee66!important;font-size:0.92rem!important;font-weight:900!important;}

    /* ── POW HQ CTA 버튼 ── */
    .br-pow-btn div[data-testid="stButton"] button{
        background:#0e0020!important;border:2px solid #8833ff!important;
        border-radius:12px!important;color:#aa66ff!important;
        font-size:0.92rem!important;font-weight:900!important;min-height:48px!important;}
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
        st.session_state.br_auto_jailed = set()  # 오답 자동 포획 추적
        st.session_state.br_jail_count = 0
        st.session_state["_br_game_uid"] = _br_game_uid
    for _bk,_bv in {"br_saved":set(),"br_auto_jailed":set(),"br_jail_count":0}.items():
        if _bk not in st.session_state: st.session_state[_bk] = _bv

    bi     = st.session_state.br_idx
    rqs    = st.session_state.round_qs
    rrs    = st.session_state.round_results
    saved  = st.session_state.br_saved
    num_qs = min(len(rqs), len(rrs))
    rn    = st.session_state.round_num
    sc_v  = st.session_state.sc
    wr_v  = st.session_state.wrong

    # ═══════════════════════════════════
    # 모든 Q 순회 완료 → 최종 요약 화면
    # ═══════════════════════════════════
    if bi >= num_qs:
        _jail_total = st.session_state.br_jail_count
        _victory_col = "#ff8833" if was_victory else "#FF2D55"
        _victory_txt = "FIREPOWER COMPLETE" if was_victory else "MISSION FAILED"
        _victory_emoji = "💥" if was_victory else "💀"

        # 약점 분석: 오답 카테고리 집계
        _weak_cats = {}
        for _wi in range(num_qs):
            if not rrs[_wi]:
                _wcat = rqs[_wi].get("cat","")
                _weak_cats[_wcat] = _weak_cats.get(_wcat,0) + 1
        _weak_str = " · ".join([f"{c}({n})" for c,n in sorted(_weak_cats.items(), key=lambda x:-x[1])]) if _weak_cats else "없음!"

        _BR_ASSETS2 = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
        _br_tori_fin = os.path.join(_BR_ASSETS2, "tori_victory.png" if was_victory else "tori_warning.png")
        if os.path.exists(_br_tori_fin):
            _fc1, _fc2, _fc3 = st.columns([1, 2, 1])
            with _fc2:
                st.image(_br_tori_fin, width=140)

        import streamlit.components.v1 as _br_comp
        _br_comp.html(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');
        *{{margin:0;padding:0;box-sizing:border-box;}}body{{background:transparent;font-family:sans-serif;text-align:center;}}
        @keyframes popIn{{from{{transform:scale(0.5);opacity:0}}to{{transform:scale(1);opacity:1}}}}
        .card{{background:radial-gradient(ellipse at top,#150a25 0%,#06080f 70%);
            border:2.5px solid {_victory_col};border-radius:18px;padding:20px 16px;}}
        .title{{font-family:'Orbitron',monospace;font-size:12px;font-weight:900;
            color:{_victory_col};letter-spacing:3px;margin-bottom:10px;}}
        .score{{font-family:'Orbitron',monospace;font-size:36px;font-weight:900;
            color:#ffffff;text-shadow:0 0 20px {_victory_col};animation:popIn 0.5s ease;}}
        .sub{{font-size:14px;color:#8899aa;font-weight:700;margin-top:6px;}}
        .jail{{background:#0a1a08;border:1.5px solid #33aa44;border-radius:12px;padding:10px;margin-top:12px;}}
        .jail-num{{font-family:'Orbitron',monospace;font-size:24px;font-weight:900;color:#44ee66;}}
        .jail-label{{font-size:12px;color:#66aa77;font-weight:700;margin-top:2px;}}
        .weak{{font-size:13px;color:#ff8866;font-weight:700;margin-top:10px;}}
        </style>
        <div class="card">
          <div class="title">{_victory_emoji} WAVE {rn} · {_victory_txt}</div>
          <div class="score">✅ {sc_v} &nbsp; ❌ {wr_v}</div>
          <div class="sub">5문제 브리핑 완료</div>
          <div class="jail">
            <div class="jail-num">⛓ {_jail_total}</div>
            <div class="jail-label">포로 포획 · 수용소 이송</div>
          </div>
          <div class="weak">⚠️ 약점: {_weak_str}</div>
        </div>
        """, height=300)

        st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

        # CTA 버튼
        if was_victory:
            _bc1, _bc2 = st.columns(2)
            with _bc1:
                st.markdown('<div class="br-pow-btn">', unsafe_allow_html=True)
                if st.button("💀 포로사령부 돌입!", use_container_width=True):
                    st.switch_page("pages/03_POW_HQ.py")
                st.markdown('</div>', unsafe_allow_html=True)
            with _bc2:
                st.markdown('<div class="br-retry-btn">', unsafe_allow_html=True)
                if st.button("🔥 다음 WAVE!", use_container_width=True):
                    for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","round_timings","br_idx","br_saved","br_auto_jailed","br_jail_count"]:
                        if k in st.session_state: del st.session_state[k]
                    for k,v in D.items():
                        if k not in st.session_state: st.session_state[k]=v
                    st.session_state.round_num = rn + 1
                    qs = pick5(st.session_state.mode, st.session_state.get("sub_mode"))
                    st.session_state.round_qs = qs; st.session_state.cq = qs[0]
                    st.session_state.qst = time.time(); st.session_state.phase = "battle"; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="br-retry-btn">', unsafe_allow_html=True)
            if st.button("🔥 설욕전!", use_container_width=True):
                for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","round_timings","br_idx","br_saved","br_auto_jailed","br_jail_count"]:
                    if k in st.session_state: del st.session_state[k]
                for k,v in D.items():
                    if k not in st.session_state: st.session_state[k]=v
                qs = pick5(st.session_state.mode, st.session_state.get("sub_mode"))
                st.session_state.round_qs = qs; st.session_state.cq = qs[0]
                st.session_state.qst = time.time(); st.session_state.phase = "battle"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            _rc1, _rc2 = st.columns([3, 1])
            with _rc1:
                st.markdown('<div class="br-pow-btn">', unsafe_allow_html=True)
                if st.button("💀 포로사령부!", use_container_width=True):
                    st.switch_page("pages/03_POW_HQ.py")
                st.markdown('</div>', unsafe_allow_html=True)
            with _rc2:
                st.markdown('<div class="br-home-btn">', unsafe_allow_html=True)
                if st.button("🏠 홈", use_container_width=True):
                    st.session_state._p5_just_left = True
                    st.session_state.ans = False
                    st.session_state["_battle_entry_ans_reset"] = True
                    _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
                    if _nick: st.query_params["nick"]=_nick; st.query_params["ag"]="1"
                    st.switch_page("main_hub.py")
                st.markdown('</div>', unsafe_allow_html=True)

    # ═══════════════════════════════════
    # Q카드 순차 표시 (bi < num_qs)
    # ═══════════════════════════════════
    else:
        q  = rqs[bi]; ok = rrs[bi]
        ans_clean = q["ch"][q["a"]].split(") ",1)[-1] if ") " in q["ch"][q["a"]] else q["ch"][q["a"]]
        kr = q.get("kr",""); exk = q.get("exk",""); cat = q.get("cat","")

        # ── 오답 타이밍 3분류 기반 저장 로직 (논문B 청구항3 핵심) ──
        # slow_wrong: 완전히 모르는 것 → 강제 저장 (Schmidt 1990 + Cepeda 2006)
        # fast/mid_wrong: 알면서 틀렸을 가능성 → 학습자 자기조절에 맡김 (Lantolf 2014)
        _timings = st.session_state.get("round_timings", [])
        _this_timing = _timings[bi] if bi < len(_timings) else None  # None or fast/mid/slow_wrong

        if not ok and bi not in st.session_state.br_auto_jailed:
            st.session_state.br_auto_jailed.add(bi)
            if _this_timing == "slow_wrong":
                # ★ slow_wrong → 강제 저장 (이론적으로 정당)
                st.session_state.br_saved.add(bi)
                st.session_state.br_jail_count += 1
                item = {"id":q["id"],"text":q["text"],"ch":q["ch"],"a":q["a"],"ex":q.get("ex",""),
                        "exk":q.get("exk",""),"cat":q.get("cat",""),"kr":q.get("kr",""),"tp":q.get("tp","grammar")}
                save_to_storage([item])
                # ★ slow_wrong만 word_prison 추출 (완전히 모르는 단어)
                try:
                    import datetime as _fdt, sys as _sys2, os as _os2
                    _sys2.path.insert(0, _os2.path.dirname(__file__))
                    from _word_family_db import find_words_in_sentence as _find_words
                    _fp_sent = q.get("text","").replace("_______", ans_clean)
                    _fp_cat  = q.get("cat","")
                    _matched = _find_words(_fp_sent, max_words=3)
                    _fp_data = _storage.load()
                    if "word_prison" not in _fp_data: _fp_data["word_prison"] = []
                    _changed = False
                    for _m in _matched:
                        _w = _m["word"].strip()
                        if not _w or len(_w) < 3: continue
                        if any(p.get("word","").lower()==_w.lower() for p in _fp_data["word_prison"]): continue
                        _fp_data["word_prison"].append({
                            "word":_w,"kr":_m["kr"],"pos":_m["pos"],"family_root":_m["family_root"],
                            "source":"P5","sentence":_fp_sent,
                            "captured_date":_fdt.datetime.now().strftime("%Y-%m-%d"),
                            "correct_streak":0,"last_reviewed":None,"cat":_fp_cat,
                        })
                        _changed = True
                    if _changed:
                        _storage.save(_fp_data)
                except Exception:
                    pass

        _is_saved = bi in st.session_state.br_saved

        # ── 진행 도트 (● ○ ○ ○ ○) ──
        _dots_html = ""
        for _di in range(num_qs):
            if _di < bi:
                _dc = "#33cc55" if rrs[_di] else "#ff4444"
                _dots_html += f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:{_dc};margin:0 4px;"></span>'
            elif _di == bi:
                _dots_html += '<span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:#00ccff;margin:0 4px;box-shadow:0 0 8px #00ccff;"></span>'
            else:
                _dots_html += '<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#1a1a2a;border:1px solid #333;margin:0 4px;"></span>'

        # ── TORI 캐릭터 (Q카드 상단) ──
        _BR_ASSETS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
        _br_tori_path = os.path.join(_BR_ASSETS, "tori_normal.png")
        if os.path.exists(_br_tori_path):
            _tc1, _tc2 = st.columns([1, 5])
            with _tc1:
                st.image(_br_tori_path, width=55)
            with _tc2:
                _TB_BR = '<span style="background:#331100;border:1px solid #ff6600;border-radius:5px;padding:1px 8px;color:#ff8833;font-weight:900;font-size:11px;letter-spacing:2px;">TORI</span>'
                st.markdown(f'<div style="padding:6px 0 0 4px;"><div style="margin-bottom:3px;">{_TB_BR}</div><div style="font-size:12px;font-weight:900;color:#ffaa55;">Q{bi+1} 브리핑 — {"맞혔다!" if ok else "틀렸다... 포획!"}</div></div>', unsafe_allow_html=True)

        # ── 상단 HUD (진행 + 포획 카운터) ──
        _jail_cnt = st.session_state.br_jail_count
        st.markdown(f'''<div style="display:flex;justify-content:space-between;align-items:center;
            background:#06080f;border:1px solid #1e2235;border-radius:10px;padding:8px 14px;margin-bottom:5px;">
            <div style="display:flex;align-items:center;gap:2px;">{_dots_html}</div>
            <span style="font-family:Orbitron,monospace;font-size:14px;color:#44ee66;font-weight:900;letter-spacing:2px;">
                ⛓ {_jail_cnt}</span>
        </div>''', unsafe_allow_html=True)

        # ── 문제 카드 ──
        if ok:
            sent_html = q["text"].replace("_______", f'<span style="color:#50c878;font-weight:900;border-bottom:2px solid #50c878;">{ans_clean}</span>')
            card_border="#00d4ff"; qnum_color="#50c878"; qnum_sym="✅"
        else:
            sent_html = q["text"].replace("_______",
                f'<span style="color:#ff4466;font-weight:900;text-decoration:line-through;margin-right:4px;">?</span>'
                f'<span style="color:#50c878;font-weight:900;border-bottom:2px solid #50c878;">{ans_clean}</span>')
            card_border="#FF2D55"; qnum_color="#ff4466"; qnum_sym="❌"

        # 오답 자동 포획 뱃지 (slow_wrong 강제 저장 시만)
        _jail_badge = ""
        if not ok:
            _jail_badge = ('<span style="background:#1a0000;border:1px solid #ff4444;border-radius:6px;'
                'padding:2px 8px;font-size:0.65rem;color:#ff6644;font-weight:900;margin-left:8px;">'
                '⛓ 적 포획!</span>')

        st.markdown(f'''<div style="background:#080c1a;border:1.5px solid {card_border};
            border-left:4px solid {card_border};border-radius:14px;padding:12px;margin:3px 0;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
                <span style="background:#0a0a20;border:1px solid #222;border-radius:8px;
                  padding:3px 10px;font-size:0.82rem;font-weight:800;color:{qnum_color};">
                  {qnum_sym} Q{bi+1}/{num_qs}</span>
                <span style="font-size:0.65rem;color:#444;letter-spacing:2px;">{cat}{_jail_badge}</span>
            </div>
            <div style="font-size:1.05rem;font-weight:700;color:#eeeeff;line-height:1.7;margin-bottom:8px;">{sent_html}</div>
            <div style="font-size:0.85rem;color:#ccddee;margin-bottom:7px;padding-bottom:5px;border-bottom:1.5px solid #aa882244;text-decoration:underline;text-decoration-color:#aa882288;text-underline-offset:4px;text-decoration-thickness:1.5px;">📖 {kr}</div>
            <div style="background:#040d04;border-left:3px solid #50c878;border-radius:0 8px 8px 0;padding:7px 10px;">
                <div style="font-size:0.82rem;color:#50c878;font-weight:700;">💡 {exk}</div>
            </div>
        </div>''', unsafe_allow_html=True)

        # ── fast/mid_wrong 오답: 선택 저장 버튼 (자기조절 원리, Lantolf 2014) ──
        if not ok and not _is_saved and _this_timing in ("fast_wrong", "mid_wrong", None):
            _timing_label = {
                "fast_wrong": "⚡ 충동형 오답",
                "mid_wrong":  "🔶 표준형 오답",
                None:         "❓ 오답"
            }.get(_this_timing, "오답")
            st.markdown('<div class="br-jail-btn">', unsafe_allow_html=True)
            if st.button(f"📌 {_timing_label} — 포로로 잡을까?", key=f"jail_wrong_{q['id']}_{bi}", use_container_width=True):
                st.session_state.br_saved.add(bi)
                st.session_state.br_jail_count += 1
                item = {"id":q["id"],"text":q["text"],"ch":q["ch"],"a":q["a"],"ex":q.get("ex",""),
                        "exk":q.get("exk",""),"cat":q.get("cat",""),"kr":q.get("kr",""),"tp":q.get("tp","grammar")}
                save_to_storage([item])
                try:
                    import datetime as _fdt3, sys as _sys4, os as _os4
                    _sys4.path.insert(0, _os4.path.dirname(__file__))
                    from _word_family_db import find_words_in_sentence as _find_words3
                    _fp_sent3 = q.get("text","").replace("_______", ans_clean)
                    _matched3 = _find_words3(_fp_sent3, max_words=3)
                    _fp_data3 = _storage.load()
                    if "word_prison" not in _fp_data3: _fp_data3["word_prison"] = []
                    for _m3 in _matched3:
                        _w3 = _m3["word"].strip()
                        if not _w3 or len(_w3) < 3: continue
                        if any(p.get("word","").lower()==_w3.lower() for p in _fp_data3["word_prison"]): continue
                        _fp_data3["word_prison"].append({
                            "word":_w3,"kr":_m3["kr"],"pos":_m3["pos"],"family_root":_m3["family_root"],
                            "source":"P5","sentence":_fp_sent3,
                            "captured_date":_fdt3.datetime.now().strftime("%Y-%m-%d"),
                            "correct_streak":0,"last_reviewed":None,
                        })
                    _storage.save(_fp_data3)
                except Exception:
                    pass
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # ── 정답: "이것도 포획할까?" 선택 버튼 ──
        if ok and not _is_saved:
            st.markdown('<div class="br-jail-btn">', unsafe_allow_html=True)
            if st.button("📌 이것도 포획할까? → 수용소 이송!", key=f"jail_{q['id']}_{bi}", use_container_width=True):
                st.session_state.br_saved.add(bi)
                st.session_state.br_jail_count += 1
                item = {"id":q["id"],"text":q["text"],"ch":q["ch"],"a":q["a"],"ex":q.get("ex",""),
                        "exk":q.get("exk",""),"cat":q.get("cat",""),"kr":q.get("kr",""),"tp":q.get("tp","grammar")}
                save_to_storage([item])
                try:
                    import datetime as _fdt2, sys as _sys3, os as _os3
                    _sys3.path.insert(0, _os3.path.dirname(__file__))
                    from _word_family_db import find_words_in_sentence as _find_words2
                    _fp_sent2 = q.get("text","").replace("_______", ans_clean)
                    _matched2 = _find_words2(_fp_sent2, max_words=3)
                    _fp_data2 = _storage.load()
                    if "word_prison" not in _fp_data2: _fp_data2["word_prison"] = []
                    for _m2 in _matched2:
                        _w2 = _m2["word"].strip()
                        if not _w2 or len(_w2) < 3: continue
                        if any(p.get("word","").lower()==_w2.lower() for p in _fp_data2["word_prison"]): continue
                        _fp_data2["word_prison"].append({
                            "word":_w2,"kr":_m2["kr"],"pos":_m2["pos"],"family_root":_m2["family_root"],
                            "source":"P5","sentence":_fp_sent2,
                            "captured_date":_fdt2.datetime.now().strftime("%Y-%m-%d"),
                            "correct_streak":0,"last_reviewed":None,"cat":q.get("cat",""),
                        })
                    _storage.save(_fp_data2)
                except Exception:
                    pass
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        elif _is_saved:
            _save_msg = "⛓ 포획 완료!" if not ok else "✅ 포획 완료!"
            st.markdown(f'<div style="text-align:center;padding:8px 0;margin:6px 0;font-size:0.82rem;color:#336644;font-weight:700;letter-spacing:1px;">{_save_msg}</div>', unsafe_allow_html=True)

        # ── 다음 심문 / 브리핑 완료 버튼 ──
        _is_last = (bi + 1 >= num_qs)
        _next_label = "🏁 브리핑 완료!" if _is_last else f"다음 심문 → Q{bi+2}"
        st.markdown('<div class="br-next-btn">', unsafe_allow_html=True)
        if st.button(_next_label, key=f"br_next_{bi}", use_container_width=True):
            st.session_state.br_idx = bi + 1
            st.rerun()
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
    lbl_map  = {"g1":"⚔️ GRM · 문법 사격","g2":"🔄 FORM · 형태 변환","g3":"🔗 LINK · 연결 작전","vocab":"📘 VOCAB · 어휘 폭격"}
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

    # ── 토리 NPC 배너 (이미지 + 메시지) ──
    import random as _rnd_npc
    _ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    _npc_nick = st.session_state.get('student_nickname', '')
    _TB = '<span style="background:#331100;border:1px solid #ff6600;border-radius:5px;padding:1px 8px;color:#ff8833;font-weight:900;font-size:11px;letter-spacing:2px;">TORI</span>'
    _tori_msgs = [
        f"{_npc_nick}! 오늘도 불처럼!",
        f"{_npc_nick}! 약점 카테고리 집중 공략!",
        f"{_npc_nick}! BLITZ 도전할 때다!",
        f"{_npc_nick}! 전장에서 기다린다!",
    ]
    _tori_img = os.path.join(_ASSETS_DIR, "tori_normal.png")
    _tori_msg = _rnd_npc.choice(_tori_msgs) if _npc_nick else "전장에 온 걸 환영한다!"
    _tc_img, _tc_txt = st.columns([1, 3])
    with _tc_img:
        if os.path.exists(_tori_img):
            st.image(_tori_img, width=75)
    with _tc_txt:
        st.markdown(f'''<div style="background:rgba(10,5,20,0.96);border:1.5px solid #cc6633;
            border-radius:10px;padding:12px 14px;margin-top:6px;">
            <div style="margin-bottom:5px;">{_TB}</div>
            <div style="font-size:13px;font-weight:900;color:#ffcc88;">
            {_tori_msg}</div>
        </div>''', unsafe_allow_html=True)

    # ── COMBAT TIME 섹션 ──
    st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:9px;color:#cc6633;letter-spacing:4px;padding:4px 0 6px;font-weight:700;">⚡  COMBAT TIME</div>', unsafe_allow_html=True)
    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        if st.button("🔥 30s\nBLITZ", key="t30", use_container_width=True):
            st.session_state.tsec=30; st.session_state.tsec_chosen=True; st.rerun()
    with tc2:
        if st.button("⚡ 40s\nSTANDARD", key="t40", use_container_width=True):
            st.session_state.tsec=40; st.session_state.tsec_chosen=True; st.rerun()
    with tc3:
        if st.button("🛡️ 50s\nSNIPER", key="t50", use_container_width=True):
            st.session_state.tsec=50; st.session_state.tsec_chosen=True; st.rerun()

    # ── MISSION SELECT 섹션 ──
    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:9px;color:#cc3355;letter-spacing:4px;padding:4px 0 6px;font-weight:700;">🎯  MISSION SELECT</div>', unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        if st.button("⚔️\nGRM\n문법 사격", key="sg1", use_container_width=True):
            st.session_state.sel_mode="g1"; st.rerun()
    with b2:
        if st.button("🔄\nFORM\n형태 변환", key="sg2", use_container_width=True):
            st.session_state.sel_mode="g2"; st.rerun()
    with b3:
        if st.button("🔗\nLINK\n연결 작전", key="sg3", use_container_width=True):
            st.session_state.sel_mode="g3"; st.rerun()
    with b4:
        if st.button("📘\nVOCAB\n어휘 폭격", key="svc", use_container_width=True):
            st.session_state.sel_mode="vocab"; st.rerun()

    # ── ADAPTIVE DIFFICULTY 상태 표시 ──────────────────────────
    _adp_now   = st.session_state.get("adp_level", "normal")
    _adp_hist  = st.session_state.get("adp_history", [])
    _last_sc   = round(_adp_hist[-1] * 100) if _adp_hist else None

    _adp_color = {"easy": "#44cc66", "normal": "#FFD600", "hard": "#ff3344"}
    _adp_bar   = {"easy": "█░░", "normal": "██░", "hard": "███"}
    _adp_tag   = {"easy": "EASY", "normal": "NORMAL", "hard": "HARD"}
    _adp_arrow = {
        "easy":   ("🔼 맞히면 올라간다",  "#44cc66"),
        "normal": ("🔼 계속 맞히면 HARD", "#FFD600"),
        "hard":   ("🔥 최고 난이도 진입!", "#ff3344"),
    }
    _adp_taunt = {
        "easy":   "지금은 기초다. 여기서 무너지면 끝이야.",
        "normal": "딱 중간이야. 올라갈래, 내려갈래?",
        "hard":   "최정예만 오는 구역. 버텨봐.",
    }
    _col, _msg_col = _adp_color[_adp_now], _adp_arrow[_adp_now][1]
    _arrow_txt = _adp_arrow[_adp_now][0]
    _score_html = (
        f'<span style="font-size:1.1rem;font-weight:900;color:{_col};">'
        f'{_last_sc}%</span>'
    ) if _last_sc is not None else ""

    st.markdown(f"""
<div style="background:linear-gradient(135deg,#07091a,#0a0c1e);
  border:1px solid {_col}44;border-left:3px solid {_col};
  border-radius:10px;padding:7px 12px;margin:10px 0 2px;
  display:flex;align-items:center;justify-content:space-between;">
  <div>
    <div style="font-size:0.6rem;color:#444;letter-spacing:3px;font-weight:700;">
      ⚙ ADAPTIVE DIFFICULTY
    </div>
    <div style="margin-top:2px;">
      <span style="font-family:Orbitron,monospace;font-size:1.0rem;
        font-weight:900;color:{_col};">{_adp_bar[_adp_now]} {_adp_tag[_adp_now]}</span>
      &nbsp;&nbsp;
      <span style="font-size:0.72rem;color:{_msg_col};font-weight:700;">
        {_arrow_txt}
      </span>
    </div>
    <div style="font-size:0.7rem;color:#666;margin-top:2px;font-style:italic;">
      {_adp_taunt[_adp_now]}
    </div>
  </div>
  <div style="text-align:right;">{_score_html}</div>
</div>""", unsafe_allow_html=True)
    # ────────────────────────────────────────────────────────────

    # ── 생존 규칙 ──
    st.markdown(
        '<div style="text-align:center;margin:20px 0 4px;font-size:0.82rem;font-weight:900;'
        'color:#cc3333;letter-spacing:1px;'
        'animation:warnBlink 1.4s ease-in-out infinite;">'
        '💀 3개 이상 격파해야 생존 · 그 이하면 전멸!</div>',
        unsafe_allow_html=True
    )

    # ── 출격 버튼 ──
    if _ready:
        _cat = lbl_map.get(_cur_sm,"")
        _tl  = _tlabel_map.get(str(_cur_tsec), str(_cur_tsec)+"s")
        if st.button(f"🔥 출격! — {_cat}  ⏱ {_tl}", key="go_start", use_container_width=True):
            try:
                _md, _grp = mode_map[_cur_sm]
                _qs = pick5(_md, _grp)
                st.session_state.mode         = _md
                st.session_state.round_qs     = _qs
                st.session_state.cq           = _qs[0]
                st.session_state.qi           = 0
                st.session_state.sc           = 0
                st.session_state.wrong        = 0
                st.session_state.ta           = 0
                st.session_state.ans          = False
                st.session_state.sel          = None
                st.session_state.round_results= []
                st.session_state.qst          = time.time()
                st.session_state["_battle_entry_ans_reset"] = False
                st.session_state.phase        = "battle"
                st.rerun()
            except Exception as _e:
                st.error(f"오류: {_e}")
    else:
        st.button("⏱ COMBAT TIME + 🎯 MISSION → 출격!", key="go_disabled", use_container_width=True, disabled=True)

    # ── 네비 ──
    st.markdown('<div style="height:1px;background:#0e0e1e;margin:4px 0 3px;"></div>', unsafe_allow_html=True)
    nc1, nc2 = st.columns(2)
    with nc1:
        if st.button("💀 포로사령부", key="p5nav1", use_container_width=True):
            st.switch_page("pages/03_POW_HQ.py")
    with nc2:
        if st.button("🏠 홈", key="p5nav2", use_container_width=True):
            st.session_state._p5_just_left = True
            _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname","")
            if _nick:
                st.query_params["nick"] = _nick
                st.query_params["ag"]   = "1"
            st.switch_page("main_hub.py")

    # ── JS: 클래스 부여 (setTimeout 2회 + 출격 border-color flicker) ──
    _sel_t  = str(_cur_tsec) if _cur_tc else ""
    _sel_m  = _cur_sm
    _js_ready = "true" if _ready else "false"
    components.html(f"""<script>
(function(){{
  var selT="{_sel_t}", selM="{_sel_m}", isReady={_js_ready};
  var doc=window.parent.document;

  function applyClasses(){{
    doc.querySelectorAll("button").forEach(function(b){{
      var txt=(b.innerText||b.textContent||"").trim();
      if(!txt) return;

      // 시간 버튼 (영문 라벨)
      if(txt.indexOf("30s")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("fp-t30");
        if(selT==="30") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("fp-t30");if(selT==="30")p.classList.add("fp-sel");else p.classList.remove("fp-sel");}});
      }}
      if(txt.indexOf("40s")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("fp-t40");
        if(selT==="40") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("fp-t40");if(selT==="40")p.classList.add("fp-sel");else p.classList.remove("fp-sel");}});
      }}
      if(txt.indexOf("50s")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("fp-t50");
        if(selT==="50") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("fp-t50");if(selT==="50")p.classList.add("fp-sel");else p.classList.remove("fp-sel");}});
      }}

      // 작전 카드
      if(txt.indexOf("\ubb38\ubc95")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("fp-mode","fp-g1");
        if(selM==="g1") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("fp-g1");if(selM==="g1")p.classList.add("fp-sel");else p.classList.remove("fp-sel");}});
      }}
      if(txt.indexOf("\ud615\ud0dc")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("fp-mode","fp-g2");
        if(selM==="g2") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("fp-g2");if(selM==="g2")p.classList.add("fp-sel");else p.classList.remove("fp-sel");}});
      }}
      if(txt.indexOf("\uc5f0\uacb0")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("fp-mode","fp-g3");
        if(selM==="g3") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("fp-g3");if(selM==="g3")p.classList.add("fp-sel");else p.classList.remove("fp-sel");}});
      }}
      if(txt.indexOf("\uc5b4\ud718")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("fp-mode","fp-vc");
        if(selM==="vocab") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("fp-vc");if(selM==="vocab")p.classList.add("fp-sel");else p.classList.remove("fp-sel");}});
      }}

      // 출격 버튼
      if(txt.indexOf("\ucd9c\uaca9!")>-1 && txt.indexOf("COMBAT")===-1){{
        if(isReady){{ b.classList.add("fp-launch"); b.classList.remove("fp-launch-off"); }}
        else{{ b.classList.add("fp-launch-off"); b.classList.remove("fp-launch"); }}
      }}
      // 네비
      if(txt.indexOf("\ud3ec\ub85c\uc0ac\ub839\ubd80")>-1||txt.indexOf("\ud648")>-1){{
        b.classList.add("fp-nav");
      }}
    }});
  }}

  setTimeout(applyClasses, 120);
  setTimeout(applyClasses, 450);

  if(isReady){{
    var _fi=0;
    var _fc=["#ff4400","#ff6600","#ff9900","#FFD600","#ff9900","#ff6600","#ff4400","#ff2200"];
    setInterval(function(){{
      doc.querySelectorAll("button.fp-launch").forEach(function(b){{
        b.style.setProperty("border-color",_fc[_fi%_fc.length],"important");
      }});
      _fi++;
    }}, 130);
  }}
}})();
</script>""", height=0)
