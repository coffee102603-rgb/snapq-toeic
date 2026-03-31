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
_inject_css()

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

/* P7 지문 카드 */
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
PASSAGES = {'article': [{'title': '📢 SIGNAL', 'steps': [{'q_type': 'purpose', 'sentences': ['Greenfield Bakery is now hiring part-time staff for its downtown location.', 'Applicants must be available on weekends and have at least six months of customer service experience.'], 'question': 'What is the purpose of this advertisement?', 'question_kr': '이 광고의 목적은 무엇인가?', 'choices': ['(A) To promote a new bakery product', '(B) To recruit part-time workers', '(C) To announce a store relocation', '(D) To offer baking classes'], 'choices_kr': ['(A) 새 베이커리 제품 홍보', '(B) 파트타임 직원 채용', '(C) 매장 이전 안내', '(D) 베이킹 강좌 제공'], 'answer': 1, 'kr': 'Greenfield Bakery는 시내 지점에서 파트타임 직원을 채용 중이다. 지원자는 주말 근무가 가능해야 하며 최소 6개월의 고객 서비스 경험이 있어야 한다.', 'expressions': [{'expr': 'part-time staff', 'meaning': '파트타임 직원'}, {'expr': 'customer service experience', 'meaning': '고객 서비스 경험'}, {'expr': 'be available on weekends', 'meaning': '주말에 근무 가능하다'}]}, {'q_type': 'detail', 'sentences': ['The position offers a starting wage of $15 per hour with opportunities for advancement.', 'Interested candidates should submit a résumé and cover letter to hr@greenfieldbakery.com by Friday, March 15.'], 'question': 'By when must applications be submitted?', 'question_kr': '지원서는 언제까지 제출해야 하는가?', 'choices': ['(A) By Monday, March 11', '(B) By Wednesday, March 13', '(C) By Friday, March 15', '(D) By Sunday, March 17'], 'choices_kr': ['(A) 3월 11일 월요일까지', '(B) 3월 13일 수요일까지', '(C) 3월 15일 금요일까지', '(D) 3월 17일 일요일까지'], 'answer': 2, 'kr': '해당 직책은 시간당 $15의 시작 임금과 승진 기회를 제공한다. 관심 있는 지원자는 3월 15일 금요일까지 hr@greenfieldbakery.com으로 이력서와 자기소개서를 제출해야 한다.', 'expressions': [{'expr': 'starting wage', 'meaning': '초봉, 시작 임금'}, {'expr': 'submit a résumé', 'meaning': '이력서를 제출하다'}, {'expr': 'opportunities for advancement', 'meaning': '승진 기회'}]}, {'q_type': 'inference', 'sentences': ['Greenfield Bakery has three locations across the city and is known for its award-winning sourdough bread.', 'The downtown branch sees the highest customer traffic and requires additional support during peak hours.'], 'question': 'What is suggested about the downtown location?', 'question_kr': '시내 지점에 대해 추론할 수 있는 것은?', 'choices': ['(A) It opened recently', '(B) It is the busiest of the three branches', '(C) It sells the most sourdough bread', '(D) It is the largest location'], 'choices_kr': ['(A) 최근에 개업했다', '(B) 세 지점 중 가장 바쁘다', '(C) 사워도우 빵이 가장 많이 팔린다', '(D) 가장 큰 지점이다'], 'answer': 1, 'kr': 'Greenfield Bakery는 시내 전역에 3개 지점이 있으며 수상 경력의 사워도우 빵으로 유명하다. 시내 지점은 고객 방문이 가장 많아 피크 시간대에 추가 지원이 필요하다.', 'expressions': [{'expr': 'customer traffic', 'meaning': '고객 방문량'}, {'expr': 'peak hours', 'meaning': '피크 시간대, 바쁜 시간'}, {'expr': 'award-winning', 'meaning': '수상 경력이 있는'}]}]}, {'title': '📢 SIGNAL', 'steps': [{'q_type': 'purpose', 'sentences': ['TechMart is offering a 30% discount on all laptops and tablets this weekend only.', 'The sale runs from Saturday, June 8, through Sunday, June 9, at all participating stores.'], 'question': 'What is the main purpose of this notice?', 'question_kr': '이 공지의 주요 목적은 무엇인가?', 'choices': ['(A) To announce the opening of a new store', '(B) To inform customers of a weekend sale', '(C) To introduce a new product line', '(D) To notify staff of policy changes'], 'choices_kr': ['(A) 새 매장 개업 안내', '(B) 주말 할인 행사 안내', '(C) 새 제품 라인 소개', '(D) 직원에게 정책 변경 통보'], 'answer': 1, 'kr': 'TechMart는 이번 주말에만 모든 노트북과 태블릿을 30% 할인 판매한다. 세일은 6월 8일 토요일부터 6월 9일 일요일까지 모든 참여 매장에서 진행된다.', 'expressions': [{'expr': 'participating stores', 'meaning': '참여 매장'}, {'expr': 'runs from ~ through ~', 'meaning': '~부터 ~까지 진행되다'}, {'expr': 'this weekend only', 'meaning': '이번 주말에만'}]}, {'q_type': 'detail', 'sentences': ['Customers who spend over $500 will receive a free carrying case.', 'The discount cannot be combined with any other offers, and all sales are final.'], 'question': 'What will customers receive if they spend more than $500?', 'question_kr': '$500 이상 구매 시 고객이 받는 것은?', 'choices': ['(A) An additional 10% discount', '(B) A free carrying case', '(C) A store gift card', '(D) Free delivery service'], 'choices_kr': ['(A) 추가 10% 할인', '(B) 무료 케이스', '(C) 매장 상품권', '(D) 무료 배송 서비스'], 'answer': 1, 'kr': '$500 이상 구매 고객은 무료 케이스를 받는다. 할인은 다른 혜택과 중복 적용이 불가하며 모든 판매는 환불이 되지 않는다.', 'expressions': [{'expr': 'cannot be combined with', 'meaning': '~와 중복 적용 불가'}, {'expr': 'all sales are final', 'meaning': '모든 판매는 최종적이다(환불 불가)'}, {'expr': 'carrying case', 'meaning': '휴대용 케이스'}]}, {'q_type': 'not', 'sentences': ['TechMart accepts cash, credit cards, and mobile payments.', 'Store hours during the sale will be extended to 10 P.M. on both days.', 'Online purchases are not eligible for the weekend discount.'], 'question': 'Which is NOT mentioned about the TechMart sale?', 'question_kr': 'TechMart 세일에 대해 언급되지 않은 것은?', 'choices': ['(A) Accepted payment methods', '(B) Extended store hours', '(C) Staff working during the sale', '(D) Online purchase restrictions'], 'choices_kr': ['(A) 허용되는 결제 방법', '(B) 연장된 영업시간', '(C) 세일 기간 중 근무 직원', '(D) 온라인 구매 제한'], 'answer': 2, 'kr': 'TechMart는 현금, 신용카드, 모바일 결제를 받는다. 세일 기간 동안 매장 영업시간은 양일 모두 오후 10시까지 연장된다. 온라인 구매는 주말 할인 대상에서 제외된다.', 'expressions': [{'expr': 'are not eligible for', 'meaning': '~의 자격이 없다, 해당되지 않는다'}, {'expr': 'extended hours', 'meaning': '연장된 영업시간'}, {'expr': 'mobile payments', 'meaning': '모바일 결제'}]}]}, {'title': '📢 SIGNAL', 'steps': [{'q_type': 'purpose', 'sentences': ['The parking garage on Level B2 will be closed for maintenance from Monday, April 3, to Friday, April 7.', 'During this time, employees are encouraged to use the surface lot on Cedar Street.'], 'question': 'What is the purpose of this notice?', 'question_kr': '이 공지의 목적은 무엇인가?', 'choices': ['(A) To announce the opening of a new parking lot', '(B) To inform employees of a temporary parking closure', '(C) To update parking rates for employees', '(D) To introduce a new parking policy'], 'choices_kr': ['(A) 새 주차장 개장 안내', '(B) 임시 주차장 폐쇄 안내', '(C) 직원 주차 요금 변경 안내', '(D) 새 주차 정책 소개'], 'answer': 1, 'kr': 'B2층 주차장은 4월 3일 월요일부터 4월 7일 금요일까지 유지보수를 위해 폐쇄된다. 이 기간 동안 직원들은 Cedar Street의 지상 주차장을 이용하도록 권장된다.', 'expressions': [{'expr': 'closed for maintenance', 'meaning': '유지보수를 위해 폐쇄된'}, {'expr': 'are encouraged to', 'meaning': '~하도록 권장된다'}, {'expr': 'surface lot', 'meaning': '지상 주차장'}]}, {'q_type': 'detail', 'sentences': ['Temporary parking passes for Cedar Street can be collected from the reception desk starting Monday morning.', 'Employees must display the pass on their dashboard at all times while parked.'], 'question': 'Where can employees get a temporary parking pass?', 'question_kr': '직원들은 임시 주차권을 어디서 받을 수 있는가?', 'choices': ['(A) At the security office', '(B) At the reception desk', '(C) At the Cedar Street entrance', '(D) At the human resources department'], 'choices_kr': ['(A) 보안 사무실', '(B) 안내 데스크', '(C) Cedar Street 입구', '(D) 인사부서'], 'answer': 1, 'kr': 'Cedar Street 임시 주차권은 월요일 아침부터 안내 데스크에서 받을 수 있다. 직원들은 주차 중에는 항상 대시보드에 주차권을 표시해야 한다.', 'expressions': [{'expr': 'display the pass', 'meaning': '주차권을 표시하다'}, {'expr': 'at all times', 'meaning': '항상'}, {'expr': 'be collected from', 'meaning': '~에서 받다, 수령하다'}]}, {'q_type': 'inference', 'sentences': ['The maintenance work includes resurfacing the floor and upgrading the lighting system.', 'Management apologizes for the inconvenience and thanks employees for their cooperation during this period.'], 'question': 'What is implied about the parking garage?', 'question_kr': '주차장에 대해 추론할 수 있는 것은?', 'choices': ['(A) It will be permanently closed after repairs', '(B) It will have new features after the maintenance', '(C) It has never been repaired before', '(D) It is located on the ground floor'], 'choices_kr': ['(A) 수리 후 영구 폐쇄될 것이다', '(B) 유지보수 후 새로운 기능이 추가될 것이다', '(C) 이전에 수리된 적이 없다', '(D) 지상층에 위치해 있다'], 'answer': 1, 'kr': '유지보수 작업에는 바닥 재포장과 조명 시스템 업그레이드가 포함된다. 경영진은 불편을 드려 사과드리며 이 기간 동안 협조해 주신 직원들에게 감사드린다.', 'expressions': [{'expr': 'resurfacing the floor', 'meaning': '바닥을 재포장하다'}, {'expr': 'upgrading the lighting system', 'meaning': '조명 시스템을 업그레이드하다'}, {'expr': 'apologizes for the inconvenience', 'meaning': '불편에 대해 사과하다'}]}]}, {'title': '📢 SIGNAL', 'steps': [{'q_type': 'purpose', 'sentences': ['Riverside Grill is pleased to announce its new lunch special, available Monday through Friday from 11 A.M. to 2 P.M.', 'The special includes a main dish, soup, and a soft drink for just $12.'], 'question': 'What is being advertised?', 'question_kr': '무엇이 광고되고 있는가?', 'choices': ['(A) A new restaurant opening', '(B) A discounted lunch menu', '(C) A weekend brunch event', '(D) A cooking competition'], 'choices_kr': ['(A) 새 레스토랑 개업', '(B) 할인 점심 메뉴', '(C) 주말 브런치 행사', '(D) 요리 대회'], 'answer': 1, 'kr': 'Riverside Grill은 월요일부터 금요일 오전 11시부터 오후 2시까지 이용 가능한 새로운 점심 특선을 발표한다. 특선에는 메인 요리, 수프, 음료가 단 $12에 포함된다.', 'expressions': [{'expr': 'lunch special', 'meaning': '점심 특선'}, {'expr': 'is pleased to announce', 'meaning': '기쁘게 발표하다'}, {'expr': 'main dish', 'meaning': '주요리, 메인 요리'}]}, {'q_type': 'detail', 'sentences': ['Customers can choose from five rotating main dishes each week, including grilled salmon, pasta, and steak.', 'Reservations are recommended but not required for groups of fewer than six people.'], 'question': 'According to the advertisement, what is true about reservations?', 'question_kr': '광고에 따르면 예약에 대한 사실은?', 'choices': ['(A) They are required for all customers', '(B) They are not necessary for small groups', '(C) They must be made one week in advance', '(D) They are only available online'], 'choices_kr': ['(A) 모든 고객에게 필수이다', '(B) 소규모 그룹에는 필요 없다', '(C) 1주일 전에 해야 한다', '(D) 온라인으로만 가능하다'], 'answer': 1, 'kr': '고객은 매주 그릴 연어, 파스타, 스테이크를 포함한 5가지 순환 메인 요리 중에서 선택할 수 있다. 6인 미만 그룹에는 예약이 권장되나 필수는 아니다.', 'expressions': [{'expr': 'rotating dishes', 'meaning': '순환 메뉴'}, {'expr': 'reservations are recommended', 'meaning': '예약을 권장한다'}, {'expr': 'not required', 'meaning': '필수가 아니다'}]}, {'q_type': 'inference', 'sentences': ['Riverside Grill has been serving the downtown community for over fifteen years.', 'The new lunch special is designed to attract nearby office workers looking for a quick and affordable meal.'], 'question': 'Who is most likely the target customer for this advertisement?', 'question_kr': '이 광고의 주요 타겟 고객은 누구일 가능성이 가장 높은가?', 'choices': ['(A) Tourists visiting the area', '(B) Office workers near the restaurant', '(C) Students from a local university', '(D) Families looking for weekend dining'], 'choices_kr': ['(A) 지역을 방문하는 관광객', '(B) 레스토랑 근처 사무직 직원', '(C) 지역 대학교 학생', '(D) 주말 외식을 원하는 가족'], 'answer': 1, 'kr': 'Riverside Grill은 15년 이상 시내 지역 주민들에게 서비스를 제공해 왔다. 새로운 점심 특선은 빠르고 저렴한 식사를 원하는 인근 사무직 직원들을 유치하기 위해 기획되었다.', 'expressions': [{'expr': 'attract nearby office workers', 'meaning': '인근 사무직 직원을 유치하다'}, {'expr': 'affordable meal', 'meaning': '저렴한 식사'}, {'expr': 'serving the community', 'meaning': '지역 사회에 서비스를 제공하다'}]}]}, {'title': '📢 SIGNAL', 'steps': [{'q_type': 'purpose', 'sentences': ['The Westside Public Library will adjust its operating hours beginning July 1.', 'The library will now be open Monday through Saturday from 9 A.M. to 8 P.M., and closed on Sundays.'], 'question': 'What is the purpose of this notice?', 'question_kr': '이 공지의 목적은 무엇인가?', 'choices': ["(A) To announce the library's permanent closure", '(B) To inform the public of new library hours', '(C) To promote new books at the library', '(D) To recruit library volunteers'], 'choices_kr': ['(A) 도서관의 영구 폐쇄 안내', '(B) 새 도서관 운영 시간 안내', '(C) 도서관 신간 도서 홍보', '(D) 도서관 자원봉사자 모집'], 'answer': 1, 'kr': 'Westside Public Library는 7월 1일부터 운영 시간을 조정한다. 도서관은 이제 월요일부터 토요일까지 오전 9시부터 오후 8시까지 개방되며 일요일은 휴관한다.', 'expressions': [{'expr': 'adjust its operating hours', 'meaning': '운영 시간을 조정하다'}, {'expr': 'beginning July 1', 'meaning': '7월 1일부터'}, {'expr': 'be closed on Sundays', 'meaning': '일요일에 휴관하다'}]}, {'q_type': 'detail', 'sentences': ['Members who have items due on a Sunday may return them the following Monday without late fees.', "The library's online catalog and e-book services will continue to be available 24 hours a day."], 'question': 'What can members do if their items are due on a Sunday?', 'question_kr': '일요일에 반납 기한인 경우 회원들은 어떻게 할 수 있는가?', 'choices': ['(A) Return items through a drop box outside', '(B) Return them on Monday without a penalty', '(C) Renew items online before Sunday', '(D) Contact a librarian by phone'], 'choices_kr': ['(A) 외부 반납함을 통해 반납', '(B) 벌금 없이 월요일에 반납', '(C) 일요일 이전에 온라인 연장', '(D) 전화로 사서에게 연락'], 'answer': 1, 'kr': '일요일에 반납 기한인 회원은 다음 월요일에 연체료 없이 반납할 수 있다. 도서관 온라인 목록과 전자책 서비스는 하루 24시간 계속 이용 가능하다.', 'expressions': [{'expr': 'items due on', 'meaning': '~에 반납 기한인 도서'}, {'expr': 'late fees', 'meaning': '연체료'}, {'expr': 'e-book services', 'meaning': '전자책 서비스'}]}, {'q_type': 'inference', 'sentences': ['The change in hours is due to budget reductions that have affected many city services.', 'Library officials hope to restore Sunday hours once funding becomes available.'], 'question': "What is implied about the library's Sunday closure?", 'question_kr': '도서관의 일요일 휴관에 대해 추론할 수 있는 것은?', 'choices': ['(A) It is expected to be permanent', '(B) It may be reversed in the future', '(C) It was requested by library members', "(D) It will reduce the library's membership"], 'choices_kr': ['(A) 영구적일 것으로 예상된다', '(B) 향후 번복될 수 있다', '(C) 도서관 회원들이 요청했다', '(D) 도서관 회원 수를 줄일 것이다'], 'answer': 1, 'kr': '운영 시간 변경은 많은 시 서비스에 영향을 미친 예산 삭감 때문이다. 도서관 관계자들은 재정 지원이 가능해지면 일요일 운영을 재개하길 희망한다.', 'expressions': [{'expr': 'budget reductions', 'meaning': '예산 삭감'}, {'expr': 'restore Sunday hours', 'meaning': '일요일 운영을 재개하다'}, {'expr': 'once funding becomes available', 'meaning': '재정 지원이 가능해지면'}]}]}], 'letter': [{'title': '✉️ CIPHER', 'steps': [{'q_type': 'purpose', 'sentences': ["Dear Ms. Thompson, I am writing to express my strong interest in the Marketing Coordinator position advertised on your company's website.", 'With three years of experience in digital marketing and a proven track record of increasing online engagement, I believe I would be a valuable addition to your team.'], 'question': 'Why was this letter written?', 'question_kr': '이 편지는 왜 작성되었는가?', 'choices': ['(A) To request a promotion within the company', '(B) To apply for an advertised job position', '(C) To follow up on a previous interview', '(D) To recommend another candidate for the role'], 'choices_kr': ['(A) 사내 승진을 요청하기 위해', '(B) 광고된 직책에 지원하기 위해', '(C) 이전 면접 후속 조치를 위해', '(D) 다른 후보자를 추천하기 위해'], 'answer': 1, 'kr': 'Thompson 씨께, 귀사 웹사이트에 광고된 마케팅 코디네이터 직책에 강한 관심을 표현하기 위해 편지를 씁니다. 디지털 마케팅 3년 경험과 온라인 참여도 향상의 검증된 실적으로, 저는 귀사 팀에 소중한 인재가 될 것이라 확신합니다.', 'expressions': [{'expr': 'express my strong interest in', 'meaning': '~에 강한 관심을 표현하다'}, {'expr': 'proven track record', 'meaning': '검증된 실적'}, {'expr': 'a valuable addition to', 'meaning': '~에 소중한 인재'}]}, {'q_type': 'detail', 'sentences': ['I have attached my résumé and a portfolio of recent campaigns for your review.', 'I am available for an interview at your earliest convenience and can be reached at j.park@email.com or at 555-0192.'], 'question': 'What has the writer included with the letter?', 'question_kr': '작성자가 편지와 함께 포함한 것은?', 'choices': ['(A) A list of professional references', '(B) A résumé and portfolio', '(C) A sample marketing plan', '(D) A letter of recommendation'], 'choices_kr': ['(A) 전문 추천인 목록', '(B) 이력서와 포트폴리오', '(C) 마케팅 계획 샘플', '(D) 추천서'], 'answer': 1, 'kr': '이력서와 최근 캠페인 포트폴리오를 첨부했습니다. 편하신 시간에 면접이 가능하며 j.park@email.com 또는 555-0192로 연락 주시기 바랍니다.', 'expressions': [{'expr': 'have attached', 'meaning': '첨부하다'}, {'expr': 'at your earliest convenience', 'meaning': '가장 편하신 시간에'}, {'expr': 'can be reached at', 'meaning': '~로 연락할 수 있다'}]}, {'q_type': 'inference', 'sentences': ['During my time at Apex Solutions, I led a social media campaign that grew our follower count by 45% in just six months.', "I am confident that similar strategies could be effectively applied to your brand's digital presence."], 'question': 'What can be inferred about the letter writer?', 'question_kr': '편지 작성자에 대해 추론할 수 있는 것은?', 'choices': ['(A) She recently graduated from university', '(B) She has experience growing social media audiences', "(C) She previously worked at Ms. Thompson's company", '(D) She specializes in traditional advertising'], 'choices_kr': ['(A) 최근 대학을 졸업했다', '(B) 소셜 미디어 팔로워 증가 경험이 있다', '(C) 이전에 Thompson 씨 회사에서 근무했다', '(D) 전통적인 광고를 전문으로 한다'], 'answer': 1, 'kr': 'Apex Solutions에서 근무할 때 소셜 미디어 캠페인을 이끌어 6개월 만에 팔로워 수를 45% 늘렸습니다. 유사한 전략이 귀사 브랜드의 디지털 존재감에 효과적으로 적용될 수 있다고 확신합니다.', 'expressions': [{'expr': 'grew our follower count', 'meaning': '팔로워 수를 늘리다'}, {'expr': 'digital presence', 'meaning': '디지털 존재감'}, {'expr': 'be effectively applied to', 'meaning': '~에 효과적으로 적용되다'}]}]}, {'title': '✉️ CIPHER', 'steps': [{'q_type': 'purpose', 'sentences': ['Dear Team, I am writing to inform you that our quarterly review meeting, originally scheduled for Thursday, has been moved to Friday, October 18, at 2:00 P.M.', 'The change was necessary due to a conflict in the conference room booking system.'], 'question': 'What is the purpose of this email?', 'question_kr': '이 이메일의 목적은 무엇인가?', 'choices': ['(A) To cancel the quarterly review meeting', '(B) To notify staff of a rescheduled meeting', '(C) To introduce a new meeting format', '(D) To request agenda items from team members'], 'choices_kr': ['(A) 분기별 검토 회의 취소', '(B) 회의 일정 변경 통보', '(C) 새로운 회의 형식 소개', '(D) 팀원들에게 안건 항목 요청'], 'answer': 1, 'kr': '팀 여러분, 목요일로 예정되어 있던 분기별 검토 회의가 10월 18일 금요일 오후 2시로 변경되었음을 알려드립니다. 회의실 예약 시스템 충돌로 인해 변경이 필요했습니다.', 'expressions': [{'expr': 'originally scheduled for', 'meaning': '원래 ~로 예정된'}, {'expr': 'has been moved to', 'meaning': '~로 변경되었다'}, {'expr': 'due to a conflict', 'meaning': '충돌로 인해'}]}, {'q_type': 'detail', 'sentences': ['The meeting will take place in Conference Room B on the third floor.', 'Please bring your updated project reports and be prepared to discuss Q3 performance figures.', 'Light refreshments will be provided.'], 'question': 'Where will the meeting be held?', 'question_kr': '회의는 어디서 열릴 것인가?', 'choices': ['(A) In the main auditorium', '(B) In Conference Room B on the third floor', "(C) In the director's office", '(D) In the cafeteria on the ground floor'], 'choices_kr': ['(A) 대강당에서', '(B) 3층 회의실 B에서', '(C) 이사실에서', '(D) 1층 구내식당에서'], 'answer': 1, 'kr': '회의는 3층 회의실 B에서 열린다. 업데이트된 프로젝트 보고서를 지참하고 3분기 실적 수치를 논의할 준비를 해 주세요. 간단한 다과가 제공될 예정입니다.', 'expressions': [{'expr': 'take place in', 'meaning': '~에서 열리다'}, {'expr': 'performance figures', 'meaning': '실적 수치'}, {'expr': 'light refreshments', 'meaning': '간단한 다과'}]}, {'q_type': 'inference', 'sentences': ['If you are unable to attend in person, please contact Sarah at ext. 304 to arrange a video call connection.', 'I apologize for any inconvenience this change may cause and appreciate your flexibility.'], 'question': 'What is implied about the meeting?', 'question_kr': '회의에 대해 추론할 수 있는 것은?', 'choices': ['(A) It will be held entirely online', '(B) Remote participation is possible', '(C) It will be recorded for absent members', '(D) Attendance is optional for all staff'], 'choices_kr': ['(A) 전적으로 온라인으로 진행된다', '(B) 원격 참여가 가능하다', '(C) 결석 직원을 위해 녹화된다', '(D) 모든 직원에게 참석이 선택적이다'], 'answer': 1, 'kr': '직접 참석할 수 없는 경우 304번으로 Sarah에게 연락하여 화상 통화 연결을 마련해 주세요. 변경으로 인한 불편에 사과드리며 협조해 주셔서 감사합니다.', 'expressions': [{'expr': 'unable to attend in person', 'meaning': '직접 참석할 수 없는'}, {'expr': 'arrange a video call', 'meaning': '화상 통화를 마련하다'}, {'expr': 'appreciate your flexibility', 'meaning': '융통성에 감사하다'}]}]}, {'title': '✉️ CIPHER', 'steps': [{'q_type': 'purpose', 'sentences': ['Dear Customer Service Team, I am writing to express my dissatisfaction with an order I received on March 10.', 'Order number 48271 contained a damaged item and was missing one of the three products I had purchased.'], 'question': 'Why did the customer write this email?', 'question_kr': '고객은 왜 이 이메일을 작성했는가?', 'choices': ['(A) To request a product catalog', '(B) To complain about a problem with an order', '(C) To inquire about delivery options', '(D) To apply for a store membership'], 'choices_kr': ['(A) 제품 카탈로그를 요청하기 위해', '(B) 주문 문제에 대해 불만을 제기하기 위해', '(C) 배송 옵션에 대해 문의하기 위해', '(D) 매장 회원권 신청을 위해'], 'answer': 1, 'kr': '고객 서비스 팀 귀중, 3월 10일에 받은 주문에 대한 불만을 표현하기 위해 이메일을 씁니다. 주문번호 48271에는 파손된 물품이 포함되어 있었고 구매한 3개 제품 중 하나가 누락되어 있었습니다.', 'expressions': [{'expr': 'express my dissatisfaction with', 'meaning': '~에 대한 불만을 표현하다'}, {'expr': 'damaged item', 'meaning': '파손된 물품'}, {'expr': 'was missing', 'meaning': '누락되다, 빠져있다'}]}, {'q_type': 'detail', 'sentences': ['I have included photographs of the damaged packaging as well as a screenshot of my original order confirmation.', 'I would like to request either a full replacement of the damaged item or a refund for the missing product.'], 'question': 'What does the customer request?', 'question_kr': '고객이 요청하는 것은?', 'choices': ['(A) A discount on a future order', '(B) A replacement or refund', '(C) Free shipping on the next purchase', '(D) An upgrade to express delivery'], 'choices_kr': ['(A) 다음 주문 할인', '(B) 교체품 또는 환불', '(C) 다음 구매 무료 배송', '(D) 빠른 배송으로 업그레이드'], 'answer': 1, 'kr': '파손된 포장의 사진과 원래 주문 확인서의 스크린샷을 첨부했습니다. 파손된 물품의 완전한 교체품이나 누락된 제품에 대한 환불을 요청합니다.', 'expressions': [{'expr': 'order confirmation', 'meaning': '주문 확인서'}, {'expr': 'full replacement', 'meaning': '완전한 교체'}, {'expr': 'refund for', 'meaning': '~에 대한 환불'}]}, {'q_type': 'inference', 'sentences': ['I have been a loyal customer for over five years and have always been satisfied with your service until now.', 'I hope this matter can be resolved promptly so that I can continue to shop with confidence.'], 'question': 'What is implied about the customer?', 'question_kr': '고객에 대해 추론할 수 있는 것은?', 'choices': ['(A) She plans to stop shopping at the store', '(B) She generally has a positive view of the company', '(C) She has complained to the company before', '(D) She is requesting compensation for emotional distress'], 'choices_kr': ['(A) 그 매장에서 쇼핑을 중단할 계획이다', '(B) 일반적으로 회사에 긍정적인 시각을 가지고 있다', '(C) 이전에 회사에 불만을 제기한 적이 있다', '(D) 정신적 피해에 대한 보상을 요청하고 있다'], 'answer': 1, 'kr': '저는 5년 이상 충성 고객이었으며 지금까지 항상 서비스에 만족했습니다. 이 문제가 신속히 해결되어 계속 안심하고 쇼핑할 수 있기를 바랍니다.', 'expressions': [{'expr': 'loyal customer', 'meaning': '충성 고객'}, {'expr': 'resolved promptly', 'meaning': '신속히 해결되다'}, {'expr': 'shop with confidence', 'meaning': '안심하고 쇼핑하다'}]}]}, {'title': '✉️ CIPHER', 'steps': [{'q_type': 'purpose', 'sentences': ['Dear Mr. Harrington, I am writing on behalf of Delton Consulting Group to inquire about the office space currently listed for rent at 240 Harbor Boulevard.', 'Our company is seeking a modern, well-connected workspace for approximately 25 employees, and your property appears to meet our requirements.'], 'question': 'What is the purpose of this letter?', 'question_kr': '이 편지의 목적은 무엇인가?', 'choices': ['(A) To negotiate the price of an existing lease', '(B) To inquire about an available office space', '(C) To report problems with a current rental property', '(D) To request a list of available properties'], 'choices_kr': ['(A) 기존 임대 가격을 협상하기 위해', '(B) 이용 가능한 사무 공간에 대해 문의하기 위해', '(C) 현재 임대 건물의 문제를 보고하기 위해', '(D) 이용 가능한 건물 목록을 요청하기 위해'], 'answer': 1, 'kr': 'Harrington 씨께, Delton Consulting Group을 대표하여 현재 240 Harbor Boulevard에 임대로 등록된 사무 공간에 대해 문의하기 위해 편지를 씁니다. 저희 회사는 약 25명의 직원을 위한 현대적이고 교통이 편리한 업무 공간을 찾고 있으며, 귀하의 건물이 요건에 부합하는 것 같습니다.', 'expressions': [{'expr': 'on behalf of', 'meaning': '~을 대표하여'}, {'expr': 'listed for rent', 'meaning': '임대로 등록된'}, {'expr': 'meets our requirements', 'meaning': '요건에 부합하다'}]}, {'q_type': 'detail', 'sentences': ['We would prefer a lease term of at least two years, with the option to renew.', 'Could you please provide information on the monthly rental rate, available parking, and whether the space includes high-speed internet infrastructure?'], 'question': 'Which of the following does the writer ask about?', 'question_kr': '작성자가 문의하는 것은?', 'choices': ["(A) The building's renovation history", '(B) The number of floors in the building', '(C) The monthly rental cost and parking', '(D) The names of current tenants'], 'choices_kr': ['(A) 건물 리모델링 이력', '(B) 건물의 층수', '(C) 월 임대료와 주차', '(D) 현재 임차인 이름'], 'answer': 2, 'kr': '저희는 갱신 옵션과 함께 최소 2년의 임대 기간을 선호합니다. 월 임대료, 이용 가능한 주차, 고속 인터넷 인프라 포함 여부에 대한 정보를 제공해 주시겠습니까?', 'expressions': [{'expr': 'lease term', 'meaning': '임대 기간'}, {'expr': 'option to renew', 'meaning': '갱신 옵션'}, {'expr': 'high-speed internet infrastructure', 'meaning': '고속 인터넷 인프라'}]}, {'q_type': 'not', 'sentences': ['We are also open to discussing flexible move-in dates, as our current lease does not expire until the end of next month.', 'Should the space meet our needs, we would be prepared to arrange a site visit at your earliest convenience.', 'Please feel free to contact me directly at d.kim@delton.com.'], 'question': 'Which of the following is NOT mentioned in the letter?', 'question_kr': '편지에서 언급되지 않은 것은?', 'choices': ["(A) The writer's contact information", "(B) The company's preferred move-in date", '(C) Willingness to schedule a property visit', "(D) The company's number of employees"], 'choices_kr': ['(A) 작성자의 연락처', '(B) 회사가 선호하는 이사 날짜', '(C) 건물 방문 일정 조율 의향', '(D) 회사 직원 수'], 'answer': 1, 'kr': '저희는 현재 임대가 다음 달 말에 만료되므로 유연한 이사 날짜 협의도 가능합니다. 공간이 요건을 충족하면 편하신 시간에 현장 방문을 준비할 용의가 있습니다. d.kim@delton.com으로 직접 연락 주시기 바랍니다.', 'expressions': [{'expr': 'open to discussing', 'meaning': '논의할 의향이 있다'}, {'expr': 'site visit', 'meaning': '현장 방문'}, {'expr': 'does not expire until', 'meaning': '~까지 만료되지 않는다'}]}]}, {'title': '✉️ CIPHER', 'steps': [{'q_type': 'purpose', 'sentences': ['Dear Ms. Chen, On behalf of the entire team at Pinnacle Financial Services, I am delighted to welcome you as our newest team member.', 'Your appointment as Senior Financial Analyst becomes effective on Monday, September 2.'], 'question': 'What is the main purpose of this email?', 'question_kr': '이 이메일의 주요 목적은 무엇인가?', 'choices': ['(A) To offer Ms. Chen a job position', '(B) To welcome a new employee to the company', "(C) To confirm Ms. Chen's resignation", '(D) To invite Ms. Chen to a company event'], 'choices_kr': ['(A) Chen 씨에게 직위를 제안하기 위해', '(B) 새 직원을 회사에 환영하기 위해', '(C) Chen 씨의 사직을 확인하기 위해', '(D) Chen 씨를 회사 행사에 초대하기 위해'], 'answer': 1, 'kr': 'Chen 씨께, Pinnacle Financial Services 팀 전체를 대표하여 최신 팀원으로 환영합니다. 수석 재무 분석가로의 임명은 9월 2일 월요일부터 발효됩니다.', 'expressions': [{'expr': 'on behalf of', 'meaning': '~을 대표하여'}, {'expr': 'appointment becomes effective', 'meaning': '임명이 발효되다'}, {'expr': 'delighted to welcome', 'meaning': '기쁘게 환영하다'}]}, {'q_type': 'detail', 'sentences': ['Please report to the main reception on the 12th floor at 9 A.M. on your first day, where you will receive your building access card and meet with HR.', 'Your direct supervisor, Mr. James Ortega, will then conduct a brief orientation session before introducing you to the rest of the team.'], 'question': 'What will Ms. Chen do when she arrives on her first day?', 'question_kr': 'Chen 씨는 첫날 도착했을 때 무엇을 하는가?', 'choices': ['(A) Attend a company-wide presentation', '(B) Go to the 12th floor reception to receive her access card', '(C) Meet with the CEO for a welcome lunch', '(D) Complete online training modules'], 'choices_kr': ['(A) 전사 발표회 참석', '(B) 12층 안내 데스크에서 출입 카드 수령', '(C) CEO와 환영 오찬', '(D) 온라인 교육 모듈 완료'], 'answer': 1, 'kr': '첫날 오전 9시에 12층 메인 안내 데스크에 출석하시면 건물 출입 카드를 받고 인사팀을 만나실 것입니다. 직속 상사인 James Ortega 씨가 간단한 오리엔테이션을 진행한 후 나머지 팀원들에게 소개해 드릴 것입니다.', 'expressions': [{'expr': 'building access card', 'meaning': '건물 출입 카드'}, {'expr': 'direct supervisor', 'meaning': '직속 상사'}, {'expr': 'conduct an orientation session', 'meaning': '오리엔테이션을 진행하다'}]}, {'q_type': 'inference', 'sentences': ['We have prepared a full onboarding package including your employee handbook, benefits information, and IT setup instructions.', 'We are confident that your expertise in risk assessment and financial modeling will make a significant impact on our department.'], 'question': 'What can be inferred about Ms. Chen?', 'question_kr': 'Chen 씨에 대해 추론할 수 있는 것은?', 'choices': ['(A) She is a recent university graduate', '(B) She has specialized skills in finance', '(C) She transferred from another department', '(D) She will manage the HR department'], 'choices_kr': ['(A) 최근 대학을 졸업했다', '(B) 재무 분야의 전문 기술을 보유하고 있다', '(C) 다른 부서에서 이동했다', '(D) 인사부서를 관리할 것이다'], 'answer': 1, 'kr': '직원 핸드북, 복리후생 정보, IT 설정 지침을 포함한 완전한 온보딩 패키지를 준비했습니다. 리스크 평가와 재무 모델링에 대한 귀하의 전문성이 우리 부서에 큰 영향을 미칠 것이라 확신합니다.', 'expressions': [{'expr': 'onboarding package', 'meaning': '신입사원 교육 패키지'}, {'expr': 'risk assessment', 'meaning': '리스크 평가'}, {'expr': 'financial modeling', 'meaning': '재무 모델링'}]}]}], 'notice': [{'title': '📰 INTERCEPT', 'steps': [{'q_type': 'purpose', 'sentences': ['The Harborview Museum of Natural History will close its doors to the public from Monday, August 5, through Friday, August 30, to undergo a comprehensive renovation of its main exhibition halls.', 'The project, funded in part by a $2 million grant from the City Arts Council, will modernize display systems and improve accessibility throughout the building.'], 'question': 'What is the purpose of this announcement?', 'question_kr': '이 공지의 목적은 무엇인가?', 'choices': ["(A) To inform the public of a museum's temporary closure", '(B) To announce the opening of a new exhibition', '(C) To request donations for museum renovations', '(D) To promote upcoming educational programs'], 'choices_kr': ['(A) 박물관의 임시 폐관을 대중에게 알리기 위해', '(B) 새 전시회 개막을 발표하기 위해', '(C) 박물관 리모델링을 위한 기부를 요청하기 위해', '(D) 다가오는 교육 프로그램을 홍보하기 위해'], 'answer': 0, 'kr': 'Harborview 자연사박물관은 주요 전시실의 종합적인 리모델링을 위해 8월 5일 월요일부터 8월 30일 금요일까지 대중에게 문을 닫는다. City Arts Council의 200만 달러 보조금으로 일부 지원되는 이 프로젝트는 전시 시스템을 현대화하고 건물 전체의 접근성을 개선할 것이다.', 'expressions': [{'expr': 'comprehensive renovation', 'meaning': '종합적인 리모델링'}, {'expr': 'funded in part by', 'meaning': '~로 일부 지원받는'}, {'expr': 'improve accessibility', 'meaning': '접근성을 개선하다'}]}, {'q_type': 'detail', 'sentences': ['Visitors who hold valid annual memberships will receive a one-month extension on their current membership period as compensation for the closure.', 'Season ticket holders are advised to contact the membership office at membership@harborviewmuseum.org to confirm their updated expiration dates.'], 'question': 'What will annual members receive during the closure period?', 'question_kr': '연간 회원들은 폐관 기간 동안 무엇을 받는가?', 'choices': ['(A) A full refund of their membership fee', '(B) Free access to partner museums', '(C) A one-month extension to their membership', '(D) Priority tickets for the reopening event'], 'choices_kr': ['(A) 회원비 전액 환불', '(B) 협력 박물관 무료 입장', '(C) 회원권 1개월 연장', '(D) 재개관 행사 우선 티켓'], 'answer': 2, 'kr': '유효한 연간 회원권을 보유한 방문객은 폐관에 대한 보상으로 현재 회원 기간이 1개월 연장된다. 시즌권 소지자는 업데이트된 만료일을 확인하기 위해 membership@harborviewmuseum.org로 회원 사무소에 연락하도록 권고된다.', 'expressions': [{'expr': 'valid annual membership', 'meaning': '유효한 연간 회원권'}, {'expr': 'as compensation for', 'meaning': '~에 대한 보상으로'}, {'expr': 'updated expiration dates', 'meaning': '업데이트된 만료일'}]}, {'q_type': 'inference', 'sentences': ["The museum's gift shop and café will remain accessible to the public throughout the renovation period via a temporary entrance on Maple Avenue.", 'Upon reopening on September 2, the museum will debut its newly redesigned permanent collection, featuring an expanded prehistoric life wing and a state-of-the-art planetarium.'], 'question': 'What can be inferred about the museum after the renovation?', 'question_kr': '리모델링 후 박물관에 대해 추론할 수 있는 것은?', 'choices': ['(A) It will charge higher admission fees', '(B) It will offer new exhibits that were not there before', '(C) It will reduce the size of its gift shop', '(D) It will close permanently after the renovation'], 'choices_kr': ['(A) 입장료를 인상할 것이다', '(B) 이전에 없던 새로운 전시를 제공할 것이다', '(C) 기념품점 규모를 줄일 것이다', '(D) 리모델링 후 영구 폐관할 것이다'], 'answer': 1, 'kr': '박물관 기념품점과 카페는 Maple Avenue의 임시 입구를 통해 리모델링 기간 내내 대중이 이용할 수 있다. 9월 2일 재개관 시 박물관은 확장된 선사시대 생명 전시관과 최첨단 플라네타리움을 갖춘 새롭게 재설계된 상설 컬렉션을 선보일 것이다.', 'expressions': [{'expr': 'remain accessible to', 'meaning': '~이 계속 이용 가능하다'}, {'expr': 'debut its redesigned collection', 'meaning': '재설계된 컬렉션을 선보이다'}, {'expr': 'state-of-the-art', 'meaning': '최첨단의'}]}]}, {'title': '📰 INTERCEPT', 'steps': [{'q_type': 'purpose', 'sentences': ['Meridian Technologies announced yesterday that it has completed its acquisition of CloudBridge Solutions, a leading provider of enterprise data management software, for an estimated $380 million.', "The deal, which was first reported in January, is expected to significantly expand Meridian's presence in the rapidly growing cloud computing market."], 'question': 'What is this article mainly about?', 'question_kr': '이 기사는 주로 무엇에 관한 것인가?', 'choices': ['(A) The launch of a new cloud computing product', '(B) The completion of a corporate acquisition', '(C) The financial difficulties of CloudBridge Solutions', '(D) Changes in cloud computing regulations'], 'choices_kr': ['(A) 새 클라우드 컴퓨팅 제품 출시', '(B) 기업 인수 완료', '(C) CloudBridge Solutions의 재정적 어려움', '(D) 클라우드 컴퓨팅 규정 변경'], 'answer': 1, 'kr': 'Meridian Technologies는 기업 데이터 관리 소프트웨어의 선도적 공급업체인 CloudBridge Solutions를 약 3억 8천만 달러에 인수 완료했다고 어제 발표했다. 1월에 처음 보도된 이 거래는 빠르게 성장하는 클라우드 컴퓨팅 시장에서 Meridian의 입지를 크게 확장할 것으로 예상된다.', 'expressions': [{'expr': 'completed its acquisition of', 'meaning': '~의 인수를 완료하다'}, {'expr': 'enterprise data management', 'meaning': '기업 데이터 관리'}, {'expr': 'expand its presence in', 'meaning': '~에서 입지를 확장하다'}]}, {'q_type': 'detail', 'sentences': ["CloudBridge's existing team of 420 employees will be integrated into Meridian's operations division, with no planned redundancies according to the company's official statement.", 'The combined entity will serve over 3,000 corporate clients across 28 countries.'], 'question': 'According to the article, what will happen to CloudBridge employees?', 'question_kr': '기사에 따르면, CloudBridge 직원들은 어떻게 되는가?', 'choices': ['(A) They will be offered voluntary retirement packages', "(B) They will join Meridian's operations division", '(C) They will work independently under a new brand', "(D) They will be relocated to Meridian's headquarters"], 'choices_kr': ['(A) 자발적 퇴직 패키지가 제공될 것이다', '(B) Meridian의 운영 부서에 합류할 것이다', '(C) 새 브랜드 아래 독립적으로 일할 것이다', '(D) Meridian 본사로 이전할 것이다'], 'answer': 1, 'kr': 'CloudBridge의 기존 420명 직원팀은 회사의 공식 성명에 따르면 감원 계획 없이 Meridian의 운영 부서에 통합될 것이다. 합병된 회사는 28개국에 걸쳐 3,000개 이상의 기업 고객에게 서비스를 제공할 것이다.', 'expressions': [{'expr': 'be integrated into', 'meaning': '~에 통합되다'}, {'expr': 'no planned redundancies', 'meaning': '계획된 감원 없음'}, {'expr': 'combined entity', 'meaning': '합병된 회사'}]}, {'q_type': 'inference', 'sentences': ["Industry analysts have responded positively to the merger, noting that CloudBridge's proprietary data encryption technology fills a critical gap in Meridian's current product lineup.", "Meridian's stock rose 4.2 percent in early trading following the announcement, reflecting investor optimism about the deal's long-term strategic value."], 'question': 'What is implied about the acquisition?', 'question_kr': '인수에 대해 추론할 수 있는 것은?', 'choices': ['(A) It was opposed by most industry analysts', "(B) It is expected to strengthen Meridian's product offerings", '(C) It will result in significant job losses at Meridian', '(D) It was motivated primarily by reducing competition'], 'choices_kr': ['(A) 대부분의 업계 분석가들이 반대했다', '(B) Meridian의 제품 라인업을 강화할 것으로 예상된다', '(C) Meridian에서 상당한 일자리 감소를 초래할 것이다', '(D) 주로 경쟁 감소를 위해 추진되었다'], 'answer': 1, 'kr': '업계 분석가들은 CloudBridge의 독자적인 데이터 암호화 기술이 Meridian의 현재 제품 라인의 중요한 공백을 채운다고 언급하며 합병에 긍정적으로 반응했다. Meridian의 주가는 발표 후 초기 거래에서 4.2% 상승해 거래의 장기적 전략적 가치에 대한 투자자들의 낙관론을 반영했다.', 'expressions': [{'expr': 'proprietary technology', 'meaning': '독자적인 기술'}, {'expr': 'fills a critical gap', 'meaning': '중요한 공백을 채우다'}, {'expr': 'reflecting investor optimism', 'meaning': '투자자들의 낙관론을 반영하다'}]}]}, {'title': '📰 INTERCEPT', 'steps': [{'q_type': 'purpose', 'sentences': ['We are pleased to announce that Vanguard Legal Associates will be relocating its offices to the newly constructed Pinnacle Tower at 88 Commerce Drive, effective November 1.', "This move reflects our firm's continued growth and our commitment to providing clients and staff with a modern, state-of-the-art working environment."], 'question': 'What is the purpose of this notice?', 'question_kr': '이 공지의 목적은 무엇인가?', 'choices': ["(A) To announce the firm's merger with another company", '(B) To inform clients and staff of an office relocation', "(C) To promote the firm's new legal services", '(D) To notify staff of changes to working hours'], 'choices_kr': ['(A) 회사의 다른 회사와의 합병 발표', '(B) 고객과 직원에게 사무소 이전 안내', '(C) 회사의 새로운 법률 서비스 홍보', '(D) 직원에게 근무 시간 변경 통보'], 'answer': 1, 'kr': 'Vanguard Legal Associates가 11월 1일부로 88 Commerce Drive에 새로 건설된 Pinnacle Tower로 사무소를 이전한다고 기쁘게 알려드립니다. 이번 이전은 우리 회사의 지속적인 성장과 고객 및 직원들에게 현대적이고 최첨단 근무 환경을 제공하려는 의지를 반영합니다.', 'expressions': [{'expr': 'relocating its offices', 'meaning': '사무소를 이전하다'}, {'expr': 'effective November 1', 'meaning': '11월 1일부로'}, {'expr': 'commitment to providing', 'meaning': '~을 제공하려는 의지'}]}, {'q_type': 'detail', 'sentences': ['All telephone numbers and email addresses will remain unchanged, and client files will be transferred securely prior to the move.', 'Clients with scheduled appointments during the transition week of October 28–31 are advised to confirm their appointment details with their assigned attorney, as some meetings may need to be rescheduled.'], 'question': 'What are clients with appointments during October 28-31 advised to do?', 'question_kr': '10월 28-31일에 예약이 있는 고객들에게 권고되는 것은?', 'choices': ['(A) Cancel their appointments and rebook after November 1', '(B) Confirm their appointment details with their attorney', '(C) Visit the new office at Pinnacle Tower', '(D) Contact the main reception to update their records'], 'choices_kr': ['(A) 예약을 취소하고 11월 1일 이후 다시 예약', '(B) 담당 변호사에게 예약 세부 사항 확인', '(C) Pinnacle Tower의 새 사무소 방문', '(D) 메인 안내 데스크에 연락하여 기록 업데이트'], 'answer': 1, 'kr': '모든 전화번호와 이메일 주소는 변경되지 않으며, 고객 파일은 이전 전에 안전하게 이전된다. 10월 28-31일 이전 주에 예약이 있는 고객들은 일부 회의가 일정 변경이 필요할 수 있으므로 담당 변호사에게 예약 세부 사항을 확인하도록 권고된다.', 'expressions': [{'expr': 'remain unchanged', 'meaning': '변경되지 않다'}, {'expr': 'transferred securely', 'meaning': '안전하게 이전되다'}, {'expr': 'assigned attorney', 'meaning': '담당 변호사'}]}, {'q_type': 'inference', 'sentences': ['The new location offers significantly expanded office space, a dedicated client consultation suite, and underground parking for up to 80 vehicles.', 'We look forward to welcoming you to our new home and continuing to deliver the exceptional legal services you have come to expect from Vanguard.'], 'question': "What is implied about Vanguard Legal Associates' current office?", 'question_kr': 'Vanguard Legal Associates의 현재 사무소에 대해 추론할 수 있는 것은?', 'choices': ['(A) It is located in a modern building', '(B) It has fewer amenities than the new location', '(C) It recently underwent major renovations', '(D) It is shared with another law firm'], 'choices_kr': ['(A) 현대적인 건물에 위치해 있다', '(B) 새 위치보다 편의시설이 적다', '(C) 최근 대규모 리모델링을 했다', '(D) 다른 법무법인과 공유하고 있다'], 'answer': 1, 'kr': '새 위치는 크게 확장된 사무 공간, 전용 고객 상담실, 최대 80대를 위한 지하 주차장을 제공한다. 새 사무소에서 여러분을 환영하고 Vanguard에서 기대하는 탁월한 법률 서비스를 계속 제공하기를 기대합니다.', 'expressions': [{'expr': 'dedicated consultation suite', 'meaning': '전용 상담실'}, {'expr': 'significantly expanded', 'meaning': '크게 확장된'}, {'expr': 'exceptional legal services', 'meaning': '탁월한 법률 서비스'}]}]}, {'title': '📰 INTERCEPT', 'steps': [{'q_type': 'purpose', 'sentences': ['Hometech Appliances has issued a voluntary recall of approximately 15,000 units of its HT-700 Series electric pressure cookers sold between January and September of this year.', 'The company identified a potential defect in the lid-locking mechanism that could, under certain conditions, cause the lid to open unexpectedly during operation, posing a burn risk to users.'], 'question': 'What is the main purpose of this article?', 'question_kr': '이 기사의 주요 목적은 무엇인가?', 'choices': ['(A) To announce a new product launch by Hometech', '(B) To warn consumers about a defective product recall', '(C) To report a lawsuit filed against Hometech Appliances', '(D) To promote safer alternatives to pressure cookers'], 'choices_kr': ['(A) Hometech의 새 제품 출시 발표', '(B) 결함 제품 리콜에 대한 소비자 경고', '(C) Hometech Appliances를 상대로 제기된 소송 보도', '(D) 압력솥의 더 안전한 대안 홍보'], 'answer': 1, 'kr': 'Hometech Appliances는 올해 1월부터 9월 사이에 판매된 약 15,000개의 HT-700 Series 전기 압력솥에 대한 자발적 리콜을 발표했다. 회사는 뚜껑 잠금 장치의 잠재적 결함이 특정 조건에서 작동 중 뚜껑이 예기치 않게 열릴 수 있어 사용자에게 화상 위험을 초래할 수 있다는 것을 확인했다.', 'expressions': [{'expr': 'voluntary recall', 'meaning': '자발적 리콜'}, {'expr': 'lid-locking mechanism', 'meaning': '뚜껑 잠금 장치'}, {'expr': 'posing a burn risk', 'meaning': '화상 위험을 초래하다'}]}, {'q_type': 'detail', 'sentences': ["Customers who own an affected unit are asked to immediately discontinue use and contact Hometech's customer support line at 1-800-HOMETECH to arrange a free replacement.", 'Proof of purchase is not required to qualify for the replacement program.'], 'question': 'What must customers do if they own an affected product?', 'question_kr': '해당 제품을 소유한 고객들은 무엇을 해야 하는가?', 'choices': ['(A) Return the product to the store where it was purchased', "(B) Stop using it and call Hometech's support line", '(C) Wait for a Hometech representative to contact them', '(D) Submit a written complaint to the consumer protection agency'], 'choices_kr': ['(A) 구매한 매장에 제품 반납', '(B) 사용을 중단하고 Hometech 지원 라인에 전화', '(C) Hometech 담당자가 연락할 때까지 기다림', '(D) 소비자 보호 기관에 서면 민원 제출'], 'answer': 1, 'kr': '해당 제품을 소유한 고객은 즉시 사용을 중단하고 무료 교체를 마련하기 위해 1-800-HOMETECH로 Hometech 고객 지원 라인에 연락하도록 요청된다. 교체 프로그램 자격을 얻기 위해 구매 증명이 필요하지 않다.', 'expressions': [{'expr': 'discontinue use', 'meaning': '사용을 중단하다'}, {'expr': 'proof of purchase', 'meaning': '구매 증명'}, {'expr': 'qualify for', 'meaning': '~의 자격을 얻다'}]}, {'q_type': 'not', 'sentences': ['The recall affects models with serial numbers beginning with HT7 followed by a letter between A and G.', 'Models purchased after October 1 are not affected, as the manufacturing defect was corrected at that time.', 'Hometech has reported no injuries related to the defect so far, but emphasizes that the recall is being conducted as a precautionary measure.'], 'question': 'Which of the following is NOT mentioned in the article?', 'question_kr': '기사에서 언급되지 않은 것은?', 'choices': ['(A) The serial numbers of affected models', '(B) The number of injuries reported so far', '(C) The countries where the recall applies', '(D) When the defect was fixed in manufacturing'], 'choices_kr': ['(A) 해당 모델의 일련번호', '(B) 현재까지 보고된 부상 수', '(C) 리콜이 적용되는 국가', '(D) 제조에서 결함이 수정된 시기'], 'answer': 2, 'kr': '리콜은 HT7로 시작하고 A에서 G 사이의 문자가 뒤따르는 일련번호의 모델에 영향을 미친다. 10월 1일 이후 구매한 모델은 그 시점에 제조 결함이 수정되었으므로 영향을 받지 않는다. Hometech는 지금까지 결함과 관련된 부상을 보고하지 않았지만, 리콜은 예방 조치로 시행되고 있다고 강조한다.', 'expressions': [{'expr': 'serial numbers', 'meaning': '일련번호'}, {'expr': 'precautionary measure', 'meaning': '예방 조치'}, {'expr': 'manufacturing defect', 'meaning': '제조 결함'}]}]}, {'title': '📰 INTERCEPT', 'steps': [{'q_type': 'purpose', 'sentences': ["The city's Metropolitan Transit Authority (MTA) has announced a $150 million infrastructure upgrade to the Central Line subway system, scheduled to begin in the spring.", 'The project aims to replace aging signal equipment, install platform screen doors at 12 stations, and introduce a new contactless fare payment system across the entire network.'], 'question': 'What is this article primarily about?', 'question_kr': '이 기사는 주로 무엇에 관한 것인가?', 'choices': ["(A) The MTA's annual financial report", "(B) A major upgrade to the city's subway system", '(C) The introduction of a new bus rapid transit line', '(D) Environmental concerns about subway construction'], 'choices_kr': ['(A) MTA의 연간 재무 보고서', '(B) 시 지하철 시스템의 대규모 업그레이드', '(C) 새로운 급행버스 노선 도입', '(D) 지하철 건설에 대한 환경 우려'], 'answer': 1, 'kr': '시의 Metropolitan Transit Authority(MTA)는 봄에 시작될 예정인 Central Line 지하철 시스템에 대한 1억 5천만 달러 규모의 인프라 업그레이드를 발표했다. 이 프로젝트는 노후화된 신호 장비 교체, 12개 역에 스크린도어 설치, 전체 네트워크에 새로운 비접촉식 요금 결제 시스템 도입을 목표로 한다.', 'expressions': [{'expr': 'infrastructure upgrade', 'meaning': '인프라 업그레이드'}, {'expr': 'aging signal equipment', 'meaning': '노후화된 신호 장비'}, {'expr': 'contactless fare payment', 'meaning': '비접촉식 요금 결제'}]}, {'q_type': 'detail', 'sentences': ['Construction will be carried out primarily during overnight hours to minimize disruption to daily commuters.', 'However, passengers should expect weekend service suspensions on the Central Line between Harbor Station and Riverside Junction from April through August.'], 'question': 'According to the article, when will service suspensions occur?', 'question_kr': '기사에 따르면, 서비스 중단은 언제 발생하는가?', 'choices': ['(A) On weekday mornings from April through August', '(B) On weekends from April through August', '(C) Every night throughout the construction period', '(D) Only during the final week of construction'], 'choices_kr': ['(A) 4월부터 8월까지 주중 아침에', '(B) 4월부터 8월까지 주말에', '(C) 공사 기간 내내 매일 밤', '(D) 공사 마지막 주에만'], 'answer': 1, 'kr': '공사는 일상 통근자들의 불편을 최소화하기 위해 주로 야간에 진행된다. 그러나 승객들은 4월부터 8월까지 Harbor Station과 Riverside Junction 사이의 Central Line에서 주말 서비스 중단을 예상해야 한다.', 'expressions': [{'expr': 'minimize disruption', 'meaning': '불편을 최소화하다'}, {'expr': 'service suspensions', 'meaning': '서비스 중단'}, {'expr': 'daily commuters', 'meaning': '일상 통근자들'}]}, {'q_type': 'inference', 'sentences': ["MTA Chairman Patricia Nguyen stated that the upgrades represent the most significant investment in the city's transit infrastructure in over three decades.", 'The new contactless payment system, compatible with most smartphones and bank cards, is expected to reduce boarding times by up to 30 percent, potentially easing congestion at peak hours.'], 'question': 'What can be inferred from the article?', 'question_kr': '기사에서 추론할 수 있는 것은?', 'choices': ['(A) The subway system was upgraded three decades ago', '(B) The current payment system slows down boarding', '(C) The MTA plans to expand the Central Line to new areas', '(D) Smartphone payments are not currently accepted on the network'], 'choices_kr': ['(A) 지하철 시스템은 30년 전에 업그레이드되었다', '(B) 현재 결제 시스템은 승차 속도를 늦춘다', '(C) MTA는 Central Line을 새 지역으로 확장할 계획이다', '(D) 현재 네트워크에서 스마트폰 결제가 허용되지 않는다'], 'answer': 1, 'kr': 'MTA 의장 Patricia Nguyen은 이번 업그레이드가 30년 이상 만에 시의 교통 인프라에 대한 가장 중요한 투자를 나타낸다고 말했다. 대부분의 스마트폰과 은행 카드와 호환되는 새로운 비접촉식 결제 시스템은 승차 시간을 최대 30% 단축하여 피크 시간대의 혼잡을 완화할 것으로 예상된다.', 'expressions': [{'expr': 'represent the most significant investment', 'meaning': '가장 중요한 투자를 나타내다'}, {'expr': 'reduce boarding times', 'meaning': '승차 시간을 단축하다'}, {'expr': 'easing congestion', 'meaning': '혼잡을 완화하다'}]}]}], 'information': [{'title': '☠️ BLACKOUT', 'steps': [{'q_type': 'purpose', 'sentences': ["Austral Energy Corporation has released its annual Sustainability and Corporate Responsibility Report, detailing the company's progress toward its ambitious 2030 environmental targets.", 'The report highlights a 22 percent reduction in carbon emissions across all domestic operations compared to the previous fiscal year, attributing this achievement to the accelerated deployment of renewable energy sources and the phased retirement of coal-fired generation facilities.'], 'question': 'What is the primary purpose of this report?', 'question_kr': '이 보고서의 주요 목적은 무엇인가?', 'choices': ["(A) To announce the company's merger with a renewable energy firm", "(B) To detail progress toward the company's environmental objectives", '(C) To respond to criticism from environmental groups', '(D) To propose new regulations for the energy industry'], 'choices_kr': ['(A) 재생에너지 기업과의 합병 발표', '(B) 회사의 환경 목표를 향한 진행 상황 상세 보고', '(C) 환경 단체의 비판에 대한 대응', '(D) 에너지 산업에 대한 새로운 규정 제안'], 'answer': 1, 'kr': 'Austral Energy Corporation은 2030년 환경 목표를 향한 회사의 진행 상황을 상세히 담은 연간 지속가능성 및 기업 책임 보고서를 발표했다. 보고서는 재생에너지원의 가속화된 배치와 석탄 발전 시설의 단계적 폐지를 통해 달성된 전년도 대비 전체 국내 사업장의 탄소 배출량 22% 감소를 강조한다.', 'expressions': [{'expr': 'carbon emissions reduction', 'meaning': '탄소 배출량 감소'}, {'expr': 'accelerated deployment', 'meaning': '가속화된 배치'}, {'expr': 'phased retirement', 'meaning': '단계적 폐지'}]}, {'q_type': 'detail', 'sentences': ["Among the report's key disclosures, Austral confirmed that it has divested its remaining stake in three offshore oil exploration projects, completing a strategic repositioning that began in 2021.", 'Furthermore, the company has committed to sourcing 60 percent of its operational electricity from certified renewable providers by the end of the next financial year, up from the current 38 percent.'], 'question': 'According to the report, what percentage of electricity does Austral currently source from renewable providers?', 'question_kr': '보고서에 따르면, Austral은 현재 재생에너지 공급업체에서 몇 퍼센트의 전력을 조달하는가?', 'choices': ['(A) 22 percent', '(B) 38 percent', '(C) 60 percent', '(D) 75 percent'], 'choices_kr': ['(A) 22퍼센트', '(B) 38퍼센트', '(C) 60퍼센트', '(D) 75퍼센트'], 'answer': 1, 'kr': '보고서의 주요 공개 내용 중 Austral은 3개의 해양 석유 탐사 프로젝트에서 남은 지분을 매각하여 2021년에 시작된 전략적 재편을 완료했다고 확인했다. 또한 회사는 현재 38%에서 다음 회계연도 말까지 운영 전력의 60%를 인증된 재생에너지 공급업체에서 조달하기로 약속했다.', 'expressions': [{'expr': 'divested its remaining stake', 'meaning': '남은 지분을 매각하다'}, {'expr': 'strategic repositioning', 'meaning': '전략적 재편'}, {'expr': 'certified renewable providers', 'meaning': '인증된 재생에너지 공급업체'}]}, {'q_type': 'inference', 'sentences': ["Despite the positive environmental metrics, some stakeholders have questioned whether Austral's timeline for transitioning away from fossil fuels is sufficiently aggressive given the urgency of the global climate crisis.", "The company's CEO, in response, emphasized that the transition must be balanced against operational stability and the economic interests of the communities in which Austral operates, particularly those reliant on traditional energy employment."], 'question': "What can be inferred about Austral Energy Corporation's environmental transition?", 'question_kr': 'Austral Energy Corporation의 환경 전환에 대해 추론할 수 있는 것은?', 'choices': ['(A) It has been completed ahead of the original schedule', '(B) It faces tension between speed and economic considerations', '(C) It has been praised by all environmental organizations', '(D) It will result in significant workforce reductions'], 'choices_kr': ['(A) 원래 일정보다 앞서 완료되었다', '(B) 속도와 경제적 고려 사이의 긴장에 직면해 있다', '(C) 모든 환경 단체로부터 칭찬을 받았다', '(D) 상당한 인력 감소를 초래할 것이다'], 'answer': 1, 'kr': '긍정적인 환경 지표에도 불구하고, 일부 이해관계자들은 글로벌 기후 위기의 긴박성을 고려할 때 Austral의 화석연료 전환 일정이 충분히 적극적인지에 의문을 제기했다. 이에 대해 회사 CEO는 전환이 운영 안정성과 Austral이 활동하는 지역사회의 경제적 이익, 특히 전통 에너지 고용에 의존하는 지역사회의 이익과 균형을 이루어야 한다고 강조했다.', 'expressions': [{'expr': 'transitioning away from fossil fuels', 'meaning': '화석연료에서 전환하다'}, {'expr': 'operational stability', 'meaning': '운영 안정성'}, {'expr': 'reliant on traditional energy employment', 'meaning': '전통 에너지 고용에 의존하는'}]}]}, {'title': '☠️ BLACKOUT', 'steps': [{'q_type': 'purpose', 'sentences': ['A landmark study published in the Journal of Organizational Psychology has found that employees who are given greater autonomy over their work schedules demonstrate significantly higher levels of job satisfaction, creative output, and long-term retention rates compared to those in strictly structured environments.', 'The five-year longitudinal research, conducted across 47 organizations in twelve countries, challenges conventional management assumptions about the relationship between oversight and productivity.'], 'question': 'What is the main subject of this article?', 'question_kr': '이 기사의 주요 주제는 무엇인가?', 'choices': ['(A) The negative effects of remote work on creativity', '(B) Research findings on workplace autonomy and employee performance', '(C) A proposal for standardizing international labor laws', '(D) The financial benefits of reducing management positions'], 'choices_kr': ['(A) 원격 근무가 창의성에 미치는 부정적 영향', '(B) 직장 자율성과 직원 성과에 관한 연구 결과', '(C) 국제 노동법 표준화 제안', '(D) 관리직 축소의 재정적 이점'], 'answer': 1, 'kr': '조직 심리학 저널에 발표된 획기적인 연구에 따르면, 업무 일정에 더 많은 자율성을 부여받은 직원들은 엄격하게 구조화된 환경의 직원들에 비해 직업 만족도, 창의적 산출물, 장기 유지율이 현저히 높다는 것을 발견했다. 12개국 47개 조직에서 수행된 5년간의 종단 연구는 감독과 생산성의 관계에 대한 기존의 경영 가정에 도전한다.', 'expressions': [{'expr': 'longitudinal research', 'meaning': '종단 연구'}, {'expr': 'conventional management assumptions', 'meaning': '기존의 경영 가정'}, {'expr': 'long-term retention rates', 'meaning': '장기 유지율'}]}, {'q_type': 'detail', 'sentences': ['Notably, the study found that the productivity gains associated with schedule flexibility were most pronounced in knowledge-intensive industries, including technology, consulting, and research and development sectors.', 'Conversely, in roles requiring physical presence or real-time coordination, such as manufacturing or emergency services, the correlation between autonomy and performance was considerably weaker.'], 'question': 'According to the study, in which industries were the benefits of flexibility most significant?', 'question_kr': '연구에 따르면, 어떤 산업에서 유연성의 이점이 가장 두드러졌는가?', 'choices': ['(A) Manufacturing and logistics', '(B) Emergency services and healthcare', '(C) Technology, consulting, and research', '(D) Retail and hospitality'], 'choices_kr': ['(A) 제조업과 물류', '(B) 응급 서비스와 의료', '(C) 기술, 컨설팅, 연구', '(D) 소매업과 접객업'], 'answer': 2, 'kr': '특히 연구는 일정 유연성과 관련된 생산성 향상이 기술, 컨설팅, 연구 개발 부문을 포함한 지식 집약적 산업에서 가장 두드러진다는 것을 발견했다. 반대로 제조업이나 응급 서비스와 같이 물리적 존재나 실시간 조정이 필요한 역할에서는 자율성과 성과 사이의 상관관계가 상당히 약했다.', 'expressions': [{'expr': 'knowledge-intensive industries', 'meaning': '지식 집약적 산업'}, {'expr': 'productivity gains', 'meaning': '생산성 향상'}, {'expr': 'real-time coordination', 'meaning': '실시간 조정'}]}, {'q_type': 'inference', 'sentences': ['The lead researcher, Dr. Amara Osei of the University of Edinburgh, cautioned that the findings should not be interpreted as a blanket endorsement of unstructured work environments.', 'Rather, she advocated for a nuanced, role-specific approach in which managers calibrate the degree of autonomy offered based on the nature of the work, individual employee characteristics, and organizational objectives.'], 'question': "What is implied by Dr. Osei's remarks?", 'question_kr': 'Osei 박사의 발언에서 추론할 수 있는 것은?', 'choices': ['(A) All organizations should immediately adopt flexible scheduling policies', '(B) The appropriate level of autonomy varies depending on the job and individual', '(C) Managers should be given less authority over employee schedules', "(D) The study's findings apply equally to all types of industries"], 'choices_kr': ['(A) 모든 조직은 즉시 유연한 일정 정책을 채택해야 한다', '(B) 적절한 자율성 수준은 직업과 개인에 따라 다르다', '(C) 관리자들은 직원 일정에 대한 권한이 줄어야 한다', '(D) 연구 결과는 모든 유형의 산업에 동일하게 적용된다'], 'answer': 1, 'kr': '수석 연구원인 에딘버러 대학교의 Amara Osei 박사는 연구 결과가 비구조적 업무 환경에 대한 전반적인 지지로 해석되어서는 안 된다고 경고했다. 오히려 그녀는 관리자가 업무 특성, 개별 직원 특성, 조직 목표에 따라 제공되는 자율성 정도를 조정하는 세밀하고 역할별 접근 방식을 지지했다.', 'expressions': [{'expr': 'blanket endorsement', 'meaning': '전반적인 지지'}, {'expr': 'nuanced approach', 'meaning': '세밀한 접근 방식'}, {'expr': 'calibrate the degree of autonomy', 'meaning': '자율성 정도를 조정하다'}]}]}, {'title': '☠️ BLACKOUT', 'steps': [{'q_type': 'purpose', 'sentences': ['The City of Harlow has unveiled an ambitious 10-year urban development plan aimed at transforming the formerly industrial Eastbank district into a mixed-use hub integrating residential housing, commercial retail, cultural institutions, and green public spaces.', "The $2.4 billion initiative, the largest in the city's history, is designed to attract over 15,000 new residents and generate approximately 8,000 permanent jobs while addressing the city's acute affordable housing shortage."], 'question': 'What is the main purpose of this article?', 'question_kr': '이 기사의 주요 목적은 무엇인가?', 'choices': ['(A) To report on environmental problems in the Eastbank district', '(B) To announce a large-scale urban development project', "(C) To criticize the city's current housing policies", '(D) To promote investment opportunities in Harlow'], 'choices_kr': ['(A) Eastbank 지구의 환경 문제 보도', '(B) 대규모 도시 개발 프로젝트 발표', '(C) 시의 현재 주택 정책 비판', '(D) Harlow의 투자 기회 홍보'], 'answer': 1, 'kr': 'Harlow 시는 이전 산업 지구인 Eastbank를 주거, 상업 소매, 문화 기관, 녹지 공공 공간을 통합하는 복합 용도 허브로 변환하는 야심찬 10년 도시 개발 계획을 발표했다. 시 역사상 최대인 24억 달러 규모의 이 계획은 시의 심각한 저렴한 주택 부족 문제를 해결하면서 15,000명 이상의 신규 주민을 유치하고 약 8,000개의 영구 일자리를 창출하도록 설계되었다.', 'expressions': [{'expr': 'mixed-use hub', 'meaning': '복합 용도 허브'}, {'expr': 'acute affordable housing shortage', 'meaning': '심각한 저렴한 주택 부족'}, {'expr': 'generate permanent jobs', 'meaning': '영구 일자리를 창출하다'}]}, {'q_type': 'detail', 'sentences': ['The plan mandates that 30 percent of all new residential units be designated as affordable housing, with rental rates capped at no more than 30 percent of the median household income for the area.', 'Additionally, a new waterfront promenade, three public parks, and a 5,000-seat performing arts center are included in the development blueprint, with construction expected to begin in phases starting next spring.'], 'question': 'What percentage of new residential units will be designated as affordable housing?', 'question_kr': '신규 주거 단위의 몇 퍼센트가 저렴한 주택으로 지정되는가?', 'choices': ['(A) 10 percent', '(B) 20 percent', '(C) 30 percent', '(D) 40 percent'], 'choices_kr': ['(A) 10퍼센트', '(B) 20퍼센트', '(C) 30퍼센트', '(D) 40퍼센트'], 'answer': 2, 'kr': '계획은 모든 신규 주거 단위의 30%를 저렴한 주택으로 지정하고, 임대료를 지역 중위 가구 소득의 30% 이하로 제한할 것을 규정한다. 또한 새로운 수변 산책로, 3개의 공원, 5,000석 규모의 공연 예술 센터가 개발 청사진에 포함되어 있으며, 내년 봄부터 단계별로 건설이 시작될 예정이다.', 'expressions': [{'expr': 'designated as affordable housing', 'meaning': '저렴한 주택으로 지정된'}, {'expr': 'median household income', 'meaning': '중위 가구 소득'}, {'expr': 'waterfront promenade', 'meaning': '수변 산책로'}]}, {'q_type': 'inference', 'sentences': ['The proposal has drawn both enthusiasm and opposition from community stakeholders.', "Residents' groups have welcomed the affordable housing provisions but expressed concern that the influx of commercial development may accelerate gentrification and displace long-term residents who cannot afford the anticipated increases in property values and living costs.", 'City planners have responded by commissioning an independent socioeconomic impact assessment, the results of which will inform any modifications to the final plan before it is submitted for council approval.'], 'question': 'What can be inferred about the development plan?', 'question_kr': '개발 계획에 대해 추론할 수 있는 것은?', 'choices': ['(A) It has received unanimous approval from all residents', '(B) It may be modified based on an upcoming impact assessment', '(C) It will be financed entirely through private investment', "(D) It is expected to reduce the city's population"], 'choices_kr': ['(A) 모든 주민으로부터 만장일치의 승인을 받았다', '(B) 곧 있을 영향 평가를 바탕으로 수정될 수 있다', '(C) 전액 민간 투자로 재원이 조달될 것이다', '(D) 시의 인구를 줄일 것으로 예상된다'], 'answer': 1, 'kr': '이 제안은 지역 사회 이해관계자들로부터 열정과 반대 모두를 불러일으켰다. 주민 단체들은 저렴한 주택 조항을 환영하면서도 상업 개발 유입이 젠트리피케이션을 가속화하고 예상되는 부동산 가치와 생활비 상승을 감당할 수 없는 장기 거주자들을 퇴거시킬 수 있다는 우려를 표명했다. 시 계획가들은 독립적인 사회경제적 영향 평가를 의뢰하여, 그 결과가 최종 계획을 시의회 승인을 위해 제출하기 전에 수정 사항을 알릴 것이라고 대응했다.', 'expressions': [{'expr': 'accelerate gentrification', 'meaning': '젠트리피케이션을 가속화하다'}, {'expr': 'socioeconomic impact assessment', 'meaning': '사회경제적 영향 평가'}, {'expr': 'submitted for council approval', 'meaning': '시의회 승인을 위해 제출된'}]}]}, {'title': '☠️ BLACKOUT', 'steps': [{'q_type': 'purpose', 'sentences': ['BioPharma Innovations announced Thursday that its experimental treatment for treatment-resistant depression, designated BPI-4400, has successfully completed Phase III clinical trials with statistically significant results, clearing the final regulatory hurdle before the company submits a New Drug Application to the Federal Health Authority.', 'The trials, which enrolled 2,800 participants across 14 countries over a three-year period, demonstrated that BPI-4400 produced a clinically meaningful reduction in depressive symptoms in 68 percent of patients who had previously failed to respond to at least two conventional antidepressant therapies.'], 'question': 'What is this article primarily reporting?', 'question_kr': '이 기사가 주로 보도하는 것은 무엇인가?', 'choices': ['(A) The approval of a new depression medication by health authorities', '(B) The successful completion of clinical trials for an experimental drug', '(C) A controversy over the safety of antidepressant medications', '(D) The merger of two pharmaceutical companies'], 'choices_kr': ['(A) 보건 당국의 새로운 우울증 약물 승인', '(B) 실험적 약물의 임상시험 성공적 완료', '(C) 항우울제 안전성에 대한 논란', '(D) 두 제약 회사의 합병'], 'answer': 1, 'kr': 'BioPharma Innovations는 치료 저항성 우울증을 위한 실험적 치료제 BPI-4400이 통계적으로 유의미한 결과로 3상 임상시험을 성공적으로 완료하여, 회사가 Federal Health Authority에 신약 신청서를 제출하기 전 마지막 규제 장벽을 넘었다고 목요일에 발표했다. 3년에 걸쳐 14개국의 2,800명 참가자를 등록한 임상시험에서 BPI-4400은 이전에 최소 2가지 기존 항우울제 치료에 반응하지 않았던 환자의 68%에서 임상적으로 의미 있는 우울 증상 감소를 보였다.', 'expressions': [{'expr': 'Phase III clinical trials', 'meaning': '3상 임상시험'}, {'expr': 'treatment-resistant depression', 'meaning': '치료 저항성 우울증'}, {'expr': 'New Drug Application', 'meaning': '신약 신청서'}]}, {'q_type': 'detail', 'sentences': ["Unlike existing therapies, BPI-4400 operates through a novel mechanism targeting the brain's glutamate signaling pathways rather than the serotonin system, which may explain its efficacy in populations that have not benefited from traditional treatments.", 'The most commonly reported adverse effects were mild and transient, including temporary dizziness and nausea, with no serious neurological events recorded during the trial period.'], 'question': 'How does BPI-4400 differ from existing antidepressant treatments?', 'question_kr': 'BPI-4400은 기존 항우울제 치료와 어떻게 다른가?', 'choices': ['(A) It targets a different brain signaling pathway', '(B) It requires fewer doses per week than current medications', '(C) It was developed specifically for mild depression', '(D) It has no reported side effects in clinical trials'], 'choices_kr': ['(A) 다른 뇌 신호 경로를 대상으로 한다', '(B) 현재 약물보다 주당 복용 횟수가 적다', '(C) 경미한 우울증을 위해 특별히 개발되었다', '(D) 임상시험에서 보고된 부작용이 없다'], 'answer': 0, 'kr': '기존 치료제와 달리 BPI-4400은 세로토닌 시스템이 아닌 뇌의 글루타메이트 신호 경로를 표적으로 하는 새로운 메커니즘을 통해 작용하며, 이는 전통적인 치료에서 효과를 보지 못한 환자들에게서의 효능을 설명할 수 있다. 가장 일반적으로 보고된 부작용은 일시적인 현기증과 메스꺼움을 포함하여 경미하고 일시적이었으며, 시험 기간 동안 심각한 신경학적 사건은 기록되지 않았다.', 'expressions': [{'expr': 'glutamate signaling pathways', 'meaning': '글루타메이트 신호 경로'}, {'expr': 'adverse effects', 'meaning': '부작용'}, {'expr': 'transient', 'meaning': '일시적인'}]}, {'q_type': 'inference', 'sentences': ['Industry analysts estimate that if approved, BPI-4400 could generate annual revenues of between $3 and $5 billion within five years of launch, given the substantial unmet medical need in the treatment-resistant depression market.', "However, health economists have cautioned that the drug's pricing strategy will be closely scrutinized by payers and patient advocacy groups, particularly in light of the significant public investment that supported the foundational research underlying its development."], 'question': "What can be inferred about BPI-4400's market prospects?", 'question_kr': 'BPI-4400의 시장 전망에 대해 추론할 수 있는 것은?', 'choices': ['(A) Its commercial success is guaranteed due to high demand', '(B) Its pricing may face pressure from various stakeholders', '(C) It will be sold exclusively in the domestic market', '(D) Analysts expect it to replace all existing antidepressants'], 'choices_kr': ['(A) 높은 수요로 인해 상업적 성공이 보장되어 있다', '(B) 다양한 이해관계자들로부터 가격 압박을 받을 수 있다', '(C) 국내 시장에서만 독점적으로 판매될 것이다', '(D) 분석가들은 기존 모든 항우울제를 대체할 것으로 예상한다'], 'answer': 1, 'kr': '업계 분석가들은 승인될 경우, 치료 저항성 우울증 시장의 상당한 미충족 의료 수요를 감안할 때 BPI-4400이 출시 5년 내에 연간 30억~50억 달러의 수익을 창출할 수 있다고 추정한다. 그러나 의료 경제학자들은 약물의 가격 전략이 특히 개발의 기초가 된 연구를 지원한 상당한 공공 투자를 고려할 때 보험사와 환자 옹호 단체의 면밀한 검토를 받을 것이라고 경고했다.', 'expressions': [{'expr': 'unmet medical need', 'meaning': '미충족 의료 수요'}, {'expr': 'closely scrutinized', 'meaning': '면밀히 검토되다'}, {'expr': 'patient advocacy groups', 'meaning': '환자 옹호 단체'}]}]}, {'title': '☠️ BLACKOUT', 'steps': [{'q_type': 'purpose', 'sentences': ['A comprehensive analysis released by the Global Trade Institute reveals that multinational corporations have been systematically restructuring their supply chains in response to escalating geopolitical tensions, pandemic-era disruptions, and the growing vulnerability of single-source procurement models.', "The report documents a pronounced shift from efficiency-driven, just-in-time sourcing frameworks toward more resilient, geographically diversified supply networks, a trend the institute's researchers have termed 'strategic supply chain decoupling.'"], 'question': 'What is the main subject of this report?', 'question_kr': '이 보고서의 주요 주제는 무엇인가?', 'choices': ['(A) The financial performance of multinational corporations', '(B) Changes in global supply chain strategies by major companies', '(C) New trade regulations introduced by international bodies', '(D) The environmental impact of global shipping networks'], 'choices_kr': ['(A) 다국적 기업들의 재무 실적', '(B) 주요 기업들의 글로벌 공급망 전략 변화', '(C) 국제 기관이 도입한 새로운 무역 규정', '(D) 글로벌 해운 네트워크의 환경적 영향'], 'answer': 1, 'kr': "Global Trade Institute가 발표한 종합 분석에 따르면 다국적 기업들이 고조되는 지정학적 긴장, 팬데믹 시대의 혼란, 단일 소스 조달 모델의 증가하는 취약성에 대응하여 공급망을 체계적으로 재편하고 있다. 보고서는 효율성 중심의 적시 조달 프레임워크에서 더 탄력적이고 지리적으로 다양화된 공급망으로의 뚜렷한 전환을 문서화하며, 연구자들은 이 추세를 '전략적 공급망 디커플링'이라고 명명했다.", 'expressions': [{'expr': 'just-in-time sourcing', 'meaning': '적시 조달'}, {'expr': 'geographically diversified', 'meaning': '지리적으로 다양화된'}, {'expr': 'supply chain decoupling', 'meaning': '공급망 디커플링'}]}, {'q_type': 'detail', 'sentences': ['Among the sectors most aggressively pursuing supply chain diversification, the semiconductor, pharmaceutical, and critical minerals industries were identified as leaders, driven by their strategic importance and the disproportionate risks they faced during recent global disruptions.', 'The report found that companies in these sectors have on average increased the number of approved suppliers by 34 percent and established secondary production facilities in at least two additional geographic regions compared to their pre-2020 configurations.'], 'question': 'According to the report, by how much have companies in key sectors increased their approved suppliers?', 'question_kr': '보고서에 따르면, 핵심 부문의 기업들은 승인된 공급업체를 얼마나 증가시켰는가?', 'choices': ['(A) By 20 percent', '(B) By 34 percent', '(C) By 50 percent', '(D) By 60 percent'], 'choices_kr': ['(A) 20퍼센트', '(B) 34퍼센트', '(C) 50퍼센트', '(D) 60퍼센트'], 'answer': 1, 'kr': '공급망 다양화를 가장 적극적으로 추진하는 부문 중 반도체, 제약, 핵심 광물 산업이 전략적 중요성과 최근 글로벌 혼란 기간 동안 직면한 불균형적 위험으로 인해 선두 주자로 확인되었다. 보고서는 이 부문의 기업들이 2020년 이전 구성과 비교하여 평균 34% 승인된 공급업체 수를 늘리고 최소 2개 추가 지역에 2차 생산 시설을 구축했다는 것을 발견했다.', 'expressions': [{'expr': 'approved suppliers', 'meaning': '승인된 공급업체'}, {'expr': 'secondary production facilities', 'meaning': '2차 생산 시설'}, {'expr': 'disproportionate risks', 'meaning': '불균형적 위험'}]}, {'q_type': 'inference', 'sentences': ["The institute's economists acknowledge that supply chain diversification entails significant short-term costs, including higher inventory expenses, redundant infrastructure, and elevated per-unit procurement costs.", 'Nevertheless, they argue that these expenditures represent a rational risk premium given the demonstrated capacity of concentrated supply chains to generate catastrophic operational disruptions, as evidenced by the semiconductor shortages and pharmaceutical supply failures witnessed between 2020 and 2023.'], 'question': "What can be inferred from the economists' assessment?", 'question_kr': '경제학자들의 평가에서 추론할 수 있는 것은?', 'choices': ['(A) Companies are willing to accept higher costs in exchange for greater supply security', '(B) Supply chain diversification is expected to reduce overall production costs', '(C) The semiconductor shortage was caused by excessive supply chain diversification', '(D) Most companies have already completed their supply chain restructuring'], 'choices_kr': ['(A) 기업들은 더 큰 공급 안보를 위해 더 높은 비용을 감수할 의향이 있다', '(B) 공급망 다양화는 전반적인 생산 비용을 절감할 것으로 예상된다', '(C) 반도체 부족은 과도한 공급망 다양화로 인해 발생했다', '(D) 대부분의 기업들이 이미 공급망 재편을 완료했다'], 'answer': 0, 'kr': '연구소 경제학자들은 공급망 다양화가 더 높은 재고 비용, 중복 인프라, 높아진 단위당 조달 비용을 포함한 상당한 단기 비용을 수반한다고 인정한다. 그럼에도 그들은 2020년부터 2023년 사이에 목격된 반도체 부족과 의약품 공급 실패로 입증된 집중된 공급망이 파국적인 운영 혼란을 초래할 수 있는 능력을 고려할 때 이 지출이 합리적인 위험 프리미엄을 나타낸다고 주장한다.', 'expressions': [{'expr': 'risk premium', 'meaning': '위험 프리미엄'}, {'expr': 'concentrated supply chains', 'meaning': '집중된 공급망'}, {'expr': 'catastrophic operational disruptions', 'meaning': '파국적인 운영 혼란'}]}]}]}

# ═══ 유틸 ═══
def pick_passage(cat):
    import random as _rnd
    pool = PASSAGES.get(cat, [])
    if isinstance(pool, list):
        return _rnd.choice(pool)
    return pool

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

/* SIGNAL LV.1 초록 */
div[data-testid="stButton"] button.p7art{
  background:#060e0a!important;border-color:#1a6633!important;color:#33aa66!important;
}
div[data-testid="stButton"] button.p7art p{color:#33aa66!important;}
div[data-testid="stButton"] button.p7art.p7sel{
  background:#081a10!important;border-color:#00cc66!important;border-width:2px!important;
  color:#00ccee!important;box-shadow:0 0 20px rgba(0,200,238,0.5)!important;
}
div[data-testid="stButton"] button.p7art.p7sel p{color:#00ccee!important;}

/* CIPHER LV.2 노랑 */
div[data-testid="stButton"] button.p7let{
  background:#0e0e06!important;border-color:#666600!important;color:#aaaa33!important;
}
div[data-testid="stButton"] button.p7let p{color:#aaaa33!important;}
div[data-testid="stButton"] button.p7let.p7sel{
  background:#1a1800!important;border-color:#cccc00!important;border-width:2px!important;
  color:#ffff44!important;box-shadow:0 0 20px rgba(204,204,0,0.5)!important;
}
div[data-testid="stButton"] button.p7let.p7sel p{color:#ffff44!important;}

/* DECRYPT LV.3 주황 */
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

    # ── 지문 선택 (SIGNAL/CIPHER/DECRYPT/BLACKOUT 4개 한 줄) ──
    st.markdown('''<div style="font-size:10px;color:#dd88aa;letter-spacing:4px;padding:14px 0 7px;font-weight:900;">
      ⚔  TARGET CLASSIFICATION</div>''', unsafe_allow_html=True)
    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1:
        if st.button("📢\nSIGNAL\n광고·공지\n▂░░░", key="p7c1", use_container_width=True):
            st.session_state.p7_cat="article"; st.rerun()
    with pc2:
        if st.button("✉️\nCIPHER\n편지·이메일\n▂▄░░", key="p7c2", use_container_width=True):
            st.session_state.p7_cat="letter"; st.rerun()
    with pc3:
        if st.button("📰\nINTERCEPT\n기사·안내\n▂▄▆░", key="p7c3", use_container_width=True):
            st.session_state.p7_cat="notice"; st.rerun()
    with pc4:
        if st.button("☠️\nBLACKOUT\n고난도\n▂▄▆█", key="p7c4", use_container_width=True):
            st.session_state.p7_cat="information"; st.rerun()

    # ── 생존 규칙 ──
    st.markdown('<div style="text-align:center;padding:16px 0 3px;font-size:0.82rem;font-weight:900;color:#00ffcc;letter-spacing:1px;text-shadow:0 0 10px #00ffcc88;">☠ 오판 1회 = 작전 종료 · 통신 두절 = 즉시 철수</div>', unsafe_allow_html=True)

    # ── 출격 버튼 ──
    if _ready:
        _cat_name = {"article":"📢 SIGNAL","letter":"✉️ CIPHER","notice":"📰 INTERCEPT","information":"☠️ BLACKOUT"}.get(cat, cat)
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
      if(txt.indexOf("SIGNAL")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("p7pass","p7art");
        if(selC==="article") b.classList.add("p7sel"); else b.classList.remove("p7sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("p7art");if(selC==="article")p.classList.add("p7sel");else p.classList.remove("p7sel");}});
      }}
      if(txt.indexOf("CIPHER")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("p7pass","p7let");
        if(selC==="letter") b.classList.add("p7sel"); else b.classList.remove("p7sel");
        b.querySelectorAll("p").forEach(function(p){{p.classList.add("p7let");if(selC==="letter")p.classList.add("p7sel");else p.classList.remove("p7sel");}});
      }}
      if(txt.indexOf("INTERCEPT")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
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
    for i, ch in enumerate(cur["choices"]):
        _ch_clean = ch.split(") ",1)[-1] if ") " in ch else ch
        _bid = _btn_ids[i]
        st.markdown(f'<div id="btn-{_bid}">', unsafe_allow_html=True)
        if st.button(f"【{_btn_labels[i]}】  {_ch_clean}", key=f"p7ch{step}_{i}", use_container_width=True):
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
                st.session_state.p7_phase = "victory"; st.rerun()
            else:
                st.session_state.p7_step += 1
            st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    components.html("""
    <script>
    function p7choiceColors(){
        const doc=window.parent.document;
        const btns=doc.querySelectorAll('button[kind="primary"]');
        const colors=[
            {bg:'#0f0f1e',bd:'1px solid #1a1a2a',bl:'4px solid #00ccee'},
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
        <div style="font-size:0.9rem;color:#00ccee;font-weight:600;letter-spacing:2px;margin-top:4px;">📡 암호해독 작전 클리어!</div>
    </div>''', unsafe_allow_html=True)
    st.markdown(f'''<div style="background:#0c0c1e;border:1.5px solid #00ccee;border-left:4px solid #00ccee;border-radius:12px;padding:10px;text-align:center;margin:8px 0;">
        <div style="font-size:0.75rem;color:#9aa5b4;margin-bottom:2px;">이번 결과</div>
        <div style="font-size:1.5rem;font-weight:900;color:#00ccee;">✅ {_ok} / 3</div>
    </div>''', unsafe_allow_html=True)
    st.markdown('''<div style="background:#0a0800;border:1px solid #00ccee;border-radius:10px;padding:8px;text-align:center;margin-bottom:10px;">
        <div style="font-size:0.82rem;color:#00ccee;font-weight:700;">⚡ 3번 반복하면 장기기억 전환율 3배!</div>
        <div style="font-size:0.72rem;color:#555;margin-top:2px;">지금 브리핑에서 핵심표현 무기로 장착하라!</div>
    </div>''', unsafe_allow_html=True)
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
    if bi >= num_steps: bi = num_steps - 1

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

    # ── 배너 ──
    if was_victory:
        st.markdown(f'''<div style="background:#001520;border:2px solid #00ccee;border-left:5px solid #00ccee;
            border-radius:10px;padding:9px 12px;">
          <div style="font-family:Orbitron,monospace;font-size:11px;font-weight:900;
            color:#00ccee;letter-spacing:2px;">📡 OP.1 · MISSION COMPLETE</div>
          <div style="font-size:10px;color:#55aacc;font-weight:700;margin-top:3px;letter-spacing:1px;">
            ✅ {ok_cnt} CAPTURED &nbsp;·&nbsp; ❌ {miss_cnt} MISSED &nbsp;·&nbsp; 📋 {data.get("title","")}</div>
        </div>''', unsafe_allow_html=True)
    else:
        st.markdown(f'''<div style="background:#0c0008;border:2px solid #FF2D55;border-left:5px solid #FF2D55;
            border-radius:10px;padding:9px 12px;">
          <div style="font-family:Orbitron,monospace;font-size:11px;font-weight:900;
            color:#FF2D55;letter-spacing:2px;">📡 OP.1 · MISSION FAILED</div>
          <div style="font-size:10px;color:#ee6688;font-weight:700;margin-top:3px;letter-spacing:1px;">
            ✅ {ok_cnt} CAPTURED &nbsp;·&nbsp; ❌ {miss_cnt} MISSED &nbsp;·&nbsp; 📋 {data.get("title","")}</div>
        </div>''', unsafe_allow_html=True)

    # ── Q 탭 ──
    tab_cols = st.columns(num_steps)
    for ti in range(num_steps):
        with tab_cols[ti]:
            _ok_i = answers[ti] if ti < len(answers) else None
            _dot  = "✅" if _ok_i else "❌" if _ok_i is not None else ""
            if st.button(f"Q{ti+1} {_dot}", key=f"br_tab_{ti}", use_container_width=True):
                st.session_state.p7_br_idx = ti; st.rerun()

    # ── 현재 스텝 데이터 ──
    s = steps[bi]
    ok = answers[bi] if bi < len(answers) else False
    sym = "✅" if ok else "❌"
    correct_choice = s["choices"][s["answer"]]
    _mark_style = "color:#00ffaa;font-weight:900;border-bottom:2px solid #00ffaa;padding:0 2px;"
    _exprs_list = [e.get("expr","") for e in s.get("expressions", []) if e.get("expr")]
    c_kr = s.get("choices_kr", [])
    answer_kr = c_kr[s["answer"]] if c_kr and s["answer"] < len(c_kr) else ""
    kr_full = s.get("kr", "")
    # 문장 분리 — 숫자 뒤 마침표(2.3 등)는 분리 안 함
    import re as _re_kr
    _kr_tmp = _re_kr.sub(r'(?<![0-9])[.](?![0-9])', '.|', kr_full)
    _kr_tmp = _kr_tmp.replace("!","!|").replace("?","?|")
    kr_sents = [x.strip() for x in _kr_tmp.split("|") if x.strip()]

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
    for si, sent in enumerate(s["sentences"]):
        sent_key = f"br_sent_saved_{bi}_{si}"
        if sent_key not in st.session_state: st.session_state[sent_key] = False
        is_saved = st.session_state[sent_key]
        sent_kr = kr_sents[si] if si < len(kr_sents) else kr_full

        # 표현 하이라이트
        _hl = sent
        for _ex in _exprs_list:
            if _ex.lower() in _hl.lower():
                try: _hl = _re3.sub(f"(?i)({_re3.escape(_ex)})", f'<span style="{_mark_style}">\\1</span>', _hl)
                except: pass

        # 이 문장에 포함된 표현만 추출 (저장용 + 하이라이트용)
        _sent_lower = sent.lower()
        _sent_exprs = [
            e for e in s.get("expressions", [])
            if e.get("expr") and e.get("expr","").lower() in _sent_lower
        ]
        _card_border = "#00aacc" if ok else "#ff4466"

        if is_saved:
            # 저장 완료 — 태그 없이 하이라이트만
            st.markdown(
                f'<div style="background:#04080a;border:1.5px solid rgba(0,150,100,0.25);border-left:4px solid #336644;border-radius:12px;padding:10px;opacity:0.85;">' +
                f'<div style="font-size:13px;font-weight:800;color:#ddeeff;line-height:1.75;margin-bottom:5px;">{_hl}</div>' +
                f'<div style="font-size:12px;color:#99bbcc;font-weight:600;margin-bottom:6px;">{sent_kr}</div>' +
                '<span style="background:#001520;border:1px solid #006688;border-radius:6px;padding:2px 8px;font-size:8px;color:#00ccee;font-weight:700;">✅ 포로 등록 완료 · 포로사령부 대기중</span>' +
                '</div>',
                unsafe_allow_html=True)
        else:
            # 미저장 — 태그 없이 하이라이트만
            st.markdown(
                f'<div style="background:#06090f;border:1.5px solid rgba(0,180,255,0.25);border-left:4px solid {_card_border};border-radius:12px;padding:10px;margin-bottom:2px;">' +
                f'<div style="font-size:13px;font-weight:800;color:#ddeeff;line-height:1.75;margin-bottom:5px;">{_hl}</div>' +
                f'<div style="font-size:12px;color:#99bbcc;font-weight:600;margin-bottom:6px;">{sent_kr}</div>' +
                '</div>',
                unsafe_allow_html=True)

            # 저장 버튼
            _sv_key = f"br_sv_{bi}_{si}"
            _btn_label = "💾 증거 확보! → 포로 등록" if ok else "💾 오답 증거 — 반드시 확보!"
            if st.button(_btn_label, key=_sv_key, use_container_width=True):
                sent_data = dict(s)
                sent_data["sentences"] = [sent]
                sent_data["kr"] = sent_kr
                # 1. 문장 → 포로사령부 (saved_expressions)
                save_expressions(_sent_exprs, step_data=sent_data)
                # 2. 문장 핵심 단어 → word_prison (DB 스캔)
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

    # ── 구분선 ──
    st.markdown('<div style="height:1px;background:#0e0e1e;margin:4px 0;"></div>', unsafe_allow_html=True)

    # ── 하단 네비 ──
    _nc1, _nc2 = st.columns([3, 1])
    with _nc1:
        if st.button("💀  포로사령부!", key="p7store", use_container_width=True):
            st.switch_page("pages/03_POW_HQ.py")
    with _nc2:
        if st.button("🏠 홈", key="p7lobby", use_container_width=True):
            for k in D: st.session_state[k] = D[k]
            _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
            if _nick:
                st.query_params["nick"] = _nick
                st.query_params["ag"] = "1"
            st.switch_page("main_hub.py")

    # ── JS: 버튼 클래스 부여 ──
    import streamlit.components.v1 as _br_cmp
    _br_cmp.html(f"""<script>
(function(){{
  var doc=window.parent.document;
  function applyBrClasses(){{
    doc.querySelectorAll("button").forEach(function(b){{
      var txt=(b.innerText||b.textContent||"").trim();
      if(!txt) return;
      if(txt.startsWith("Q") && (txt.indexOf("✅")>-1||txt.indexOf("❌")>-1||txt.match(/^Q\d/)))
        b.classList.add("br-qtab");
      if(txt.indexOf("증거 확보")>-1) b.classList.add("br-save");
      if(txt.indexOf("오답 증거")>-1) b.classList.add("br-save-wrong");
      if(txt.indexOf("포로사령부!")>-1) b.classList.add("br-pow");
      if(txt.indexOf("홈")>-1 && txt.length<5) b.classList.add("br-home");
    }});
    // 현재 Q탭 on 표시
    doc.querySelectorAll("button.br-qtab").forEach(function(b,i){{
      if(i==={bi}) b.classList.add("br-qtab-on");
      else b.classList.remove("br-qtab-on");
    }});
  }}
  setTimeout(applyBrClasses,120);
  setTimeout(applyBrClasses,450);
}})();
</script>""", height=0)

