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
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import random, time, json, os

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
_inject_css()

# ═══ STORAGE PATH ═══
STORAGE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage_data.json")

def load_storage():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
            if isinstance(d, dict):
                return d
            return {"saved_questions": d, "saved_expressions": []}
    return {"saved_questions": [], "saved_expressions": []}

def save_to_storage(items):
    data = load_storage()
    existing = data.get("saved_questions", [])
    ids = {x["id"] for x in existing if isinstance(x, dict) and "id" in x}
    for it in items:
        if it["id"] not in ids:
            existing.append(it)
            ids.add(it["id"])
    data["saved_questions"] = existing
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ═══ 전역 CSS — 화력전 전용 폰게임 스타일 ═══
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');

/* ── 기반 ── */
.stApp{background:#06060e!important;color:#eeeeff!important;}
section[data-testid="stSidebar"]{display:none!important;}
header[data-testid="stHeader"]{background:transparent!important;height:0!important;min-height:0!important;overflow:hidden!important;}
.block-container{padding-top:0!important;padding-bottom:0!important;margin-top:-8px!important;}

/* ── 타이틀 헤더 ── */
.ah{text-align:center;padding:0;margin:0 0 2px 0;line-height:1;}
.ah h1{font-family:'Orbitron',monospace!important;font-size:1.0rem;font-weight:900;margin:0;
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

/* ── 라운드 도트 ── */
.rd-dots{display:flex;justify-content:center;gap:0.5rem;}
.rd-dot{width:24px;height:24px;border-radius:50%;border:2px solid #333;
  display:flex;align-items:center;justify-content:center;
  font-size:0.72rem;font-weight:900;}
.rd-cur{border-color:#00d4ff!important;color:#00d4ff!important;box-shadow:0 0 12px #00d4ff!important;animation:neonPulse 1s infinite;}
.rd-ok{background:#00d4ff;border-color:#00d4ff;color:#000;}
.rd-no{background:#ff2244;border-color:#ff2244;color:#fff;}
.rd-wait{background:transparent;border-color:#333;color:#444;}

/* ── 문제 카드 ── */
.qb{border-radius:12px;padding:0.35rem 0.6rem;margin:0.05rem 0;background:#0a0c18;}
.qb-g{background:#080c18!important;border:2px solid rgba(0,212,255,0.5)!important;border-radius:12px!important;
  box-shadow:0 0 20px rgba(0,212,255,0.08);}
.qb-v{background:#08100c!important;border:2px solid rgba(0,180,100,0.4)!important;border-radius:12px!important;
  box-shadow:0 0 20px rgba(0,180,100,0.06);}
.qc{font-family:'Orbitron',monospace;font-size:0.65rem;font-weight:700;margin-bottom:2px;
  letter-spacing:3px;color:#555!important;}
.qc-g{color:#3388aa;}
.qc-v{color:#2a8855;}
.qt{font-family:'Rajdhani',sans-serif;color:#f0f0ff;font-size:0.95rem;font-weight:700;line-height:1.55;word-break:keep-all;}
.qk{color:#00d4ff;font-weight:900;font-size:1.0rem;border-bottom:2px solid #00d4ff;
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
  .qt{font-size:1.75rem!important;}.qk{font-size:1.9rem!important;}
  .wb-s{font-size:1.6rem!important;}.wb-h,.wb-hn{font-size:1.75rem!important;}
  .wb-k{font-size:1.25rem!important;}.wb-e{font-size:1.15rem!important;}
  .bq{font-size:1.2rem!important;}
}
@media(max-width:480px){
  .block-container{padding-top:0.3rem!important;padding-bottom:1.5rem!important;padding-left:0.3rem!important;padding-right:0.3rem!important;}
  .ah h1{font-size:0.95rem!important;letter-spacing:1px!important;}
  div[data-testid="stButton"] button{font-size:0.98rem!important;padding:0.5rem 0.6rem!important;min-height:52px!important;border-radius:8px!important;}
  div[data-testid="stButton"] button p{font-size:0.98rem!important;}
  .qt{font-size:1.15rem!important;line-height:1.6!important;}.qk{font-size:1.25rem!important;}
  .qb{padding:0.7rem!important;border-radius:10px!important;}
  .bq{font-size:0.95rem!important;}.bs{font-size:0.82rem!important;}
  .rd-dot{width:20px!important;height:20px!important;}
}
@media(max-width:360px){
  .ah h1{font-size:0.9rem!important;}
  div[data-testid="stButton"] button{font-size:1.0rem!important;}
  div[data-testid="stButton"] button p{font-size:1.0rem!important;}
  .qt{font-size:1.2rem!important;}.qk{font-size:1.3rem!important;}
}
</style>
""", unsafe_allow_html=True)

# ═══ 문제 ═══
GQ=[
{"id":"G1","text":"All employees _______ to attend the safety training session scheduled for next Monday.","ch":["(A) require","(B) are required","(C) requiring","(D) has required"],"a":1,"ex":"주어 'All employees'는 복수+수동태 → 'are required'가 정답. require(능동)는 목적어 필요, has required는 수 불일치.","exk":"쉽게: '직원들이 요구된다'니까 수동태! 복수 주어니까 are!","cat":"수동태/수일치","kr":"모든 직원들은 다음 월요일로 예정된 안전 교육 세션에 참석하도록 요구된다."},
{"id":"G2","text":"The manager suggested that the report _______ submitted by Friday.","ch":["(A) is","(B) be","(C) was","(D) will be"],"a":1,"ex":"suggest 뒤 that절 → (should)+동사원형. 'be submitted'가 정답.","exk":"쉽게: suggest(제안) 뒤에는 항상 동사원형! should가 숨어있다고 생각!","cat":"가정법/당위","kr":"매니저는 그 보고서가 금요일까지 제출되어야 한다고 제안했다."},
{"id":"G3","text":"_______ the budget has been approved, the project can begin immediately.","ch":["(A) Now that","(B) In case","(C) So that","(D) Even if"],"a":0,"ex":"'Now that~'='~이므로'. 예산 승인→프로젝트 시작 인과관계.","exk":"쉽게: '이제 ~했으니까'라는 뜻! 원인→결과 연결!","cat":"접속사","kr":"예산이 승인되었으므로, 프로젝트는 즉시 시작될 수 있다."},
{"id":"G4","text":"Neither the supervisor nor the team members _______ aware of the policy change.","ch":["(A) is","(B) was","(C) were","(D) has been"],"a":2,"ex":"Neither A nor B → B에 수 일치. B=team members(복수) → 'were'","exk":"쉽게: neither nor에서는 뒤쪽(B)에 맞추기! members=복수 → were!","cat":"수일치","kr":"상사도 팀원들도 정책 변경을 알지 못했다."},
{"id":"G5","text":"The equipment, along with all the spare parts, _______ shipped yesterday.","ch":["(A) were","(B) have been","(C) was","(D) are"],"a":2,"ex":"'along with'는 주어 불포함. 주어=equipment(단수) → 'was'","exk":"쉽게: along with는 무시! 진짜 주어만 보기! equipment=단수 → was!","cat":"수일치","kr":"그 장비는 모든 여분 부품과 함께 어제 배송되었다."},
{"id":"G6","text":"Ms. Kim is responsible for _______ that all invoices are processed on time.","ch":["(A) ensure","(B) ensuring","(C) ensured","(D) to ensure"],"a":1,"ex":"전치사 for 뒤 → 동명사(-ing). 'ensuring'이 정답.","exk":"쉽게: for 다음에는 ~ing! 전치사+동명사 공식!","cat":"동명사/준동사","kr":"김 씨는 모든 송장이 제때 처리되는 것을 보장할 책임이 있다."},
{"id":"G7","text":"Had the shipment arrived on time, we _______ the deadline.","ch":["(A) will meet","(B) would meet","(C) would have met","(D) had met"],"a":2,"ex":"Had+S+p.p.=가정법 과거완료 도치 → 주절 would have+p.p.","exk":"쉽게: Had로 시작=과거 가정법! → would have p.p.가 짝꿍!","cat":"가정법","kr":"만약 배송이 제때 도착했더라면, 우리는 마감을 맞출 수 있었을 텐데."},
{"id":"G8","text":"The number of participants _______ increased significantly this year.","ch":["(A) have","(B) has","(C) are","(D) were"],"a":1,"ex":"'The number of~'=단수 → 'has'","exk":"쉽게: The number of=그 수(하나) → 단수! A number of=많은 → 복수! 구별!","cat":"수일치","kr":"참가자의 수가 올해 크게 증가했다."},
{"id":"G9","text":"_______ reviewed the contract, the lawyer found several clauses that needed revision.","ch":["(A) Having","(B) Have","(C) Had","(D) To have"],"a":0,"ex":"분사구문 앞선 시제 → Having+p.p.","exk":"쉽게: 먼저 한 일+나중 한 일 → Having이 '먼저'를 표시!","cat":"분사구문","kr":"계약서를 검토한 후, 변호사는 수정이 필요한 여러 조항을 발견했다."},
{"id":"G10","text":"It is essential that every employee _______ the new security protocol.","ch":["(A) follows","(B) follow","(C) following","(D) followed"],"a":1,"ex":"It is essential that+S+(should) 동사원형 → 'follow'","exk":"쉽게: essential(필수적) 뒤에도 동사원형! suggest랑 같은 규칙!","cat":"가정법/당위","kr":"모든 직원이 새 보안 프로토콜을 따르는 것이 필수적이다."},
{"id":"G11","text":"The CEO, _______ founded the company in 2005, announced her retirement today.","ch":["(A) who","(B) whom","(C) which","(D) whose"],"a":0,"ex":"관계대명사 주어 역할 → 주격 'who'. 사람 → which 불가.","exk":"쉽게: 빈칸 뒤에 바로 동사(founded) → 주격 who! 사람이니까 which 안 됨!","cat":"관계대명사","kr":"2005년에 회사를 설립한 CEO가 오늘 은퇴를 발표했다."},
{"id":"G12","text":"Not until the final report is submitted _______ begin the evaluation process.","ch":["(A) we can","(B) we will","(C) can we","(D) will"],"a":2,"ex":"Not until~ 문두 → 주절 도치 → 'can we'","exk":"쉽게: Not until이 앞에 오면 뒤집기! can+we 순서!","cat":"도치","kr":"최종 보고서가 제출될 때까지는 평가 과정을 시작할 수 없다."},
{"id":"G13","text":"The policies _______ by the board last week will take effect next month.","ch":["(A) approve","(B) approving","(C) approved","(D) to approve"],"a":2,"ex":"명사 수식 수동 → 과거분사 approved","exk":"쉽게: 정책이 승인되는 것이니 수동! approved!","cat":"수동태/수일치","kr":"지난주 이사회에 의해 승인된 정책들은 다음 달부터 효력을 발휘할 것이다."},
{"id":"G14","text":"A number of employees _______ volunteered to work overtime this week.","ch":["(A) has","(B) have","(C) is","(D) was"],"a":1,"ex":"A number of=많은 → 복수 → have","exk":"쉽게: A number of=여러 명→복수! The number of=그 수→단수!","cat":"수일치","kr":"많은 직원들이 이번 주 초과 근무를 자원했다."},
{"id":"G15","text":"If the company _______ more staff last year, the project would have been completed.","ch":["(A) hired","(B) had hired","(C) would hire","(D) has hired"],"a":1,"ex":"가정법 과거완료 → if절 had+p.p.","exk":"쉽게: 과거 못한 일 가정 → if절에 had p.p.!","cat":"가정법","kr":"회사가 작년에 직원을 더 채용했더라면 프로젝트가 완료되었을 것이다."},
{"id":"G16","text":"Only after the meeting ended _______ the final decision.","ch":["(A) they announced","(B) announced they","(C) did they announce","(D) they did announce"],"a":2,"ex":"Only after~ 문두 도치 → did+주어+동사원형","exk":"쉽게: Only로 시작하면 뒤집기! did+they+announce!","cat":"도치","kr":"회의가 끝난 후에야 그들은 최종 결정을 발표했다."},
{"id":"G17","text":"The contractor, _______ proposal was accepted last week, will start work Monday.","ch":["(A) who","(B) whom","(C) whose","(D) which"],"a":2,"ex":"빈칸 뒤 명사(proposal) → 소유격 관계대명사 whose","exk":"쉽게: 빈칸 뒤에 명사 바로 오면 whose!","cat":"관계대명사","kr":"지난주 제안서가 채택된 계약업체가 월요일에 작업을 시작할 것이다."},
{"id":"G18","text":"_______ the construction noise, the staff managed to concentrate on their work.","ch":["(A) Despite","(B) Although","(C) However","(D) Because of"],"a":0,"ex":"빈칸 뒤 명사구 → 전치사 Despite","exk":"쉽게: Despite 뒤=명사! Although 뒤=주어+동사!","cat":"접속사","kr":"공사 소음에도 불구하고 직원들은 업무에 집중할 수 있었다."},
{"id":"G19","text":"The report _______ by the committee before the deadline was praised by the board.","ch":["(A) submit","(B) submitting","(C) submitted","(D) to submit"],"a":2,"ex":"명사 수식 수동 → 과거분사 submitted","exk":"쉽게: 보고서가 제출된 것 → 수동! submitted!","cat":"수동태/수일치","kr":"마감 전에 위원회에 의해 제출된 보고서는 이사회의 칭찬을 받았다."},
{"id":"G20","text":"Not only _______ the project on time, but they also exceeded expectations.","ch":["(A) they completed","(B) did they complete","(C) they did complete","(D) completed they"],"a":1,"ex":"Not only~ 문두 도치 → did+주어+동사원형","exk":"쉽게: Not only가 앞에 오면 뒤집기! did+they+complete!","cat":"도치","kr":"그들은 프로젝트를 제때 완료했을 뿐만 아니라 기대를 초과했다."},
{"id":"G21","text":"The employee _______ performance has improved significantly received a bonus.","ch":["(A) who","(B) whom","(C) whose","(D) which"],"a":2,"ex":"빈칸 뒤 명사(performance) → 소유격 whose","exk":"쉽게: 뒤에 명사 바로 오면 whose!","cat":"관계대명사","kr":"성과가 크게 향상된 직원은 보너스를 받았다."},
{"id":"G22","text":"_______ she had more experience, she might have gotten the promotion.","ch":["(A) If","(B) Unless","(C) Had","(D) Since"],"a":2,"ex":"Had+S → 가정법 과거완료 도치","exk":"쉽게: Had로 시작=과거 가정법 도치!","cat":"가정법","kr":"그녀가 더 많은 경험이 있었다면 승진했을 것이다."},
{"id":"G23","text":"The team is proud of _______ the project under budget.","ch":["(A) complete","(B) completed","(C) having completed","(D) to complete"],"a":2,"ex":"전치사 of 뒤 + 완료 → having+p.p.","exk":"쉽게: of 뒤=동명사! 이미 완료된 일=having completed!","cat":"동명사/준동사","kr":"팀은 예산 내에서 프로젝트를 완료한 것을 자랑스러워한다."},
{"id":"G24","text":"_______ all the data, the analyst presented her findings to the board.","ch":["(A) Having reviewed","(B) Have reviewed","(C) Reviewed","(D) To reviewing"],"a":0,"ex":"앞선 동작 분사구문 → Having+p.p.","exk":"쉽게: 먼저 한 일+나중 한 일 → Having p.p.가 먼저!","cat":"분사구문","kr":"모든 데이터를 검토한 후 분석가는 이사회에 결과를 발표했다."},
]
VQ=[
{"id":"V1","diff":"easy","text":"The company plans to _______ its operations to three new countries next year.","ch":["(A) expand","(B) expend","(C) expect","(D) expose"],"a":0,"ex":"expand=확장하다. 사업을 새 나라로 확장.","exk":"쉽게: expand=넓히다! expend=쓰다, expect=기대, expose=노출 → 소거법!","cat":"동사 어휘","kr":"그 회사는 내년에 3개 신규 국가로 사업을 확장할 계획이다.","diff":"easy"},
{"id":"V2","diff":"hard","text":"Please _______ your receipt as proof of purchase for warranty claims.","ch":["(A) retain","(B) attain","(C) obtain","(D) contain"],"a":0,"ex":"retain=보유하다. 영수증을 보관하라는 맥락.","exk":"쉽게: retain=re(다시)+tain(잡다)=계속 잡고 있다=보관!","cat":"동사 어휘","kr":"보증 청구를 위한 구매 증빙으로 영수증을 보관해 주세요."},
{"id":"V3","diff":"easy","text":"The new software update offers _______ improvements in processing speed.","ch":["(A) significant","(B) signified","(C) significance","(D) signify"],"a":0,"ex":"명사 수식 → 형용사 'significant'","exk":"쉽게: improvements(명사) 앞 = 형용사 자리! significant만 형용사!","cat":"품사(형용사)","kr":"새 소프트웨어 업데이트는 처리 속도에서 상당한 개선을 제공한다."},
{"id":"V4","diff":"hard","text":"Due to _______ demand, the product launch has been moved to an earlier date.","ch":["(A) overwhelming","(B) underwhelming","(C) overlooking","(D) overcoming"],"a":0,"ex":"overwhelming=압도적인","exk":"쉽게: over(넘치는)+whelming(덮치는)=압도적! 수요 폭발 → 출시 앞당김!","cat":"형용사 어휘","kr":"압도적인 수요로 인해 제품 출시가 더 이른 날짜로 앞당겨졌다."},
{"id":"V5","diff":"easy","text":"The marketing team will _______ a survey to gather customer feedback.","ch":["(A) conduct","(B) connect","(C) convince","(D) confirm"],"a":0,"ex":"conduct a survey=설문조사 실시(콜로케이션)","exk":"쉽게: conduct+survey는 짝꿍! '조사를 실시하다'는 항상 conduct!","cat":"콜로케이션","kr":"마케팅 팀은 고객 피드백을 수집하기 위해 설문조사를 실시할 것이다."},
{"id":"V6","diff":"easy","text":"All sales representatives must submit their reports _______.","ch":["(A) prompt","(B) promptly","(C) prompting","(D) prompted"],"a":1,"ex":"동사 수식 → 부사 'promptly'","exk":"쉽게: submit(동사) 꾸미기 = 부사! -ly 붙은 promptly!","cat":"품사(부사)","kr":"모든 영업 사원은 보고서를 신속하게 제출해야 한다."},
{"id":"V7","diff":"hard","text":"The _______ between the two proposals was discussed at length during the meeting.","ch":["(A) distinct","(B) distinction","(C) distinctive","(D) distinctly"],"a":1,"ex":"관사+전치사 사이 → 명사 'distinction'","exk":"쉽게: The ___ between = 관사+전치사 사이 = 명사 자리! -tion이 명사!","cat":"품사(명사)","kr":"두 제안 사이의 차이점이 회의 중 길게 논의되었다."},
{"id":"V8","diff":"easy","text":"The factory must _______ with all local environmental regulations.","ch":["(A) comply","(B) apply","(C) supply","(D) imply"],"a":0,"ex":"comply with=준수하다","exk":"쉽게: comply with=규칙을 따르다! apply=지원, supply=공급, imply=암시","cat":"동사 어휘","kr":"그 공장은 모든 지역 환경 규정을 준수해야 한다."},
{"id":"V9","diff":"hard","text":"The annual conference was attended by _______ 500 professionals from various industries.","ch":["(A) approximation","(B) approximate","(C) approximately","(D) approximated"],"a":2,"ex":"수사 수식 → 부사 'approximately'","exk":"쉽게: 500(숫자) 앞에서 꾸미기 = 부사! approximately='대략'","cat":"품사(부사)","kr":"연례 컨퍼런스에 다양한 산업의 약 500명의 전문가가 참석했다."},
{"id":"V10","diff":"easy","text":"Employees are encouraged to _______ any workplace hazards to their supervisors immediately.","ch":["(A) report","(B) deport","(C) import","(D) support"],"a":0,"ex":"report=보고하다","exk":"쉽게: report=알리다/보고하다! deport=추방, import=수입, support=지원","cat":"동사 어휘","kr":"직원들은 직장 내 위험 요소를 즉시 상사에게 보고하도록 권장된다."},
{"id":"V11","diff":"hard","text":"The board expressed _______ satisfaction with the quarterly earnings report.","ch":["(A) consider","(B) considerate","(C) considerable","(D) considerably"],"a":2,"ex":"명사 수식 → 형용사 'considerable'. considerate='사려 깊은'으로 의미 다름.","exk":"쉽게: satisfaction(명사) 앞 = 형용사! considerable=상당한, considerate=배려하는 → 헷갈림 주의!","cat":"품사(형용사)","kr":"이사회는 분기 실적 보고서에 상당한 만족을 표했다."},
{"id":"V12","diff":"hard","text":"The renovation project is expected to _______ the building's energy efficiency.","ch":["(A) enhance","(B) enforce","(C) endure","(D) enclose"],"a":0,"ex":"enhance=향상시키다","exk":"쉽게: enhance=더 좋게! enforce=시행, endure=견디다, enclose=동봉","cat":"동사 어휘","kr":"리노베이션 프로젝트는 건물의 에너지 효율을 향상시킬 것으로 예상된다."},
]

# ═══ 세션 ═══
D={"started":False,"cq":None,"qi":0,"sc":0,"wrong":0,"ta":0,"sk":0,"msk":0,
    "ans":False,"sel":None,"tsec":30,"qst":None,"round_qs":[],"round_results":[],
    "round_num":1,"phase":"lobby","mode":None,"used":[],
    "adp_level":"normal",
    "adp_history":[],
}
for k,v in D.items():
    if k not in st.session_state: st.session_state[k]=v

if st.session_state.get("_p5_just_left", False):
    st.session_state._p5_just_left = False
    for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","round_num","mode"]:
        if k in D: st.session_state[k] = D[k]
    st.session_state.phase = "lobby"
    st.session_state.sel_mode = None
    st.session_state.tsec = 30
    st.session_state.tsec_chosen = False

def pool(m): return GQ if m=="grammar" else VQ if m=="vocab" else GQ+VQ
GRP={"g1":["수일치","수동태/수일치"],"g2":["가정법","가정법/당위","도치"],"g3":["접속사","동명사/준동사","분사구문","관계대명사"]}
VGRP={"v1":"easy","v2":"hard"}

def _calc_adp_level():
    hist = st.session_state.get("adp_history", [])
    if len(hist) < 1:
        return st.session_state.get("adp_level", "normal")
    recent = hist[-3:]
    avg = sum(recent) / len(recent)
    cur = st.session_state.get("adp_level", "normal")
    if avg >= 0.8:
        if cur == "easy": return "normal"
        if cur == "normal": return "hard"
        return "hard"
    elif avg <= 0.4:
        if cur == "hard": return "normal"
        if cur == "normal": return "easy"
        return "easy"
    return cur

def pick5(m, grp=None):
    p=pool(m)
    if grp and grp in GRP:
        cats=GRP[grp]
        p=[q for q in p if q.get("cat","") in cats]
        adp = _calc_adp_level()
        st.session_state.adp_level = adp
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
                for q in chosen: st.session_state.used.append(q["id"]); q["tp"]="grammar"
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
                for q in chosen: st.session_state.used.append(q["id"]); q["tp"]="grammar"
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
    for q in chosen: st.session_state.used.append(q["id"]); q["tp"]="grammar" if q["id"].startswith("G") else "vocab"
    return chosen

def fq(t): return t.replace("_______",'<span class="qk">________</span>')
def tcls(r,t):
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
    ig=q.get("tp")=="grammar"; th="g" if ig else "v"; bt="primary" if ig else "secondary"
    ej="🔴" if ig else "🔵"; tn="문법" if ig else "어휘"

    st.markdown(f'<div class="ah"><h1>⚡ {tn} 화력전 — 라운드 {st.session_state.round_num} ⚔️</h1></div>', unsafe_allow_html=True)

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
        st_autorefresh(interval=1000, limit=st.session_state.tsec+5, key="battle_timer")
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
        .safe{{color:#44ff88;text-shadow:0 0 20px #44ff88,0 0 40px #22cc66;}}
        .warn{{color:#FFD600;text-shadow:0 0 25px #FFD600,0 0 50px #ff8800;}}
        .danger{{color:#ff4444;text-shadow:0 0 35px #ff4444,0 0 70px #ff0000;animation:shakeNum 0.3s infinite!important;}}
        .critical{{color:#ff0000;text-shadow:0 0 50px #ff0000,0 0 100px #ff0000;font-size:2.8rem!important;animation:shakeNum 0.15s infinite!important;}}
        .bs{{background:linear-gradient(90deg,#22cc66,#44ff88);box-shadow:0 0 10px #44ff88;}}
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
        var l={rem},t={total};
        var e=document.getElementById("n"),b=document.getElementById("b");
        setInterval(function(){{
            l--;if(l<0)l=0;
            e.textContent=l;
            var r=l/t;
            var c=r>0.6?"safe":r>0.35?"warn":r>0.15?"danger":"critical";
            e.className=c;
            b.className="b"+(r>0.6?"s":r>0.35?"w":r>0.15?"d":"c");
            b.style.width=(r*100)+"%";
        }},1000);
        </script>""", height=52)

        if rem<=0:
            st.session_state.phase="lost"; st.rerun()

    # ── 문제 카드 ──
    st.markdown(f'<div class="qb qb-{th}"><div class="qc qc-{th}">{ej} {tn} · {q.get("cat","")}</div><div class="qt">{fq(q["text"])}</div></div>', unsafe_allow_html=True)

    # ── 답 버튼 4개 — A/B/C/D 네온 스타일 ──
    if not st.session_state.ans:
        _qi = st.session_state.get('qi', 0)
        _rn = st.session_state.get('round_num', 0)

        # A/B/C/D 각각 다른 네온 색상 (A=파이어오렌지, B=시안, C=레드, D=그린)
        _btn_colors = [
            ("#ff6633", "#160800"),   # A — 파이어 오렌지
            ("#00E5FF", "#001518"),   # B — 시안
            ("#FF2D55", "#140008"),   # C — 레드
            ("#44FF88", "#001408"),   # D — 그린
        ]
        _labels = ["A", "B", "C", "D"]

        st.markdown("""<style>
        /* 답 버튼 개별 색상 오버라이드 */
        div[data-testid="stButton"]:nth-of-type(1) button{
            border-left:5px solid #ff6633!important;
            background:#160800!important;
        }
        div[data-testid="stButton"]:nth-of-type(1) button p{color:#ff6633!important;}
        div[data-testid="stButton"]:nth-of-type(1) button:hover{box-shadow:0 0 25px rgba(255,102,51,0.5)!important;border-color:#ff6633!important;}
        div[data-testid="stButton"]:nth-of-type(2) button{
            border-left:5px solid #00E5FF!important;
            background:#001518!important;
        }
        div[data-testid="stButton"]:nth-of-type(2) button p{color:#00E5FF!important;}
        div[data-testid="stButton"]:nth-of-type(2) button:hover{box-shadow:0 0 25px rgba(0,229,255,0.5)!important;border-color:#00E5FF!important;}
        div[data-testid="stButton"]:nth-of-type(3) button{
            border-left:5px solid #FF2D55!important;
            background:#140008!important;
        }
        div[data-testid="stButton"]:nth-of-type(3) button p{color:#FF2D55!important;}
        div[data-testid="stButton"]:nth-of-type(3) button:hover{box-shadow:0 0 25px rgba(255,45,85,0.5)!important;border-color:#FF2D55!important;}
        div[data-testid="stButton"]:nth-of-type(4) button{
            border-left:5px solid #44FF88!important;
            background:#001408!important;
        }
        div[data-testid="stButton"]:nth-of-type(4) button p{color:#44FF88!important;}
        div[data-testid="stButton"]:nth-of-type(4) button:hover{box-shadow:0 0 25px rgba(68,255,136,0.5)!important;border-color:#44FF88!important;}
        div[data-testid="stButton"] button{
            min-height:50px!important;
            font-size:0.95rem!important;
            font-weight:800!important;
            border-radius:10px!important;
            text-align:left!important;
            padding:0.45rem 0.9rem!important;
            margin-bottom:2px!important;
        }
        div[data-testid="stButton"] button p{
            font-size:0.95rem!important;
            font-weight:800!important;
        }
        </style>""", unsafe_allow_html=True)

        _clicked = None
        for _ii, _ch in enumerate(q['ch']):
            # (A) (B) 등 중복 제거 — 선택지에서 앞의 "(X) " 패턴 제거
            _ch_clean = _ch.split(") ", 1)[-1] if ") " in _ch else _ch
            _display = f"【{_labels[_ii]}】  {_ch_clean}"
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
    if _sc_v == 5:
        _grade = "👑 PERFECT!"; _praise = "완벽해! 토익 만점도 따놓은 당상! 🔥"; _pcol = "#FFD600"
    elif _sc_v == 4:
        _grade = "⚔️ VICTORY!"; _praise = "강해! 이 기세면 토익 900+ 간다! 💪"; _pcol = "#44FF88"
    else:
        _grade = "✅ CLEAR!"; _praise = "아슬아슬 살아남았어. 더 갈고닦아! 😤"; _pcol = "#88ccff"

    _stars_html = "".join([
        f'<div style="position:absolute;left:{random.randint(2,98)}%;top:{random.randint(2,98)}%;'
        f'width:{random.randint(3,10)}px;height:{random.randint(3,10)}px;'
        f'border-radius:50%;background:{"#FFD600" if random.random()>0.4 else "#fff8cc"};'
        f'animation:twinkle {0.5+random.random()*1:.1f}s ease-in-out infinite {random.random():.2f}s both;"></div>'
        for _ in range(60)])
    _coins_html = "".join([
        f'<div style="position:absolute;top:-10px;left:{random.randint(5,95)}%;font-size:1.4rem;'
        f'animation:coinFall {1.2+random.random():.1f}s ease-in infinite {random.random():.2f}s;">{"💰" if random.random()>0.5 else "⭐"}</div>'
        for _ in range(14)])
    _lightning_html = "".join([
        f'<div style="position:absolute;left:{random.randint(5,90)}%;top:{random.randint(5,85)}%;'
        f'font-size:{random.randint(20,40)}px;opacity:0.15;'
        f'animation:twinkle {0.3+random.random()*0.5:.1f}s ease-in-out infinite {random.random():.2f}s;">⚡</div>'
        for _ in range(8)])

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
        <div class="round-tag">⚔️ ROUND {_rn_v} CLEAR ⚔️</div>
        <div class="grade">{_grade}</div>
        <div class="scorebox">
            <div class="sc-num">{_sc_v}<span style="font-size:1.6rem;color:#886600;"> / 5</span></div>
            <div class="sc-label">✅ {_sc_v}격파 &nbsp;·&nbsp; ❌ {_wr_v}개 놓침</div>
        </div>
        <div class="bar-wrap"><div class="bar-fill"></div></div>
        <div class="praise">{_praise}</div>
    </div>
    """, height=290)

    st.markdown("""<style>
    div[data-testid="stButton"]:nth-of-type(1) button{
      background:#0c0c00!important;border:2px solid #FFD600!important;
      border-left:5px solid #FFD600!important;border-radius:12px!important;
    }
    div[data-testid="stButton"]:nth-of-type(1) button p{color:#FFD600!important;font-size:1.1rem!important;font-weight:900!important;}
    div[data-testid="stButton"]:nth-of-type(1) button:hover{box-shadow:0 0 25px rgba(255,214,0,0.6)!important;}
    div[data-testid="stButton"]:nth-of-type(2) button{
      background:#0a0a0a!important;border:1.5px solid rgba(255,255,255,0.2)!important;
    }
    div[data-testid="stButton"]:nth-of-type(2) button p{color:#777!important;font-size:0.95rem!important;}
    </style>""", unsafe_allow_html=True)
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
    if _pct == 0:
        _taunt = "문법책 한 번이라도 펴봤어? 📚"; _sub = "수일치도 모르면서 토익 점수 바라지 마 😶"
    elif _is_timeout:
        _taunt = "시간이 부족했다고? 그게 실력이야 ⏰"; _sub = "토익은 느린 사람 기다려주지 않아 🐢"
    elif _pct <= 20:
        _taunt = "찍어서 맞춘 거 다 알아 😂"; _sub = "운도 실력이라고? 그건 토익엔 없어 🙃"
    elif _pct <= 40:
        _taunt = f"겨우 {_sc}개... 어법이 이 정도면 문장도 못 읽겠다 😤"; _sub = "접속사? 수일치? 기초부터 다시 해"
    else:
        _taunt = "딱 한 문제 차이야. 억울하지? 😭"; _sub = "그 한 문제가 토익 점수 50점 차이야"

    _embers = "".join([
        f'<div style="position:absolute;left:{random.randint(5,95)}%;bottom:{random.randint(0,30)}%;'
        f'width:{random.randint(4,12)}px;height:{random.randint(4,12)}px;border-radius:50%;'
        f'background:{"#ff4400" if random.random()>0.4 else "#ff8800"};'
        f'animation:rise {1+random.random():.1f}s ease-in infinite {random.random():.1f}s;"></div>'
        for _ in range(50)])
    _skulls = "".join([
        f'<div style="position:absolute;left:{random.randint(5,90)}%;top:{random.randint(5,80)}%;'
        f'font-size:{random.randint(12,28)}px;opacity:{random.random()*0.15:.2f};'
        f'animation:fadeFloat {1.5+random.random():.1f}s ease-in-out infinite {random.random():.1f}s;">💀</div>'
        for _ in range(10)])

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
    body{{animation:redPulse 0.6s ease-in-out infinite;}}
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
    </div>""", height=240)

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
    section[data-testid="stSidebar"]{display:none!important;}
    header[data-testid="stHeader"]{height:0!important;visibility:hidden!important;}
    .block-container{padding-top:0!important;padding-bottom:0!important;margin-top:0!important;}
    .stMarkdown{margin:0!important;padding:0!important;}
    div[data-testid="stVerticalBlock"]{gap:0rem!important;}
    div[data-testid="stVerticalBlockBorderWrapper"]{padding:0!important;}
    .element-container{margin:0!important;padding:0!important;}
    div[data-testid="stHorizontalBlock"]{margin:0!important;padding:0!important;flex-wrap:nowrap!important;gap:6px!important;}
    div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]{min-width:0!important;flex:1!important;padding:0!important;}
    div[data-testid="stButton"] button{width:100%!important;min-height:44px!important;font-size:0.88rem!important;padding:6px 4px!important;}
    </style>""", unsafe_allow_html=True)

    was_victory = st.session_state.sc >= 3
    if "br_idx" not in st.session_state: st.session_state.br_idx = 0
    if "br_saved" not in st.session_state: st.session_state.br_saved = set()
    bi    = st.session_state.br_idx
    rqs   = st.session_state.round_qs
    rrs   = st.session_state.round_results
    saved = st.session_state.br_saved
    num_qs = min(len(rqs), len(rrs))
    if bi >= num_qs: bi = num_qs - 1
    if bi < 0: bi = 0
    rn    = st.session_state.round_num
    sc_v  = st.session_state.sc
    wr_v  = st.session_state.wrong

    # 상단 배너
    if was_victory:
        st.markdown(f'''<div style="background:#0c0c00;border:2px solid #FFD600;border-left:5px solid #FFD600;
            border-radius:10px;padding:12px;margin-bottom:6px;">
            <div style="font-size:1.0rem;font-weight:900;color:#FFD600;">🏆 라운드 {rn} — VICTORY!</div>
            <div style="font-size:0.75rem;color:#886600;margin-top:2px;">✅{sc_v}문제 격파! ❌{wr_v}개 놓침</div>
        </div>''', unsafe_allow_html=True)
    else:
        st.markdown(f'''<div style="background:#0c0008;border:2px solid #FF2D55;border-left:5px solid #FF2D55;
            border-radius:10px;padding:12px;margin-bottom:6px;">
            <div style="font-size:1.0rem;font-weight:900;color:#FF2D55;">💀 라운드 {rn} — GAME OVER</div>
            <div style="font-size:0.75rem;color:#661122;margin-top:2px;">✅{sc_v}문제 / ❌{wr_v}개 틀림</div>
        </div>''', unsafe_allow_html=True)

    # 문제 번호 네비
    st.markdown('''<style>
    .nav-size div[data-testid="stButton"] button{font-size:0.7rem!important;min-height:26px!important;padding:2px!important;border-radius:50%!important;}
    .nav-size div[data-testid="stButton"] button p{font-size:0.7rem!important;}
    </style>''', unsafe_allow_html=True)
    st.markdown('<div class="nav-size">', unsafe_allow_html=True)
    _ncols = st.columns(num_qs)
    for _i in range(num_qs):
        with _ncols[_i]:
            _ok_i = rrs[_i] if _i < len(rrs) else None
            _border = "#50c878" if _ok_i else "#ff4466" if _ok_i is not None else "#9aa5b4"
            _bg = "#001a00" if _ok_i else "#1a0008" if _ok_i is not None else "#0d0d18"
            _sel = "outline:3px solid #9aa5b4;outline-offset:2px;" if _i==bi else ""
            st.markdown(f'''<style>
            div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]:nth-child({_i+1}) button{{
                background:{_bg}!important;border:2px solid {_border}!important;
                color:{_border}!important;border-radius:50%!important;{_sel}
            }}</style>''', unsafe_allow_html=True)
            if st.button(str(_i+1), key=f"dot_{_i}", use_container_width=True):
                st.session_state.br_idx = _i; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 문제 카드
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

    st.markdown(f'''<div style="background:#0a0c18;border:2px solid {card_border};
        border-left:5px solid {card_border};border-radius:12px;padding:12px;margin:5px 0;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="background:#0a0a20;border:1px solid #222;border-radius:10px;
              padding:3px 12px;font-size:0.9rem;font-weight:800;color:{qnum_color};">{qnum_sym} Q{bi+1}/{num_qs}</span>
            <span style="font-size:0.72rem;color:#444;letter-spacing:2px;">{cat}</span>
        </div>
        <div style="font-size:1.1rem;font-weight:700;color:#eeeeff;line-height:1.75;margin-bottom:10px;">{sent_html}</div>
        <div style="font-size:0.88rem;color:#7a8a9a;margin-bottom:8px;">📖 {kr}</div>
        <div style="background:#050f05;border-left:4px solid #50c878;border-radius:0 10px 10px 0;padding:8px 12px;">
            <div style="font-size:0.88rem;color:#50c878;font-weight:700;">💡 {exk}</div>
        </div>
    </div>''', unsafe_allow_html=True)

    # 저장 버튼
    _sv1, _sv2 = st.columns([3, 1])
    with _sv2:
        _is_saved = bi in saved
        _slabel = "✅ 저장됨" if _is_saved else "💾 저장!"
        st.markdown('''<style>
        div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]:last-child button{
            border:2px solid #9aa5b4!important;color:#9aa5b4!important;
            background:#0d0d18!important;border-radius:50px!important;font-size:0.82rem!important;
        }
        div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]:last-child button p{color:#9aa5b4!important;}
        </style>''', unsafe_allow_html=True)
        if st.button(_slabel, key=f"sv_{q['id']}_{bi}", use_container_width=True, disabled=_is_saved):
            item = {"id":q["id"],"text":q["text"],"ch":q["ch"],"a":q["a"],"ex":q.get("ex",""),
                    "exk":q.get("exk",""),"cat":q.get("cat",""),"kr":q.get("kr",""),"tp":q.get("tp","grammar")}
            save_to_storage([item])
            st.session_state.br_saved.add(bi)
            st.rerun()

    st.markdown('<div style="height:1px;background:#1a1a2a;margin:4px 0;"></div>', unsafe_allow_html=True)

    # 하단 버튼
    st.markdown('''<style>
    .bottom-row div[data-testid="stButton"] button{
        background:transparent!important;border:1px solid rgba(255,255,255,0.3)!important;
        color:rgba(255,255,255,0.6)!important;font-weight:600!important;
        font-size:0.85rem!important;border-radius:10px!important;min-height:46px!important;
    }
    .bottom-row div[data-testid="stButton"] button p{color:rgba(255,255,255,0.6)!important;font-size:0.85rem!important;}
    .bottom-row div[data-testid="stButton"]:nth-of-type(1) button{
        border-color:rgba(0,212,255,0.5)!important;color:#00d4ff!important;
    }
    .bottom-row div[data-testid="stButton"]:nth-of-type(1) button p{color:#00d4ff!important;}
    </style>''', unsafe_allow_html=True)
    st.markdown('<div class="bottom-row">', unsafe_allow_html=True)
    if was_victory:
        _c1, _c2 = st.columns([2,1])
        with _c1:
            if st.button("💀 포로사령부!", use_container_width=True):
                st.switch_page("pages/03_POW_HQ.py")
        with _c2:
            if st.button("🏠 홈", use_container_width=True):
                st.session_state._p5_just_left = True
                st.session_state.ans = False
                st.session_state["_battle_entry_ans_reset"] = True
                _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
                if _nick:
                    st.query_params["nick"] = _nick
                    st.query_params["ag"] = "1"
                st.switch_page("main_hub.py")
    else:
        _c1, _c2 = st.columns([2,1])
        with _c1:
            if st.button("🔥 설욕전! 다시 싸운다!", use_container_width=True):
                for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx","br_saved"]:
                    if k in st.session_state: del st.session_state[k]
                for k,v in D.items():
                    if k not in st.session_state: st.session_state[k]=v
                qs = pick5(st.session_state.mode)
                st.session_state.round_qs = qs; st.session_state.cq = qs[0]
                st.session_state.qst = time.time(); st.session_state.phase = "battle"; st.rerun()
        with _c2:
            if st.button("🏠 홈", use_container_width=True):
                st.session_state._p5_just_left = True
                st.session_state.ans = False
                st.session_state["_battle_entry_ans_reset"] = True
                _nick = st.session_state.get("battle_nickname") or st.session_state.get("nickname", "")
                if _nick:
                    st.query_params["nick"] = _nick
                    st.query_params["ag"] = "1"
                st.switch_page("main_hub.py")
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════
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
    lbl_map  = {"g1":"⚔️ 문법력","g2":"⚔️ 구조력","g3":"⚔️ 연결력","vocab":"📘 어휘력"}
    mode_map = {"g1":("grammar","g1"),"g2":("grammar","g2"),"g3":("grammar","g3"),"vocab":("vocab",None)}
    _cur_sm  = st.session_state.get("sel_mode","") or ""
    _cur_tc  = st.session_state.get("tsec_chosen", False)
    _cur_tsec= st.session_state.get("tsec", 30)
    _ready   = _cur_tc and _cur_sm in ["g1","g2","g3","vocab"]
    _adp     = st.session_state.get("adp_level","normal")
    _adp_lbl = {"easy":"🟢 입문","normal":"🟡 표준","hard":"🔴 심화"}.get(_adp,"🟡 표준")
    _hist_len= len(st.session_state.get("adp_history",[]))

    # ══════════════════════════════════════════════════════
    # 로비 CSS — JS 최소화, 클래스 기반 스타일링
    # ══════════════════════════════════════════════════════
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');

/* ── 기반 ── */
.stApp { background:#04040c !important; }
section[data-testid="stSidebar"] { display:none !important; }
header[data-testid="stHeader"]   { height:0 !important; overflow:hidden !important; }
.block-container { padding:14px 14px 30px !important; margin:0 !important; }
div[data-testid="stVerticalBlock"] { gap:0.55rem !important; }
.element-container { margin:0 !important; padding:0 !important; }
div[data-testid="stHorizontalBlock"] {
  gap:8px !important; margin:0 !important; flex-wrap:nowrap !important;
}
div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"] {
  padding:0 !important; min-width:0 !important; flex:1 !important;
}

/* ── 애니메이션 ── */
@keyframes titleShine {
  0%   { background-position:200% center }
  100% { background-position:-200% center }
}
@keyframes warnBlink {
  0%,100% { opacity:1;    color:#ff4466; text-shadow:0 0 8px rgba(255,68,102,0.5); }
  50%     { opacity:0.65; color:#ff7788; text-shadow:0 0 20px rgba(255,68,102,1), 0 0 40px rgba(220,0,30,0.5); }
}
/* 출격 glow — box-shadow 에는 경쟁하는 !important 없음 -> CSS animation 정상 작동 */
@keyframes launchGlow {
  0%,100% { box-shadow: 0 0 14px rgba(255,70,0,0.7),  0 0 30px rgba(255,50,0,0.3); }
  50%     { box-shadow: 0 0 55px rgba(255,210,0,1),    0 0 110px rgba(255,140,0,0.6); }
}
@keyframes selPulse {
  0%,100% { filter:brightness(1); }
  50%     { filter:brightness(1.1); }
}

/* ── 공통 버튼 기본값 ── */
div[data-testid="stButton"] button {
  background:#070b17 !important;
  border:1.5px solid rgba(0,180,255,0.18) !important;
  border-radius:12px !important;
  font-family:'Rajdhani',sans-serif !important;
  font-size:0.88rem !important; font-weight:700 !important;
  padding:8px 10px !important; color:#6688aa !important;
  min-height:46px !important; width:100% !important;
  white-space:pre-line !important; line-height:1.3 !important;
  transition:border-color 0.12s, box-shadow 0.12s !important;
}
div[data-testid="stButton"] button p {
  font-size:0.88rem !important; font-weight:700 !important;
  color:#6688aa !important; white-space:pre-line !important; line-height:1.3 !important;
}

/* ════ 시간 버튼 — 30초 주황/불꽃계 ════ */
div[data-testid="stButton"] button.fp-t30 {
  background:linear-gradient(145deg,#0e0700,#180b00) !important;
  border-color:rgba(200,90,20,0.32) !important; color:#aa5520 !important;
  min-height:58px !important; font-family:'Orbitron',monospace !important; font-size:0.8rem !important;
}
div[data-testid="stButton"] button.fp-t30 p { color:#aa5520 !important; }
div[data-testid="stButton"] button.fp-t30:hover {
  border-color:rgba(255,120,40,0.65) !important;
  box-shadow:0 0 14px rgba(255,100,30,0.3) !important;
}
div[data-testid="stButton"] button.fp-t30.fp-sel {
  background:linear-gradient(145deg,#220e00,#2e1400) !important;
  border-color:#ff8833 !important; color:#ffaa44 !important;
  box-shadow:0 0 22px rgba(255,130,50,0.55) !important;
  animation:selPulse 1.6s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-t30.fp-sel p { color:#ffaa44 !important; }

/* ════ 40초 파랑계 ════ */
div[data-testid="stButton"] button.fp-t40 {
  background:linear-gradient(145deg,#03091a,#060e26) !important;
  border-color:rgba(40,110,230,0.32) !important; color:#2c5eaa !important;
  min-height:58px !important; font-family:'Orbitron',monospace !important; font-size:0.8rem !important;
}
div[data-testid="stButton"] button.fp-t40 p { color:#2c5eaa !important; }
div[data-testid="stButton"] button.fp-t40:hover {
  border-color:rgba(60,140,255,0.65) !important;
  box-shadow:0 0 14px rgba(50,110,255,0.3) !important;
}
div[data-testid="stButton"] button.fp-t40.fp-sel {
  background:linear-gradient(145deg,#07152e,#0a1e42) !important;
  border-color:#3388ff !important; color:#55aaff !important;
  box-shadow:0 0 22px rgba(60,140,255,0.55) !important;
  animation:selPulse 1.6s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-t40.fp-sel p { color:#55aaff !important; }

/* ════ 50초 보라계 ════ */
div[data-testid="stButton"] button.fp-t50 {
  background:linear-gradient(145deg,#0a051e,#12082c) !important;
  border-color:rgba(130,55,220,0.32) !important; color:#6e30bb !important;
  min-height:58px !important; font-family:'Orbitron',monospace !important; font-size:0.8rem !important;
}
div[data-testid="stButton"] button.fp-t50 p { color:#6e30bb !important; }
div[data-testid="stButton"] button.fp-t50:hover {
  border-color:rgba(170,80,255,0.65) !important;
  box-shadow:0 0 14px rgba(150,60,255,0.3) !important;
}
div[data-testid="stButton"] button.fp-t50.fp-sel {
  background:linear-gradient(145deg,#180836,#22104c) !important;
  border-color:#aa44ff !important; color:#cc77ff !important;
  box-shadow:0 0 22px rgba(170,80,255,0.55) !important;
  animation:selPulse 1.6s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-t50.fp-sel p { color:#cc77ff !important; }

/* ════ 작전 카드 공통 ════ */
div[data-testid="stButton"] button.fp-mode {
  min-height:84px !important;
  text-align:left !important; padding:13px 15px !important;
  font-family:'Rajdhani',sans-serif !important; font-size:0.9rem !important;
}

/* 문법력 파랑 */
div[data-testid="stButton"] button.fp-g1 {
  background:linear-gradient(145deg,#05102a,#081630) !important;
  border-color:rgba(55,130,255,0.35) !important; color:#4d8eee !important;
}
div[data-testid="stButton"] button.fp-g1 p { color:#4d8eee !important; }
div[data-testid="stButton"] button.fp-g1:hover {
  border-color:rgba(100,170,255,0.7) !important;
  box-shadow:0 0 18px rgba(80,150,255,0.28) !important;
}
div[data-testid="stButton"] button.fp-g1.fp-sel {
  background:linear-gradient(145deg,#091e44,#0d2a5a) !important;
  border-color:#6aadff !important; color:#88ccff !important;
  box-shadow:0 0 28px rgba(106,173,255,0.5) !important;
  animation:selPulse 1.8s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-g1.fp-sel p { color:#88ccff !important; }

/* 구조력 보라 */
div[data-testid="stButton"] button.fp-g2 {
  background:linear-gradient(145deg,#120520,#180830) !important;
  border-color:rgba(158,68,248,0.35) !important; color:#9244dd !important;
}
div[data-testid="stButton"] button.fp-g2 p { color:#9244dd !important; }
div[data-testid="stButton"] button.fp-g2:hover {
  border-color:rgba(200,120,255,0.7) !important;
  box-shadow:0 0 18px rgba(180,100,255,0.28) !important;
}
div[data-testid="stButton"] button.fp-g2.fp-sel {
  background:linear-gradient(145deg,#200a3e,#2c1054) !important;
  border-color:#cc88ff !important; color:#ddaaff !important;
  box-shadow:0 0 28px rgba(200,136,255,0.5) !important;
  animation:selPulse 1.8s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-g2.fp-sel p { color:#ddaaff !important; }

/* 연결력 청록 */
div[data-testid="stButton"] button.fp-g3 {
  background:linear-gradient(145deg,#051a18,#072220) !important;
  border-color:rgba(0,198,178,0.35) !important; color:#00a898 !important;
}
div[data-testid="stButton"] button.fp-g3 p { color:#00a898 !important; }
div[data-testid="stButton"] button.fp-g3:hover {
  border-color:rgba(0,220,200,0.7) !important;
  box-shadow:0 0 18px rgba(0,200,180,0.28) !important;
}
div[data-testid="stButton"] button.fp-g3.fp-sel {
  background:linear-gradient(145deg,#092a24,#0e362e) !important;
  border-color:#00ddc8 !important; color:#00eecc !important;
  box-shadow:0 0 28px rgba(0,220,200,0.5) !important;
  animation:selPulse 1.8s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-g3.fp-sel p { color:#00eecc !important; }

/* 어휘력 초록 */
div[data-testid="stButton"] button.fp-vc {
  background:linear-gradient(145deg,#061808,#091e0b) !important;
  border-color:rgba(48,196,72,0.35) !important; color:#2faa50 !important;
}
div[data-testid="stButton"] button.fp-vc p { color:#2faa50 !important; }
div[data-testid="stButton"] button.fp-vc:hover {
  border-color:rgba(80,230,100,0.7) !important;
  box-shadow:0 0 18px rgba(60,210,80,0.28) !important;
}
div[data-testid="stButton"] button.fp-vc.fp-sel {
  background:linear-gradient(145deg,#0c2412,#102e16) !important;
  border-color:#55ee77 !important; color:#77ff99 !important;
  box-shadow:0 0 28px rgba(85,238,119,0.5) !important;
  animation:selPulse 1.8s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-vc.fp-sel p { color:#77ff99 !important; }

/* ════ 출격 버튼 (active) — CSS animation으로 box-shadow glow ════ */
div[data-testid="stButton"] button.fp-launch {
  background:linear-gradient(135deg,#280800,#1c0500) !important;
  border:2.5px solid #ff4400 !important;
  border-radius:14px !important;
  color:#ffcc55 !important;
  font-family:'Orbitron',monospace !important;
  font-weight:900 !important; font-size:0.92rem !important;
  letter-spacing:3px !important; min-height:58px !important;
  transition:none !important;
  animation:launchGlow 0.55s ease-in-out infinite !important;
}
div[data-testid="stButton"] button.fp-launch p {
  color:#ffcc55 !important; font-family:'Orbitron',monospace !important;
  font-size:0.92rem !important; font-weight:900 !important; letter-spacing:3px !important;
}

/* ════ 출격 버튼 (disabled) ════ */
div[data-testid="stButton"] button.fp-launch-off {
  background:#06060f !important;
  border:1px solid #0e0e1c !important; border-radius:12px !important;
  color:#18182a !important; font-family:'Orbitron',monospace !important;
  font-size:0.8rem !important; min-height:52px !important;
}
div[data-testid="stButton"] button.fp-launch-off p { color:#18182a !important; }

/* ════ 네비 버튼 ════ */
div[data-testid="stButton"] button.fp-nav {
  background:#05050e !important;
  border:1px solid #151525 !important; border-radius:10px !important;
  color:#3d5066 !important; min-height:42px !important; font-size:0.82rem !important;
}
div[data-testid="stButton"] button.fp-nav p { color:#3d5066 !important; }
div[data-testid="stButton"] button.fp-nav:hover {
  border-color:rgba(80,120,180,0.4) !important; color:#7799aa !important;
}

/* 모바일 반응형 */
@media(max-width:768px) {
  div[data-testid="stButton"] button.fp-t30,
  div[data-testid="stButton"] button.fp-t40,
  div[data-testid="stButton"] button.fp-t50  { min-height:64px !important; font-size:1.0rem !important; }
  div[data-testid="stButton"] button.fp-mode { min-height:90px !important; font-size:1.1rem !important; }
  div[data-testid="stButton"] button.fp-launch { min-height:66px !important; font-size:1.1rem !important; }
}
@media(max-width:480px) {
  div[data-testid="stButton"] button.fp-t30,
  div[data-testid="stButton"] button.fp-t40,
  div[data-testid="stButton"] button.fp-t50  { min-height:56px !important; }
  div[data-testid="stButton"] button.fp-mode { min-height:80px !important; }
}
</style>""", unsafe_allow_html=True)

    # ── 타이틀 ──
    _rb = f'<span style="background:#1a0800;border:1px solid #cc6600;border-radius:20px;padding:1px 10px;font-size:0.68rem;color:#ffaa44;font-weight:900;">🏆 ROUND {rn}</span> ' if rn > 1 else ''
    st.markdown(f"""<div style="text-align:center;padding:16px 0 20px;">
      <div style="font-family:Orbitron,monospace;font-size:2rem;font-weight:900;letter-spacing:6px;
        background:linear-gradient(90deg,#00e5ff,#ffffff,#FFD600,#ff3300,#00e5ff);background-size:300%;
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        animation:titleShine 2s linear infinite;line-height:1.2;">{_rb}⚡ 화력전</div>
      <div style="font-size:0.7rem;color:#445577;letter-spacing:2.5px;margin-top:8px;font-weight:500;">
        5문제 서바이벌 · 문법·어휘 실전 포격전</div>
    </div>""", unsafe_allow_html=True)

    # ── 섹션: 전투 시간 ──
    st.markdown('''<div style="display:flex;align-items:center;gap:10px;margin:4px 0 8px;">
      <div style="flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(85,170,255,0.35));"></div>
      <span style="font-size:0.68rem;color:#55aaff;font-weight:900;letter-spacing:4px;
        font-family:Orbitron,monospace;white-space:nowrap;
        text-shadow:0 0 10px rgba(85,170,255,0.7);">&#9201; 전투 시간</span>
      <div style="flex:1;height:1px;background:linear-gradient(90deg,rgba(85,170,255,0.35),transparent);"></div>
    </div>''', unsafe_allow_html=True)

    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        if st.button("🔥 30초\n속공", key="t30", use_container_width=True):
            st.session_state.tsec=30; st.session_state.tsec_chosen=True; st.rerun()
    with tc2:
        if st.button("⚡ 40초\n표준", key="t40", use_container_width=True):
            st.session_state.tsec=40; st.session_state.tsec_chosen=True; st.rerun()
    with tc3:
        if st.button("🛡️ 50초\n정밀", key="t50", use_container_width=True):
            st.session_state.tsec=50; st.session_state.tsec_chosen=True; st.rerun()

    # ── 섹션: 작전 선택 ──
    st.markdown('''<div style="display:flex;align-items:center;gap:10px;margin:8px 0 8px;">
      <div style="flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(255,85,119,0.35));"></div>
      <span style="font-size:0.68rem;color:#ff5577;font-weight:900;letter-spacing:4px;
        font-family:Orbitron,monospace;white-space:nowrap;
        text-shadow:0 0 10px rgba(255,85,119,0.7);">&#9876; 작전 선택</span>
      <div style="flex:1;height:1px;background:linear-gradient(90deg,rgba(255,85,119,0.35),transparent);"></div>
    </div>''', unsafe_allow_html=True)

    b1, b2 = st.columns(2)
    with b1:
        if st.button("⚔️ 문법력\n수일치 · 시제 · 수동", key="sg1", use_container_width=True):
            st.session_state.sel_mode="g1"; st.rerun()
    with b2:
        if st.button("🏛️ 구조력\n가정법 · 도치 · 당위", key="sg2", use_container_width=True):
            st.session_state.sel_mode="g2"; st.rerun()
    b3, b4 = st.columns(2)
    with b3:
        if st.button("🔗 연결력\n접속사 · 관계사 · 분사", key="sg3", use_container_width=True):
            st.session_state.sel_mode="g3"; st.rerun()
    with b4:
        if st.button("📘 어휘력\n품사 · 동사 · 콜로케이션", key="svc", use_container_width=True):
            st.session_state.sel_mode="vocab"; st.rerun()

    # ── 생존 규칙 ──
    st.markdown(
        '<div style="text-align:center;margin:2px 0 4px;font-size:0.65rem;font-weight:900;'
        'letter-spacing:1.5px;font-family:Orbitron,monospace;'
        'animation:warnBlink 1.4s ease-in-out infinite;">'
        '&#128128; 3개 이상 격파해야 생존 · 그 이하면 전멸!</div>',
        unsafe_allow_html=True
    )

    # ── 출격 버튼 ──
    if _ready:
        _cat = lbl_map.get(_cur_sm,"")
        if st.button(f"🔥 출격! — {_cat}  ⏱{_cur_tsec}초", key="go_start", use_container_width=True):
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
        st.button("⏱ 시간 + ⚔️ 작전 선택 → 출격!", key="go_disabled", use_container_width=True, disabled=True)

    # ── 네비 ──
    st.markdown('<div style="height:1px;background:#0e0e1e;margin:3px 0 2px;"></div>', unsafe_allow_html=True)
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

    # ═══════════════════════════════════════════════════════════════
    # JS — 최소화 버전 (setInterval 1개 + setTimeout 2개)
    # 역할: CSS 클래스 부여 + 출격 border-color 지글지글
    # applyColors setInterval 완전 제거 → CSS animation 방해 없음
    # border-color keyframe은 !important 충돌로 JS inline만 가능
    # ═══════════════════════════════════════════════════════════════
    _sel_t = str(_cur_tsec) if _cur_tc else ""
    _sel_m = _cur_sm
    _js_ready = "true" if _ready else "false"
    components.html(f"""<script>
(function(){{
  var selT="{_sel_t}", selM="{_sel_m}", isReady={_js_ready};
  var doc=window.parent.document;

  function applyClasses(){{
    doc.querySelectorAll("button").forEach(function(b){{
      var txt=(b.innerText||b.textContent||"").trim();
      if(!txt) return;

      // 시간 버튼
      if(txt.indexOf("30\ucd08")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("fp-t30");
        if(selT==="30") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
      }}
      if(txt.indexOf("40\ucd08")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("fp-t40");
        if(selT==="40") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
      }}
      if(txt.indexOf("50\ucd08")>-1 && txt.indexOf("\ucd9c\uaca9")===-1){{
        b.classList.add("fp-t50");
        if(selT==="50") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
      }}

      // 작전 카드
      if(txt.indexOf("\ubb38\ubc95\ub825")>-1){{
        b.classList.add("fp-mode","fp-g1");
        if(selM==="g1") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
      }}
      if(txt.indexOf("\uad6c\uc870\ub825")>-1){{
        b.classList.add("fp-mode","fp-g2");
        if(selM==="g2") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
      }}
      if(txt.indexOf("\uc5f0\uacb0\ub825")>-1){{
        b.classList.add("fp-mode","fp-g3");
        if(selM==="g3") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
      }}
      if(txt.indexOf("\uc5b4\ud718\ub825")>-1){{
        b.classList.add("fp-mode","fp-vc");
        if(selM==="vocab") b.classList.add("fp-sel"); else b.classList.remove("fp-sel");
      }}

      // 출격 버튼
      if(txt.indexOf("\ucd9c\uaca9!")>-1 && txt.indexOf("\uc2dc\uac04")===-1 && txt.indexOf("\uc791\uc804")===-1){{
        if(isReady){{ b.classList.add("fp-launch"); b.classList.remove("fp-launch-off"); }}
        else{{ b.classList.add("fp-launch-off"); b.classList.remove("fp-launch"); }}
      }}

      // 네비 버튼
      if(txt.indexOf("\ud3ec\ub85c\uc0ac\ub839\ubd80")>-1||txt.indexOf("\ud648")>-1){{
        b.classList.add("fp-nav");
      }}
    }});
  }}

  // 클래스 부여 2회 (Streamlit 렌더링 지연 대응)
  setTimeout(applyClasses, 150);
  setTimeout(applyClasses, 500);

  // 출격 border-color 지글지글 (border-color는 CSS keyframe + !important 충돌 → JS만 가능)
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

