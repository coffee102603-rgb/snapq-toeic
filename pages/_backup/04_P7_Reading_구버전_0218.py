"""P7 Reading Arena — 60초 독해 전투 (V2)"""
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import random, time, json, os

st.set_page_config(page_title="P7 Reading ⚔️", page_icon="📖", layout="wide", initial_sidebar_state="collapsed")

# ═══ STORAGE ═══
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
def save_expressions(exprs, step_data=None):
    data=load_storage()
    if "saved_expressions" not in data: data["saved_expressions"]=[]
    for e in exprs:
        # 문장+해석 추가
        enriched = dict(e)
        if step_data:
            enriched["sentences"] = step_data.get("sentences", [])
            enriched["kr"] = step_data.get("kr", "")
        # 중복 체크 (expr 기준)
        exists = any(x.get("expr") == e.get("expr") for x in data["saved_expressions"])
        if not exists:
            data["saved_expressions"].append(enriched)
    save_storage(data)

# ═══ CSS (공통) ═══
st.markdown("""<style>
.stApp{background:linear-gradient(180deg,#0a0a1a,#0e1028,#0a0a1a)!important;}
section[data-testid="stSidebar"]{background:#0a0a1a!important;}
.block-container{max-width:100%!important;padding-left:1rem!important;padding-right:1rem!important;}
@keyframes rb{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}
@keyframes hlDraw{from{background-size:0% 4px}to{background-size:100% 4px}}

/* 전투 버튼 */
button[kind="primary"]{background:linear-gradient(135deg,#cc2200,#ff4422,#ff6644)!important;color:#fff!important;border:2px solid #ff5533!important;border-radius:14px!important;font-size:2.1rem!important;font-weight:900!important;padding:1.2rem 1.4rem!important;box-shadow:0 0 15px rgba(255,68,34,0.4)!important;text-shadow:0 1px 3px rgba(0,0,0,0.5)!important;text-align:center!important;}
button[kind="primary"] p{font-size:2.1rem!important;font-weight:900!important;text-align:center!important;}
button[kind="secondary"]{background:linear-gradient(135deg,#0077aa,#00aacc,#00ccee)!important;color:#fff!important;border:2px solid #00bbdd!important;border-radius:14px!important;font-size:2.1rem!important;font-weight:900!important;padding:1.2rem 1.4rem!important;box-shadow:0 0 15px rgba(0,170,204,0.4)!important;text-shadow:0 1px 3px rgba(0,0,0,0.5)!important;text-align:center!important;}
button[kind="secondary"] p{font-size:2.1rem!important;font-weight:900!important;text-align:center!important;}

/* P7 지문 카드 */
.p7-pass{background:linear-gradient(145deg,#0a1520,#101a2a);border:2px solid #00aacc;border-radius:18px;padding:1.5rem;margin:0.5rem 0;}
.p7-sent{color:#e8e8e8;font-size:1.85rem;font-weight:700;line-height:1.9;}
.p7-new{color:#44ffcc;font-weight:900;font-size:1.9rem;}
.p7-qbox{background:linear-gradient(145deg,#1a0a20,#2a1030);border:2px solid #cc44aa;border-radius:18px;padding:1.5rem;margin:0.5rem 0;}
.p7-q{color:#ffcc00;font-size:1.8rem;font-weight:800;line-height:1.8;}

/* 진행 표시 */
.p7-step{text-align:center;font-size:1.2rem;font-weight:900;color:#44ffcc;margin:0.3rem 0;}
.p7-hud{background:linear-gradient(135deg,#0a1828,#0d2238);border:2px solid #00aacc;border-radius:14px;padding:0.8rem 1.2rem;margin:0.3rem 0;display:flex;justify-content:space-between;align-items:center;}
.p7-hud-l{font-size:1.3rem;font-weight:900;color:#44ffcc;}
.p7-hud-r{font-size:1.1rem;font-weight:800;color:#ffcc00;}

/* 브리핑 */
.p7-br-s{font-size:2rem;font-weight:700;color:#1a1a1a;line-height:2;margin-bottom:0.8rem;}
.p7-br-hl{color:#00aa88;font-weight:900;font-size:2.1rem;text-decoration:underline;text-underline-offset:5px;text-decoration-thickness:3px;}
.p7-br-kr{font-size:1.5rem;font-weight:600;color:#333;line-height:1.7;margin-bottom:0.5rem;}
.p7-br-ex{font-size:1.4rem;color:#444;line-height:1.6;padding:0.5rem 0.7rem;background:rgba(0,180,150,0.1);border-left:4px solid #00aa88;border-radius:0 10px 10px 0;}

/* VICTORY/LOST 배너 */
.p7-ban{text-align:center;padding:0.8rem;border-radius:14px;margin:0.3rem 0;font-size:1.3rem;font-weight:900;}
.p7-ban-v{background:linear-gradient(135deg,#005533,#00aa66);color:#fff;border:2px solid #00cc77;}
.p7-ban-l{background:linear-gradient(135deg,#550000,#aa0000);color:#fff;border:2px solid #cc0000;}
</style>""", unsafe_allow_html=True)

# ═══ 문제 데이터: 4개 카테고리 × 1세트 ═══
PASSAGES = {
"article": {
    "title": "📰 Article",
    "steps": [
        {
            "sentences": [
                "GreenTech Solutions has announced plans to open a new research facility in Austin, Texas.",
                "The company expects the facility to be fully operational by the third quarter of next year."
            ],
            "question": "What is GreenTech Solutions planning to do?",
            "question_kr": "GreenTech Solutions는 무엇을 할 계획인가?",
            "choices": ["(A) Hire new executives", "(B) Open a research facility", "(C) Merge with another company", "(D) Close its Texas office"],
            "choices_kr": ["(A) 새 임원 채용", "(B) 연구 시설 개설", "(C) 다른 회사와 합병", "(D) 텍사스 사무소 폐쇄"],
            "answer": 1,
            "kr": "GreenTech Solutions는 텍사스 오스틴에 새 연구 시설을 열 계획을 발표했다. 회사는 내년 3분기까지 시설이 완전히 가동될 것으로 예상한다.",
            "expressions": [
                {"expr": "be fully operational", "meaning": "완전히 가동되다"},
                {"expr": "announce plans to", "meaning": "~할 계획을 발표하다"},
                {"expr": "the third quarter", "meaning": "3분기"}
            ]
        },
        {
            "sentences": [
                "According to CEO Maria Chen, the facility will focus on developing sustainable energy storage systems.",
                "The project is expected to create over 200 jobs in the local community.",
                "GreenTech has already secured $50 million in funding from private investors."
            ],
            "question": "What will the new facility primarily focus on?",
            "question_kr": "새 시설은 주로 무엇에 집중할 것인가?",
            "choices": ["(A) Manufacturing solar panels", "(B) Training new employees", "(C) Developing energy storage systems", "(D) Conducting market research"],
            "choices_kr": ["(A) 태양광 패널 제조", "(B) 신입 직원 교육", "(C) 에너지 저장 시스템 개발", "(D) 시장 조사 수행"],
            "answer": 2,
            "kr": "CEO Maria Chen에 따르면 시설은 지속 가능한 에너지 저장 시스템 개발에 집중할 것이다. 이 프로젝트는 지역 사회에 200개 이상의 일자리를 창출할 것으로 예상된다. GreenTech는 이미 민간 투자자로부터 5천만 달러의 자금을 확보했다.",
            "expressions": [
                {"expr": "focus on", "meaning": "~에 집중하다"},
                {"expr": "secure funding", "meaning": "자금을 확보하다"},
                {"expr": "sustainable", "meaning": "지속 가능한"}
            ]
        },
        {
            "sentences": [
                "Local officials have expressed strong support for the project, citing its potential economic benefits.",
                "The city of Austin has offered tax incentives to encourage GreenTech's investment in the region.",
                "Construction of the facility is scheduled to begin in early January and will take approximately 14 months."
            ],
            "question": "How long will the construction of the facility take?",
            "question_kr": "시설 건설은 얼마나 걸릴 것인가?",
            "choices": ["(A) About 6 months", "(B) About 10 months", "(C) About 14 months", "(D) About 18 months"],
            "choices_kr": ["(A) 약 6개월", "(B) 약 10개월", "(C) 약 14개월", "(D) 약 18개월"],
            "answer": 2,
            "kr": "지역 관리들은 잠재적 경제적 이점을 들어 프로젝트를 강력히 지지했다. 오스틴 시는 이 지역에 대한 GreenTech의 투자를 장려하기 위해 세금 혜택을 제공했다. 시설 건설은 1월 초에 시작되어 약 14개월이 소요될 예정이다.",
            "expressions": [
                {"expr": "tax incentives", "meaning": "세금 혜택/인센티브"},
                {"expr": "approximately", "meaning": "대략, 약"},
                {"expr": "be scheduled to", "meaning": "~할 예정이다"}
            ]
        }
    ]
},
"letter": {
    "title": "✉️ Letter",
    "steps": [
        {
            "sentences": [
                "Dear Mr. Thompson, I am writing to inform you that your annual membership at Riverside Fitness Club has been approved for renewal.",
                "Your new membership period will begin on March 1 and will remain valid for twelve months."
            ],
            "question": "What is the purpose of this letter?",
            "question_kr": "이 편지의 목적은 무엇인가?",
            "choices": ["(A) To cancel a membership", "(B) To approve a membership renewal", "(C) To request a payment", "(D) To introduce a new program"],
            "choices_kr": ["(A) 회원권 취소", "(B) 회원권 갱신 승인", "(C) 결제 요청", "(D) 새 프로그램 소개"],
            "answer": 1,
            "kr": "Thompson씨에게 Riverside Fitness Club의 연간 회원권 갱신이 승인되었음을 알립니다. 새 회원 기간은 3월 1일에 시작되며 12개월간 유효합니다.",
            "expressions": [
                {"expr": "be approved for", "meaning": "~이 승인되다"},
                {"expr": "renewal", "meaning": "갱신, 연장"},
                {"expr": "remain valid", "meaning": "유효하다"}
            ]
        },
        {
            "sentences": [
                "As a valued member, you are entitled to a 15 percent discount on all personal training sessions.",
                "Additionally, we have recently upgraded our swimming pool and added a new yoga studio on the second floor.",
                "These improvements were made based on feedback from members like you."
            ],
            "question": "What benefit does Mr. Thompson receive as a member?",
            "question_kr": "Thompson씨는 회원으로서 어떤 혜택을 받는가?",
            "choices": ["(A) Free parking", "(B) A discount on training sessions", "(C) A complimentary meal plan", "(D) Priority booking for events"],
            "choices_kr": ["(A) 무료 주차", "(B) 트레이닝 세션 할인", "(C) 무료 식단 제공", "(D) 이벤트 우선 예약"],
            "answer": 1,
            "kr": "소중한 회원으로서 모든 개인 트레이닝 세션에 15% 할인을 받을 수 있습니다. 또한 수영장을 업그레이드하고 2층에 새 요가 스튜디오를 추가했습니다. 이 개선 사항은 회원들의 피드백을 기반으로 이루어졌습니다.",
            "expressions": [
                {"expr": "be entitled to", "meaning": "~할 자격/권리가 있다"},
                {"expr": "based on feedback", "meaning": "피드백을 기반으로"},
                {"expr": "complimentary", "meaning": "무료의, 무상의"}
            ]
        },
        {
            "sentences": [
                "Please note that the annual membership fee of $480 is due by February 20.",
                "Payment can be made online through our website or in person at the front desk.",
                "If you have any questions regarding your membership, please do not hesitate to contact us at (555) 234-5678."
            ],
            "question": "By when must the membership fee be paid?",
            "question_kr": "회원비는 언제까지 납부해야 하는가?",
            "choices": ["(A) By January 15", "(B) By February 20", "(C) By March 1", "(D) By March 15"],
            "choices_kr": ["(A) 1월 15일까지", "(B) 2월 20일까지", "(C) 3월 1일까지", "(D) 3월 15일까지"],
            "answer": 1,
            "kr": "연간 회원비 $480는 2월 20일까지 납부해야 합니다. 결제는 웹사이트 또는 프론트 데스크에서 직접 할 수 있습니다. 회원권 관련 문의는 (555) 234-5678로 연락하세요.",
            "expressions": [
                {"expr": "due by", "meaning": "~까지 납부/제출해야 하는"},
                {"expr": "do not hesitate to", "meaning": "주저하지 말고 ~하다"},
                {"expr": "regarding", "meaning": "~에 관하여"}
            ]
        }
    ]
},
"notice": {
    "title": "📋 Notice",
    "steps": [
        {
            "sentences": [
                "All employees are hereby notified that the main parking garage will be closed for maintenance starting Monday, April 7.",
                "The closure is expected to last for two weeks."
            ],
            "question": "What will happen starting April 7?",
            "question_kr": "4월 7일부터 무슨 일이 일어나는가?",
            "choices": ["(A) A new office will open", "(B) The parking garage will close", "(C) Employee reviews will begin", "(D) A training session will start"],
            "choices_kr": ["(A) 새 사무실 개장", "(B) 주차장 폐쇄", "(C) 직원 평가 시작", "(D) 교육 세션 시작"],
            "answer": 1,
            "kr": "모든 직원에게 주 주차장이 4월 7일 월요일부터 유지보수를 위해 폐쇄됨을 알립니다. 폐쇄는 2주간 지속될 예정입니다.",
            "expressions": [{"expr": "be closed for maintenance", "meaning": "유지보수를 위해 폐쇄되다"}, {"expr": "hereby", "meaning": "이로써, 이에"}, {"expr": "closure", "meaning": "폐쇄, 휴업"}]
        },
        {
            "sentences": [
                "During this period, employees may use the temporary parking lot located at 45 Oak Street, approximately a five-minute walk from the office.",
                "A free shuttle service will operate between the temporary lot and the main entrance every 15 minutes from 7:00 A.M. to 7:00 P.M.",
                "Employees who wish to use the shuttle should display their company ID badges."
            ],
            "question": "How often will the shuttle service run?",
            "question_kr": "셔틀 서비스는 얼마나 자주 운행되는가?",
            "choices": ["(A) Every 5 minutes", "(B) Every 10 minutes", "(C) Every 15 minutes", "(D) Every 30 minutes"],
            "choices_kr": ["(A) 5분마다", "(B) 10분마다", "(C) 15분마다", "(D) 30분마다"],
            "answer": 2,
            "kr": "이 기간 동안 직원들은 사무실에서 도보 약 5분 거리인 45 Oak Street의 임시 주차장을 이용할 수 있습니다. 무료 셔틀이 오전 7시부터 오후 7시까지 15분 간격으로 운행됩니다. 셔틀 이용 시 사원증을 제시해야 합니다.",
            "expressions": [{"expr": "approximately", "meaning": "대략, 약"}, {"expr": "temporary", "meaning": "임시의"}, {"expr": "display", "meaning": "제시하다, 보여주다"}]
        },
        {
            "sentences": [
                "We apologize for any inconvenience this may cause and appreciate your patience during the renovation.",
                "The upgraded garage will feature additional spaces, improved lighting, and electric vehicle charging stations.",
                "For further information, please contact the Facilities Department at extension 4200."
            ],
            "question": "What improvement will the garage have after renovation?",
            "question_kr": "리모델링 후 주차장에 어떤 개선 사항이 있는가?",
            "choices": ["(A) A rooftop garden", "(B) A coffee shop", "(C) Electric vehicle charging stations", "(D) A fitness center"],
            "choices_kr": ["(A) 옥상 정원", "(B) 커피숍", "(C) 전기차 충전소", "(D) 피트니스 센터"],
            "answer": 2,
            "kr": "불편을 끼쳐 죄송하며 리모델링 기간 동안 양해 부탁드립니다. 업그레이드된 주차장에는 추가 공간, 개선된 조명, 전기차 충전소가 설치됩니다. 추가 정보는 시설 관리부 내선 4200으로 연락하세요.",
            "expressions": [{"expr": "apologize for any inconvenience", "meaning": "불편을 드려 죄송합니다"}, {"expr": "for further information", "meaning": "추가 정보는"}, {"expr": "feature", "meaning": "(특징으로) 갖추다"}]
        }
    ]
},
"information": {
    "title": "ℹ️ Information",
    "steps": [
        {
            "sentences": [
                "The Westfield Convention Center offers a variety of meeting rooms and event spaces for corporate and private use.",
                "All rooms are equipped with high-speed Wi-Fi, projectors, and sound systems at no additional charge."
            ],
            "question": "What is provided at no extra cost in the meeting rooms?",
            "question_kr": "회의실에서 추가 비용 없이 제공되는 것은?",
            "choices": ["(A) Catering services", "(B) Printed materials", "(C) Wi-Fi and projectors", "(D) Parking passes"],
            "choices_kr": ["(A) 케이터링 서비스", "(B) 인쇄 자료", "(C) Wi-Fi와 프로젝터", "(D) 주차 패스"],
            "answer": 2,
            "kr": "Westfield Convention Center는 기업 및 개인용 다양한 회의실과 이벤트 공간을 제공합니다. 모든 회의실에는 고속 Wi-Fi, 프로젝터, 음향 시스템이 추가 비용 없이 갖추어져 있습니다.",
            "expressions": [{"expr": "at no additional charge", "meaning": "추가 비용 없이"}, {"expr": "be equipped with", "meaning": "~을 갖추다"}, {"expr": "corporate", "meaning": "기업의, 법인의"}]
        },
        {
            "sentences": [
                "Catering services are available upon request and must be arranged at least 48 hours in advance.",
                "A dedicated event coordinator will be assigned to assist with planning and setup for groups of 50 or more.",
                "Discounted rates are offered for bookings made more than 30 days prior to the event date."
            ],
            "question": "How far in advance must catering be arranged?",
            "question_kr": "케이터링은 얼마나 미리 예약해야 하는가?",
            "choices": ["(A) 24 hours", "(B) 48 hours", "(C) 72 hours", "(D) One week"],
            "choices_kr": ["(A) 24시간 전", "(B) 48시간 전", "(C) 72시간 전", "(D) 1주일 전"],
            "answer": 1,
            "kr": "케이터링 서비스는 요청 시 이용 가능하며 최소 48시간 전에 예약해야 합니다. 50명 이상 그룹에는 전담 이벤트 코디네이터가 배정됩니다. 행사 30일 전 예약 시 할인 요금이 적용됩니다.",
            "expressions": [{"expr": "upon request", "meaning": "요청 시"}, {"expr": "in advance", "meaning": "미리, 사전에"}, {"expr": "prior to", "meaning": "~에 앞서, ~전에"}]
        },
        {
            "sentences": [
                "The center is conveniently located near the downtown transit hub, with direct access to bus and subway lines.",
                "On-site parking is available for up to 300 vehicles, and valet parking can be arranged for an additional fee.",
                "To make a reservation or request a tour of our facilities, please visit www.westfieldcc.com or call (555) 678-9012."
            ],
            "question": "How can someone make a reservation?",
            "question_kr": "예약은 어떻게 할 수 있는가?",
            "choices": ["(A) By visiting the center only", "(B) By email only", "(C) By website or phone", "(D) By fax only"],
            "choices_kr": ["(A) 센터 방문만", "(B) 이메일만", "(C) 웹사이트 또는 전화", "(D) 팩스만"],
            "answer": 2,
            "kr": "센터는 도심 교통 허브 근처에 위치하며 버스와 지하철에 직접 연결됩니다. 최대 300대 주차 가능하며 추가 요금으로 발렛 파킹도 가능합니다. 예약이나 시설 투어는 웹사이트 또는 전화로 문의하세요.",
            "expressions": [{"expr": "conveniently located", "meaning": "편리하게 위치한"}, {"expr": "on-site", "meaning": "현장의, 구내의"}, {"expr": "valet parking", "meaning": "발렛 파킹"}]
        }
    ]
}
}

# ═══ 유틸 ═══
def pick_passage(cat):
    return PASSAGES[cat]

# ═══ 세션 초기화 ═══
D = {"p7_phase":"lobby","p7_cat":None,"p7_tsec":80,"p7_step":0,
     "p7_started_at":None,"p7_answers":[],"p7_data":None,"p7_br_idx":0}
for k,v in D.items():
    if k not in st.session_state: st.session_state[k]=v

# ═══════════════════════════════════════
# PHASE: LOBBY
# ═══════════════════════════════════════
if st.session_state.p7_phase == "lobby":
    tsec = st.session_state.p7_tsec
    cat = st.session_state.p7_cat

    # 로비 CSS (청록/시안 테마)
    st.markdown("""<style>
    .p7rmt{max-width:95vw;margin:0 auto;background:linear-gradient(180deg,#0a1520,#0d1a2a);
        border-radius:32px;padding:24px 16px 16px 16px;border:3px solid #00aacc;
        box-shadow:0 8px 40px rgba(0,170,204,0.15);text-align:center;}
    .p7rmt-t{font-size:2.6rem;font-weight:900;
        background:linear-gradient(90deg,#00ccee,#44ffcc,#00aacc,#00eeff);
        background-size:300% 300%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
        animation:rb 4s ease infinite;letter-spacing:2px;}
    .p7rmt-s{font-size:0.85rem;color:#558899;letter-spacing:1px;}

    .p7zn{border-radius:18px;padding:18px 14px 14px 14px;margin:16px 0 8px 0;text-align:center;}
    .p7zn-t{background:linear-gradient(135deg,#0a1a28,#0d2235);border:2px solid #336677;}
    .p7zn-b{background:linear-gradient(135deg,#0a1520,#0d1a2a);border:3px solid #00aacc;}
    .p7zn-n{background:linear-gradient(135deg,#0a1a28,#0d2235);border:2px solid #336677;}
    .p7zl{font-size:1.8rem;font-weight:900;letter-spacing:6px;text-transform:uppercase;text-align:center;}
    .p7zl-t{color:#6699aa;}
    .p7zl-b{color:#00ddff;}
    .p7zl-n{color:#6699aa;}

    .p7dis{text-align:center;background:linear-gradient(135deg,#006688,#008899);border:3px solid #333;border-radius:50px;
        padding:20px;font-size:2.2rem;opacity:0.35;margin:14px 0;font-weight:900;color:#fff;}

    button[kind="secondary"]{
        min-height:80px!important;border-radius:20px!important;
        font-size:2rem!important;font-weight:900!important;
        padding:20px 10px!important;color:#fff!important;
        text-shadow:0 2px 4px rgba(0,0,0,0.4)!important;
        border:3px solid #333!important;
        transition:transform 0.15s, box-shadow 0.15s!important;
    }
    button[kind="secondary"] p{
        font-size:2rem!important;font-weight:900!important;
        white-space:pre-line!important;line-height:1.3!important;
        text-align:center!important;margin:0!important;
    }
    @keyframes p7pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.02);box-shadow:0 0 25px rgba(0,255,200,0.25)}}
    </style>""", unsafe_allow_html=True)

    # 상단
    st.markdown('<div class="p7rmt"><div class="p7rmt-t">📖 P7 READING 📖</div><div class="p7rmt-s">TOEIC Part 7 · 독해 전투</div></div>', unsafe_allow_html=True)

    # TIMER
    st.markdown('<div class="p7zn p7zn-t"><div class="p7zl p7zl-t">⏱ T I M E R</div></div>', unsafe_allow_html=True)
    tc1,tc2,tc3 = st.columns(3)
    with tc1:
        if st.button("🔥 60초", key="p7t60", type="secondary", use_container_width=True):
            st.session_state.p7_tsec=60; st.rerun()
    with tc2:
        if st.button("⚡ 80초", key="p7t80", type="secondary", use_container_width=True):
            st.session_state.p7_tsec=80; st.rerun()
    with tc3:
        if st.button("✅ 100초", key="p7t100", type="secondary", use_container_width=True):
            st.session_state.p7_tsec=100; st.rerun()

    # CATEGORY
    st.markdown('<div class="p7zn p7zn-b"><div class="p7zl p7zl-b">📚 C A T E G O R Y</div></div>', unsafe_allow_html=True)
    b1,b2 = st.columns(2)
    with b1:
        if st.button("📰 Article\n기사·보도", key="p7c1", type="secondary", use_container_width=True):
            st.session_state.p7_cat="article"; st.rerun()
    with b2:
        if st.button("✉️ Letter\n편지·서신", key="p7c2", type="secondary", use_container_width=True):
            st.session_state.p7_cat="letter"; st.rerun()
    b3,b4 = st.columns(2)
    with b3:
        if st.button("📋 Notice\n공지·안내", key="p7c3", type="secondary", use_container_width=True):
            st.session_state.p7_cat="notice"; st.rerun()
    with b4:
        if st.button("ℹ️ Information\n정보·안내문", key="p7c4", type="secondary", use_container_width=True):
            st.session_state.p7_cat="information"; st.rerun()

    # START
    if cat and cat in PASSAGES:
        lbl = PASSAGES[cat]["title"] + " 전투!"
        if st.button(lbl, key="p7go", type="primary", use_container_width=True):
            st.session_state.p7_data = PASSAGES[cat]
            st.session_state.p7_step = 0
            st.session_state.p7_answers = []
            st.session_state.p7_started_at = time.time()
            st.session_state.p7_phase = "battle"
            st.rerun()
    else:
        st.markdown('<div class="p7dis">▶ START</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;color:#558899;font-size:0.95rem;font-weight:700;margin:6px 0;">↑ 카테고리를 선택하세요!</div>', unsafe_allow_html=True)

    # NAVIGATE
    st.markdown('<div class="p7zn p7zn-n"><div class="p7zl p7zl-n">🧭 N A V I G A T E</div></div>', unsafe_allow_html=True)
    nc1,nc2 = st.columns(2)
    with nc1:
        if st.button("📦 저장고", key="p7nav1", type="secondary", use_container_width=True):
            st.switch_page("pages/03_저장고.py")
    with nc2:
        if st.button("🏠 메인", key="p7nav2", type="secondary", use_container_width=True):
            st.switch_page("main_hub.py")

    # JS 색상 (로비)
    _sel60 = "border:4px solid #fff!important;box-shadow:0 0 20px rgba(0,255,200,0.5)!important;" if tsec==60 else ""
    _sel80 = "border:4px solid #fff!important;box-shadow:0 0 20px rgba(0,255,200,0.5)!important;" if tsec==80 else ""
    _sel100 = "border:4px solid #fff!important;box-shadow:0 0 20px rgba(0,255,200,0.5)!important;" if tsec==100 else ""
    _selA = "border:4px solid #fff!important;box-shadow:0 0 20px rgba(0,255,200,0.5)!important;" if cat=="article" else ""
    _selL = "border:4px solid #fff!important;box-shadow:0 0 20px rgba(0,255,200,0.5)!important;" if cat=="letter" else ""
    _selN = "border:4px solid #fff!important;box-shadow:0 0 20px rgba(0,255,200,0.5)!important;" if cat=="notice" else ""
    _selI = "border:4px solid #fff!important;box-shadow:0 0 20px rgba(0,255,200,0.5)!important;" if cat=="information" else ""

    components.html("""
    <script>
    function p7colors(){
        const doc=window.parent.document;
        if(!doc.getElementById('p7ps')){const s=doc.createElement('style');s.id='p7ps';
        s.textContent='@keyframes p7pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.02);box-shadow:0 0 25px rgba(0,255,200,0.25)}}';
        doc.head.appendChild(s);}
        const btns=doc.querySelectorAll('button[kind="secondary"]');
        const cm={
            '60':{bg:'linear-gradient(135deg,#1a4050,#2a5565)',s:'"""+_sel60+"""',x:'border:2px solid #447788!important;'},
            '80':{bg:'linear-gradient(135deg,#153848,#1e4858)',s:'"""+_sel80+"""',x:'border:2px solid #447788!important;'},
            '100':{bg:'linear-gradient(135deg,#103040,#183e4e)',s:'"""+_sel100+"""',x:'border:2px solid #447788!important;'},
            'Article':{bg:'linear-gradient(135deg,#cc4400,#ff6622)',s:'"""+_selA+"""',x:'border:3px solid #fff!important;animation:p7pulse 2s ease-in-out infinite!important;'},
            'Letter':{bg:'linear-gradient(135deg,#0088aa,#00bbdd)',s:'"""+_selL+"""',x:'border:3px solid #fff!important;animation:p7pulse 2s ease-in-out infinite!important;'},
            'Notice':{bg:'linear-gradient(135deg,#008855,#00cc77)',s:'"""+_selN+"""',x:'border:3px solid #fff!important;animation:p7pulse 2s ease-in-out infinite!important;'},
            'Information':{bg:'linear-gradient(135deg,#6633aa,#8855cc)',s:'"""+_selI+"""',x:'border:3px solid #fff!important;animation:p7pulse 2s ease-in-out infinite!important;'},
            '저장고':{bg:'linear-gradient(135deg,#1a4050,#2a5565)',s:'',x:'border:2px solid #447788!important;'},
            '메인':{bg:'linear-gradient(135deg,#1a4050,#2a5565)',s:'',x:'border:2px solid #447788!important;'}
        };
        btns.forEach(btn=>{
            const t=btn.textContent||'';
            for(const[k,st]of Object.entries(cm)){
                if(t.includes(k)){
                    btn.style.cssText='background:'+st.bg+'!important;'+st.x+'box-shadow:0 4px 15px rgba(0,100,120,0.3)!important;border-radius:20px!important;color:#fff!important;font-size:2rem!important;font-weight:900!important;text-shadow:0 2px 4px rgba(0,0,0,0.4)!important;text-align:center!important;padding:20px 10px!important;min-height:80px!important;'+st.s;
                    btn.querySelectorAll('p').forEach(p=>{p.style.cssText='text-align:center!important;font-size:2rem!important;font-weight:900!important;white-space:pre-line!important;line-height:1.3!important;margin:0!important;';});
                    break;
                }
            }
        });
        const pri=doc.querySelectorAll('button[kind="primary"]');
        pri.forEach(btn=>{
            const t=btn.textContent||'';
            if(t.includes('전투')){
                btn.style.cssText='background:linear-gradient(135deg,#006688,#00aacc)!important;border:3px solid #00ddff!important;border-radius:50px!important;padding:22px!important;font-size:2.4rem!important;font-weight:900!important;color:#fff!important;text-shadow:0 2px 6px rgba(0,0,0,0.5)!important;letter-spacing:3px!important;box-shadow:0 6px 30px rgba(0,170,204,0.4)!important;text-align:center!important;min-height:75px!important;';
                btn.querySelectorAll('p').forEach(p=>{p.style.cssText='font-size:2.4rem!important;font-weight:900!important;text-align:center!important;margin:0!important;';});
            }
        });
    }
    setTimeout(p7colors,200);setTimeout(p7colors,800);setTimeout(p7colors,2000);
    const obs=new MutationObserver(()=>{setTimeout(p7colors,100);});
    obs.observe(window.parent.document.body,{childList:true,subtree:true});
    </script>
    """, height=0)

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

    pass_html = '<div class="p7-sent">'
    for i, s in enumerate(all_sents):
        if i >= new_start:
            pass_html += f'<span class="p7-new">{s}</span> '
        else:
            pass_html += f'{s} '
    pass_html += '</div>'
    st.markdown(f'<div style="background:{pass_bg};border:2px solid {pass_border};border-radius:14px;padding:0.8rem 1rem;margin:0.3rem 0;box-shadow:{pass_shadow};transition:border-color 1s,background 1s;">{pass_html}</div>', unsafe_allow_html=True)

    # 질문 - [Q1] 형식 + 최소 패딩
    st.markdown(f'<div style="background:linear-gradient(145deg,#1a0a20,#2a1030);border:2px solid #cc44aa;border-radius:14px;padding:0.6rem 1rem;margin:0.3rem 0;text-align:center;"><div style="color:#ffcc00;font-size:1.7rem;font-weight:900;line-height:1.6;">[Q{step+1}] {cur["question"]}</div></div>', unsafe_allow_html=True)

    # 선택지 - 세로 4줄 + 글자 10% 작게
    for i, ch in enumerate(cur["choices"]):
        if st.button(ch, key=f"p7ch{step}_{i}", type="primary", use_container_width=True):
            ok = (i == cur["answer"])
            st.session_state.p7_answers.append(ok)

            if not ok:
                st.session_state.p7_phase = "lost"; st.rerun()

            if step >= 2:
                st.session_state.p7_phase = "victory"; st.rerun()
            else:
                st.session_state.p7_step += 1
                st.rerun()  # 타이머 리셋 안 함 (전체 시간 유지)

    # 전투용 버튼 CSS 오버라이드 (선택지 작게 + 패딩 최소)
    st.markdown("""<style>
    button[kind="primary"]{font-size:1.7rem!important;padding:0.7rem 1rem!important;min-height:auto!important;border-radius:12px!important;font-weight:900!important;text-shadow:0 1px 3px rgba(0,0,0,0.5)!important;}
    button[kind="primary"] p{font-size:1.7rem!important;font-weight:900!important;}
    </style>""", unsafe_allow_html=True)

    # 선택지 A/B/C/D 색상 구분
    components.html("""
    <script>
    function p7choiceColors(){
        const doc=window.parent.document;
        const btns=doc.querySelectorAll('button[kind="primary"]');
        const colors=[
            {bg:'linear-gradient(135deg,#cc3300,#ee4411)',bd:'2px solid #ff5533'},
            {bg:'linear-gradient(135deg,#cc6600,#ee7711)',bd:'2px solid #ffaa33'},
            {bg:'linear-gradient(135deg,#0077aa,#0099cc)',bd:'2px solid #33bbee'},
            {bg:'linear-gradient(135deg,#6633aa,#8844cc)',bd:'2px solid #aa66ee'}
        ];
        let ci=0;
        btns.forEach(btn=>{
            const t=btn.textContent||'';
            if(t.match(/\\(A\\)|\\(B\\)|\\(C\\)|\\(D\\)/)){
                const c=colors[ci%4];
                btn.style.background=c.bg;
                btn.style.border=c.bd;
                btn.style.textAlign='center';
                ci++;
            }
        });
    }
    setTimeout(p7choiceColors,200);setTimeout(p7choiceColors,800);setTimeout(p7choiceColors,2000);
    </script>
    """, height=0)

# ═══════════════════════════════════════
# PHASE: VICTORY
# ═══════════════════════════════════════
elif st.session_state.p7_phase == "victory":
    components.html("""
    <style>
    *{margin:0;padding:0;}body{background:#000;overflow:hidden;display:flex;align-items:center;justify-content:center;height:100vh;}
    .v{text-align:center;animation:vi 0.8s ease-out;}
    .v h1{font-size:4.5rem;font-weight:900;color:#44ffcc;text-shadow:0 0 40px #44ffcc,0 0 80px #00aacc;}
    .v p{font-size:1.5rem;color:#00ddff;font-weight:700;margin-top:0.5rem;}
    @keyframes vi{0%{transform:scale(0);opacity:0}100%{transform:scale(1);opacity:1}}
    </style>
    <div class="v"><h1>📖 CLEAR! 📖</h1><p>독해 전투 클리어!</p></div>
    """, height=300)

    if st.button("📝 브리핑 보기", type="primary", use_container_width=True):
        st.session_state.p7_phase = "briefing"; st.rerun()

# ═══════════════════════════════════════
# PHASE: LOST
# ═══════════════════════════════════════
elif st.session_state.p7_phase == "lost":
    components.html("""
    <style>
    *{margin:0;padding:0;}body{background:#000;overflow:hidden;display:flex;align-items:center;justify-content:center;height:100vh;}
    .l{text-align:center;animation:vi 0.8s ease-out;}
    .l h1{font-size:4.5rem;font-weight:900;color:#ff4444;text-shadow:0 0 40px #ff4444,0 0 80px #cc0000;}
    .l p{font-size:1.5rem;color:#ff8888;font-weight:700;margin-top:0.5rem;}
    @keyframes vi{0%{transform:scale(0);opacity:0}100%{transform:scale(1);opacity:1}}
    </style>
    <div class="l"><h1>💀 YOU LOST 💀</h1><p>다시 도전하세요!</p></div>
    """, height=300)

    if st.button("📝 브리핑 보기", type="primary", use_container_width=True):
        st.session_state.p7_phase = "briefing"; st.rerun()

    if st.button("🏠 로비로", type="secondary", use_container_width=True):
        for k in D: st.session_state[k] = D[k]
        st.rerun()

# ═══════════════════════════════════════
# PHASE: BRIEFING
# ═══════════════════════════════════════
elif st.session_state.p7_phase == "briefing":
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

    # 배너 + 화살표 한 줄
    ac1, ac2, ac3 = st.columns([0.6, 6, 0.6])
    with ac1:
        if st.button("◀", key="p7brp", disabled=bi<=0, use_container_width=True):
            st.session_state.p7_br_idx = bi - 1; st.rerun()
    with ac2:
        st.markdown(f'<div class="p7-ban {v_cls}">{data["title"]} — {v_label} ✅{ok_cnt} ❌{len(answers)-ok_cnt}</div>', unsafe_allow_html=True)
    with ac3:
        if st.button("▶", key="p7brn", disabled=bi>=num_steps-1, use_container_width=True):
            st.session_state.p7_br_idx = bi + 1; st.rerun()

    # 현재 스텝 데이터
    s = steps[bi]
    ok = answers[bi] if bi < len(answers) else False
    sym = "✅" if ok else "❌"
    correct_choice = s["choices"][s["answer"]]

    # ─── 카드: 통일된 크기 영어1.8rem굵게 / 한글1.7rem일반 ───
    wb = '<div style="background:#fffff5;border-radius:16px;padding:1rem;border:2px solid #ddd;margin:0.3rem 0;">'
    wb += f'<div style="font-size:1.1rem;font-weight:900;color:#00aa88;margin-bottom:0.4rem;">{sym} Step {bi+1} / {num_steps}</div>'

    # 영어 지문 (핵심 표현 형광 밑줄)
    wb += '<div style="font-size:1.8rem;font-weight:900;color:#1a1a1a;line-height:1.6;margin-bottom:0.3rem;">'
    _mark_style = "background:none;display:inline;background-image:linear-gradient(#ffe066,#ffe066);background-size:0% 4px;background-position:left bottom;background-repeat:no-repeat;animation:hlDraw 0.8s ease-out 0.3s forwards;color:#008855;font-weight:900;padding:0 2px;"
    _exprs_list = [e.get("expr","") for e in s.get("expressions", []) if e.get("expr")]
    import re as _re3
    for sent in s["sentences"]:
        _hl = sent
        for _ex in _exprs_list:
            if _ex.lower() in _hl.lower():
                try:
                    _hl = _re3.sub(f"(?i)({_re3.escape(_ex)})", f'<mark style="{_mark_style}">\\1</mark>', _hl)
                except: pass
            else:
                for _w in _ex.split():
                    if len(_w) >= 4 and _w.lower() in _hl.lower():
                        try:
                            _hl = _re3.sub(f"(?i)(\\b{_re3.escape(_w)}\\w*)", f'<mark style="{_mark_style}">\\1</mark>', _hl, count=1)
                        except: pass
        wb += f'{_hl} '
    wb += '</div>'

    # 한글 해석
    wb += '<div style="border-top:1px dashed #ccc;margin:0.4rem 0;"></div>'
    wb += f'<div style="font-size:1.7rem;font-weight:400;color:#444;line-height:1.7;margin-bottom:0.3rem;">📖 {s["kr"]}</div>'

    # 문제: 영어 (한글) 한 줄
    q_kr = s.get("question_kr", "")
    c_kr = s.get("choices_kr", [])
    answer_kr = c_kr[s["answer"]] if c_kr and s["answer"] < len(c_kr) else ""
    wb += '<div style="border-top:1px dashed #ccc;margin:0.4rem 0;"></div>'
    wb += f'<div style="margin-bottom:0.3rem;"><span style="font-size:1.8rem;font-weight:900;color:#6633aa;">[Q{bi+1}] {s["question"]}</span>'
    if q_kr:
        wb += f' <span style="font-size:1.7rem;font-weight:400;color:#8866bb;">({q_kr})</span>'
    wb += '</div>'

    # 정답: 영어 (한글) 한 줄
    wb += f'<div><span style="font-size:1.8rem;font-weight:900;color:#008844;">{sym} {correct_choice}</span>'
    if answer_kr:
        wb += f' <span style="font-size:1.7rem;font-weight:400;color:#22aa66;">({answer_kr})</span>'
    wb += '</div>'
    wb += '</div>'
    st.markdown(wb, unsafe_allow_html=True)

    # ─── 핵심 표현 (해당 Step의 표현만) ───
    exprs = s.get("expressions", [])
    if exprs:
        st.markdown('<div style="text-align:center;color:#44ffcc;font-size:1.3rem;font-weight:900;margin:0.4rem 0;">💎 핵심 표현</div>', unsafe_allow_html=True)
        expr_html = ''
        for e in exprs:
            expr_html += f'<div style="background:#0a1a28;border:1px solid #00aacc;border-radius:12px;padding:0.7rem 1rem;margin:0.3rem 0;display:flex;justify-content:space-between;align-items:center;"><span style="color:#44ffcc;font-size:1.8rem;font-weight:900;">{e["expr"]}</span><span style="color:#bbccdd;font-size:1.5rem;font-weight:700;">{e["meaning"]}</span></div>'
        st.markdown(expr_html, unsafe_allow_html=True)

    # ─── 하단 4버튼 한 줄 ───
    bc1, bc2, bc3, bc4 = st.columns(4)
    with bc1:
        if st.button("📝 단어저장", key=f"p7sv_{bi}", type="primary", use_container_width=True):
            save_expressions(exprs, step_data=s)
    with bc2:
        if st.button("🔄 다시!", key="p7retry", type="primary", use_container_width=True):
            for k in D: st.session_state[k] = D[k]
            st.rerun()
    with bc3:
        if st.button("📦 저장고", key="p7store", type="secondary", use_container_width=True):
            st.switch_page("pages/03_저장고.py")
    with bc4:
        if st.button("🏠 메인", key="p7lobby", type="secondary", use_container_width=True):
            for k in D: st.session_state[k] = D[k]
            st.switch_page("main_hub.py")
