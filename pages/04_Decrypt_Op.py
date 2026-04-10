"""
FILE: 04_Decrypt_Op.py  (구: 04_P7_Reading.py)
ROLE: 암호해독 작전 — 독해 지문 3문제 전투 전장
PHASES: LOBBY → BATTLE → BRIEFING → RESULT
DATA:   storage_data.json → saved_expressions, cross_logs(논문B), rt_logs(논문D)
LINKS:  main_hub.py (작전사령부 귀환) | 03_POW_HQ.py (포로사령부)
PAPERS: 논문B(cross_logs P7→P5 크로스스킬 전이 ★★★), 논문D(rt_logs 반응속도)
EXTEND: P7 어휘 → 포로수용소 자동 포획 고도화 예정
EXTEND: 지문 유형별 전략 브리핑 추가 예정
"""
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import random, time, json, os

# ★ 공유 반응형 CSS (iOS Safari 수정 + PC 글씨 확대)
import sys as _sys
_sys.path.insert(0, os.path.dirname(__file__))
from _responsive_css import inject_css as _inject_css
# inject_css()는 set_page_config() 이후에 호출해야 함 → 아래로 이동

# ═══ GOOGLE SHEETS 연동 ═══
def save_to_sheets(record):
    """연구 데이터를 Google Sheets에 저장"""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(creds)
        spreadsheet_id = st.secrets["SPREADSHEET_ID"]
        sh = gc.open_by_key(spreadsheet_id)
        ws = sh.sheet1
        # 헤더가 없으면 추가
        if ws.row_count == 0 or ws.cell(1,1).value is None:
            headers = ["session_id","timestamp","player_id","player_type","category",
                      "timer_sec","result","total_score",
                      "step1_qtype","step1_correct","step1_sec",
                      "step2_qtype","step2_correct","step2_sec",
                      "step3_qtype","step3_correct","step3_sec","step3_type_guess"]
            ws.append_row(headers)
        steps = record.get("steps", [])
        def sv(steps, i, key, default=""):
            return steps[i].get(key, default) if i < len(steps) else default
        row = [
            record.get("session_id",""),
            record.get("timestamp",""),
            record.get("player_id",""),
            record.get("player_type",""),
            record.get("category",""),
            record.get("timer_sec",""),
            record.get("result",""),
            record.get("total_score",""),
            sv(steps,0,"q_type"), sv(steps,0,"correct"), sv(steps,0,"response_sec"),
            sv(steps,1,"q_type"), sv(steps,1,"correct"), sv(steps,1,"response_sec"),
            sv(steps,2,"q_type"), sv(steps,2,"correct"), sv(steps,2,"response_sec"),
            sv(steps,2,"type_guess_correct",""),
        ]
        ws.append_row(row)
    except Exception as e:
        st.error(f"Sheets 오류: {e}")

st.set_page_config(page_title="암호해독 작전 📡", page_icon="📡", layout="wide", initial_sidebar_state="collapsed")
_inject_css()  # set_page_config 직후 호출 (StreamlitSetPageConfigMustBeFirst 방지)
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



# ═══ STORAGE ═══
STORAGE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage_data.json")
RESEARCH_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "p7_research_data.json")

def load_research_data():
    if os.path.exists(RESEARCH_FILE):
        with open(RESEARCH_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def save_research_record(record):
    """플레이 1회 기록을 누적 저장 (논문용) + Google Sheets"""
    try:
        data = load_research_data()
        data.append(record)
        with open(RESEARCH_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass
    save_to_sheets(record)

# ═══ _storage 공통 모듈 연동 ═══════════════════════════════════
# PURPOSE: cross_logs / recon_xyz_logs / unified storage 연동
# PAPER:   논문B(cross_logs), X·Y·Z 스캐폴딩 로그(신규 논문)
import _storage

def _save_cross_log(passage_id):
    """
    PURPOSE: P7 암호해독 완료 후 P5 화력전 어휘와 겹치는 단어 감지 → cross_logs 저장
    INPUT:   passage_id (암호해독 지문 ID)
    OUTPUT:  None
    PAPER:   논문B — P7 독해 어휘가 P5 문법전투에서도 출현하는 크로스스킬 전이 효과
    PATENT:  크로스모듈 어휘 전이 자동 감지 (신규 청구항 후보)
    """
    try:
        import re as _re
        data = _storage.load()
        # P5 오답 문제 어휘 수집
        saved_qs = data.get("saved_questions", [])
        p5_words = set()
        for q in saved_qs:
            words = _re.findall(r"[a-zA-Z]{4,}", q.get("text", "") + " " + q.get("ex", ""))
            p5_words.update(w.lower() for w in words)
        # 현재 P7 지문 어휘 추출
        p7_data = st.session_state.get("p7_data", {})
        p7_text = " ".join(
            " ".join(s.get("sentences", []))
            for s in p7_data.get("steps", [])
        )
        p7_words = set(w.lower() for w in _re.findall(r"[a-zA-Z]{4,}", p7_text))
        # 겹치는 어휘
        matched = list(p5_words & p7_words)
        matched_ids = [q.get("id", "") for q in saved_qs
                       if any(w in q.get("text", "").lower() for w in matched)]
        _storage.save_cross_log(
            p7_passage_id=passage_id,
            p5_matched_ids=matched_ids[:10],
            match_count=len(matched),
        )
    except Exception:
        pass

def _save_recon_xyz_log(passage_id, session_no):
    """
    PURPOSE: X·Y·Z 3단계 정답여부·소요시간 저장
    INPUT:   passage_id, session_no
    PAPER:   X·Y·Z 스캐폴딩 효과 논문 (전 세계 0건 연구공백)
    PATENT:  청구항 1B 실증 데이터
    """
    try:
        answers = st.session_state.get("p7_answers", [])
        analytics = st.session_state.get("p7_analytics", {})
        step_times = analytics.get("step_times", [])
        _storage.save_recon_xyz_log(
            passage_id=passage_id,
            step_results=answers[:3],
            step_times=step_times[:3],
            session_no=session_no,
        )
    except Exception:
        pass

def build_research_record(result):
    """현재 세션 데이터로 논문용 레코드 생성"""
    import uuid
    from datetime import datetime
    an = st.session_state.get("p7_analytics", {})
    steps_data = st.session_state.get("p7_data", {}).get("steps", [])
    answers = st.session_state.get("p7_answers", [])
    step_records = []
    for i, s in enumerate(steps_data):
        rec = {
            "step": i + 1,
            "q_type": s.get("q_type", "detail"),
            "correct": answers[i] if i < len(answers) else None,
            "response_sec": an.get("step_times", [])[i] if i < len(an.get("step_times", [])) else None,
        }
        type_corrects = an.get("step_type_correct", [])
        if i == 2:
            rec["type_guess_correct"] = type_corrects[0] if type_corrects else None
        step_records.append(rec)
    return {
        "session_id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "player_id": st.session_state.get("p7_player_id", "unknown"),
        "player_type": st.session_state.get("p7_player_type", "student"),
        "category": st.session_state.get("p7_cat", "unknown"),
        "timer_sec": st.session_state.get("p7_tsec", 80),
        "result": result,
        "total_score": len([a for a in answers if a]),
        "steps": step_records,
    }
def load_storage():
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE,"r",encoding="utf-8") as f:
                content = f.read().strip()
            if not content:
                return {"saved_questions":[],"saved_expressions":[]}
            d = json.loads(content)
            if isinstance(d, list): return {"saved_questions":d,"saved_expressions":[]}
            if "saved_questions" not in d: d["saved_questions"]=[]
            if "saved_expressions" not in d: d["saved_expressions"]=[]
            return d
        except (json.JSONDecodeError, ValueError, Exception):
            return {"saved_questions":[],"saved_expressions":[]}
    return {"saved_questions":[],"saved_expressions":[]}
def save_storage(data):
    try:
        with open(STORAGE_FILE,"w",encoding="utf-8") as f:
            json.dump(data,f,ensure_ascii=False,indent=2)
    except Exception: pass
def save_expressions(exprs, step_data=None):
    data=load_storage()
    if "saved_expressions" not in data: data["saved_expressions"]=[]
    new_sentence = step_data.get("sentences", [None])[0] if step_data else None
    for e in exprs:
        enriched = dict(e)
        if step_data:
            enriched["sentences"] = step_data.get("sentences", [])
            enriched["kr"] = step_data.get("kr", "")
        if new_sentence:
            exists = any((x.get("sentences") or [None])[0] == new_sentence for x in data["saved_expressions"])
        else:
            exists = any(x.get("expr") == e.get("expr") for x in data["saved_expressions"])
        if not exists:
            data["saved_expressions"].append(enriched)
    save_storage(data)
    import streamlit as _st
    _st.session_state["saved_expressions"] = data["saved_expressions"]

# ═══ CSS (공통) ═══
st.markdown("""<style>
.stApp{background:#0d0d1a!important;}
section[data-testid="stSidebar"]{background:#0a0a1a!important;}
.block-container{padding-top:0.2rem!important;padding-bottom:1rem!important;max-width:100%!important;padding-left:1rem!important;padding-right:1rem!important;}
header[data-testid="stHeader"]{background:transparent!important;}
div[data-testid="stDecoration"]{display:none!important;}
div[data-testid="stToolbar"]{display:none!important;}
@keyframes rb{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
@keyframes hlDraw{from{background-size:0% 4px}to{background-size:100% 4px}}

/* 전투 버튼 */
button[kind="primary"]{background:#111111!important;color:#ffffff!important;border:2px solid #ff4400!important;border-radius:10px!important;font-size:1.2rem!important;font-weight:900!important;padding:0.84rem 1rem!important;box-shadow:0 0 10px rgba(255,68,0,0.3)!important;text-align:center!important;}
button[kind="primary"] p{font-size:1.2rem!important;font-weight:900!important;text-align:center!important;}
button[kind="secondary"]{background:#111111!important;color:#ffffff!important;border:2px solid #ffffff!important;border-radius:10px!important;font-size:1.2rem!important;font-weight:900!important;padding:0.48rem 0.5rem!important;box-shadow:0 0 10px rgba(255,255,255,0.3)!important;text-align:center!important;min-height:43px!important;}
button[kind="secondary"] p{font-size:1.2rem!important;font-weight:900!important;text-align:center!important;color:#ffffff!important;}

/* 지문 카드 */
.p7-pass{background:linear-gradient(145deg,#001a22,#002233);border:2px solid rgba(0,180,220,0.7);border-radius:18px;padding:1.5rem;margin:0.5rem 0;box-shadow:0 0 20px rgba(0,180,220,0.15);}
.p7-sent{color:#e8e0cc;font-size:0.82rem;font-weight:400;line-height:1.55;}
.p7-new{color:#9aa5b4;font-weight:400;font-size:0.82rem;}
.p7-qbox{background:linear-gradient(145deg,#001822,#002a38);border:2px solid rgba(0,200,238,0.8);border-radius:18px;padding:1.5rem;margin:0.5rem 0;box-shadow:0 0 15px rgba(0,200,238,0.2);}
.p7-q{color:#ffffff;font-size:clamp(0.85rem,3vw,1rem);font-weight:800;line-height:1.8;}

/* 진행 표시 */
.p7-step{text-align:center;font-size:1.2rem;font-weight:900;color:#44ffcc;margin:0.3rem 0;}
#MainMenu{visibility:hidden!important;}olbar"]{visibility:hidden!important;}.block-container{padding-top:0!important;}.p7-hud{background:#000000;border:2px solid rgba(0,200,238,0.7);border-radius:14px;padding:0.8rem 1.2rem;margin:0.3rem 0;display:flex;justify-content:space-between;align-items:center;}
.p7-hud-l{font-size:1.3rem;font-weight:900;color:#44ffcc;}
.p7-hud-r{font-size:1.1rem;font-weight:800;color:#ffcc00;}

/* 브리핑 */
.stButton[data-testid] button[kind="secondary"]{min-height:32px!important;padding:2px 4px!important;font-size:0.9rem!important;}
.p7-br-s{font-size:2rem;font-weight:700;color:#1a1a1a;line-height:2;margin-bottom:0.8rem;}
.p7-br-hl{color:#00aa88;font-weight:900;font-size:2.1rem;text-decoration:underline;text-underline-offset:5px;text-decoration-thickness:3px;}
.p7-br-kr{font-size:1.5rem;font-weight:600;color:#333;line-height:1.7;margin-bottom:0.5rem;}
.p7-br-ex{font-size:1.4rem;color:#444;line-height:1.6;padding:0.5rem 0.7rem;background:rgba(0,180,150,0.1);border-left:4px solid #00ccee;border-radius:0 10px 10px 0;}

/* VICTORY/LOST 배너 */
.p7-ban{text-align:center;padding:3px 6px!important;border-radius:10px;margin:1px 0;font-size:0.85rem!important;font-weight:900;}
.p7-ban-v{background:#000000;color:#fff;border:2px solid rgba(0,200,238,0.7);}
.p7-ban-l{background:linear-gradient(135deg,#550000,#aa0000);color:#fff;border:2px solid rgba(255,255,255,0.55);}
@media(max-width:768px){
.block-container{padding-left:0.6rem!important;padding-right:0.6rem!important;}
button[kind="primary"],button[kind="secondary"]{font-size:1rem!important;padding:0.6rem 0.7rem!important;}
button[kind="primary"] p,button[kind="secondary"] p{font-size:1rem!important;}
.p7-sent{font-size:1rem!important;}.p7-new{font-size:1.05rem!important;}
.p7-q{font-size:1rem!important;}.p7-pass,.p7-qbox{padding:0.8rem!important;}
.p7-br-s{font-size:1.05rem!important;}.p7-br-hl{font-size:1.1rem!important;}
.p7-br-kr{font-size:0.9rem!important;}.p7-br-ex{font-size:0.85rem!important;}
.p7-hud-l{font-size:0.9rem!important;}.p7-hud-r{font-size:0.85rem!important;}
}
@media(max-width:480px){
.block-container{padding-left:0.3rem!important;padding-right:0.3rem!important;padding-top:0.5rem!important;}
button[kind="primary"],button[kind="secondary"]{font-size:0.75rem!important;padding:0.1rem 0.1rem!important;border-radius:8px!important;min-height:28px!important;}
button[kind="primary"] p,button[kind="secondary"] p{font-size:0.95rem!important;}
.p7-sent{font-size:0.95rem!important;line-height:1.5!important;}.p7-new{font-size:1rem!important;}
.p7-q{font-size:0.95rem!important;line-height:1.5!important;}
.p7-pass,.p7-qbox{padding:0.7rem 0.6rem!important;border-radius:12px!important;margin:0.3rem 0!important;}
.p7-br-s{font-size:1rem!important;line-height:1.6!important;}.p7-br-hl{font-size:1.05rem!important;}
.p7-br-kr{font-size:0.85rem!important;}.p7-br-ex{font-size:0.8rem!important;}
.p7-hud{padding:0.5rem 0.8rem!important;margin-bottom:0.3rem!important;}.p7-hud-l{font-size:0.85rem!important;}.p7-hud-r{font-size:0.8rem!important;}
.p7-step{font-size:0.85rem!important;}.p7-ban{font-size:0.85rem!important;}
.element-container:has(button[kind="secondary"]){margin:0!important;padding:0!important;}
button[kind="secondary"]{min-height:28px!important;padding:2px 4px!important;font-size:0.85rem!important;line-height:1!important;}
button[kind="secondary"] p{font-size:0.85rem!important;line-height:1!important;}
}
@media(max-width:360px){
button[kind="primary"],button[kind="secondary"]{font-size:1rem!important;}
button[kind="primary"] p,button[kind="secondary"] p{font-size:1rem!important;}
.p7-sent{font-size:1.05rem!important;}.p7-q{font-size:1rem!important;}
.p7-br-s{font-size:1.1rem!important;}
}
.stButton button{min-height:43px!important;padding:4px 6px!important;touch-action:manipulation!important;-webkit-tap-highlight-color:transparent!important;user-select:none!important;-webkit-user-select:none!important;}
.stButton button p{font-size:1.0rem!important;}

/* 브리핑 버튼 강제 가로배치 */
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

# ═══ 문제 데이터: 4개 카테고리 × 1세트 ═══
# 문제 유형 키: "purpose"=주제/목적, "detail"=세부사항, "inference"=추론, "not"=NOT문제, "synonym"=동의어
import json as _json, os as _os, random as _rnd

def _load_passages():
    _base = _os.path.join(_os.path.dirname(_os.path.dirname(__file__)), "data")
    _map = {
        "recon":       "passages_recon.json",       # 1단계 RECON — 이메일·편지·메모 (X·Y·Z)
        "article":     "passages_signal.json",       # 2단계 SIGNAL — 광고·공지
        "notice":      "passages_intercept.json",    # 3단계 CIPHER — 기사·안내
        "information": "passages_blackout.json",     # 4단계 BLACKOUT — 고난도
    }
    _result = {}
    for _cat, _fname in _map.items():
        _path = _os.path.join(_base, _fname)
        try:
            with open(_path, "r", encoding="utf-8") as _f:
                _result[_cat] = _json.load(_f)
        except Exception as _e:
            _result[_cat] = []
    return _result

PASSAGES = _load_passages()
def pick_passage(cat):
    pool = PASSAGES.get(cat, [])
    return _rnd.choice(pool) if pool else {}

# ═══ 세션 초기화 ═══
D = {"p7_phase":"lobby","p7_cat":None,"p7_tsec":80,"p7_tsec_chosen":False,"p7_step":0,
     "p7_started_at":None,"p7_answers":[],"p7_data":None,"p7_br_idx":0,
     "p7_type_guessed":False,"p7_type_correct":None,
     "p7_player_id":"","p7_player_type":"student","p7_player_set":False,
     "p7_analytics":{"step_times":[],"step_correct":[],"step_type_correct":[],"step_started_at":None}}
for k,v in D.items():
    if k not in st.session_state: st.session_state[k]=v

# 메인허브에서 재진입 시 완전 리셋
if st.session_state.get("_p7_just_left", False):
    st.session_state._p7_just_left = False
    for k,v in D.items(): st.session_state[k] = v

# ═══════════════════════════════════════
# ════════════════════════════════════════
# PHASE: LOBBY
# 기능: 지문 선택, 작전 선택, 난이도 표시
# ════════════════════════════════════════
# ═══════════════════════════════════════
if st.session_state.p7_phase == "lobby":
    tsec = st.session_state.p7_tsec
    cat  = st.session_state.p7_cat
    _p7_tsec = st.session_state.get("p7_tsec", 80)
    _p7_tc   = st.session_state.get("p7_tsec_chosen", False)
    _p7_cat  = st.session_state.get("p7_cat", None)
    _ready   = _p7_tc and cat and cat in PASSAGES
    _sel_time = str(_p7_tsec) if _p7_tc else ""
    _sel_cat  = _p7_cat or ""

    # ── CSS ──
    st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
#MainMenu{visibility:hidden!important;}
header[data-testid="stHeader"]{height:0!important;visibility:hidden!important;}
div[data-testid="stToolbar"]{visibility:hidden!important;}
.block-container{padding-top:0.3rem!important;padding-bottom:1rem!important;}
.stMarkdown{margin:0!important;padding:0!important;}
.element-container{margin:0!important;padding:0!important;}
div[data-testid="stVerticalBlock"]{gap:8px!important;}
div[data-testid="stHorizontalBlock"]{gap:5px!important;margin:0!important;}
div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]{padding:0!important;min-width:0!important;flex:1!important;}

/* ── 공통 버튼 ── */
div[data-testid="stButton"] button{
  background:#0a0d1c!important;border:1px solid #1a2248!important;
  border-radius:9px!important;color:#4a6688!important;
  font-size:0.85rem!important;font-weight:700!important;
  padding:6px 4px!important;min-height:46px!important;width:100%!important;
  white-space:pre-line!important;line-height:1.3!important;
  transition:border-color .12s,box-shadow .12s!important;
}
div[data-testid="stButton"] button p{
  font-size:0.85rem!important;font-weight:700!important;
  color:#4a6688!important;white-space:pre-line!important;line-height:1.3!important;
}

/* ── 시간: 60s ── */
div[data-testid="stButton"] button.p7t60{
  background:#0a0d1c!important;border-color:rgba(204,68,0,0.22)!important;color:#886644!important;
  min-height:58px!important;font-family:'Orbitron',monospace!important;font-size:0.78rem!important;
}
div[data-testid="stButton"] button.p7t60 p{color:#886644!important;}
div[data-testid="stButton"] button.p7t60.p7sel{
  background:#1c0800!important;border-color:#cc4400!important;color:#ff7733!important;
  box-shadow:0 0 18px rgba(204,68,0,0.45)!important;
}
div[data-testid="stButton"] button.p7t60.p7sel p{color:#ff7733!important;}

/* ── 시간: 80s ── */
div[data-testid="stButton"] button.p7t80{
  background:#0a0d1c!important;border-color:rgba(0,85,187,0.22)!important;color:#446688!important;
  min-height:58px!important;font-family:'Orbitron',monospace!important;font-size:0.78rem!important;
}
div[data-testid="stButton"] button.p7t80 p{color:#446688!important;}
div[data-testid="stButton"] button.p7t80.p7sel{
  background:#00081c!important;border-color:#0055bb!important;color:#44aaff!important;
  box-shadow:0 0 18px rgba(0,85,187,0.45)!important;
}
div[data-testid="stButton"] button.p7t80.p7sel p{color:#44aaff!important;}

/* ── 시간: 100s ── */
div[data-testid="stButton"] button.p7t100{
  background:#0a0d1c!important;border-color:rgba(102,34,204,0.22)!important;color:#775599!important;
  min-height:58px!important;font-family:'Orbitron',monospace!important;font-size:0.78rem!important;
}
div[data-testid="stButton"] button.p7t100 p{color:#775599!important;}
div[data-testid="stButton"] button.p7t100.p7sel{
  background:#0e0018!important;border-color:#6622cc!important;color:#aa55ff!important;
  box-shadow:0 0 18px rgba(102,34,204,0.45)!important;
}
div[data-testid="stButton"] button.p7t100.p7sel p{color:#aa55ff!important;}

/* ── 지문 카드 공통 ── */
div[data-testid="stButton"] button.p7pass{
  min-height:92px!important;text-align:center!important;padding:10px 4px!important;
}

/* RECON LV.1 초록 */
div[data-testid="stButton"] button.p7rec{
  background:#060e0a!important;border-color:#1a6633!important;color:#33aa66!important;
}
div[data-testid="stButton"] button.p7rec p{color:#33aa66!important;}
div[data-testid="stButton"] button.p7rec.p7sel{
  background:#081a10!important;border-color:#00cc66!important;border-width:2px!important;
  color:#00ccee!important;box-shadow:0 0 20px rgba(0,200,238,0.5)!important;
}
div[data-testid="stButton"] button.p7rec.p7sel p{color:#00ccee!important;}

/* SIGNAL LV.2 노랑 */
div[data-testid="stButton"] button.p7art{
  background:#0e0e06!important;border-color:#666600!important;color:#aaaa33!important;
}
div[data-testid="stButton"] button.p7art p{color:#aaaa33!important;}
div[data-testid="stButton"] button.p7art.p7sel{
  background:#1a1800!important;border-color:#cccc00!important;border-width:2px!important;
  color:#ffff44!important;box-shadow:0 0 20px rgba(204,204,0,0.5)!important;
}
div[data-testid="stButton"] button.p7art.p7sel p{color:#ffff44!important;}

/* CIPHER LV.3 주황 */
div[data-testid="stButton"] button.p7not{
  background:#0e0700!important;border-color:#663300!important;color:#aa6622!important;
}
div[data-testid="stButton"] button.p7not p{color:#aa6622!important;}
div[data-testid="stButton"] button.p7not.p7sel{
  background:#1e0e00!important;border-color:#ff8800!important;border-width:2px!important;
  color:#ffaa33!important;box-shadow:0 0 20px rgba(255,136,0,0.5)!important;
}
div[data-testid="stButton"] button.p7not.p7sel p{color:#ffaa33!important;}

/* BLACKOUT LV.4 빨강 */
div[data-testid="stButton"] button.p7inf{
  background:#120008!important;border-color:#660022!important;color:#aa2244!important;
}
div[data-testid="stButton"] button.p7inf p{color:#aa2244!important;}
div[data-testid="stButton"] button.p7inf.p7sel{
  background:#200010!important;border-color:#cc0033!important;border-width:2px!important;
  color:#ff4466!important;box-shadow:0 0 20px rgba(204,0,51,0.5)!important;
}
div[data-testid="stButton"] button.p7inf.p7sel p{color:#ff4466!important;}

/* ── 출격 버튼 ── */
div[data-testid="stButton"] button.p7launch{
  background:#1a0600!important;border:2px solid #cc4400!important;border-radius:12px!important;
  color:#ffaa44!important;font-size:0.88rem!important;font-weight:900!important;
  min-height:54px!important;letter-spacing:2px!important;
  font-family:'Orbitron',monospace!important;
}
div[data-testid="stButton"] button.p7launch p{
  color:#ffaa44!important;font-size:0.88rem!important;
  font-weight:900!important;letter-spacing:2px!important;
}

/* ── 네비 버튼 ── */
div[data-testid="stButton"] button.p7nav{
  background:#05050e!important;border:1px solid #151525!important;
  border-radius:10px!important;color:#3d5066!important;
  min-height:40px!important;font-size:0.82rem!important;
}
div[data-testid="stButton"] button.p7nav p{color:#3d5066!important;}
div[data-testid="stButton"] button.p7nav:hover{
  border-color:rgba(80,120,180,0.4)!important;color:#7799aa!important;
}

@media(max-width:480px){
  div[data-testid="stButton"] button.p7pass{min-height:76px!important;}
  div[data-testid="stButton"] button.p7t60,
  div[data-testid="stButton"] button.p7t80,
  div[data-testid="stButton"] button.p7t100{min-height:50px!important;}
}
</style>""", unsafe_allow_html=True)

    # ── 타이틀 ──
    st.markdown('''<div style="text-align:center;padding:6px 0 4px;">
      <div style="font-size:9px;color:#6699bb;letter-spacing:4px;margin-bottom:3px;font-weight:900;">DECRYPT OPERATION</div>
      <div style="font-size:1.32rem;font-weight:900;color:#aaccff;letter-spacing:3px;">📡 암호해독 작전</div>
      <div style="font-size:0.72rem;color:#8899aa;letter-spacing:1.5px;margin-top:3px;font-weight:700;">CLASSIFIED · PRIORITY LEVEL 7</div>
    </div>''', unsafe_allow_html=True)

    import streamlit.components.v1 as _nc
    # ── 해 NPC 배너 (이미지 + 메시지) ──
    import random as _rnd_npc2
    _ASSETS_DIR2 = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    _npc_nick = st.session_state.get('student_nickname', '')
    _HB = '<span style="background:#001520;border:1px solid #00ccee;border-radius:5px;padding:1px 8px;color:#00ddff;font-weight:900;font-size:11px;letter-spacing:2px;">HAE</span>'
    _hae_msgs = [
        f"{_npc_nick}, 답은 지문 안에 있다.",
        f"{_npc_nick}, 시간 줄일 준비 됐나?",
        f"{_npc_nick}, 유형별 현황 분석 완료.",
        f"{_npc_nick}, 신호에 집중하라.",
    ]
    _hae_img = os.path.join(_ASSETS_DIR2, "hae_normal.png")
    _hae_msg = _rnd_npc2.choice(_hae_msgs) if _npc_nick else "정독이 답이다. 집중."
    _hc_img, _hc_txt = st.columns([1, 3])
    with _hc_img:
        if os.path.exists(_hae_img):
            st.image(_hae_img, width=75)
    with _hc_txt:
        st.markdown(f'''<div style="background:rgba(5,10,20,0.96);border:1.5px solid #0099cc;
            border-radius:10px;padding:12px 14px;margin-top:6px;">
            <div style="margin-bottom:5px;">{_HB}</div>
            <div style="font-size:13px;font-weight:900;color:#00ccee;">
            {_hae_msg}</div>
        </div>''', unsafe_allow_html=True)

    # ── 시간 선택 (A안: SIGNAL FREQUENCY 세그먼트) ──
    st.markdown('''<div style="font-size:10px;color:#88aacc;letter-spacing:4px;padding:14px 0 7px;font-weight:900;">
      ⏱  SIGNAL FREQUENCY</div>''', unsafe_allow_html=True)
    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        if st.button("🔥 60s\nRAPID", key="p7t60", use_container_width=True):
            st.session_state.p7_tsec=60; st.session_state.p7_tsec_chosen=True; st.rerun()
    with tc2:
        if st.button("⚡ 80s\nSTANDARD", key="p7t80", use_container_width=True):
            st.session_state.p7_tsec=80; st.session_state.p7_tsec_chosen=True; st.rerun()
    with tc3:
        if st.button("💎 100s\nPRECISION", key="p7t100", use_container_width=True):
            st.session_state.p7_tsec=100; st.session_state.p7_tsec_chosen=True; st.rerun()

    # ── 지문 선택 (RECON/SIGNAL/CIPHER/BLACKOUT 4개 한 줄) ──
    st.markdown('''<div style="font-size:10px;color:#dd88aa;letter-spacing:4px;padding:14px 0 7px;font-weight:900;">
      ⚔  TARGET CLASSIFICATION</div>''', unsafe_allow_html=True)
    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1:
        if st.button("🎯\nRECON\n편지·이메일\n▂░░░", key="p7c1", use_container_width=True):
            st.session_state.p7_cat="recon"; st.rerun()
    with pc2:
        if st.button("📢\nSIGNAL\n광고·공지\n▂▄░░", key="p7c2", use_container_width=True):
            st.session_state.p7_cat="article"; st.rerun()
    with pc3:
        if st.button("📰\nCIPHER\n기사·안내\n▂▄▆░", key="p7c3", use_container_width=True):
            st.session_state.p7_cat="notice"; st.rerun()
    with pc4:
        if st.button("☠️\nBLACKOUT\n고난도\n▂▄▆█", key="p7c4", use_container_width=True):
            st.session_state.p7_cat="information"; st.rerun()

    # ── 생존 규칙 ──
    st.markdown('<div style="text-align:center;padding:16px 0 3px;font-size:0.82rem;font-weight:900;color:#00ffcc;letter-spacing:1px;text-shadow:0 0 10px #00ffcc88;">☠ 오판 1회 = 작전 종료 · 통신 두절 = 즉시 철수</div>', unsafe_allow_html=True)

    # ── 출격 버튼 ──
    if _ready:
        _cat_name = {"recon":"🎯 RECON","article":"📢 SIGNAL","notice":"📰 CIPHER","information":"☠️ BLACKOUT"}.get(cat, cat)
        _tlabel = {"60":"🔥 60s RAPID","80":"⚡ 80s STANDARD","100":"💎 100s PRECISION"}.get(str(_p7_tsec), str(_p7_tsec)+"초")
        if st.button(f"▶ 출격! — {_cat_name}  ⏱ {_tlabel}", key="p7go", use_container_width=True):
            st.session_state.p7_data = pick_passage(cat)
            st.session_state.p7_step = 0
            st.session_state.p7_answers = []
            st.session_state.p7_started_at = time.time()
            st.session_state.p7_type_guessed = False
            st.session_state.p7_type_correct = None
            st.session_state.p7_analytics = {"step_times":[],"step_correct":[],"step_type_correct":[],"step_started_at":time.time()}
            st.session_state.p7_phase = "battle"
            st.rerun()
    else:
        st.markdown('<div style="background:#0a0a18;border:1.5px solid #334466;border-radius:12px;color:#6688aa;font-size:0.88rem;font-weight:800;padding:14px;text-align:center;letter-spacing:1px;">⏱ 시간 + 🎯 지문 선택 → 출격!</div>', unsafe_allow_html=True)

    # ── 네비 ──
    st.markdown('<div style="height:1px;background:#0e0e1e;margin:4px 0 3px;"></div>', unsafe_allow_html=True)
    nc1, nc2 = st.columns(2)
    with nc1:
        if st.button("💀  사령부 귀환", key="p7nav1", use_container_width=True):
            st.switch_page("pages/03_POW_HQ.py")
    with nc2:
        if st.button("🏠 홈", key="p7nav2", use_container_width=True):
            st.session_state._p7_just_left = True
            _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
            if _nick:
                st.query_params["nick"] = _nick
                st.query_params["ag"] = "1"
            st.switch_page("main_hub.py")

    # ── JS: 클래스 부여 (setTimeout 2회, setInterval 없음) ──
    import streamlit.components.v1 as _cmp
    _cmp.html(f"""<script>
(function(){{
  var selT="{_sel_time}", selC="{_sel_cat}";
  var doc=window.parent.document;

  function applyClasses(){{
    doc.querySelectorAll("button").forEach(function(b){{
      var txt=(b.innerText||b.textContent||"").trim();
      if(!txt) return;

      // 시간 버튼
      if(txt.indexOf("60s")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("p7t60");
        if(selT==="60") b.classList.add("p7sel"); else b.classList.remove("p7sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("p7t60");if(selT==="60")p.classList.add("p7sel");else p.classList.remove("p7sel");}});
      }}
      if(txt.indexOf("80s")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("p7t80");
        if(selT==="80") b.classList.add("p7sel"); else b.classList.remove("p7sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("p7t80");if(selT==="80")p.classList.add("p7sel");else p.classList.remove("p7sel");}});
      }}
      if(txt.indexOf("100s")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("p7t100");
        if(selT==="100") b.classList.add("p7sel"); else b.classList.remove("p7sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("p7t100");if(selT==="100")p.classList.add("p7sel");else p.classList.remove("p7sel");}});
      }}

      // 지문 카드
      if(txt.indexOf("RECON")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("p7pass","p7rec");
        if(selC==="recon") b.classList.add("p7sel"); else b.classList.remove("p7sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("p7rec");if(selC==="recon")p.classList.add("p7sel");else p.classList.remove("p7sel");}});
      }}
      if(txt.indexOf("SIGNAL")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("p7pass","p7art");
        if(selC==="article") b.classList.add("p7sel"); else b.classList.remove("p7sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("p7art");if(selC==="article")p.classList.add("p7sel");else p.classList.remove("p7sel");}});
      }}
      if(txt.indexOf("CIPHER")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("p7pass","p7not");
        if(selC==="notice") b.classList.add("p7sel"); else b.classList.remove("p7sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("p7not");if(selC==="notice")p.classList.add("p7sel");else p.classList.remove("p7sel");}});
      }}
      if(txt.indexOf("BLACKOUT")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("p7pass","p7inf");
        if(selC==="information") b.classList.add("p7sel"); else b.classList.remove("p7sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("p7inf");if(selC==="information")p.classList.add("p7sel");else p.classList.remove("p7sel");}});
      }}

      // 출격 버튼
      if(txt.indexOf("\ucd9c\uaca9!")>-1) b.classList.add("p7launch");

      // 네비
      if(txt.indexOf("\ud3ec\ub85c\uc0ac\ub839\ubd80")>-1||txt.indexOf("\ud648")>-1) b.classList.add("p7nav");
    }});
  }}

  setTimeout(applyClasses, 120);
  setTimeout(applyClasses, 450);
}})();
</script>""", height=0)

# ═══════════════════════════════════════
# ════════════════════════════════════════
# PHASE: BATTLE
# 기능: 독해 지문 3문제 전투 (60초 타이머, 1오답 즉사, 시간초과 즉사)
# 관련함수: run_reading_battle(), save_cross_log(), save_rt_log()
# ════════════════════════════════════════
# ═══════════════════════════════════════
elif st.session_state.p7_phase == "battle":
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
    #MainMenu{visibility:hidden!important;}
    header[data-testid="stHeader"]{height:0!important;overflow:hidden!important;}
    .block-container{padding:6px 10px 16px!important;margin:0!important;}
    div[data-testid="stVerticalBlock"]{gap:4px!important;}
    .element-container{margin:0!important;padding:0!important;}
    div[data-testid="stHorizontalBlock"]{gap:6px!important;margin:0!important;flex-wrap:nowrap!important;}
    div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]{padding:0!important;min-width:0!important;flex:1!important;}

    /* 답 버튼 */
    div[data-testid="stButton"] button{
      background:#07090f!important;border:1.5px solid rgba(100,140,200,0.3)!important;
      border-radius:10px!important;color:#8899bb!important;
      font-size:0.88rem!important;font-weight:700!important;
      padding:0.5rem 0.8rem!important;min-height:46px!important;
      text-align:left!important;width:100%!important;
      transition:border-color .12s,box-shadow .12s!important;
    }
    div[data-testid="stButton"] button p{color:#8899bb!important;font-size:0.88rem!important;font-weight:700!important;}
    div[data-testid="stButton"] button:hover{border-color:rgba(100,180,255,0.7)!important;color:#aaccff!important;}

    /* A/B/C/D 색상 */
    #btn-p7a div[data-testid="stButton"] button{border-left:4px solid #ff6633!important;background:#160800!important;color:#ff8855!important;}
    #btn-p7a div[data-testid="stButton"] button p{color:#ff8855!important;}
    #btn-p7b div[data-testid="stButton"] button{border-left:4px solid #00E5FF!important;background:#001518!important;color:#00ccee!important;}
    #btn-p7b div[data-testid="stButton"] button p{color:#00ccee!important;}
    #btn-p7c div[data-testid="stButton"] button{border-left:4px solid #FF2D55!important;background:#140008!important;color:#ee4466!important;}
    #btn-p7c div[data-testid="stButton"] button p{color:#ee4466!important;}
    #btn-p7d div[data-testid="stButton"] button{border-left:4px solid #00ccee!important;background:#001520!important;color:#00ccee!important;}
    #btn-p7d div[data-testid="stButton"] button p{color:#00ccee!important;}
    </style>""", unsafe_allow_html=True)

    data = st.session_state.p7_data
    step = st.session_state.p7_step
    steps = data["steps"]
    cur = steps[step]

    st_autorefresh(interval=1000, limit=st.session_state.p7_tsec+10, key="p7_timer")

    elapsed = time.time() - st.session_state.p7_started_at
    total   = st.session_state.p7_tsec
    rem     = max(0, total - int(elapsed))

    if rem <= 0:
        try: save_research_record(build_research_record("timeout"))
        except: pass
        st.session_state.p7_phase = "lost"; st.rerun()

    pct = rem / total if total > 0 else 0
    if pct > 0.6:   stage, bar_col = "safe",     "#00ccee"
    elif pct > 0.3: stage, bar_col = "warn",     "#ffcc00"
    elif pct > 0.1: stage, bar_col = "danger",   "#ff4444"
    else:           stage, bar_col = "critical",  "#ff0000"

    if rem <= 10:
        pass_border = "#ff2200"; pass_bg = "linear-gradient(145deg,#1a0505,#2a0a0a)"
    elif rem <= 20:
        pass_border = "#ff6600"; pass_bg = "linear-gradient(145deg,#1a0f05,#2a1508)"
    elif rem <= 30:
        pass_border = "#ffaa00"; pass_bg = "linear-gradient(145deg,#1a1505,#2a1a08)"
    else:
        pass_border = "#00aacc"; pass_bg = "linear-gradient(145deg,#0a1520,#101a2a)"

    q_type = cur.get("q_type", "detail")
    correct_cnt = len([a for a in st.session_state.p7_answers if a])
    wrong_cnt   = len([a for a in st.session_state.p7_answers if not a])

    # ── 상단 HUD ──
    st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;
        background:#06080f;border:1px solid #1a2240;border-radius:10px;
        padding:5px 10px;margin-bottom:4px;">
      <div style="font-family:Orbitron,monospace;font-size:8px;color:#334466;
        letter-spacing:3px;font-weight:700;">DECRYPT OP</div>
      <div style="display:flex;gap:8px;align-items:center;">
        <span style="background:#0a1808;border:1px solid #226633;border-radius:5px;
          padding:2px 8px;font-size:9px;color:#00ccee;font-weight:700;">Q{step+1}/3</span>
        <span style="font-size:11px;font-weight:700;">✅{correct_cnt} ❌{wrong_cnt}</span>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── RECON 전용: X·Y·Z 스텝 라벨 + 대명사 감지 힌트 ──
    if st.session_state.get("p7_cat") == "recon":
        _xyz_labels = {0: "X — 발신자(Sender) 파악", 1: "Y — 수신자(Recipient) 파악", 2: "Z — 목적(Purpose) 파악"}
        _xyz_cols   = {0: "#00cc66", 1: "#cccc00", 2: "#ff8800"}
        _xyz_icons  = {0: "🔍", 1: "📨", 2: "🎯"}
        _slabel = _xyz_labels.get(step, f"Q{step+1}")
        _scol   = _xyz_cols.get(step, "#00ccee")
        _sicon  = _xyz_icons.get(step, "")
        st.markdown(
            f'<div style="text-align:center;background:#050a06;border:1px solid {_scol}55;'
            f'border-radius:8px;padding:5px 10px;margin-bottom:3px;">'
            f'<span style="font-size:10px;font-weight:900;letter-spacing:3px;color:{_scol};">'
            f'{_sicon} {_slabel}</span></div>',
            unsafe_allow_html=True)
        # 대명사 자동 감지 힌트
        _cur_sent = cur.get("sentences", [""])[0]
        _pronouns_check = ["I ", "I'", "I've", "I'm", "We ", "We'", "My ", "Our ", "You ", "You'", "Your "]
        _found_p = [p.strip("'") for p in _pronouns_check if p in _cur_sent]
        if _found_p:
            _p_str = " / ".join(f"<b>{p}</b>" for p in sorted(set(_found_p)))
            st.markdown(
                f'<div style="background:#030805;border:1px solid #00aa4433;border-radius:6px;'
                f'padding:3px 10px;margin-bottom:3px;font-size:10px;color:#00aa55;">'
                f'💡 대명사 감지: {_p_str} → 맥락 파악 힌트!</div>',
                unsafe_allow_html=True)

    # 지문 (누적)
    all_sents = []
    for i in range(step + 1):
        all_sents.extend(steps[i]["sentences"])
    new_start = len(all_sents) - len(cur["sentences"])

    pass_html = ''
    for i, s in enumerate(all_sents):
        if i >= new_start:
            pass_html += f'<span style="color:#ffffff;font-weight:800;">{s}</span> '
        else:
            pass_html += f'<span style="color:#7a8a9a;">{s}</span> '

    _btn_ids = ["p7a","p7b","p7c","p7d"]
    _btn_labels = ["A","B","C","D"]

    # ── 지문 카드 — 좌우 테두리 타이머 (st.markdown 자동 높이) ──
    st.markdown(f'''<div id="p7-pass" style="position:relative;
        background:{pass_bg};
        border-top:2px solid {bar_col};border-bottom:2px solid {bar_col};
        border-radius:12px;padding:0.7rem 14px;margin:2px 0;
        transition:border-color 1s;font-size:0.9rem;
        font-weight:600;line-height:1.75;color:#aab8cc;">
      <div id="p7-lbar" style="position:absolute;left:0;top:0;bottom:0;width:6px;
        background:#0a0c14;border-radius:3px 0 0 3px;overflow:hidden;">
        <div id="p7-lfill" style="position:absolute;bottom:0;width:100%;
          height:{pct*100:.1f}%;border-radius:3px 0 0 3px;
          background:linear-gradient(to bottom,{bar_col},{bar_col}88);
          box-shadow:0 0 6px {bar_col};transition:height 1s linear;"></div>
      </div>
      <div id="p7-rbar" style="position:absolute;right:0;top:0;bottom:0;width:6px;
        background:#0a0c14;border-radius:0 3px 3px 0;overflow:hidden;">
        <div id="p7-rfill" style="position:absolute;top:0;width:100%;
          height:{pct*100:.1f}%;border-radius:0 3px 3px 0;
          background:linear-gradient(to top,{bar_col},{bar_col}88);
          box-shadow:0 0 6px {bar_col};transition:height 1s linear;"></div>
      </div>
      {pass_html}
    </div>''', unsafe_allow_html=True)

    # ── 타이머 JS (height=0, 지문 아래 즉시) ──
    components.html(f"""<script>
    (function(){{
      var doc=window.parent.document;
      var r={rem},t={total};
      function run(){{
        var lf=doc.getElementById('p7-lfill');
        var rf=doc.getElementById('p7-rfill');
        var card=doc.getElementById('p7-pass');
        if(!lf||!rf){{setTimeout(run,100);return;}}
        setInterval(function(){{
          r--;if(r<0)r=0;
          var p=r/t,pct=(p*100)+'%';
          var c=p>0.6?'#00ccee':p>0.3?'#ffcc00':p>0.1?'#ff4444':'#ff0000';
          lf.style.height=pct;
          lf.style.background='linear-gradient(to bottom,'+c+','+c+'88)';
          lf.style.boxShadow='0 0 6px '+c;
          rf.style.height=pct;
          rf.style.background='linear-gradient(to top,'+c+','+c+'88)';
          rf.style.boxShadow='0 0 6px '+c;
          if(card){{
            card.style.borderTopColor=c;
            card.style.borderBottomColor=c;
            /* 지문 흔들림 제거 — 테두리 색상 변화만 유지 */
          }}
        }},1000);
      }}
      var st2=doc.createElement('style');
      st2.textContent='/* shake removed */';
      doc.head.appendChild(st2);
      run();
    }})();
    </script>""", height=0)

    # 질문
    st.markdown(f'''<div style="background:#08090f;border:1px solid #1a2240;
        border-left:3px solid #00ccee;border-radius:10px;
        padding:7px 10px;margin:3px 0;">
      <span style="font-family:Orbitron,monospace;font-size:8px;color:#4466aa;
        font-weight:700;letter-spacing:2px;">[Q{step+1}] </span>
      <span style="color:#dde8f0;font-size:0.85rem;font-weight:700;">{cur["question"]}</span>
    </div>''', unsafe_allow_html=True)

    # 답 버튼 — div id 래퍼로 색상 고정
    if st.session_state.get("_p7_processing"):
        st.session_state.pop("_p7_processing")
        st.rerun()

    for i, ch in enumerate(cur["choices"]):
        _ch_clean = ch.split(") ",1)[-1] if ") " in ch else ch
        _bid = _btn_ids[i]
        st.markdown(f'<div id="btn-{_bid}">', unsafe_allow_html=True)
        if st.button(f"【{_btn_labels[i]}】  {_ch_clean}", key=f"p7ch{step}_{i}", use_container_width=True):
            if st.session_state.get("_p7_processing"):
                st.markdown('</div>', unsafe_allow_html=True)
                continue
            st.session_state["_p7_processing"] = True
            ok = (i == cur["answer"])
            st.session_state.p7_answers.append(ok)
            # ─── analytics 기록 ───
            _an = st.session_state.p7_analytics
            _step_t = time.time() - (_an.get("step_started_at") or time.time())
            _an["step_times"].append(round(_step_t, 1))
            _an["step_correct"].append(ok)
            _an["step_started_at"] = time.time()
            st.session_state.p7_analytics = _an
            # Step 3 유형선택 상태 리셋
            st.session_state.p7_type_guessed = False
            st.session_state.p7_type_correct = None

            # ══════════════════════════════════════════════════
            # ★ cross_logs + p7_logs 저장 (논문 04 SSCI + 특허)
            # ══════════════════════════════════════════════════
            try:
                _dt_p7 = __import__("datetime")
                _today_p7 = _dt_p7.datetime.now().strftime("%Y-%m-%d")
                _uid_p7   = st.session_state.get("nickname", "guest")
                _cat_p7   = st.session_state.get("p7_cat", "unknown")
                _tsec_p7  = st.session_state.get("p7_tsec", 80)

                # 지문 고유 ID (카테고리 + 스텝)
                _passage_id  = f"{_cat_p7}_step{step+1}"
                # 이 지문에서 파생될 P5 문제 ID들 (expressions 기반)
                _expressions = cur.get("expressions", [])
                _derived_ids = [f"P5_from_{_cat_p7}_{e.get('expr','?').replace(' ','_')[:20]}"
                                for e in _expressions]

                # 세션 번호
                if "p7_session_no" not in st.session_state:
                    st.session_state.p7_session_no = 0

                # 주차 계산
                if "p7_start_date" not in st.session_state:
                    st.session_state.p7_start_date = _today_p7
                try:
                    _days_p7 = (_dt_p7.datetime.strptime(_today_p7, "%Y-%m-%d") -
                                _dt_p7.datetime.strptime(st.session_state.p7_start_date, "%Y-%m-%d")).days
                    _week_p7 = _days_p7 // 7 + 1
                except:
                    _week_p7 = 1

                _st_p7 = load_storage()

                # ── A. cross_logs: P7→P5 크로스스킬 전이 (논문 04 핵심) ──
                for _did in _derived_ids:
                    _cl = {
                        "user_id":          _uid_p7,
                        "p7_passage_id":    _passage_id,
                        "p7_category":      _cat_p7,
                        "p7_step":          step + 1,
                        "p7_q_type":        cur.get("q_type", "detail"),
                        "p7_correct":       ok,
                        "p7_session_date":  _today_p7,
                        "p7_session_no":    st.session_state.p7_session_no,
                        "derived_p5_id":    _did,
                        "p5_correct":       None,   # P5 풀이 시 업데이트
                        "p5_session_date":  None,
                        "p7_first_exposed": True,
                        "days_gap":         0,
                        "week":             _week_p7,
                        "timer_setting":    _tsec_p7,
                        "timestamp":        _dt_p7.datetime.now().isoformat(),
                    }
                    if "cross_logs" not in _st_p7:
                        _st_p7["cross_logs"] = []
                    _st_p7["cross_logs"].append(_cl)

                # ── B. p7_logs: 세션 단계 기록 ──
                _p7l = {
                    "user_id":       _uid_p7,
                    "session_date":  _today_p7,
                    "session_no":    st.session_state.p7_session_no,
                    "category":      _cat_p7,
                    "timer_setting": _tsec_p7,
                    "step":          step + 1,
                    "q_type":        cur.get("q_type", "detail"),
                    "correct":       ok,
                    "response_sec":  round(_step_t, 1),
                    "week":          _week_p7,
                    "timestamp":     _dt_p7.datetime.now().isoformat(),
                }
                if "p7_logs" not in _st_p7:
                    _st_p7["p7_logs"] = []
                _st_p7["p7_logs"].append(_p7l)

                # ZPD: LOST 시 종료 지점 기록
                if not ok:
                    _st_p7.setdefault("zpd_logs", []).append({
                        "user_id":        _uid_p7,
                        "session_date":   _today_p7,
                        "session_no":     st.session_state.p7_session_no,
                        "arena":          "P7",
                        "timer_setting":  _tsec_p7,
                        "game_over_q_no": step + 1,
                        "result":         "GAME_OVER",
                        "max_q_reached":  step + 1,
                        "week":           _week_p7,
                        "timestamp":      _dt_p7.datetime.now().isoformat(),
                    })
                elif step >= 2:
                    _st_p7.setdefault("zpd_logs", []).append({
                        "user_id":        _uid_p7,
                        "session_date":   _today_p7,
                        "session_no":     st.session_state.p7_session_no,
                        "arena":          "P7",
                        "timer_setting":  _tsec_p7,
                        "game_over_q_no": None,
                        "result":         "VICTORY",
                        "max_q_reached":  3,
                        "week":           _week_p7,
                        "timestamp":      _dt_p7.datetime.now().isoformat(),
                    })
                    st.session_state.p7_session_no += 1

                with open(STORAGE_FILE, "w", encoding="utf-8") as _fp7:
                    json.dump(_st_p7, _fp7, ensure_ascii=False, indent=2)
            except:
                pass

            if not ok:
                try: save_research_record(build_research_record("lost"))
                except: pass
                st.session_state.p7_phase = "lost"; st.rerun()
            if step >= 2:
                try: save_research_record(build_research_record("victory"))
                except: pass
                # ── cross_logs: P7→P5 크로스스킬 전이 감지 (논문B) ──
                try:
                    _pid = st.session_state.get("p7_data", {}).get("id", "unknown")
                    _save_cross_log(_pid)
                except: pass
                # ── recon_xyz_logs: X·Y·Z 단계별 정답·소요시간 (신규 논문) ──
                try:
                    _pid2 = st.session_state.get("p7_data", {}).get("id", "unknown")
                    _sno = st.session_state.get("p7_session_no", 0)
                    st.session_state.p7_session_no = _sno + 1
                    _save_recon_xyz_log(_pid2, _sno + 1)
                except: pass
                st.session_state.p7_phase = "victory"; st.rerun()
            else:
                st.session_state.p7_step += 1
            st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # ★ p7choiceColors 제거 — 정규식 오류+iframe 터치 방해. 버튼색상은 #btn-p7a/b/c/d CSS로 처리됨.

# ═══════════════════════════════════════
# PHASE: VICTORY
# ═══════════════════════════════════════
elif st.session_state.p7_phase == "victory":
    _answers = st.session_state.p7_answers
    _ok = len([a for a in _answers if a])
    st.markdown('<style>.stApp{background:#08080f!important;}</style>', unsafe_allow_html=True)
    # ── HAE Victory 메인 이미지 ──
    _ASSETS_CL = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    _hae_v_img = os.path.join(_ASSETS_CL, "hae_victory.png")
    _ch1, _ch2, _ch3 = st.columns([1, 2, 1])
    with _ch2:
        if os.path.exists(_hae_v_img): st.image(_hae_v_img, width=180)
    st.markdown('''<div style="text-align:center;padding:0.3rem 0 0.5rem 0;">
        <div style="font-size:2.2rem;font-weight:900;color:#ffd700;letter-spacing:3px;text-shadow:0 0 30px #ffd700;">CLEAR!</div>
        <div style="font-size:0.82rem;color:#00ccee;font-weight:600;letter-spacing:2px;margin-top:4px;">암호해독 작전 클리어!</div>
    </div>''', unsafe_allow_html=True)
    st.markdown(f'''<div style="background:#0c0c1e;border:1.5px solid #00ccee;border-left:4px solid #00ccee;border-radius:12px;padding:10px;text-align:center;margin:8px 0;">
        <div style="font-size:0.75rem;color:#9aa5b4;margin-bottom:2px;">이번 결과</div>
        <div style="font-size:1.5rem;font-weight:900;color:#00ccee;">✅ {_ok} / 3</div>
    </div>''', unsafe_allow_html=True)
    st.markdown('''<div style="background:#0a0800;border:1px solid #00ccee;border-radius:10px;padding:8px;text-align:center;margin-bottom:10px;">
        <div style="font-size:0.82rem;color:#00ccee;font-weight:700;">⚡ 3번 반복하면 장기기억 전환율 3배!</div>
        <div style="font-size:0.72rem;color:#555;margin-top:2px;">지금 브리핑에서 핵심표현 무기로 장착하라!</div>
    </div>''', unsafe_allow_html=True)
    _nick_cl = st.session_state.get("battle_nickname") or st.session_state.get("nickname","요원")
    _HB = '<span style="background:#001520;border:1px solid #00ccee;border-radius:5px;padding:1px 8px;color:#00ddff;font-weight:900;font-size:11px;letter-spacing:2px;">HAE</span>'
    st.markdown(f'<div style="text-align:center;padding:6px 0;"><div style="margin-bottom:4px;">{_HB}</div><div style="font-size:13px;font-weight:900;color:#00ccee;">{_nick_cl}, 정보 확보 완료. 브리핑 준비.</div></div>', unsafe_allow_html=True)
    st.markdown('''<style>
    button[data-testid="stBaseButton-primary"]{
        background:#0c0c00!important;border:2px solid #00ccee!important;
        border-left:4px solid #00ccee!important;
        color:#00ccee!important;font-size:1.1rem!important;font-weight:900!important;
        min-height:48px!important;animation:none!important;
    }
    button[data-testid="stBaseButton-primary"] p{color:#ffd700!important;font-size:1.1rem!important;font-weight:900!important;}
    </style>''', unsafe_allow_html=True)
    if st.button("📋 브리핑 보기", type="primary", use_container_width=True):
        st.session_state.p7_phase = "briefing"; st.rerun()
    _vc1, _vc2 = st.columns(2)
    with _vc1:
        if st.button("🔄 다시 도전", key="v_retry", use_container_width=True):
            for k in ["p7_phase","p7_cat","p7_tsec","p7_tsec_chosen","p7_step","p7_started_at","p7_answers","p7_data"]:
                if k in st.session_state: del st.session_state[k]
            st.rerun()
    with _vc2:
        if st.button("🏠 홈", key="v_main", use_container_width=True):
            st.session_state._p7_just_left = True
            _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
            if _nick:
                st.query_params["nick"] = _nick
                st.query_params["ag"] = "1"
            st.switch_page("main_hub.py")
    import streamlit.components.v1 as _vc
    _vc_js = '''<script>
    (function(){
        function styleVBtns(){
            var doc=window.parent.document;
            var rows=doc.querySelectorAll('[data-testid="stHorizontalBlock"]');
            if(!rows.length) return;
            var lastRow=rows[rows.length-1];
            var btns=lastRow.querySelectorAll('button');
            if(btns[0]){
                btns[0].style.setProperty('background','#0f0f1e','important');
                btns[0].style.setProperty('border','1px solid #1a1a2a','important');
                btns[0].style.setProperty('border-left','4px solid #00ccee','important');
                btns[0].style.setProperty('color','#e8e0cc','important');
                btns[0].style.setProperty('animation','none','important');
            }
            if(btns[1]){
                btns[1].style.setProperty('background','#0f0f1e','important');
                btns[1].style.setProperty('border','1px solid #1a1a2a','important');
                btns[1].style.setProperty('border-left','4px solid #4488cc','important');
                btns[1].style.setProperty('color','#e8e0cc','important');
                btns[1].style.setProperty('animation','none','important');
            }
        }
        setTimeout(styleVBtns,150);setTimeout(styleVBtns,500);setTimeout(styleVBtns,1200);
    })();
    </script>'''
    _vc.html(_vc_js, height=0)


# ═══════════════════════════════════════
# PHASE: LOST
# ═══════════════════════════════════════
elif st.session_state.p7_phase == "lost":
    import random as _rnd2
    _answers = st.session_state.p7_answers
    _ok = len([a for a in _answers if a])
    _is_timeout = (st.session_state.get("p7_phase_reason","") == "timeout")
    st.markdown('<style>.stApp{background:#080008!important;}</style>', unsafe_allow_html=True)
    # ── HAE Warning 메인 이미지 ──
    _ASSETS_GO2 = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    _hae_w_img = os.path.join(_ASSETS_GO2, "hae_warning.png")
    _cg1, _cg2, _cg3 = st.columns([1, 2, 1])
    with _cg2:
        if os.path.exists(_hae_w_img): st.image(_hae_w_img, width=200)
    st.markdown(f'''<div style="text-align:center;padding:0.3rem 0;">
        <div style="font-size:2rem;font-weight:900;color:#cc0000;letter-spacing:2px;">GAME OVER</div>
        <div style="font-size:0.75rem;color:#660000;letter-spacing:2px;margin-top:3px;">넌 오늘도 졌다...</div>
    </div>''', unsafe_allow_html=True)
    st.markdown(f'''<div style="background:#0c0008;border:1.5px solid #cc2244;border-left:4px solid #cc2244;border-radius:12px;padding:10px;text-align:center;margin:6px 0;">
        <div style="font-size:0.72rem;color:#9aa5b4;margin-bottom:2px;">처참한 결과</div>
        <div style="font-size:1.5rem;font-weight:900;color:#cc2244;">{_ok} / 3</div>
    </div>''', unsafe_allow_html=True)

    if _is_timeout:
        _nag1 = _rnd2.choice(["독해 속도가 거북이냐 🐢","토익은 널 기다려주지 않아 ⏰"])
        _nag2 = "시간 안에 못 읽으면 실전에서도 똑같이 망해 😤"
    elif _ok == 0:
        _nag1 = _rnd2.choice(["눈 뜨고 읽긴 한 거야? 🫣","이거 토익이야, 점자가 아니야 😶"])
        _nag2 = "에빙하우스: 복습 없이 24시간 후 80% 망각이야"
    elif _ok == 1:
        _nag1 = _rnd2.choice(["찍어서 맞춘 거 다 알아 😂","운도 실력이라고? 그건 토익엔 없어 🙃"])
        _nag2 = "3문제 중 1개... 이게 실력이야"
    else:
        _nag1 = _rnd2.choice(["딱 한 문제 차이야. 억울하지? 😭","그 한 문제가 토익 점수 50점 차이야 😤"])
        _nag2 = "아깝다고? 그럼 다시 싸워"

    st.markdown(f'''<div style="background:#0a0008;border:1px solid #441122;border-radius:10px;padding:10px 12px;margin-bottom:10px;">
        <div style="font-size:0.92rem;color:#ff4466;font-weight:700;margin-bottom:4px;">{_nag1}</div>
        <div style="font-size:0.78rem;color:#664433;">{_nag2}</div>
    </div>''', unsafe_allow_html=True)

    _nick_go2 = st.session_state.get("battle_nickname") or st.session_state.get("nickname","요원")
    _HB = '<span style="background:#001520;border:1px solid #00ccee;border-radius:5px;padding:1px 8px;color:#00ddff;font-weight:900;font-size:11px;letter-spacing:2px;">HAE</span>'
    st.markdown(f'<div style="text-align:center;padding:6px 0;"><div style="margin-bottom:4px;">{_HB}</div><div style="font-size:13px;font-weight:900;color:#ff6644;">{_nick_go2}, 통신 두절. 재접속하라.</div></div>', unsafe_allow_html=True)

    st.markdown('''<style>
    button[data-testid="stBaseButton-primary"]{
        background:#0a0008!important;border:2px solid #cc2244!important;
        border-left:4px solid #cc2244!important;
        color:#ff4466!important;font-size:1.1rem!important;font-weight:900!important;
        min-height:48px!important;animation:none!important;
    }
    button[data-testid="stBaseButton-primary"] p{color:#ff4466!important;font-size:1.1rem!important;font-weight:900!important;}
    </style>''', unsafe_allow_html=True)
    if st.button("🔥 설욕전! 다시 싸운다!", type="primary", use_container_width=True):
        for k in ["p7_phase","p7_cat","p7_tsec","p7_tsec_chosen","p7_step","p7_started_at","p7_answers","p7_data","p7_phase_reason"]:
            if k in st.session_state: del st.session_state[k]
        st.rerun()
    if st.button("🏠 홈", key="lost_home", use_container_width=True):
        st.session_state._p7_just_left = True
        _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
        if _nick:
            st.query_params["nick"] = _nick
            st.query_params["ag"] = "1"
        st.switch_page("main_hub.py")
    import streamlit.components.v1 as _lc
    _lc_js = '''<script>
    (function(){
        function styleLostBtn(){
            var doc=window.parent.document;
            var btns=doc.querySelectorAll('button[kind="secondary"]');
            btns.forEach(function(b){
                var t=b.textContent||"";
                if(t.indexOf("홈")>-1&&t.indexOf("설욕")==-1){
                    b.style.setProperty("background","#0f0f1e","important");
                    b.style.setProperty("border","1px solid #1a1a2a","important");
                    b.style.setProperty("border","1.5px solid rgba(255,255,255,0.3)","important");
                    b.style.setProperty("color","#666","important");
                    b.style.setProperty("animation","none","important");
                    b.style.setProperty("font-size","0.85rem","important");
                }
            });
        }
        setTimeout(styleLostBtn,150);setTimeout(styleLostBtn,500);setTimeout(styleLostBtn,1200);
    })();
    </script>'''
    _lc.html(_lc_js, height=0)


elif st.session_state.p7_phase == "briefing":
    import re as _re3

    data    = st.session_state.p7_data
    steps   = data["steps"]
    answers = st.session_state.p7_answers
    ok_cnt  = len([a for a in answers if a])
    miss_cnt= len(answers) - ok_cnt
    was_victory = len(answers) == 3 and all(answers)

    if "p7_br_idx" not in st.session_state: st.session_state.p7_br_idx = 0
    bi = st.session_state.p7_br_idx

    # ── 지문이 바뀌면 저장 상태 초기화 ──
    _passage_uid = data.get("title","") + str(len(steps))
    if st.session_state.get("p7_br_passage_uid") != _passage_uid:
        # 이전 지문의 br_sent_saved_* 키 전부 삭제
        for _k in list(st.session_state.keys()):
            if _k.startswith("br_sent_saved_") or _k.startswith("br_sv_"):
                del st.session_state[_k]
        st.session_state["p7_br_passage_uid"] = _passage_uid
    num_steps = min(len(steps), len(answers))
    if num_steps == 0: num_steps = 1
    # bi clamping handled by sequential mode below

    # query_params 처리
    _qp = st.query_params.get("p7action", "")
    if _qp == "store":
        st.query_params.clear(); st.switch_page("pages/03_POW_HQ.py")
    elif _qp == "lobby":
        for k in D: st.session_state[k] = D[k]
        st.query_params.clear()
        _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
        if _nick:
            st.query_params["nick"] = _nick
            st.query_params["ag"] = "1"
        st.switch_page("main_hub.py")

    # ── CSS ──
    st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
#MainMenu{visibility:hidden!important;}
header[data-testid="stHeader"]{height:0!important;overflow:hidden!important;}
.block-container{padding:8px 12px 20px!important;margin:0!important;}
div[data-testid="stVerticalBlock"]{gap:6px!important;}
.element-container{margin:0!important;padding:0!important;}
div[data-testid="stHorizontalBlock"]{gap:5px!important;margin:0!important;flex-wrap:nowrap!important;}
div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]{padding:0!important;min-width:0!important;flex:1!important;}

/* Q탭 버튼 */
div[data-testid="stButton"] button{
  background:#07090f!important;border:1px solid #1a2240!important;
  border-radius:8px!important;color:#334466!important;
  font-size:0.88rem!important;font-weight:700!important;
  padding:6px 4px!important;min-height:38px!important;width:100%!important;
  transition:all .12s!important;
}
div[data-testid="stButton"] button p{color:#334466!important;font-size:0.88rem!important;font-weight:700!important;}

/* Q탭 선택됨 */
div[data-testid="stButton"] button.br-qtab-on{
  background:#0d1a2a!important;border-color:#00aacc!important;color:#00ccee!important;}
div[data-testid="stButton"] button.br-qtab-on p{color:#00ccee!important;}

/* 저장 버튼 */
div[data-testid="stButton"] button.br-save{
  background:#001520!important;border:1.5px solid rgba(0,180,220,0.5)!important;
  border-radius:10px!important;color:#00ccee!important;
  font-size:0.88rem!important;font-weight:900!important;min-height:44px!important;
}
div[data-testid="stButton"] button.br-save p{color:#00ccee!important;font-size:0.88rem!important;font-weight:900!important;}

/* 오답 문장 저장 버튼 (빨강 강조) */
div[data-testid="stButton"] button.br-save-wrong{
  background:#100008!important;border:1.5px solid rgba(255,80,80,0.5)!important;
  border-radius:10px!important;color:#ff6666!important;
  font-size:0.88rem!important;font-weight:900!important;min-height:44px!important;
}
div[data-testid="stButton"] button.br-save-wrong p{color:#ff6666!important;font-size:0.88rem!important;font-weight:900!important;}

/* 포로사령부 CTA */
div[data-testid="stButton"] button.br-pow{
  background:#0e0020!important;border:2px solid #8833ff!important;
  border-radius:12px!important;color:#aa66ff!important;
  font-size:0.9rem!important;font-weight:900!important;min-height:48px!important;
}
div[data-testid="stButton"] button.br-pow p{color:#aa66ff!important;font-size:0.9rem!important;font-weight:900!important;}

/* 홈 버튼 */
div[data-testid="stButton"] button.br-home{
  background:#05050e!important;border:1px solid #151525!important;
  border-radius:10px!important;color:#3d5066!important;min-height:40px!important;
}
div[data-testid="stButton"] button.br-home p{color:#3d5066!important;}
</style>""", unsafe_allow_html=True)

    # ══════════════════════════════════════
    # 최종 요약 (bi >= num_steps)
    # ══════════════════════════════════════
    if bi >= num_steps:
        _ASSETS_HAE2 = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
        _hae_fin = os.path.join(_ASSETS_HAE2, "hae_victory.png" if was_victory else "hae_warning.png")
        if os.path.exists(_hae_fin):
            _hfc1, _hfc2, _hfc3 = st.columns([1, 2, 1])
            with _hfc2:
                st.image(_hae_fin, width=140)

        _HB_BR = '<span style="background:#001520;border:1px solid #00ccee;border-radius:5px;padding:1px 8px;color:#00ddff;font-weight:900;font-size:11px;letter-spacing:2px;">HAE</span>'
        _victory_col = "#00ccee" if was_victory else "#FF2D55"
        _victory_txt = "OP COMPLETE" if was_victory else "OP FAILED"
        _victory_emoji = "📡" if was_victory else "💀"

        import streamlit.components.v1 as _br_comp2
        _br_comp2.html(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap');
        *{{margin:0;padding:0;box-sizing:border-box;}}body{{background:transparent;font-family:sans-serif;text-align:center;}}
        @keyframes popIn{{from{{transform:scale(0.5);opacity:0}}to{{transform:scale(1);opacity:1}}}}
        .card{{background:radial-gradient(ellipse at top,#001520 0%,#06080f 70%);
            border:2.5px solid {_victory_col};border-radius:18px;padding:16px 14px;}}
        .title{{font-family:'Orbitron',monospace;font-size:11px;font-weight:900;
            color:{_victory_col};letter-spacing:3px;margin-bottom:8px;}}
        .score{{font-family:'Orbitron',monospace;font-size:32px;font-weight:900;
            color:#ffffff;text-shadow:0 0 20px {_victory_col};animation:popIn 0.5s ease;}}
        .sub{{font-size:13px;color:#8899aa;font-weight:700;margin-top:5px;}}
        </style>
        <div class="card">
          <div class="title">{_victory_emoji} DECRYPT OP · {_victory_txt}</div>
          <div class="score">✅ {ok_cnt} &nbsp; ❌ {miss_cnt}</div>
          <div class="sub">3문제 브리핑 완료 · {data.get("title","")}</div>
        </div>
        """, height=180)

        st.markdown(f'<div style="text-align:center;margin:6px 0;">{_HB_BR}</div>', unsafe_allow_html=True)

        if was_victory:
            _hvc1, _hvc2 = st.columns(2)
            with _hvc1:
                if st.button("💀 포로사령부!", key="p7br_pow", use_container_width=True):
                    st.switch_page("pages/03_POW_HQ.py")
            with _hvc2:
                if st.button("🔄 다음 암호!", key="p7br_next", use_container_width=True):
                    for k in ["p7_data","p7_answers","p7_br_idx","p7_br_passage_uid"]:
                        if k in st.session_state: del st.session_state[k]
                    for _kk in list(st.session_state.keys()):
                        if _kk.startswith("br_sent_saved_") or _kk.startswith("br_sv_"):
                            del st.session_state[_kk]
                    st.session_state.p7_phase = "lobby"; st.rerun()
        else:
            if st.button("🔄 설욕전!", key="p7br_retry", use_container_width=True):
                for k in ["p7_data","p7_answers","p7_br_idx","p7_br_passage_uid"]:
                    if k in st.session_state: del st.session_state[k]
                for _kk in list(st.session_state.keys()):
                    if _kk.startswith("br_sent_saved_") or _kk.startswith("br_sv_"):
                        del st.session_state[_kk]
                st.session_state.p7_phase = "lobby"; st.rerun()
            _rc1, _rc2 = st.columns([3, 1])
            with _rc1:
                if st.button("💀 포로사령부!", key="p7br_pow2", use_container_width=True):
                    st.switch_page("pages/03_POW_HQ.py")
            with _rc2:
                if st.button("🏠 홈", key="p7br_home2", use_container_width=True):
                    for k in D: st.session_state[k] = D[k]
                    _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
                    if _nick:
                        st.query_params["nick"] = _nick
                        st.query_params["ag"] = "1"
                    st.switch_page("main_hub.py")

    # ══════════════════════════════════════
    # Q카드 순차 표시 (bi < num_steps)
    # ══════════════════════════════════════
    else:
        s = steps[bi]
        ok = answers[bi] if bi < len(answers) else False
        sym = "✅" if ok else "❌"
        correct_choice = s["choices"][s["answer"]]
        _mark_style = "color:#00ffaa;font-weight:900;border-bottom:2px solid #00ffaa;padding:0 2px;"
        _exprs_list = [e.get("expr","") for e in s.get("expressions", []) if e.get("expr")]
        c_kr = s.get("choices_kr", [])
        answer_kr = c_kr[s["answer"]] if c_kr and s["answer"] < len(c_kr) else ""
        kr_full = s.get("kr", "")
        import re as _re_kr
        _kr_tmp = _re_kr.sub(r'(?<![0-9])[.](?![0-9])', '.||', kr_full)
        _kr_tmp = _kr_tmp.replace("!","!|").replace("?","?|")
        kr_sents = [x.strip() for x in _kr_tmp.split("|") if x.strip()]

        # ── HAE 캐릭터 (Q카드 상단) ──
        _ASSETS_HAE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
        _br_hae_path = os.path.join(_ASSETS_HAE, "hae_normal.png")
        if os.path.exists(_br_hae_path):
            _hc1, _hc2 = st.columns([1, 5])
            with _hc1:
                st.image(_br_hae_path, width=55)
            with _hc2:
                _HB_Q = '<span style="background:#001520;border:1px solid #00ccee;border-radius:5px;padding:1px 8px;color:#00ddff;font-weight:900;font-size:11px;letter-spacing:2px;">HAE</span>'
                st.markdown(f'<div style="padding:6px 0 0 4px;"><div style="margin-bottom:3px;">{_HB_Q}</div><div style="font-size:12px;font-weight:900;color:#00ccee;">Q{bi+1} 브리핑 — {"해독 완료!" if ok else "해독 실패... 분석하라!"}</div></div>', unsafe_allow_html=True)

        # ── 진행 도트 ──
        _dots_html = ""
        for _di in range(num_steps):
            if _di < bi:
                _dc = "#00ccee" if answers[_di] else "#ff4466"
                _dots_html += f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:{_dc};margin:0 4px;"></span>'
            elif _di == bi:
                _dots_html += '<span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:#00ccee;margin:0 4px;box-shadow:0 0 8px #00ccee;"></span>'
            else:
                _dots_html += '<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:#1a1a2a;border:1px solid #333;margin:0 4px;"></span>'

        st.markdown(f'<div style="display:flex;justify-content:center;align-items:center;padding:4px 0 6px;">{_dots_html}</div>', unsafe_allow_html=True)

        # ── 문제 + 정답 카드 ──
        _q_border = "#00ccee" if ok else "#ff4466"
        st.markdown(f'''<div style="background:#06090f;border:1px solid #1a2240;
            border-left:3px solid {_q_border};border-radius:10px;padding:8px 10px;">
          <div style="font-size:10px;color:#5588aa;font-weight:700;letter-spacing:2px;margin-bottom:4px;">[ Q{bi+1} ] RESULT</div>
          <div style="font-size:13px;color:#aaccdd;font-weight:600;margin-bottom:4px;">{s["question"]}</div>
          <div style="font-size:13px;font-weight:700;color:{_q_border};">{sym} {correct_choice}</div>
          {f'<div style="font-size:11px;color:#88bbcc;font-weight:600;margin-top:3px;">{answer_kr}</div>' if answer_kr else ""}
        </div>''', unsafe_allow_html=True)

        # ── 문장 카드들 ──
        import re as _re3
        for si, sent in enumerate(s["sentences"]):
            sent_key = f"br_sent_saved_{bi}_{si}"
            if sent_key not in st.session_state: st.session_state[sent_key] = False
            is_saved = st.session_state[sent_key]
            sent_kr = kr_sents[si] if si < len(kr_sents) else kr_full

            _hl = sent
            for _ex in _exprs_list:
                if _ex.lower() in _hl.lower():
                    try: _hl = _re3.sub(f"(?i)({_re3.escape(_ex)})", f'<span style="{_mark_style}">\\1</span>', _hl)
                    except: pass

            _sent_lower = sent.lower()
            _sent_exprs = [
                e for e in s.get("expressions", [])
                if e.get("expr") and e.get("expr","").lower() in _sent_lower
            ]
            _card_border = "#00aacc" if ok else "#ff4466"

            if is_saved:
                st.markdown(
                    f'<div style="background:#04080a;border:1.5px solid rgba(0,150,100,0.25);border-left:4px solid #336644;border-radius:12px;padding:10px;opacity:0.85;">' +
                    f'<div style="font-size:13px;font-weight:800;color:#ddeeff;line-height:1.75;margin-bottom:5px;">{_hl}</div>' +
                    f'<div style="font-size:12px;color:#99bbcc;font-weight:600;margin-bottom:6px;">{sent_kr}</div>' +
                    '<span style="background:#001520;border:1px solid #006688;border-radius:6px;padding:2px 8px;font-size:8px;color:#00ccee;font-weight:700;">✅ 포획 완료 · 수용소 대기중</span>' +
                    '</div>',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div style="background:#06090f;border:1.5px solid rgba(0,180,255,0.25);border-left:4px solid {_card_border};border-radius:12px;padding:10px;margin-bottom:2px;">' +
                    f'<div style="font-size:13px;font-weight:800;color:#ddeeff;line-height:1.75;margin-bottom:5px;">{_hl}</div>' +
                    f'<div style="font-size:12px;color:#99bbcc;font-weight:600;margin-bottom:6px;">{sent_kr}</div>' +
                    '</div>',
                    unsafe_allow_html=True)

                _sv_key = f"br_sv_{bi}_{si}"
                _btn_label = "📌 정보 포획! → 수용소 이송" if ok else "⛓ 오답 정보 — 자동 포획!"
                if st.button(_btn_label, key=_sv_key, use_container_width=True):
                    sent_data = dict(s)
                    sent_data["sentences"] = [sent]
                    sent_data["kr"] = sent_kr
                    save_expressions(_sent_exprs, step_data=sent_data)
                    try:
                        import sys as _sys4, os as _os4, datetime as _bdt
                        _sys4.path.insert(0, _os4.path.dirname(__file__))
                        from _word_family_db import find_words_in_sentence as _find_w
                        _storage_br = load_storage()
                        if "word_prison" not in _storage_br: _storage_br["word_prison"] = []
                        _cat_br = st.session_state.get("p7_cat", "P7")
                        _matched_br = _find_w(sent, max_words=3)
                        _br_changed = False
                        for _m in _matched_br:
                            _w = _m["word"].strip()
                            if not _w or len(_w) < 3: continue
                            if any(p.get("word","").lower()==_w.lower() for p in _storage_br["word_prison"]): continue
                            _storage_br["word_prison"].append({
                                "word":           _w,
                                "kr":             _m["kr"],
                                "pos":            _m["pos"],
                                "family_root":    _m["family_root"],
                                "source":         "P7",
                                "sentence":       sent,
                                "sent_kr":        sent_kr,
                                "captured_date":  _bdt.datetime.now().strftime("%Y-%m-%d"),
                                "correct_streak": 0,
                                "last_reviewed":  None,
                                "cat":            _cat_br,
                            })
                            _br_changed = True
                        if _br_changed:
                            save_storage(_storage_br)
                    except Exception:
                        pass
                    st.session_state[sent_key] = True
                    st.rerun()

        # ── 다음 심문 / 브리핑 완료 버튼 ──
        st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)
        _is_last = (bi + 1 >= num_steps)
        _next_label = "🏁 브리핑 완료!" if _is_last else f"다음 심문 → Q{bi+2}"
        st.markdown('''<style>
        div[data-testid="stButton"]:last-of-type button{
            background:#0a0a20!important;border:2px solid #00ccff!important;
            border-radius:12px!important;color:#00ddff!important;
            font-size:1.0rem!important;font-weight:900!important;min-height:50px!important;}
        div[data-testid="stButton"]:last-of-type button p{color:#00ddff!important;font-size:1.0rem!important;font-weight:900!important;}
        </style>''', unsafe_allow_html=True)
        if st.button(_next_label, key=f"p7br_next_{bi}", use_container_width=True):
            st.session_state.p7_br_idx = bi + 1
            st.rerun()

        # ── 하단 홈 버튼 (작게) ──
        st.markdown('''<style>
        div[data-testid="stButton"] button.p7-home-sm{
            background:#05050e!important;border:1px solid #151525!important;
            border-radius:10px!important;color:#3d5066!important;
            min-height:36px!important;font-size:0.82rem!important;}
        </style>''', unsafe_allow_html=True)
        if st.button("🏠 홈", key=f"p7br_home_{bi}", use_container_width=True):
            for k in D: st.session_state[k] = D[k]
            _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
            if _nick:
                st.query_params["nick"] = _nick
                st.query_params["ag"] = "1"
            st.switch_page("main_hub.py")

