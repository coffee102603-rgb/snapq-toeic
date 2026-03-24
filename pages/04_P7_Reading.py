"""P7 Reading Arena — 60초 독해 전투 (V2)"""
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import random, time, json, os

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

st.set_page_config(page_title="P7 Reading ⚔️", page_icon="📖", layout="wide", initial_sidebar_state="collapsed")


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
        with open(STORAGE_FILE,"r",encoding="utf-8") as f:
            d = json.load(f)
            if isinstance(d, list): return {"saved_questions":d,"saved_expressions":[]}
            if "saved_questions" not in d: d["saved_questions"]=[]
            if "saved_expressions" not in d: d["saved_expressions"]=[]
            return d
    return {"saved_questions":[],"saved_expressions":[]}
def save_storage(data):
    with open(STORAGE_FILE,"w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2)
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

/* P7 지문 카드 */
.p7-pass{background:linear-gradient(145deg,#13112a,#1a1535);border:2px solid rgba(155,89,182,0.7);border-radius:18px;padding:1.5rem;margin:0.5rem 0;box-shadow:0 0 20px rgba(155,89,182,0.15);}
.p7-sent{color:#e8e0cc;font-size:0.82rem;font-weight:400;line-height:1.55;}
.p7-new{color:#9aa5b4;font-weight:400;font-size:0.82rem;}
.p7-qbox{background:linear-gradient(145deg,#1e1040,#2a1555);border:2px solid rgba(155,89,182,0.8);border-radius:18px;padding:1.5rem;margin:0.5rem 0;box-shadow:0 0 15px rgba(155,89,182,0.2);}
.p7-q{color:#ffffff;font-size:clamp(0.85rem,3vw,1rem);font-weight:800;line-height:1.8;}

/* 진행 표시 */
.p7-step{text-align:center;font-size:1.2rem;font-weight:900;color:#44ffcc;margin:0.3rem 0;}
#MainMenu{visibility:hidden!important;}olbar"]{visibility:hidden!important;}.block-container{padding-top:0!important;}.p7-hud{background:#000000;border:2px solid rgba(255,255,255,0.55);border-radius:14px;padding:0.8rem 1.2rem;margin:0.3rem 0;display:flex;justify-content:space-between;align-items:center;}
.p7-hud-l{font-size:1.3rem;font-weight:900;color:#44ffcc;}
.p7-hud-r{font-size:1.1rem;font-weight:800;color:#ffcc00;}

/* 브리핑 */
.stButton[data-testid] button[kind="secondary"]{min-height:32px!important;padding:2px 4px!important;font-size:0.9rem!important;}
.p7-br-s{font-size:2rem;font-weight:700;color:#1a1a1a;line-height:2;margin-bottom:0.8rem;}
.p7-br-hl{color:#00aa88;font-weight:900;font-size:2.1rem;text-decoration:underline;text-underline-offset:5px;text-decoration-thickness:3px;}
.p7-br-kr{font-size:1.5rem;font-weight:600;color:#333;line-height:1.7;margin-bottom:0.5rem;}
.p7-br-ex{font-size:1.4rem;color:#444;line-height:1.6;padding:0.5rem 0.7rem;background:rgba(0,180,150,0.1);border-left:4px solid #00aa88;border-radius:0 10px 10px 0;}

/* VICTORY/LOST 배너 */
.p7-ban{text-align:center;padding:3px 6px!important;border-radius:10px;margin:1px 0;font-size:0.85rem!important;font-weight:900;}
.p7-ban-v{background:#000000;color:#fff;border:2px solid rgba(255,255,255,0.55);}
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
.stButton button{min-height:43px!important;padding:4px 6px!important;}
.stButton button p{font-size:1.0rem!important;}

/* P7브리핑 버튼 강제 가로배치 */
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
PASSAGES = {
"article": {
    "title": "📰 Article",
    "steps": [
        {
            "q_type": "purpose",
            "sentences": [
                "Norfield Pharmaceuticals announced on Tuesday that it will suspend production at its Vancouver manufacturing plant for a period of six weeks.",
                "The temporary shutdown is intended to allow the company to upgrade its quality control systems in compliance with new federal regulations."
            ],
            "question": "What is the purpose of this article?",
            "question_kr": "이 기사의 목적은 무엇인가?",
            "choices": [
                "(A) To announce the permanent closure of a plant",
                "(B) To report a company's temporary production halt",
                "(C) To introduce new federal regulations",
                "(D) To advertise upgraded manufacturing equipment"
            ],
            "choices_kr": [
                "(A) 공장의 영구 폐쇄 발표",
                "(B) 회사의 일시적 생산 중단 보도",
                "(C) 새 연방 규정 소개",
                "(D) 업그레이드된 제조 장비 광고"
            ],
            "answer": 1,
            "kr": "Norfield Pharmaceuticals는 화요일에 밴쿠버 제조 공장의 생산을 6주간 중단한다고 발표했다. 이 일시적 가동 중단은 새 연방 규정을 준수하기 위해 품질 관리 시스템을 업그레이드하기 위한 것이다.",
            "expressions": [
                {"expr": "suspend production", "meaning": "생산을 중단하다"},
                {"expr": "in compliance with", "meaning": "~을 준수하여"},
                {"expr": "temporary shutdown", "meaning": "일시적 가동 중단"}
            ]
        },
        {
            "q_type": "detail",
            "sentences": [
                "During the shutdown, approximately 340 workers will be temporarily reassigned to the company's Calgary facility.",
                "Norfield has assured shareholders that no permanent job losses are anticipated as a result of the upgrade.",
                "The company expects to resume full operations by the end of the second quarter."
            ],
            "question": "What will happen to workers during the shutdown?",
            "question_kr": "가동 중단 기간 동안 직원들은 어떻게 되는가?",
            "choices": [
                "(A) They will be permanently laid off",
                "(B) They will be reassigned to another facility",
                "(C) They will work reduced hours at Vancouver",
                "(D) They will receive additional training on-site"
            ],
            "choices_kr": [
                "(A) 영구 해고됨",
                "(B) 다른 시설로 재배치됨",
                "(C) 밴쿠버에서 단축 근무",
                "(D) 현장에서 추가 교육 받음"
            ],
            "answer": 1,
            "kr": "가동 중단 기간 동안 약 340명의 직원이 캘거리 시설로 임시 재배치된다. Norfield는 주주들에게 이번 업그레이드로 인한 영구적 일자리 감소는 없을 것이라고 보장했다. 회사는 2분기 말까지 전면 가동을 재개할 것으로 예상한다.",
            "expressions": [
                {"expr": "be reassigned to", "meaning": "~로 재배치되다"},
                {"expr": "permanent job losses", "meaning": "영구적 일자리 감소"},
                {"expr": "resume full operations", "meaning": "전면 가동을 재개하다"}
            ]
        },
        {
            "q_type": "inference",
            "sentences": [
                "Analysts have noted that Norfield's competitors underwent similar upgrades last year following the introduction of the regulations.",
                "Norfield's delay in addressing the requirements has prompted some industry observers to question the company's regulatory preparedness.",
                "Nevertheless, the company's stock rose 2.3 percent following the announcement, suggesting that investors view the upgrade as a positive long-term move."
            ],
            "question": "What is implied about Norfield Pharmaceuticals?",
            "question_kr": "Norfield Pharmaceuticals에 대해 추론할 수 있는 것은?",
            "choices": [
                "(A) It was the first company to comply with the new regulations",
                "(B) It acted more slowly than rivals on regulatory requirements",
                "(C) Its stock price fell after the announcement was made",
                "(D) Its Vancouver plant will not reopen after the shutdown"
            ],
            "choices_kr": [
                "(A) 새 규정을 가장 먼저 준수한 회사",
                "(B) 규정 요건 대응이 경쟁사보다 늦었음",
                "(C) 발표 후 주가가 하락함",
                "(D) 밴쿠버 공장이 중단 후 재개되지 않을 것"
            ],
            "answer": 1,
            "kr": "분석가들은 Norfield의 경쟁사들이 규정 도입 후 작년에 유사한 업그레이드를 완료했다고 언급했다. Norfield의 늦은 대응은 일부 업계 관계자들이 회사의 규정 준비 태세에 의문을 갖게 했다. 그럼에도 발표 후 주가가 2.3% 상승해 투자자들이 장기적으로 긍정적 조치로 본다는 것을 시사한다.",
            "expressions": [
                {"expr": "regulatory preparedness", "meaning": "규정 준비 태세"},
                {"expr": "prompt A to do", "meaning": "A가 ~하도록 촉구하다"},
                {"expr": "in the long term", "meaning": "장기적으로"}
            ]
        }
    ]
},
"letter": {
    "title": "✉️ Letter",
    "steps": [
        {
            "q_type": "purpose",
            "sentences": [
                "Dear Ms. Harrington, I am writing on behalf of Delton Consulting Group to express our sincere interest in the office space currently listed for lease at 18 Meridian Tower.",
                "We are seeking a fully furnished suite of approximately 1,200 square feet to accommodate our expanding regional team."
            ],
            "question": "Why was this letter written?",
            "question_kr": "이 편지는 왜 작성되었는가?",
            "choices": [
                "(A) To confirm a signed lease agreement",
                "(B) To inquire about available office space",
                "(C) To request a reduction in monthly rent",
                "(D) To notify a landlord of an early departure"
            ],
            "choices_kr": [
                "(A) 서명된 임대 계약 확인",
                "(B) 사무 공간에 대한 문의",
                "(C) 월세 인하 요청",
                "(D) 임대인에게 조기 퇴거 통보"
            ],
            "answer": 1,
            "kr": "Delton Consulting Group을 대표하여 18 Meridian Tower에 현재 임대 중인 사무 공간에 큰 관심이 있음을 알립니다. 우리는 확장 중인 지역 팀을 수용하기 위해 약 1,200평방피트의 완전 가구 구비 스위트를 찾고 있습니다.",
            "expressions": [
                {"expr": "on behalf of", "meaning": "~을 대표하여"},
                {"expr": "listed for lease", "meaning": "임대 매물로 올라와 있는"},
                {"expr": "accommodate", "meaning": "수용하다"}
            ]
        },
        {
            "q_type": "detail",
            "sentences": [
                "Our team requires reliable high-speed internet access, a private conference room, and proximity to public transportation.",
                "We would prefer a lease term of at least 18 months, with the option to renew for an additional year.",
                "Our budget for monthly rent is $4,500, inclusive of all utility costs."
            ],
            "question": "What lease term does Delton Consulting Group prefer?",
            "question_kr": "Delton Consulting Group이 선호하는 임대 기간은?",
            "choices": [
                "(A) At least 6 months",
                "(B) Exactly 12 months",
                "(C) At least 18 months",
                "(D) Exactly 24 months"
            ],
            "choices_kr": [
                "(A) 최소 6개월",
                "(B) 정확히 12개월",
                "(C) 최소 18개월",
                "(D) 정확히 24개월"
            ],
            "answer": 2,
            "kr": "우리 팀은 안정적인 고속 인터넷, 전용 회의실, 대중교통 접근성이 필요합니다. 최소 18개월 임대 기간을 선호하며, 추가 1년 연장 옵션이 있으면 좋겠습니다. 월 임대료 예산은 모든 공과금 포함 $4,500입니다.",
            "expressions": [
                {"expr": "lease term", "meaning": "임대 기간"},
                {"expr": "inclusive of", "meaning": "~을 포함하여"},
                {"expr": "proximity to", "meaning": "~에 근접함"}
            ]
        },
        {
            "q_type": "not",
            "sentences": [
                "Should the space meet our requirements, we would be prepared to arrange a site visit at your earliest convenience.",
                "We are also open to discussing flexible move-in dates, as our current lease does not expire until the end of next month.",
                "Please feel free to contact me directly at j.park@deltonconsulting.com or by phone at (416) 882-3300."
            ],
            "question": "Which is NOT mentioned in the letter?",
            "question_kr": "편지에서 언급되지 않은 것은?",
            "choices": [
                "(A) The writer's contact information",
                "(B) Willingness to schedule a site visit",
                "(C) A request for a floor plan of the office",
                "(D) Flexibility regarding the move-in date"
            ],
            "choices_kr": [
                "(A) 작성자의 연락처 정보",
                "(B) 현장 방문 일정 조율 의향",
                "(C) 사무실 평면도 요청",
                "(D) 입주일에 대한 유연성"
            ],
            "answer": 2,
            "kr": "공간이 요건을 충족하면 편한 시간에 현장 방문을 준비할 의향이 있습니다. 현재 임대 계약이 다음 달 말에 만료되므로 유연한 입주일도 논의 가능합니다. j.park@deltonconsulting.com 또는 (416) 882-3300으로 직접 연락해 주세요.",
            "expressions": [
                {"expr": "at your earliest convenience", "meaning": "가능한 빨리, 편한 시간에"},
                {"expr": "be open to", "meaning": "~에 열려 있다, 받아들일 의향이 있다"},
                {"expr": "expire", "meaning": "만료되다"}
            ]
        }
    ]
},
"notice": {
    "title": "📋 Notice",
    "steps": [
        {
            "q_type": "purpose",
            "sentences": [
                "To: All Staff — Effective Monday, November 4, the company's remote work policy will be revised to require all employees to be present in the office a minimum of three days per week.",
                "This change applies to all departments and is being implemented to strengthen cross-team collaboration."
            ],
            "question": "What is the purpose of this notice?",
            "question_kr": "이 공지의 목적은 무엇인가?",
            "choices": [
                "(A) To announce the elimination of remote work",
                "(B) To inform staff of a change to the remote work policy",
                "(C) To request feedback on current working arrangements",
                "(D) To introduce a new project management system"
            ],
            "choices_kr": [
                "(A) 재택근무 폐지 발표",
                "(B) 재택근무 정책 변경 안내",
                "(C) 현재 근무 방식에 대한 피드백 요청",
                "(D) 새 프로젝트 관리 시스템 도입"
            ],
            "answer": 1,
            "kr": "전 직원에게 알립니다. 11월 4일 월요일부터 재택근무 정책이 개정되어 모든 직원은 주 최소 3일 사무실에 출근해야 합니다. 이 변경 사항은 전 부서에 적용되며 팀 간 협업 강화를 위해 시행됩니다.",
            "expressions": [
                {"expr": "effective", "meaning": "(날짜)부터 효력이 발생하는"},
                {"expr": "be revised to", "meaning": "~하도록 개정되다"},
                {"expr": "implement", "meaning": "시행하다, 실행하다"}
            ]
        },
        {
            "q_type": "detail",
            "sentences": [
                "Employees who require an exemption due to medical reasons or caregiving responsibilities may submit a formal request to the Human Resources Department.",
                "All exemption requests must be accompanied by supporting documentation and submitted no later than October 25.",
                "Managers are asked to confirm their team's weekly schedules by the end of each Friday to ensure adequate office capacity."
            ],
            "question": "By when must exemption requests be submitted?",
            "question_kr": "면제 신청은 언제까지 제출해야 하는가?",
            "choices": [
                "(A) By October 18",
                "(B) By October 25",
                "(C) By November 1",
                "(D) By November 4"
            ],
            "choices_kr": [
                "(A) 10월 18일까지",
                "(B) 10월 25일까지",
                "(C) 11월 1일까지",
                "(D) 11월 4일까지"
            ],
            "answer": 1,
            "kr": "의료적 이유나 돌봄 책임으로 면제가 필요한 직원은 인사부에 공식 신청서를 제출할 수 있습니다. 모든 면제 신청서는 지원 서류를 첨부하여 10월 25일까지 제출해야 합니다. 관리자는 적절한 사무실 수용을 위해 매주 금요일까지 팀 주간 일정을 확인해야 합니다.",
            "expressions": [
                {"expr": "exemption", "meaning": "면제"},
                {"expr": "be accompanied by", "meaning": "~을 첨부하다, ~와 함께하다"},
                {"expr": "adequate", "meaning": "적절한, 충분한"}
            ]
        },
        {
            "q_type": "inference",
            "sentences": [
                "Hot-desking will remain available for employees on their remote days, and all bookings must be made through the internal portal.",
                "Please note that the number of available desks has been reduced from 120 to 85 following last year's office renovation.",
                "Questions about the new policy may be directed to your department head or to HR at hr@company.com."
            ],
            "question": "What is implied about the office space?",
            "question_kr": "사무실 공간에 대해 추론할 수 있는 것은?",
            "choices": [
                "(A) It was recently expanded to accommodate more staff",
                "(B) It may not have enough desks for all staff on busy days",
                "(C) It is undergoing renovation during November",
                "(D) It will be replaced by a new facility next year"
            ],
            "choices_kr": [
                "(A) 더 많은 직원을 수용하기 위해 최근 확장됨",
                "(B) 바쁜 날에는 모든 직원을 위한 책상이 부족할 수 있음",
                "(C) 11월에 리노베이션 진행 중",
                "(D) 내년에 새 시설로 교체될 예정"
            ],
            "answer": 1,
            "kr": "핫데스킹은 재택근무일에도 이용 가능하며, 내부 포털을 통해 예약해야 합니다. 지난해 사무실 리노베이션 이후 이용 가능한 책상 수가 120개에서 85개로 줄었습니다. 새 정책에 대한 문의는 부서장 또는 hr@company.com으로 연락하세요.",
            "expressions": [
                {"expr": "hot-desking", "meaning": "공유 좌석제"},
                {"expr": "internal portal", "meaning": "내부 포털/시스템"},
                {"expr": "be directed to", "meaning": "~에게 문의하다"}
            ]
        }
    ]
},
"information": {
    "title": "ℹ️ Information",
    "steps": [
        {
            "q_type": "detail",
            "sentences": [
                "The Crestwood Public Library will be closed to the public from January 13 through January 27 for its annual systems upgrade.",
                "During this period, the library's online catalog and digital borrowing services will remain accessible through the library's website."
            ],
            "question": "According to the notice, what will remain available during the closure?",
            "question_kr": "공지에 따르면 폐관 기간 동안 무엇이 계속 이용 가능한가?",
            "choices": [
                "(A) In-person reference services",
                "(B) The physical book collection",
                "(C) Online catalog and digital borrowing",
                "(D) Meeting rooms for community use"
            ],
            "choices_kr": [
                "(A) 대면 참고 서비스",
                "(B) 실물 도서 컬렉션",
                "(C) 온라인 목록 및 디지털 대출",
                "(D) 지역 사회 회의실"
            ],
            "answer": 2,
            "kr": "Crestwood 공립 도서관은 연간 시스템 업그레이드를 위해 1월 13일부터 27일까지 휴관합니다. 이 기간 동안 도서관 온라인 목록과 디지털 대출 서비스는 도서관 웹사이트를 통해 계속 이용 가능합니다.",
            "expressions": [
                {"expr": "annual systems upgrade", "meaning": "연간 시스템 업그레이드"},
                {"expr": "remain accessible", "meaning": "계속 이용 가능하다"},
                {"expr": "digital borrowing services", "meaning": "디지털 대출 서비스"}
            ]
        },
        {
            "q_type": "not",
            "sentences": [
                "Patrons with items currently on loan will not be penalized for late returns during the closure period.",
                "All overdue fines will be automatically waived for books returned within two weeks of the library's reopening on January 28.",
                "Staff will be available by phone at (604) 551-7700 on weekdays between 9:00 A.M. and 4:00 P.M. to assist with account inquiries."
            ],
            "question": "Which of the following is NOT mentioned in the notice?",
            "question_kr": "공지에서 언급되지 않은 것은?",
            "choices": [
                "(A) A phone number for patron inquiries",
                "(B) That overdue fines will be waived",
                "(C) That the library will reopen on January 28",
                "(D) A list of new books added during the upgrade"
            ],
            "choices_kr": [
                "(A) 이용자 문의를 위한 전화번호",
                "(B) 연체료가 면제된다는 사실",
                "(C) 도서관이 1월 28일에 재개관한다는 사실",
                "(D) 업그레이드 중 추가된 신규 도서 목록"
            ],
            "answer": 3,
            "kr": "현재 대출 중인 항목이 있는 이용자는 휴관 기간 동안 연체에 대한 패널티를 받지 않습니다. 모든 연체료는 1월 28일 재개관 후 2주 이내에 반납된 도서에 대해 자동으로 면제됩니다. 직원은 평일 오전 9시~오후 4시에 (604) 551-7700으로 계정 문의를 도와드립니다.",
            "expressions": [
                {"expr": "be penalized for", "meaning": "~에 대해 불이익을 받다"},
                {"expr": "waive", "meaning": "면제하다, 포기하다"},
                {"expr": "overdue fines", "meaning": "연체료"}
            ]
        },
        {
            "q_type": "synonym",
            "sentences": [
                "The library would like to thank patrons for their understanding and patience during this necessary upgrade.",
                "The improvements will significantly enhance the speed and reliability of all library systems.",
                "We look forward to welcoming our community back and offering an even more streamlined experience when we reopen."
            ],
            "question": "The word 'streamlined' in the last sentence is closest in meaning to:",
            "question_kr": "마지막 문장의 'streamlined'와 의미가 가장 가까운 것은?",
            "choices": [
                "(A) complicated",
                "(B) efficient",
                "(C) expensive",
                "(D) traditional"
            ],
            "choices_kr": [
                "(A) 복잡한",
                "(B) 효율적인",
                "(C) 비싼",
                "(D) 전통적인"
            ],
            "answer": 1,
            "kr": "도서관은 이번 필수 업그레이드에 대한 이용자 여러분의 이해와 인내에 감사드립니다. 개선 사항은 모든 도서관 시스템의 속도와 안정성을 크게 향상시킬 것입니다. 재개관 시 더욱 효율적인 서비스로 지역 사회를 다시 맞이하기를 기대합니다.",
            "expressions": [
                {"expr": "streamlined", "meaning": "효율적인, 간소화된"},
                {"expr": "significantly enhance", "meaning": "크게 향상시키다"},
                {"expr": "look forward to -ing", "meaning": "~을 기대하다"}
            ]
        }
    ]
}
}

# ═══ 유틸 ═══
def pick_passage(cat):
    return PASSAGES[cat]

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
# PHASE: LOBBY
# ═══════════════════════════════════════
if st.session_state.p7_phase == "lobby":
    tsec = st.session_state.p7_tsec
    cat = st.session_state.p7_cat
    _p7_tsec = st.session_state.get("p7_tsec", 80)
    _p7_tc = st.session_state.get("p7_tsec_chosen", False)

    st.markdown('''<style>
    #MainMenu{visibility:hidden!important;}header[data-testid="stHeader"]{height:0!important;visibility:hidden!important;}
    div[data-testid="stToolbar"]{visibility:hidden!important;}.block-container{padding-top:0.2rem!important;}
    @keyframes p7float{0%,100%{transform:translateY(0);box-shadow:0 0 12px rgba(212,175,55,0.3);}50%{transform:translateY(-4px);box-shadow:0 0 25px rgba(212,175,55,0.7);}}
    button[kind="secondary"]{
        background:#0a0a14!important;border:1.5px solid #333!important;
        border-radius:10px!important;font-size:1.0rem!important;font-weight:600!important;
        padding:6px!important;color:#aaa!important;min-height:61px!important;
        animation:none!important;transform:none!important;box-shadow:none!important;
    }
    button[kind="secondary"] p{font-size:1.0rem!important;font-weight:600!important;color:#aaa!important;}
    button[data-testid="stBaseButton-primary"]{
        background:#0c0c00!important;border:2px solid #d4af37!important;
        border-left:4px solid #d4af37!important;
        color:#d4af37!important;font-size:1.0rem!important;font-weight:900!important;
        min-height:43px!important;animation:none!important;border-radius:12px!important;
    }
    button[data-testid="stBaseButton-primary"] p{color:#d4af37!important;font-size:1.1rem!important;font-weight:900!important;}
    </style>''', unsafe_allow_html=True)

    # 타이틀
    st.markdown('''<div style="text-align:center;padding:6px 0 4px 0;">
        <div style="font-size:1.2rem;font-weight:900;color:#d4af37;letter-spacing:3px;">📖 P7전장</div>
        <div style="font-size:0.7rem;color:#aaa;letter-spacing:2px;margin-top:2px;font-weight:600;">TOEIC Part 7 · 단 한 번의 실수 — 즉사</div>
    </div>''', unsafe_allow_html=True)



    # 시간 선택
    st.markdown('''<style>
    div[data-testid="stHorizontalBlock"] button[kind="secondary"]{
        min-height:46px!important;font-size:0.82rem!important;
    }
    div[data-testid="stHorizontalBlock"] button[kind="secondary"] p{
        font-size:0.82rem!important;
    }
    </style>''', unsafe_allow_html=True)
    st.markdown('''<div style="display:flex;align-items:flex-end;margin-bottom:0;">
        <div style="background:#0c0c1e;border:1.5px solid #9aa5b4;border-bottom:none;border-radius:8px 8px 0 0;padding:3px 12px;font-size:0.72rem;font-weight:900;color:#9aa5b4;">⏱ 시간 선택</div>
    </div>''', unsafe_allow_html=True)
    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        if st.button("🔥 60초", key="p7t60", use_container_width=True):
            st.session_state.p7_tsec=60; st.session_state.p7_tsec_chosen=True; st.rerun()
    with tc2:
        if st.button("⚡ 80초", key="p7t80", use_container_width=True):
            st.session_state.p7_tsec=80; st.session_state.p7_tsec_chosen=True; st.rerun()
    with tc3:
        if st.button("✅ 100초", key="p7t100", use_container_width=True):
            st.session_state.p7_tsec=100; st.session_state.p7_tsec_chosen=True; st.rerun()
    st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)

    # 지문 선택
    st.markdown('''<div style="display:flex;align-items:flex-end;margin-top:4px;margin-bottom:0;">
        <div style="background:#140008;border:1.5px solid #cc2244;border-bottom:none;border-radius:8px 8px 0 0;padding:3px 12px;font-size:0.72rem;font-weight:900;color:#cc2244;">⚔️ 지문 선택</div>
    </div>''', unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("📰 Article\n기사·보도", key="p7c1", use_container_width=True):
            st.session_state.p7_cat="article"; st.rerun()
    with b2:
        if st.button("✉️ Letter\n편지·서신", key="p7c2", use_container_width=True):
            st.session_state.p7_cat="letter"; st.rerun()
    b3, b4 = st.columns(2)
    with b3:
        if st.button("📋 Notice\n공지·안내", key="p7c3", use_container_width=True):
            st.session_state.p7_cat="notice"; st.rerun()
    with b4:
        if st.button("ℹ️ Info\n정보·안내문", key="p7c4", use_container_width=True):
            st.session_state.p7_cat="information"; st.rerun()
    st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)


    st.markdown('''<style>@keyframes warningPulse{0%,100%{color:#ff4466;text-shadow:0 0 8px rgba(255,68,102,0.8);}50%{color:#ff8888;text-shadow:0 0 20px rgba(255,68,102,1),0 0 40px rgba(255,0,50,0.6);}}</style>''', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;padding:6px 0 2px 0;"><span style="font-size:0.88rem;font-weight:900;color:#ff4466;">💀 생존 규칙: 오답 1개 즉사 · 시간초과 즉사</span></div>', unsafe_allow_html=True)

    # 전투 시작 버튼
    _ready = _p7_tc and cat and cat in PASSAGES
    if _ready:
        _cat_name = PASSAGES[cat]["title"]
        if st.button(f"▶ 전투 시작!", key="p7go", type="primary", use_container_width=True):
            st.session_state.p7_data = PASSAGES[cat]
            st.session_state.p7_step = 0
            st.session_state.p7_answers = []
            st.session_state.p7_started_at = time.time()
            st.session_state.p7_type_guessed = False
            st.session_state.p7_type_correct = None
            st.session_state.p7_analytics = {"step_times":[],"step_correct":[],"step_type_correct":[],"step_started_at":time.time()}
            st.session_state.p7_phase = "battle"
            st.rerun()
    else:
        st.markdown('<div style="background:#0a0a14;border:1px solid #222;border-radius:12px;padding:12px;text-align:center;color:#333;font-size:0.9rem;">시간 + 지문을 선택하면 시작!</div>', unsafe_allow_html=True)

    # 하단 네비
    st.markdown('<div style="height:1px;background:#1a1a2a;margin:8px 0;"></div>', unsafe_allow_html=True)
    nc1, nc2 = st.columns(2)
    with nc1:
        if st.button("🔥 오답전장", key="p7nav1", use_container_width=True):
            st.switch_page("pages/03_오답전장.py")
    with nc2:
        if st.button("🏠 홈", key="p7nav2", use_container_width=True):
            st.session_state._p7_just_left = True
            st.switch_page("main_hub.py")
    import streamlit.components.v1 as _cmp
    _p7_tsec_val = st.session_state.get("p7_tsec", 80)
    _p7_tc_val = st.session_state.get("p7_tsec_chosen", False)
    _p7_cat_val = st.session_state.get("p7_cat", None)
    _time_map = {"60": "🔥 60초", "80": "⚡ 80초", "100": "✅ 100초"}
    _cat_map = {"article": "📰 Article", "letter": "✉️ Letter", "notice": "📋 Notice", "information": "ℹ️ Info"}
    _sel_time = str(_p7_tsec_val) if _p7_tc_val else ""
    _sel_cat = _p7_cat_val or ""
    _cmp.html(f'''<script>
    (function(){{
        var selTime = "{_sel_time}";
        var selCat = "{_sel_cat}";
        var timeMap = {{"60":"🔥 60초","80":"⚡ 80초","100":"✅ 100초"}};
        var catMap = {{"article":"📰 Article","letter":"✉️ Letter","notice":"📋 Notice","information":"ℹ️ Info"}};
        function styleAllBtns(){{
            var doc=window.parent.document;
            var btns=doc.querySelectorAll('button[kind="secondary"]');
            btns.forEach(function(b){{
                var t=(b.textContent||"").trim().replace(/\s+/g," ");
                var isSelTime = selTime && t.indexOf(timeMap[selTime]&&timeMap[selTime].replace("🔥 ","").replace("⚡ ","").replace("✅ ",""))>-1;
                var isSelCat = selCat && catMap[selCat] && t.indexOf(catMap[selCat].replace("📰 ","").replace("✉️ ","").replace("📋 ","").replace("ℹ️ ",""))>-1;
                if(isSelTime||isSelCat){{
                    b.style.setProperty("background","#1a1400","important");
                    b.style.setProperty("border","2px solid #d4af37","important");
                    b.style.setProperty("color","#d4af37","important");
                    b.querySelectorAll("p").forEach(function(p){{p.style.setProperty("color","#d4af37","important");}});
                }} else {{
                    b.style.setProperty("animation","none","important");
                    b.style.setProperty("transform","none","important");
                    b.style.setProperty("box-shadow","none","important");
                }}
            }});
        }}
        setTimeout(styleAllBtns,100);setTimeout(styleAllBtns,400);setTimeout(styleAllBtns,900);
        setInterval(styleAllBtns,800);
    }})();
    </script>''', height=0)
    _cmp2 = _cmp
    _cmp2.html('''<script>
    (function(){
        function styleNavBtns(){
            var doc=window.parent.document;
            var rows=doc.querySelectorAll('[data-testid="stHorizontalBlock"]');
            if(!rows.length) return;
            var lastRow=rows[rows.length-1];
            var btns=lastRow.querySelectorAll('button');
            if(btns[0]){
                btns[0].style.setProperty('animation','none','important');
                btns[0].style.setProperty('border','1.5px solid rgba(255,255,255,0.5)','important');
                btns[0].style.setProperty('background','#0f0f1e','important');
                btns[0].style.setProperty('color','#bbb','important');
            }
            if(btns[1]){
                btns[1].style.setProperty('animation','none','important');
                btns[1].style.setProperty('border','1.5px solid rgba(255,255,255,0.5)','important');
                btns[1].style.setProperty('background','#0f0f1e','important');
                btns[1].style.setProperty('color','#bbb','important');
            }
        }
        setTimeout(styleNavBtns,150);setTimeout(styleNavBtns,500);setTimeout(styleNavBtns,1200);
        new MutationObserver(function(){setTimeout(styleNavBtns,100);}).observe(
            window.parent.document.body,{childList:true,subtree:true});
    })();
    </script>''', height=0)


# ═══════════════════════════════════════
# PHASE: BATTLE
# ═══════════════════════════════════════
elif st.session_state.p7_phase == "battle":
    # 전투에서만 상단 여백 줄이기
    st.markdown('<style>.block-container{padding-top:0.5rem!important;}</style>', unsafe_allow_html=True)
    data = st.session_state.p7_data
    step = st.session_state.p7_step  # 0, 1, 2
    steps = data["steps"]
    cur = steps[step]

    # 전투 전용 CSS - 상단 패딩 줄이기
    st.markdown("""<style>
    .block-container{padding-top:0.5rem!important;}
    </style>""", unsafe_allow_html=True)

    # autorefresh
    st_autorefresh(interval=1000, limit=st.session_state.p7_tsec+10, key="p7_timer")

    # 타이머 계산
    elapsed = time.time() - st.session_state.p7_started_at
    total = st.session_state.p7_tsec
    rem = max(0, total - int(elapsed))

    # 시간초과
    if rem <= 0:
        try: save_research_record(build_research_record("timeout"))
        except: pass
        st.session_state.p7_phase = "lost"; st.rerun()

    # 위기 단계
    pct = rem / total if total > 0 else 0
    if pct > 0.6: stage = "safe"
    elif pct > 0.3: stage = "warn"
    elif pct > 0.1: stage = "danger"
    else: stage = "critical"

    # 지문 테두리 색상 (10초 남으면 붉어짐)
    if rem <= 10:
        pass_border = "#ff2200"
        pass_bg = "linear-gradient(145deg,#1a0505,#2a0a0a)"
        pass_shadow = "0 0 20px rgba(255,0,0,0.4)"
    elif rem <= 20:
        pass_border = "#ff6600"
        pass_bg = "linear-gradient(145deg,#1a0f05,#2a1508)"
        pass_shadow = "0 0 15px rgba(255,100,0,0.3)"
    elif rem <= 30:
        pass_border = "#ffaa00"
        pass_bg = "linear-gradient(145deg,#1a1505,#2a1a08)"
        pass_shadow = "0 0 10px rgba(255,170,0,0.2)"
    else:
        pass_border = "#00aacc"
        pass_bg = "linear-gradient(145deg,#0a1520,#101a2a)"
        pass_shadow = "none"

    # HUD + 타이머 (바 안에 큰 숫자 + 위기감)
    bar_color = {"safe":"#44ff88","warn":"#ffcc00","danger":"#ff4444","critical":"#ff0000"}[stage]
    bar_glow = {"safe":"rgba(68,255,136,0.3)","warn":"rgba(255,204,0,0.4)","danger":"rgba(255,68,68,0.5)","critical":"rgba(255,0,0,0.7)"}[stage]
    shake_css = "animation:shake 0.3s infinite;" if stage=="critical" else "animation:shake 0.8s infinite;" if stage=="danger" else ""
    components.html(f"""
    <style>
    *{{margin:0;padding:0;}}body{{background:transparent;overflow:hidden;font-family:sans-serif;}}
    .hud-row{{display:flex;align-items:center;gap:6px;}}
    .hud-l{{font-size:1rem;font-weight:900;color:#44ffcc;white-space:nowrap;}}
    .hud-r{{font-size:0.95rem;font-weight:800;color:#ffcc00;white-space:nowrap;}}
    .timer-box{{flex:1;position:relative;height:38px;background:#0a0a1a;border-radius:19px;border:2px solid {bar_color};overflow:hidden;box-shadow:0 0 12px {bar_glow};{shake_css}}}
    .timer-fill{{height:100%;border-radius:19px;background:linear-gradient(90deg,{bar_color}88,{bar_color});transition:width 1s linear;}}
    .timer-num{{position:absolute;top:0;left:0;right:0;bottom:0;display:flex;align-items:center;justify-content:center;
        font-size:1.5rem;font-weight:900;color:#fff;text-shadow:0 0 8px {bar_color},0 0 16px {bar_color},0 2px 4px #000;letter-spacing:3px;}}
    @keyframes shake{{0%,100%{{transform:translateX(0)}}25%{{transform:translateX(-4px)}}75%{{transform:translateX(4px)}}}}
    </style>
    <div class="hud-row">
        <span class="hud-l">📖 {step+1}/3</span>
        <div class="timer-box" id="tbox">
            <div class="timer-fill" id="tf" style="width:{pct*100}%"></div>
            <div class="timer-num" id="tn">{rem}</div>
        </div>
        <span class="hud-r">✅{len([a for a in st.session_state.p7_answers if a])} ❌{len([a for a in st.session_state.p7_answers if not a])}</span>
    </div>
    <script>
    var r={rem},t={total};
    var tn=document.getElementById('tn'),tf=document.getElementById('tf'),tb=document.getElementById('tbox');
    setInterval(function(){{r--;if(r<0)r=0;tn.textContent=r;
    var p=r/t;tf.style.width=(p*100)+'%';
    var c=p>0.6?'#44ff88':p>0.3?'#ffcc00':p>0.1?'#ff4444':'#ff0000';
    var g=p>0.6?'rgba(68,255,136,0.3)':p>0.3?'rgba(255,204,0,0.4)':p>0.1?'rgba(255,68,68,0.5)':'rgba(255,0,0,0.7)';
    tb.style.borderColor=c;tb.style.boxShadow='0 0 12px '+g;
    tn.style.textShadow='0 0 8px '+c+',0 0 16px '+c+',0 2px 4px #000';
    tf.style.background='linear-gradient(90deg,'+c+'88,'+c+')';
    if(r<=10){{tb.style.animation='shake 0.3s infinite';tn.style.fontSize='1.8rem';}}
    else if(r<=20){{tb.style.animation='shake 0.8s infinite';tn.style.fontSize='1.6rem';}}
    else{{tb.style.animation='none';tn.style.fontSize='1.5rem';}}}},1000);
    </script>
    """, height=46)

    # 지문 (누적) - 공간 절약 패딩
    all_sents = []
    for i in range(step + 1):
        all_sents.extend(steps[i]["sentences"])
    new_start = len(all_sents) - len(cur["sentences"])

    # ─── q_type: analytics 기록용 (화면 표시 없음) ───
    q_type = cur.get("q_type", "detail")

    pass_html = '<div class="p7-sent">'
    for i, s in enumerate(all_sents):
        if i >= new_start:
            pass_html += f'<span class="p7-new">{s}</span> '
        else:
            pass_html += f'{s} '
    pass_html += '</div>'
    _p_border = "#ff2200" if rem<=10 else "#ff6600" if rem<=20 else "#ffaa00" if rem<=30 else "#d4af37"
    st.markdown(f'<div style="background:{pass_bg};border:1.5px solid {_p_border};border-left:4px solid {_p_border};border-radius:10px;padding:0.6rem 0.8rem 0.6rem 0.9rem;margin:0.2rem 0;box-shadow:{pass_shadow};transition:border-color 1s,background 1s;">{pass_html}</div>', unsafe_allow_html=True)

    # 질문 - [Q1] 형식 + 최소 패딩
    st.markdown(f'<div style="background:#10101e;border:1px solid #9aa5b4;border-radius:8px;padding:6px 10px;margin:0.3rem 0 0.5rem 0;"><span style="color:#9aa5b4;font-size:0.78rem;font-weight:900;">[Q{step+1}]</span> <span style="color:#e8e0cc;font-size:0.85rem;font-weight:700;">{cur["question"]}</span></div>', unsafe_allow_html=True)

    # 선택지 - 2x2 격자 (공간 절약)
    st.markdown("""<style>
    button[kind="primary"]{font-size:0.82rem!important;padding:2px 8px 2px 12px!important;min-height:32px!important;max-height:36px!important;border-radius:8px!important;font-weight:600!important;line-height:1.1!important;color:#e8e0cc!important;margin:2px 0!important;text-align:left!important;background:#0f0f1e!important;}
    button[kind="primary"] p{font-size:0.82rem!important;font-weight:600!important;line-height:1.1!important;white-space:nowrap!important;overflow:hidden!important;text-overflow:ellipsis!important;text-align:left!important;color:#e8e0cc!important;}
    </style>""", unsafe_allow_html=True)
    st.markdown("""<style>.stVerticalBlock{gap:0!important;}.stHorizontalBlock{gap:4px!important;}
    div[data-testid="stVerticalBlock"] > div:nth-child(1) button[kind="primary"]{background:#0f0f1e!important;border:1px solid #1a1a2a!important;border-left:4px solid #d4af37!important;}
    div[data-testid="stVerticalBlock"] > div:nth-child(2) button[kind="primary"]{background:#0f0f1e!important;border:1px solid #1a1a2a!important;border-left:4px solid #9aa5b4!important;}
    div[data-testid="stVerticalBlock"] > div:nth-child(3) button[kind="primary"]{background:#0f0f1e!important;border:1px solid #1a1a2a!important;border-left:4px solid #50c878!important;}
    div[data-testid="stVerticalBlock"] > div:nth-child(4) button[kind="primary"]{background:#0f0f1e!important;border:1px solid #1a1a2a!important;border-left:4px solid #4488cc!important;}</style>""", unsafe_allow_html=True)
    for i, ch in enumerate(cur["choices"]):
        if st.button(ch, key=f"p7ch{step}_{i}", type="primary", use_container_width=True):
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
            if not ok:
                try: save_research_record(build_research_record("lost"))
                except: pass
                st.session_state.p7_phase = "lost"; st.rerun()
            if step >= 2:
                try: save_research_record(build_research_record("victory"))
                except: pass
                st.session_state.p7_phase = "victory"; st.rerun()
            else:
                st.session_state.p7_step += 1
                st.rerun()

    components.html("""
    <script>
    function p7choiceColors(){
        const doc=window.parent.document;
        const btns=doc.querySelectorAll('button[kind="primary"]');
        const colors=[
            {bg:'#0f0f1e',bd:'1px solid #1a1a2a',bl:'4px solid #d4af37'},
            {bg:'#0f0f1e',bd:'1px solid #1a1a2a',bl:'4px solid #9aa5b4'},
            {bg:'#0f0f1e',bd:'1px solid #1a1a2a',bl:'4px solid #50c878'},
            {bg:'#0f0f1e',bd:'1px solid #1a1a2a',bl:'4px solid #4488cc'}
        ];
        let ci=0;
        btns.forEach(btn=>{
            const t=btn.textContent||'';
            if(t.match(/\(A\)|\(B\)|\(C\)|\(D\)/)){
                const c=colors[ci%4];
                btn.style.background=c.bg;
                btn.style.setProperty('background', c.bg, 'important');
                btn.style.setProperty('border', c.bd, 'important');
                btn.style.setProperty('border-left', c.bl||c.bd, 'important');
                btn.style.setProperty('color', '#e8e0cc', 'important');
                ci++;
            }
        });
    }
    setTimeout(p7choiceColors,100);setTimeout(p7choiceColors,300);setTimeout(p7choiceColors,600);setTimeout(p7choiceColors,1000);setInterval(p7choiceColors,500);
    </script>
    """, height=0)

# ═══════════════════════════════════════
# PHASE: VICTORY
# ═══════════════════════════════════════
elif st.session_state.p7_phase == "victory":
    _answers = st.session_state.p7_answers
    _ok = len([a for a in _answers if a])
    st.markdown('<style>.stApp{background:#08080f!important;}</style>', unsafe_allow_html=True)
    st.markdown('''<div style="text-align:center;padding:1.2rem 0 0.5rem 0;">
        <div style="font-size:0.9rem;letter-spacing:4px;opacity:0.6;margin-bottom:6px;">💎 ⭐ ✨ 🏆 🌟 💫 💎</div>
        <div style="font-size:2.8rem;font-weight:900;color:#ffd700;letter-spacing:3px;text-shadow:0 0 30px #ffd700,0 0 60px #ff8800;">CLEAR!</div>
        <div style="font-size:0.9rem;color:#d4af37;font-weight:600;letter-spacing:2px;margin-top:4px;">독해 전투 클리어!</div>
    </div>''', unsafe_allow_html=True)
    st.markdown(f'''<div style="background:#0c0c1e;border:1.5px solid #d4af37;border-left:4px solid #d4af37;border-radius:12px;padding:10px;text-align:center;margin:8px 0;">
        <div style="font-size:0.75rem;color:#9aa5b4;margin-bottom:2px;">이번 결과</div>
        <div style="font-size:1.5rem;font-weight:900;color:#d4af37;">✅ {_ok} / 3</div>
    </div>''', unsafe_allow_html=True)
    st.markdown('''<div style="background:#0a0800;border:1px solid #d4af37;border-radius:10px;padding:8px;text-align:center;margin-bottom:10px;">
        <div style="font-size:0.82rem;color:#d4af37;font-weight:700;">⚡ 3번 반복하면 장기기억 전환율 3배!</div>
        <div style="font-size:0.72rem;color:#555;margin-top:2px;">지금 브리핑에서 핵심표현 무기로 장착하라!</div>
    </div>''', unsafe_allow_html=True)
    st.markdown('''<style>
    button[data-testid="stBaseButton-primary"]{
        background:#0c0c00!important;border:2px solid #d4af37!important;
        border-left:4px solid #d4af37!important;
        color:#d4af37!important;font-size:1.1rem!important;font-weight:900!important;
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
                btns[0].style.setProperty('border-left','4px solid #d4af37','important');
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
    st.markdown('''<div style="text-align:center;padding:1rem 0 0.4rem 0;">
        <div style="font-size:0.9rem;letter-spacing:3px;opacity:0.5;margin-bottom:6px;">💀 ☠️ 🪦 💔 ⚰️ 🩸 💀</div>
        <div style="font-size:2.6rem;font-weight:900;color:#cc0000;letter-spacing:2px;">💀 GAME OVER</div>
        <div style="font-size:0.8rem;color:#660000;letter-spacing:2px;margin-top:3px;">넌 오늘도 졌다...</div>
    </div>''', unsafe_allow_html=True)
    st.markdown(f'''<div style="background:#0c0008;border:1.5px solid #cc2244;border-left:4px solid #cc2244;border-radius:12px;padding:10px;text-align:center;margin:6px 0;">
        <div style="font-size:0.72rem;color:#9aa5b4;margin-bottom:2px;">처참한 결과</div>
        <div style="font-size:1.5rem;font-weight:900;color:#cc2244;">💀 {_ok} / 3</div>
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
    st.markdown('''<style>
    .block-container{padding-top:0.5rem!important;margin-top:-1rem!important;padding-bottom:0!important;}
    div[data-testid="stVerticalBlock"]{gap:0.3rem!important;}
    .element-container{margin-bottom:0!important;}
        div[data-testid="stAppViewBlockContainer"]{padding-top:0.2rem!important;}
    </style>''', unsafe_allow_html=True)
    data = st.session_state.p7_data
    steps = data["steps"]
    answers = st.session_state.p7_answers
    was_victory = len(answers) == 3 and all(answers)

    v_cls = "p7-ban-v" if was_victory else "p7-ban-l"
    v_label = "CLEAR!" if was_victory else "YOU LOST"
    ok_cnt = len([a for a in answers if a])

    if "p7_br_idx" not in st.session_state: st.session_state.p7_br_idx = 0
    bi = st.session_state.p7_br_idx
    num_steps = min(len(steps), len(answers))
    if num_steps == 0: num_steps = 1
    if bi >= num_steps: bi = num_steps - 1

    # query_params 버튼 처리
    _qp = st.query_params.get("p7action", "")
    if _qp == "prev" and bi > 0:
        st.session_state.p7_br_idx = bi - 1
        st.query_params.clear()
        st.rerun()
    elif _qp == "next" and bi < num_steps - 1:
        st.session_state.p7_br_idx = bi + 1
        st.query_params.clear()
        st.rerun()
    elif _qp == "retry":
        for k in D: st.session_state[k] = D[k]
        st.query_params.clear()
        st.rerun()
    elif _qp == "store":
        st.query_params.clear()
        st.switch_page("pages/03_오답전장.py")
    elif _qp == "lobby":
        for k in D: st.session_state[k] = D[k]
        st.query_params.clear()
        st.switch_page("main_hub.py")

    # 오답전장/본부귀환 골드 스타일
    st.markdown("""<style>
    button[kind="secondary"]{
        border:2px solid #FFD700!important;
        color:#ffffff!important;
    }
    button[kind="secondary"] p{
        color:#ffffff!important;
    }
    </style>""", unsafe_allow_html=True)
    # CT expander 글자 흰색
    st.markdown("""<style>
    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary span,
    div[data-testid="stExpander"] details summary{
        color:rgba(255,255,255,0.4)!important;
        font-weight:400!important;
        font-size:0.8rem!important;
    }
    div[data-testid="stExpander"]{
        transform:scale(0.9)!important;
        transform-origin:top left!important;
    }
    </style>""", unsafe_allow_html=True)
    # 브리핑 전용 버튼 CSS 강제 적용
    st.markdown("""<style>
    div[data-testid="stVerticalBlockBorderWrapper"] button[kind="primary"] p,
    div[data-testid="stVerticalBlock"] button[kind="primary"] p{
        text-align:center!important;
        color:#ffdd44!important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] button[kind="secondary"] p,
    div[data-testid="stVerticalBlock"] button[kind="secondary"] p{
        text-align:center!important;
        color:#44ffcc!important;
    }
    </style>""", unsafe_allow_html=True)
    st.markdown("""<style>
    div[data-testid="stVerticalBlockBorderWrapper"] button[kind],
    div[data-testid="stVerticalBlock"] button[kind]{
        padding:1px 2px!important;
        min-height:36px!important;
        max-height:36px!important;
        font-size:0.7rem!important;
        line-height:1!important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] button[kind] p,
    div[data-testid="stVerticalBlock"] button[kind] p{
        font-size:0.7rem!important;
        line-height:1!important;
        margin:0!important;
        padding:0!important;
    }
    </style>""", unsafe_allow_html=True)
    st.markdown('''<style>
    .block-container{padding-top:0.1rem!important;}
    div[data-testid="stHorizontalBlock"] button{
        border:2px solid #4488ff!important;
        border-radius:8px!important;
        background:#0a1a2e!important;
        color:#4488ff!important;
        font-size:1.1rem!important;
        font-weight:900!important;
    }
    div[data-testid="stHorizontalBlock"] button p{
        color:#4488ff!important;
        font-size:1.1rem!important;
        font-weight:900!important;
    }
    </style>''', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;font-size:1.2rem;font-weight:900;color:#4488cc;letter-spacing:3px;padding:14px 0 10px 0;">📖 P7 브리핑</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="p7-ban {v_cls}" style="margin-top:4px!important;margin-bottom:6px!important;padding:6px 10px!important;">{data["title"]} — {v_label} ✅{ok_cnt} ❌{len(answers)-ok_cnt}</div>', unsafe_allow_html=True)

    # ─── 탭 [1][2][3] ───
    st.markdown('''<style>
    .tab-sel{background:#0a1628!important;border:2px solid #4488cc!important;color:#4488cc!important;border-radius:8px!important;padding:4px!important;text-align:center!important;font-size:1rem!important;font-weight:900!important;cursor:default!important;display:block!important;min-height:36px!important;max-height:36px!important;line-height:1.8!important;}
    div[data-testid="stHorizontalBlock"] button{border:1px solid #1a2a3a!important;border-radius:8px!important;background:#060c14!important;color:#3a4a5a!important;font-size:1rem!important;font-weight:700!important;min-height:36px!important;max-height:36px!important;padding:4px!important;}
    div[data-testid="stHorizontalBlock"] button p{color:#3a4a5a!important;font-size:1rem!important;font-weight:700!important;}
    div[data-testid="stHorizontalBlock"] button:hover{border-color:#4488cc!important;}
    div[data-testid="stHorizontalBlock"] button:hover p{color:#4488cc!important;}
    button[kind="secondary"]{border:1px solid #1a2a3a!important;color:#4a5a6a!important;background:#060c14!important;}
    button[kind="secondary"] p{color:#4a5a6a!important;}
    button[kind="primary"]{border:1px solid #4488cc!important;color:#4488cc!important;background:#060c14!important;}
    button[kind="primary"] p{color:#4488cc!important;}
    </style>''', unsafe_allow_html=True)
    tab_cols = st.columns(num_steps)
    for ti in range(num_steps):
        with tab_cols[ti]:
            if ti == bi:
                st.markdown(f'<div class="tab-sel">{ti+1}</div>', unsafe_allow_html=True)
            else:
                if st.button(str(ti+1), key=f"br_tab_{ti}", use_container_width=True):
                    st.session_state.p7_br_idx = ti; st.rerun()


    # ─── CT 피드백 + 데이터 패널 ───
    _an = st.session_state.get("p7_analytics", {})
    _times = _an.get("step_times", [])
    _corrects = _an.get("step_correct", [])
    num_steps = min(len(steps), len(answers))

    # CT 알고리즘 안내 (전체 결과 요약 - 한 번만 표시)
    if bi == 0:
        _ct_html = '<div style="background:#030a12;border:2px solid rgba(68,255,204,0.4);border-radius:14px;padding:0.8rem 1rem;margin:0.3rem 0;">'
        _ct_html += '<div style="color:#44ffcc;font-size:0.9rem;font-weight:900;margin-bottom:0.3rem;">🧠 내 전투 분석</div>'

        ct_step_labels = ["🎯 분해", "🔍 패턴인식", "✂️ 추상화"]
        ct_type_map = {"purpose":"주제/목적","detail":"세부사항","inference":"추론","not":"NOT문제","synonym":"동의어"}
        for si in range(num_steps):
            _c = _corrects[si] if si < len(_corrects) else None
            _t = f"{_times[si]}초" if si < len(_times) else "-"
            _sym = "✅" if _c else ("❌" if _c is False else "⬜")
            _color = "#44ff88" if _c else ("#ff4444" if _c is False else "#888")
            _qtype = steps[si].get("q_type","detail")
            _type_kr = ct_type_map.get(_qtype, _qtype)
            _ct_html += f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.3rem 0;border-bottom:1px solid rgba(255,255,255,0.07);">'
            _ct_html += f'<span style="color:{_color};font-size:0.85rem;font-weight:700;">{_sym} Step {si+1} · {ct_step_labels[si]} <span style="color:#aaa;font-size:0.75rem;">[{_type_kr}]</span></span>'
            _ct_html += f'<span style="color:#aaa;font-size:0.8rem;">⏱ {_t}</span></div>'

        # 4단계: 알고리즘화 메시지
        _all_ok = all(_corrects[:num_steps]) if _corrects else False
        if _all_ok:
            _algo_msg = "🎯 완벽! 이 흐름을 기억해!"
            _algo_color = "#44ffcc"
        elif len(_corrects) > 0 and _corrects[0]:
            _algo_msg = "⚡ 분해 OK. 패턴인식·추상화 더 연습!"
            _algo_color = "#ffcc44"
        else:
            _algo_msg = "💡 Step1부터 다시: 2문장→핵심단어→주제가설"
            _algo_color = "#ff8844"
        _ct_html += f'<div style="color:{_algo_color};font-size:0.85rem;font-weight:900;margin-top:0.3rem;padding-top:0.3rem;">📌 {_algo_msg}</div>'
        _ct_html += '</div>'
        with st.expander("🧠 전투 분석", expanded=False):
            st.markdown(_ct_html, unsafe_allow_html=True)

    # 현재 스텝 데이터
    s = steps[bi]
    ok = answers[bi] if bi < len(answers) else False
    sym = "✅" if ok else "❌"
    correct_choice = s["choices"][s["answer"]]

    # ─── 문제 + 정답 카드 ───
    import re as _re3
    _mark_style = "color:#008855;font-weight:900;text-decoration:underline;text-underline-offset:3px;"
    _exprs_list = [e.get("expr","") for e in s.get("expressions", []) if e.get("expr")]
    q_kr = s.get("question_kr", "")
    c_kr = s.get("choices_kr", [])
    answer_kr = c_kr[s["answer"]] if c_kr and s["answer"] < len(c_kr) else ""

    st.markdown(f'''<div style="background:#020408;border:1px solid #1a4a2a;border-left:2px solid #2a7a4a;border-radius:8px;padding:6px 10px;margin-bottom:12px;">
        <div style="font-size:0.85rem;font-weight:700;color:#888;margin-bottom:2px;">[Q{bi+1}] {s["question"]}</div>
        <div style="font-size:0.9rem;font-weight:900;color:#4488cc;">{sym} {correct_choice}</div>
        ''' + (f'<div style="font-size:0.85rem;color:#88dd88;margin-top:2px;">{answer_kr}</div>' if answer_kr else "") + '''
    </div>''', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.85rem;font-weight:900;text-align:center;margin:10px 0;padding:8px 12px;background:#0a0800;border:1.5px solid #ffd700;border-radius:8px;color:#ffd700;">💾 이 문장 저장 → 오답전장 반복 → 실력 UP!</div>', unsafe_allow_html=True)

    kr_full = s.get("kr", "")
    kr_sents = [x.strip() for x in kr_full.replace("!","!|").replace("?","?|").replace(".",".|").split("|") if x.strip()]

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
        if is_saved:
            st.markdown(f'''<div style="background:#0a0e1a;border:1px solid #2a3a5a;border-left:3px solid #4488cc;border-radius:12px;padding:12px 14px;margin-bottom:6px;">
                <div style="font-size:1.0rem;font-weight:700;color:#e8eef8;line-height:1.7;">{_hl}</div>
                <div style="font-size:0.85rem;color:#c0ccd8;margin-top:4px;">{sent_kr}</div>
                <div style="text-align:right;margin-top:6px;font-size:0.9rem;color:#4488cc;font-weight:900;">💾 저장완료!</div>
            </div>''', unsafe_allow_html=True)
        else:
            save_btn_html = f'''<div style="background:#0a0e1a;border:1px solid #1a2a3a;border-left:3px solid #4488cc;border-radius:12px;padding:12px 14px;margin-bottom:2px;background-image:repeating-linear-gradient(transparent,transparent 27px,#e8e0c8 27px,#e8e0c8 28px);background-position:0 12px;">
                <div style="font-size:1.0rem;font-weight:700;color:#ffffff;line-height:1.8;">{_hl}</div>
                <div style="font-size:0.85rem;color:#c0ccd8;margin-top:4px;">{sent_kr}</div>
            </div>'''
            st.markdown(save_btn_html, unsafe_allow_html=True)
            _sv_key = f"br_sv_{bi}_{si}"
            if st.button("💾 저장!", key=_sv_key, use_container_width=False):
                sent_data = dict(s)
                sent_data["sentences"] = [sent]
                sent_data["kr"] = sent_kr
                save_expressions(s.get("expressions", []), step_data=sent_data)
                st.session_state[sent_key] = True
                st.rerun()
            st.markdown(f'''<style>
            div[data-testid="stBaseButton-secondary"] button{{display:none!important;height:0!important;min-height:0!important;padding:0!important;margin:0!important;border:none!important;}}
            div[data-testid="stBaseButton-secondary"]{{height:0!important;min-height:0!important;padding:0!important;margin:0!important;overflow:hidden!important;}}
            </style>''', unsafe_allow_html=True)

    st.markdown('''<style>
    div[data-testid="stHorizontalBlock"]:last-of-type button{
        background:#000000!important;
        border:1.5px solid rgba(255,255,255,0.5)!important;
        border-radius:12px!important;
        color:rgba(255,255,255,0.5)!important;
        font-size:0.85rem!important;
        font-weight:500!important;
    }
    div[data-testid="stHorizontalBlock"]:last-of-type button p{
        color:rgba(255,255,255,0.5)!important;
        font-size:0.85rem!important;
    }
    </style>''', unsafe_allow_html=True)
    bc3, bc4 = st.columns(2)
    with bc3:
        if st.button("🔥 오답전장", key="p7store", use_container_width=True):
            st.switch_page("pages/03_오답전장.py")
    with bc4:
        if st.button("🏠 홈", key="p7lobby", use_container_width=True):
            for k in D: st.session_state[k] = D[k]
            st.switch_page("main_hub.py")






