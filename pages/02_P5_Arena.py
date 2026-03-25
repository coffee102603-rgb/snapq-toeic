"""P5 Arena v13b — 로비 구역별 색감 적용 (틸/핑크오렌지에메랄드인디고/포레스트)"""
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import random, time, json, os

st.set_page_config(page_title="P5 Arena ⚔️", page_icon="⚔️", layout="wide", initial_sidebar_state="collapsed")

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
            # 구버전 리스트 형태 → 신규 형태로 변환
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

# ═══ CSS ═══
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');
.stApp{background:#06060e!important;color:#eeeeff!important;}
section[data-testid="stSidebar"]{display:none!important;}
header[data-testid="stHeader"]{background:transparent!important;height:0!important;min-height:0!important;overflow:hidden!important;}
.block-container{padding-top:0!important;padding-bottom:0!important;margin-top:-8px!important;}
.ah{text-align:center;padding:0;margin:-4px 0 -4px 0;line-height:0.6;}
.ah h1{font-family:'Orbitron',monospace!important;font-size:0.95rem;font-weight:900;margin:0;background:linear-gradient(90deg,#00d4ff,#ffffff,#00d4ff);background-size:200%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:titleShine 3s linear infinite;letter-spacing:4px;}
@keyframes titleShine{0%{background-position:200% center}100%{background-position:-200% center}}
@keyframes warningPulse{0%,100%{color:#ff4466;text-shadow:0 0 8px rgba(255,68,102,0.8);}50%{color:#ff8888;text-shadow:0 0 20px rgba(255,68,102,1),0 0 40px rgba(255,0,50,0.6);}}
@keyframes p5bounce{0%,100%{transform:translateY(0);}30%{transform:translateY(-6px);}60%{transform:translateY(-3px);}80%{transform:translateY(-5px);}}
@keyframes p5flash{0%,75%,100%{box-shadow:0 0 12px rgba(0,212,255,0.15);}88%{box-shadow:0 0 45px rgba(0,255,255,1),0 0 90px rgba(0,212,255,0.7);}}
button[kind="primary"],button[kind="secondary"]{background:#0d0d0d!important;color:#fff!important;border:1.5px solid rgba(0,212,255,0.5)!important;border-radius:8px!important;font-size:1.0rem!important;font-weight:500!important;padding:0.35rem 0.8rem!important;text-align:left!important;transition:none!important;animation:none!important;transform:none!important;box-shadow:none!important;min-height:38px!important;}
button[kind="primary"] p,button[kind="secondary"] p{font-size:1.05rem!important;font-weight:700!important;color:#ddd8c8!important;text-align:left!important;}
button[kind="primary"]:hover,button[kind="secondary"]:hover{background:rgba(0,212,255,0.08)!important;border-color:#00d4ff!important;box-shadow:0 0 25px rgba(0,212,255,0.4)!important;transform:none!important;}
.qb{border-radius:12px;padding:0.3rem 0.5rem;margin:0.05rem 0;background:#0d0d0d;}
.qb-g{background:#0d0d0d!important;border:1.5px solid rgba(0,212,255,0.35)!important;border-radius:12px!important;animation:none;}.qb-v{background:#0d0d0d!important;border:1.5px solid rgba(68,136,204,0.35)!important;border-radius:12px!important;animation:none;}
@keyframes borderGlow{0%{box-shadow:0 0 0 2px #00d4ff,0 0 15px rgba(0,212,255,0.4);}50%{box-shadow:0 0 0 2px #fff,0 0 25px rgba(0,212,255,0.6);}100%{box-shadow:0 0 0 2px #00d4ff,0 0 15px rgba(0,212,255,0.4);}}
.qc{font-family:'Orbitron',monospace;font-size:0.72rem;font-weight:400;margin-bottom:0.3rem;letter-spacing:2px;color:#555!important;}
.qc-g,.qc-v{color:#444;text-shadow:none;}
.qt{font-family:'Rajdhani',sans-serif;color:#fff;font-size:0.95rem;font-weight:700;line-height:1.5;word-break:keep-all;}
.qk{color:#00d4ff;font-weight:900;font-size:0.95rem;border-bottom:2px solid #00d4ff;text-shadow:0 0 10px rgba(0,212,255,0.8);}
.bt{display:flex;align-items:center;justify-content:space-between;padding:0.01rem 0.8rem;border-radius:6px;margin-bottom:0;transform:scale(0.85);transform-origin:top center;margin-top:-8px;}
.bt-g,.bt-v{background:#0d0d0d;border:1px solid rgba(0,212,255,0.4);box-shadow:0 0 15px rgba(0,212,255,0.1);}
.bq{font-family:'Orbitron',monospace;font-size:1.6rem;font-weight:900;}
.bq-g,.bq-v{color:#00d4ff;text-shadow:0 0 10px rgba(0,212,255,0.8);}
.bs{font-family:'Orbitron',monospace;font-size:1.1rem;font-weight:800;color:#fff;}
.rd-dots{display:flex;justify-content:center;gap:0.6rem;margin:0 0;}
.rd-dot{width:22px;height:22px;border-radius:50%;border:2px solid #333;display:flex;align-items:center;justify-content:center;font-size:0.7rem;font-weight:900;}
.rd-cur{border-color:#00d4ff!important;color:#00d4ff!important;box-shadow:0 0 10px #00d4ff!important;}
.rd-ok{background:#00d4ff;border-color:#00d4ff;color:#000;}
.rd-no{background:#ff2244;border-color:#ff2244;color:#fff;}
.rd-wait{background:transparent;border-color:#333;color:#444;}
.cg,.cv{border-radius:18px;padding:1.5rem 1.2rem;margin-bottom:0.8rem;min-height:190px;display:flex;flex-direction:column;justify-content:center;animation:none;}
@keyframes fl{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
.cg{background:#0d0d0d;border:1.5px solid rgba(0,212,255,0.3);}
.cv{background:#0d0d0d;border:1.5px solid rgba(0,212,255,0.2);}
.ct{font-size:1.7rem;font-weight:900;margin-bottom:0.4rem;font-family:'Orbitron',monospace;}
.cg .ct{color:#00d4ff;}.cv .ct{color:#88ddff;}
.cd{font-size:1.3rem;font-weight:800;color:#ccc;line-height:1.5;}
.wb{background:#0d0d0d;border-radius:16px;padding:1.8rem 1.5rem;margin:0.5rem 0;border:1px solid rgba(0,212,255,0.3);min-height:250px;}
.wb-qn-ok{color:#00d4ff;}.wb-qn-no{color:#ff2244;}
.wb-s{font-size:2.15rem;font-weight:700;color:#f0f0f0;line-height:2;margin-bottom:1rem;word-break:keep-all;}
.wb-h{color:#00d4ff;font-weight:900;font-size:2.3rem;text-decoration:underline;text-decoration-color:#00d4ff;}
.wb-hn{color:#ff2244;font-weight:900;font-size:2.3rem;text-decoration:underline;text-decoration-color:#ff2244;}
.wb-k{font-size:1.6rem;font-weight:600;color:#ccc;line-height:1.7;}
.wb-e{font-size:1.5rem;color:#aaa;padding:0.6rem 0.8rem;background:rgba(0,212,255,0.06);border-left:4px solid #00d4ff;border-radius:0 10px 10px 0;}
.br-ban-v{border:1.5px solid #00d4ff;color:#00d4ff;}
.br-ban-l{border:1.5px solid #ff2244;color:#ff2244;}
.zl{color:#00d4ff!important;font-family:'Orbitron',monospace!important;letter-spacing:4px!important;}
details{background:rgba(0,212,255,0.03)!important;border-radius:12px!important;}
summary{color:#aaa!important;font-weight:700!important;}
::-webkit-scrollbar{width:4px;}::-webkit-scrollbar-track{background:#0a0a0a;}
::-webkit-scrollbar-thumb{background:rgba(0,212,255,0.4);border-radius:2px;}
@media(max-width:768px){
.block-container{padding-top:0.5rem!important;padding-bottom:2rem!important;padding-left:0.6rem!important;padding-right:0.6rem!important;}
.ah h1{font-size:1.5rem!important;letter-spacing:2px!important;}
button[kind="primary"],button[kind="secondary"]{font-size:1.6rem!important;padding:0.9rem 1rem!important;}
button[kind="primary"] p,button[kind="primary"] span,button[kind="secondary"] p,button[kind="secondary"] span{font-size:1.6rem!important;}
.qt{font-size:1.9rem!important;}.qk{font-size:2rem!important;}
.wb-s{font-size:1.7rem!important;}.wb-h,.wb-hn{font-size:1.85rem!important;}
.wb-k{font-size:1.3rem!important;}.wb-e{font-size:1.2rem!important;}
.bq{font-size:1.3rem!important;}.ct{font-size:1.4rem!important;}.cd{font-size:1.1rem!important;}
}
@media(max-width:480px){
.block-container{padding-top:0.3rem!important;padding-bottom:1.5rem!important;padding-left:0.3rem!important;padding-right:0.3rem!important;}
.ah h1{font-size:0.95rem!important;letter-spacing:1px!important;}
button[kind="primary"],button[kind="secondary"]{font-size:1rem!important;padding:0.5rem 0.5rem!important;border-radius:6px!important;}
button[kind="primary"] p,button[kind="primary"] span,button[kind="secondary"] p,button[kind="secondary"] span{font-size:1rem!important;}
.qt{font-size:1.2rem!important;line-height:1.6!important;}.qk{font-size:1.3rem!important;}
.qb{padding:0.8rem 0.7rem!important;border-radius:12px!important;}
.wb{padding:0.8rem 0.7rem!important;}.wb-s{font-size:1.1rem!important;line-height:1.6!important;}
.wb-h,.wb-hn{font-size:1.2rem!important;}.wb-k{font-size:0.95rem!important;}.wb-e{font-size:0.9rem!important;}
.bq{font-size:1rem!important;}.bs{font-size:0.85rem!important;}
.ct{font-size:1rem!important;}.cd{font-size:0.88rem!important;}
.rd-dot{width:16px!important;height:16px!important;}
.cg,.cv{min-height:120px!important;padding:0.8rem!important;}
}
@media(max-width:360px){
.ah h1{font-size:0.95rem!important;}
button[kind="primary"],button[kind="secondary"]{font-size:1.05rem!important;}
button[kind="primary"] p,button[kind="secondary"] p{font-size:1.05rem!important;}
.qt{font-size:1.25rem!important;}.qk{font-size:1.35rem!important;}
.wb-s{font-size:1.15rem!important;}
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
    "round_num":1,"phase":"lobby","mode":None,"used":[]}
for k,v in D.items():
    if k not in st.session_state: st.session_state[k]=v

# 메인허브에서 재진입 시에만 리셋 (_p5_just_left 플래그)
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
def pick5(m, grp=None):
    p=pool(m)
    if grp and grp in GRP:
        cats=GRP[grp]
        p=[q for q in p if q.get("cat","") in cats]
    elif grp and grp in VGRP:
        diff=VGRP[grp]
        p=[q for q in p if q.get("diff","")==diff]
        if len(p)<5: p=pool(m)
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
    if st.session_state.get("_battle_entry_ans_reset", True):
        st.session_state.ans = False
        st.session_state["_battle_entry_ans_reset"] = False
    q=st.session_state.cq
    if not q: st.session_state.phase="lobby"; st.rerun()
    ig=q.get("tp")=="grammar"; th="g" if ig else "v"; bt="primary" if ig else "secondary"
    ej="🔴" if ig else "🔵"; tn="문법" if ig else "어휘"

    st.markdown(f'<div class="ah"><h1>⚔️ {tn} 전장 — 라운드 {st.session_state.round_num} ⚔️</h1></div>', unsafe_allow_html=True)

    # 상단바 + 라운드 진행 dots
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

    # 타이머 (JS components.html)
    if not st.session_state.ans:
        # 1초마다 자동 새로고침 → 시간초과 감지
        st_autorefresh(interval=1000, limit=st.session_state.tsec+5, key="battle_timer")
        elapsed=time.time()-st.session_state.qst
        total=st.session_state.tsec; rem=max(0,total-int(elapsed))
        tcl=tcls(rem,total); pct=rem/total*100 if total>0 else 0

        components.html(f"""
        <style>
        *{{margin:0;padding:0;box-sizing:border-box;}}body{{background:transparent;overflow:hidden;font-family:sans-serif;margin:0;padding:0;}}
        #w{{text-align:center;padding:0;margin:0;line-height:1;}}
        #n{{font-size:1.8rem;font-weight:900;animation:p 1s ease-in-out infinite;}}
        #bw{{background:#1a1a2e;border-radius:8px;height:10px;margin:0.1rem 0.3rem;overflow:hidden;border:1px solid #333;}}
        #b{{height:100%;border-radius:10px;transition:width 1s linear;}}
        .safe{{color:#44ff88;text-shadow:0 0 20px #44ff88;}}
        .warn{{color:#ffcc00;text-shadow:0 0 25px #ffcc00,0 0 50px #ff8800;}}
        .danger{{color:#ff4444;text-shadow:0 0 35px #ff4444,0 0 70px #ff0000;}}
        .critical{{color:#ff0000;text-shadow:0 0 50px #ff0000;font-size:1.8rem!important;}}
        .bs{{background:linear-gradient(90deg,#22cc66,#44ff88);box-shadow:0 0 10px #44ff88;}}
        .bw{{background:linear-gradient(90deg,#cc8800,#ffcc00);box-shadow:0 0 10px #ffcc00;}}
        .bd{{background:linear-gradient(90deg,#cc2200,#ff4444);box-shadow:0 0 15px #ff4444;animation:bp 0.5s infinite;}}
        .bc{{background:linear-gradient(90deg,#ff0000,#ff4444);box-shadow:0 0 25px #ff0000;animation:bp 0.25s infinite;}}
        @keyframes p{{0%,100%{{transform:scale(1);opacity:1}}50%{{transform:scale(1.07);opacity:0.8}}}}
        @keyframes bp{{0%,100%{{opacity:1}}50%{{opacity:0.4}}}}@keyframes shake{{0%{{transform:translate(0,0)}}20%{{transform:translate(-3px,2px)}}40%{{transform:translate(3px,-2px)}}60%{{transform:translate(-2px,3px)}}80%{{transform:translate(2px,-3px)}}100%{{transform:translate(0,0)}}}}
        </style>
        <div id="w"><div id="n" class="{tcl}">{rem}</div>
        <div id="bw"><div id="b" class="b{'s' if tcl=='safe' else 'w' if tcl=='warn' else 'd' if tcl=='danger' else 'c'}" style="width:{pct}%"></div></div></div>
        <script>
        var l={rem},t={total};var e=document.getElementById("n"),b=document.getElementById("b");
        setInterval(function(){{l--;if(l<0)l=0;e.textContent=l;var r=l/t;
        var c=r>0.6?"safe":r>0.35?"warn":r>0.15?"danger":"critical";e.className=c;
        b.className="b"+(r>0.6?"s":r>0.35?"w":r>0.15?"d":"c");b.style.width=(r*100)+"%";}},1000);
        </script>""", height=44)

        # 시간초과 → YOU LOST
        if rem<=0:
            st.session_state.phase="lost"; st.rerun()

    # 문제
    st.markdown(f'<div class="qb qb-{th}"><div class="qc qc-{th}">{ej} {tn} · {q.get("cat","")}</div><div class="qt">{fq(q["text"])}</div></div>', unsafe_allow_html=True)

    # st.radio
    if not st.session_state.ans:
        _qi = st.session_state.get('qi', 0)
        _rn = st.session_state.get('round_num', 0)
        st.markdown('<style>div[data-testid=stRadio]>label{display:none!important;}div[data-testid=stRadio]>div{gap:7px!important;}div[data-testid=stRadio]>div>label{background:#0c0c14!important;border:1px solid #1a1a28!important;border-radius:8px!important;padding:0.65rem 0.9rem!important;cursor:pointer!important;width:100%!important;box-sizing:border-box!important;display:flex!important;align-items:center!important;}div[data-testid=stRadio]>div>label>div:first-child{display:none!important;}div[data-testid=stRadio]>div>label>div:last-child p{font-size:1.05rem!important;font-weight:700!important;color:#ddd8c8!important;margin:0!important;text-align:left!important;}div[data-testid=stRadio]>div>label:nth-child(1){border-left:4px solid #d4af37!important;}div[data-testid=stRadio]>div>label:nth-child(1)>div:last-child p{color:#d4af37!important;}div[data-testid=stRadio]>div>label:nth-child(2){border-left:4px solid #9aa5b4!important;}div[data-testid=stRadio]>div>label:nth-child(2)>div:last-child p{color:#9aa5b4!important;}div[data-testid=stRadio]>div>label:nth-child(3){border-left:4px solid #50c878!important;}div[data-testid=stRadio]>div>label:nth-child(3)>div:last-child p{color:#50c878!important;}div[data-testid=stRadio]>div>label:nth-child(4){border-left:4px solid #4488cc!important;}div[data-testid=stRadio]>div>label:nth-child(4)>div:last-child p{color:#4488cc!important;}</style>', unsafe_allow_html=True)
        _choice = st.radio('sel', options=q['ch'], index=None, key='ch_%s_%s' % (_rn, _qi), label_visibility='collapsed')
        if _choice is not None:
            if time.time()-st.session_state.qst>st.session_state.tsec:
                st.session_state.phase='lost'; st.rerun()
            i = q['ch'].index(_choice)
            st.session_state.ans=True; st.session_state.sel=i
            ok=i==q['a']
            st.session_state.round_results.append(ok)
            if ok: st.session_state.sc+=1
            else: st.session_state.wrong+=1
            st.session_state.ta+=1

            # ══════════════════════════════════════════════════
            # ★ 논문·특허 데이터 수집 (rt_logs + zpd_logs + p5_logs)
            # ══════════════════════════════════════════════════
            try:
                _elapsed_now = time.time() - st.session_state.qst
                _tsec_now    = st.session_state.tsec
                _sec_rem     = round(max(0.0, _tsec_now - _elapsed_now), 2)
                _rt_proxy    = round(_tsec_now - _sec_rem, 2)
                _rem_ratio   = _sec_rem / _tsec_now if _tsec_now > 0 else 0

                # 오답 타이밍 유형 분류 (논문 03 핵심)
                if ok:
                    _err_type = "correct"
                elif _rem_ratio > 0.8:
                    _err_type = "fast_wrong"   # 빠른 오답 = 충동 반응
                elif _rem_ratio < 0.2:
                    _err_type = "slow_wrong"   # 느린 오답 = 인지부하
                else:
                    _err_type = "mid_wrong"

                _uid  = st.session_state.get("nickname", "guest")
                _cat  = q.get("cat", "")
                _qid  = q.get("id", "?")
                _today = datetime.now().strftime("%Y-%m-%d") if "datetime" in dir() else __import__("datetime").datetime.now().strftime("%Y-%m-%d")

                # 세션 번호 (누적) — 없으면 초기화
                if "p5_session_no" not in st.session_state:
                    st.session_state.p5_session_no = 0
                _sno = st.session_state.p5_session_no

                # 주차 계산 (첫 접속일 기준)
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

                # ── A. rt_logs (논문 01·03 핵심) ──────────────
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
                    "week":             _week,
                    "timestamp":        __import__("datetime").datetime.now().isoformat(),
                }
                if "rt_logs" not in _st_data:
                    _st_data["rt_logs"] = []
                _st_data["rt_logs"].append(_rt_log)

                # ── B. zpd_logs — 게임오버 시 종료 지점 기록 (논문 06) ──
                # (게임오버 직전 마지막 문제 번호를 기록 → 세션 끝날 때 저장)
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
                pass  # 데이터 수집 실패해도 게임은 계속

            # ── 기존 DataCollector 유지 ──
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
# ════════════════════════════════════════
elif st.session_state.phase=="victory":
    # ★ 세션 번호 증가 + ZPD VICTORY 기록
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

        # zpd_logs: VICTORY = 5번 문제까지 도달
        _zpd_entry = {
            "user_id":        _uid2,
            "session_date":   _today2,
            "session_no":     _sno2,
            "arena":          "P5",
            "timer_setting":  st.session_state.tsec,
            "game_over_q_no": None,
            "result":         "VICTORY",
            "max_q_reached":  5,
            "week":           _week2,
            "timestamp":      __import__("datetime").datetime.now().isoformat(),
        }
        if "zpd_logs" not in _st2:
            _st2["zpd_logs"] = []
        _st2["zpd_logs"].append(_zpd_entry)

        # p5_logs: 라운드 결과 요약
        _p5_entry = {
            "user_id":       _uid2,
            "session_date":  _today2,
            "session_no":    _sno2,
            "timer_selected": st.session_state.tsec,
            "mode":          st.session_state.mode,
            "result":        "VICTORY",
            "correct_count": st.session_state.sc,
            "wrong_count":   st.session_state.wrong,
            "week":          _week2,
            "timestamp":     __import__("datetime").datetime.now().isoformat(),
        }
        if "p5_logs" not in _st2:
            _st2["p5_logs"] = []
        # 같은 세션 중복 방지
        if not any(p.get("session_no") == _sno2 and p.get("user_id") == _uid2 and p.get("result") == "VICTORY"
                   for p in _st2["p5_logs"]):
            _st2["p5_logs"].append(_p5_entry)

        with open(STORAGE_FILE, "w", encoding="utf-8") as _f2:
            json.dump(_st2, _f2, ensure_ascii=False, indent=2)
    except:
        pass
    _sc_v = st.session_state.sc
    _wr_v = st.session_state.wrong
    _rn_v = st.session_state.round_num
    if _sc_v == 5:
        _grade = "👑 PERFECT!"; _praise = "완벽해! 토익 만점도 따놓은 당상! 🔥"; _pcol = "#ffd700"
    elif _sc_v == 4:
        _grade = "⚔️ VICTORY!"; _praise = "강해! 이 기세면 토익 900+ 간다! 💪"; _pcol = "#44ff88"
    else:
        _grade = "✅ CLEAR!"; _praise = "아슬아슬하게 살아남았어. 더 갈고닦아! 😤"; _pcol = "#88ccff"
    _stars_html = "".join([f'<div class="star" style="left:{random.randint(2,98)}%;top:{random.randint(2,98)}%;width:{random.randint(3,10)}px;height:{random.randint(3,10)}px;animation-delay:{random.random():.2f}s;animation-duration:{0.5+random.random()*1:.1f}s;background:{"#ffd700" if random.random()>0.4 else "#fff8cc"};border-radius:50%;position:absolute;"></div>' for _ in range(50)])
    _coins_html = "".join([f'<div class="coin" style="left:{random.randint(5,95)}%;animation-delay:{random.random():.2f}s;animation-duration:{1.2+random.random():.1f}s;">{"💰" if random.random()>0.5 else "⭐"}</div>' for _ in range(10)])
    components.html(f"""
    <style>
    *{{margin:0;padding:0;box-sizing:border-box;}}
    body{{background:linear-gradient(180deg,#080600 0%,#1a1200 100%);overflow:hidden;height:100vh;font-family:'Arial Black',sans-serif;display:flex;align-items:center;justify-content:center;}}
    @keyframes vi{{0%{{transform:scale(0) rotate(-15deg);opacity:0;}}65%{{transform:scale(1.1) rotate(3deg);}}100%{{transform:scale(1) rotate(0deg);opacity:1;}}}}
    @keyframes goldGlow{{0%,100%{{text-shadow:0 0 20px #ffd700,0 0 50px #ff8800;}}50%{{text-shadow:0 0 50px #ffd700,0 0 100px #ff8800,0 0 160px #ff4400;}}}}
    @keyframes twinkle{{0%,100%{{opacity:1;transform:scale(1) rotate(0deg);}}50%{{opacity:0.15;transform:scale(0.2) rotate(180deg);}}}}
    @keyframes coinFall{{0%{{transform:translateY(-20px) rotate(0deg) scale(1);opacity:1;}}100%{{transform:translateY(130px) rotate(540deg) scale(0.5);opacity:0;}}}}
    @keyframes scoreIn{{0%{{transform:translateY(30px);opacity:0;}}100%{{transform:translateY(0);opacity:1;}}}}
    @keyframes barFill{{0%{{width:0%;}}100%{{width:{int(_sc_v/5*100)}%;}}}}
    @keyframes pulse{{0%,100%{{transform:scale(1);}}50%{{transform:scale(1.04);}}}}
    .wrap{{text-align:center;animation:vi 0.8s cubic-bezier(0.34,1.56,0.64,1) forwards;position:relative;z-index:10;width:88%;}}
    .round-tag{{font-size:0.7rem;color:#886600;font-weight:700;letter-spacing:3px;margin-bottom:6px;}}
    .grade{{font-size:2.6rem;font-weight:900;color:#ffd700;animation:goldGlow 2s ease-in-out infinite, pulse 1.5s ease-in-out infinite;letter-spacing:2px;line-height:1.1;}}
    .scorebox{{background:rgba(212,175,55,0.1);border:2px solid rgba(212,175,55,0.6);border-radius:14px;padding:12px 24px;margin:10px auto;display:inline-block;animation:scoreIn 0.6s ease 0.3s both;}}
    .sc-num{{font-size:3rem;font-weight:900;color:#ffd700;line-height:1;text-shadow:0 0 20px rgba(255,215,0,0.6);}}
    .sc-label{{font-size:0.72rem;color:#886600;font-weight:700;letter-spacing:1px;margin-top:2px;}}
    .bar-wrap{{background:#1a1200;border-radius:20px;height:10px;margin:10px auto;width:82%;overflow:hidden;border:1px solid #443300;}}
    .bar-fill{{height:100%;border-radius:20px;background:linear-gradient(90deg,#a07800,#ffd700,#fff8aa);box-shadow:0 0 8px #ffd700;animation:barFill 1s ease 0.6s both;}}
    .praise{{font-size:0.9rem;color:{_pcol};font-weight:900;margin:8px 0 2px;animation:scoreIn 0.5s ease 0.8s both;}}
    .star{{position:absolute;animation:twinkle var(--dur,1s) ease-in-out infinite;}}
    .coin{{position:absolute;top:-10px;font-size:1.4rem;animation:coinFall var(--dur,1.5s) ease-in infinite;}}
    </style>
    <div style="position:absolute;width:100%;height:100%;overflow:hidden;top:0;left:0;">{_stars_html}{_coins_html}</div>
    <div class="wrap">
        <div class="round-tag">⚔️ ROUND {_rn_v} CLEAR ⚔️</div>
        <div class="grade">{_grade}</div>
        <div class="scorebox">
            <div class="sc-num">{_sc_v}<span style="font-size:1.4rem;color:#886600;"> / 5</span></div>
            <div class="sc-label">✅ {_sc_v}격파 &nbsp;·&nbsp; ❌ {_wr_v}개 놓침</div>
        </div>
        <div class="bar-wrap"><div class="bar-fill"></div></div>
        <div class="praise">{_praise}</div>
    </div>
    """, height=230)

    st.markdown("""<style>
    button[kind="primary"]{background:#0c0c00!important;border:2px solid #d4af37!important;}
    button[kind="primary"] p{color:#ffd700!important;font-size:1.1rem!important;font-weight:900!important;}
    button[kind="primary"]:hover{background:rgba(212,175,55,0.12)!important;box-shadow:0 0 20px rgba(212,175,55,0.5)!important;}
    button[kind="secondary"]{background:#0a0a0a!important;border:1.5px solid rgba(255,255,255,0.2)!important;}
    button[kind="secondary"] p{color:#888!important;font-size:1.0rem!important;}
    </style>""", unsafe_allow_html=True)
    vc=st.columns(2)
    with vc[0]:
        if st.button("📋 브리핑 보기", type="primary", use_container_width=True):
            st.session_state.phase="briefing"; st.rerun()
    with vc[1]:
        if st.button("🏠 홈", type="secondary", use_container_width=True):
            st.session_state._p5_just_left = True
            st.session_state.ans = False
            st.session_state["_battle_entry_ans_reset"] = True
            st.switch_page("main_hub.py")

# ════════════════════════════════════════
# PHASE: YOU LOST
# ════════════════════════════════════════
elif st.session_state.phase=="lost":
    # ★ 세션 번호 증가 + ZPD GAME_OVER 기록
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

        # zpd_logs: _zpd_pending에서 꺼내서 저장
        _pending = _st3.get("_zpd_pending", {}).get(_uid3, {})
        _go_q = _pending.get("game_over_q_no", st.session_state.qi + 1)
        _zpd3 = {
            "user_id":        _uid3,
            "session_date":   _today3,
            "session_no":     _sno3,
            "arena":          "P5",
            "timer_setting":  st.session_state.tsec,
            "game_over_q_no": _go_q,
            "result":         "GAME_OVER",
            "max_q_reached":  st.session_state.qi + 1,
            "week":           _week3,
            "timestamp":      __import__("datetime").datetime.now().isoformat(),
        }
        if "zpd_logs" not in _st3:
            _st3["zpd_logs"] = []
        if not any(z.get("session_no") == _sno3 and z.get("user_id") == _uid3
                   for z in _st3["zpd_logs"]):
            _st3["zpd_logs"].append(_zpd3)

        # p5_logs: 라운드 결과 요약
        _p5e3 = {
            "user_id":        _uid3,
            "session_date":   _today3,
            "session_no":     _sno3,
            "timer_selected": st.session_state.tsec,
            "mode":           st.session_state.mode,
            "result":         "GAME_OVER",
            "correct_count":  st.session_state.sc,
            "wrong_count":    st.session_state.wrong,
            "week":           _week3,
            "timestamp":      __import__("datetime").datetime.now().isoformat(),
        }
        if "p5_logs" not in _st3:
            _st3["p5_logs"] = []
        if not any(p.get("session_no") == _sno3 and p.get("user_id") == _uid3 and p.get("result") == "GAME_OVER"
                   for p in _st3["p5_logs"]):
            _st3["p5_logs"].append(_p5e3)

        with open(STORAGE_FILE, "w", encoding="utf-8") as _f3:
            json.dump(_st3, _f3, ensure_ascii=False, indent=2)
    except:
        pass
    _sc = st.session_state.sc
    _wrong = st.session_state.wrong
    _pct = int(_sc / 5 * 100)
    _is_timeout = (time.time()-st.session_state.qst > st.session_state.tsec)
    _reason = "시간초과" if _is_timeout else f"오답 {_wrong}개"
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
    components.html(f"""
    <style>
    *{{margin:0;padding:0;box-sizing:border-box;}}
    body{{background:#0a0000;overflow:hidden;display:flex;align-items:center;justify-content:center;height:100vh;font-family:'Arial Black',sans-serif;}}
    @keyframes redPulse{{0%,100%{{background:#0a0000;}}50%{{background:#1a0000;}}}}
    @keyframes crashIn{{0%{{transform:scale(4) rotate(-5deg);opacity:0;}}60%{{transform:scale(0.9) rotate(2deg);}}100%{{transform:scale(1) rotate(0deg);opacity:1;}}}}
    @keyframes shakeX{{0%,100%{{transform:translateX(0);}}20%{{transform:translateX(-8px);}}40%{{transform:translateX(8px);}}60%{{transform:translateX(-5px);}}80%{{transform:translateX(5px);}}}}
    @keyframes rise{{0%{{opacity:1;transform:translateY(0) scale(1);}}100%{{opacity:0;transform:translateY(-300px) scale(0.3);}}}}
    @keyframes flicker{{0%,100%{{opacity:1;}}50%{{opacity:0.7;}}}}
    body{{animation:redPulse 0.8s ease-in-out infinite;}}
    .wrap{{text-align:center;animation:crashIn 0.6s cubic-bezier(0.34,1.56,0.64,1) forwards;z-index:10;position:relative;padding:6px;}}
    .skull{{font-size:2rem;animation:shakeX 0.4s ease-in-out infinite;display:inline-block;margin-bottom:4px;}}
    .lost-txt{{font-size:1.5rem;font-weight:900;color:#ff0000;text-shadow:0 0 10px #ff0000;animation:flicker 0.3s infinite;letter-spacing:2px;}}
    .reason{{font-size:0.8rem;color:#ff6644;font-weight:700;margin:3px 0;letter-spacing:1px;}}
    .score{{font-size:2.2rem;font-weight:900;color:#ffcc00;text-shadow:0 0 20px #ffaa00,0 0 40px #ff8800;margin:6px 0;}}
    .taunt{{font-size:1.0rem;color:#ff8888;font-weight:900;margin:6px 0;animation:shakeX 3s ease-in-out infinite;}}
    .sub{{font-size:0.8rem;color:#ff6666;margin-top:3px;font-weight:700;}}
    .embers{{position:absolute;width:100%;height:100%;top:0;left:0;pointer-events:none;}}
    .ember{{position:absolute;border-radius:50%;animation:rise 1.5s ease-in infinite;}}
    </style>
    <div class="embers">""" + "".join([f'<div class="ember" style="left:{random.randint(5,95)}%;bottom:{random.randint(0,20)}%;width:{random.randint(4,10)}px;height:{random.randint(4,10)}px;background:{"#ff4400" if random.random()>0.5 else "#ff8800"};animation-delay:{random.random():.1f}s;animation-duration:{1+random.random():.1f}s;"></div>' for _ in range(40)]) + f"""</div>
    <div class="wrap">
        <div class="skull">💀</div>
        <div class="lost-txt">GAME OVER</div>
        <div class="reason">[ {_reason} ]</div>
        <div class="score">{_pct}점</div>
        <div class="taunt">{_taunt}</div>
        <div class="sub">{_sub}</div>
    </div>""", height=160)
    st.markdown("""<style>
    button[kind="primary"]{background:#0a0000!important;border:2px solid #cc2244!important;}
    button[kind="primary"] p{color:#ff4466!important;font-size:1.1rem!important;font-weight:900!important;}
    button[kind="primary"]:hover{background:rgba(204,34,68,0.15)!important;box-shadow:0 0 20px rgba(255,0,60,0.5)!important;}
    button[kind="secondary"]{background:#0a0a0a!important;border:1.5px solid rgba(255,255,255,0.2)!important;}
    button[kind="secondary"] p{color:#888!important;font-size:1.0rem!important;}
    </style>""", unsafe_allow_html=True)
    bc=st.columns(2)
    with bc[0]:
        if st.button("🔥 설욕전! 다시 싸운다!", type="primary", use_container_width=True):
            for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","round_num"]:
                if k in D: st.session_state[k]=D[k]
            st.session_state.phase="lobby"; st.rerun()
    with bc[1]:
        if st.button("🏠 홈", type="secondary", use_container_width=True):
            st.session_state._p5_just_left = True
            st.session_state.ans = False
            st.session_state["_battle_entry_ans_reset"] = True
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
    div[data-testid="stHorizontalBlock"]{margin:0!important;padding:0!important;}
    div[data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:6px!important;}
    div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]{min-width:0!important;flex:1!important;padding:0!important;}
    div[data-testid="stHorizontalBlock"] button{width:100%!important;min-height:40px!important;font-size:0.9rem!important;padding:4px 2px!important;animation:none!important;transform:none!important;}
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
        st.markdown(f'''<div style="background:#0c0c00;border:2px solid #d4af37;border-left:5px solid #d4af37;border-radius:10px;padding:13px 12px;margin-bottom:6px;">
            <div style="font-size:1.0rem;font-weight:900;color:#d4af37;">🏆 라운드 {rn} — VICTORY!</div>
            <div style="font-size:0.75rem;color:#886600;margin-top:2px;">✅{sc_v}문제 격파! ❌{wr_v}개 놓침</div>
        </div>''', unsafe_allow_html=True)
    else:
        st.markdown(f'''<div style="background:#0c0008;border:2px solid #cc2244;border-left:5px solid #cc2244;border-radius:10px;padding:13px 12px;margin-bottom:6px;">
            <div style="font-size:1.0rem;font-weight:900;color:#cc2244;">💀 라운드 {rn} — GAME OVER</div>
            <div style="font-size:0.75rem;color:#661122;margin-top:2px;">✅{sc_v}문제 / ❌{wr_v}개 틀림</div>
        </div>''', unsafe_allow_html=True)

    # 네비 — 숫자만 (화살표 없음)
    st.markdown('''<style>
    .nav-size [data-testid="stHorizontalBlock"] button{font-size:0.58rem!important;min-height:22px!important;padding:1px 2px!important;line-height:1!important;}
    .nav-size [data-testid="stHorizontalBlock"] button p{font-size:0.72rem!important;}
    .sv-size [data-testid="stColumn"]:last-child button{font-size:0.72rem!important;min-height:32px!important;}
    .sv-size [data-testid="stColumn"]:last-child button p{font-size:0.72rem!important;}
    .br-size [data-testid="stHorizontalBlock"] button{font-size:0.66rem!important;min-height:36px!important;padding:4px!important;}
    .br-size [data-testid="stHorizontalBlock"] button p{font-size:0.66rem!important;}
    </style>''', unsafe_allow_html=True)
    st.markdown('<div class="nav-size">', unsafe_allow_html=True)
    _ncols = st.columns(num_qs)
    for _i in range(num_qs):
        with _ncols[_i]:
            _sel = "outline:2px solid #9aa5b4;outline-offset:2px;" if _i==bi else ""
            _bg = "#1a1a2a" if _i==bi else "#0d0d18"
            st.markdown(f'''<style>
            div[data-testid="stHorizontalBlock"] div[data-testid="stColumn"]:nth-child({_i+1}) button{{
                background:{_bg}!important;
                border:2px solid #9aa5b4!important;
                color:#9aa5b4!important;
                border-radius:50%!important;
                {_sel}
            }}</style>''', unsafe_allow_html=True)
            if st.button(str(_i+1), key=f"dot_{_i}", use_container_width=True):
                st.session_state.br_idx = _i; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 문제 카드
    q  = rqs[bi]; ok = rrs[bi]
    ans_clean = q["ch"][q["a"]].split(") ",1)[-1] if ") " in q["ch"][q["a"]] else q["ch"][q["a"]]
    if ok:
        sent_html = q["text"].replace("_______", '<span style="color:#50c878;font-weight:900;border-bottom:2px solid #50c878;">'+ans_clean+'</span>')
        card_border="#00d4ff"; qnum_color="#50c878"; qnum_sym="✅"
    else:
        sent_html = q["text"].replace("_______", '<span style="color:#ff4466;font-weight:900;text-decoration:line-through;margin-right:4px;">?</span><span style="color:#50c878;font-weight:900;border-bottom:2px solid #50c878;">'+ans_clean+'</span>')
        card_border="#cc2244"; qnum_color="#ff4466"; qnum_sym="❌"
    kr=q.get("kr",""); exk=q.get("exk",""); cat=q.get("cat","")

    st.markdown(f'''<div style="background:#0c0c18;border:1.5px solid {card_border};border-left:4px solid {card_border};border-radius:12px;padding:10px 12px;margin:4px 0;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <span style="background:#0a0a20;border:1px solid #222;border-radius:10px;padding:2px 10px;font-size:0.86rem;font-weight:700;color:{qnum_color};">{qnum_sym} Q{bi+1}/{num_qs}</span>
            <span style="font-size:0.7rem;color:#444;">{cat}</span>
        </div>
        <div style="font-size:1.1rem;font-weight:700;color:#eeeeff;line-height:1.7;margin-bottom:8px;">{sent_html}</div>
        <div style="font-size:0.88rem;color:#9aa5b4;margin-bottom:6px;">📖 {kr}</div>
        <div style="background:#081008;border-left:3px solid #50c878;border-radius:0 8px 8px 0;padding:6px 10px;">
            <div style="font-size:0.88rem;color:#50c878;font-weight:700;">💡 {exk}</div>
        </div>
    </div>''', unsafe_allow_html=True)

    # 저장 버튼
    st.markdown('<div class="sv-size">', unsafe_allow_html=True)
    _sv1, _sv2 = st.columns([3, 1])
    with _sv2:
        _is_saved = bi in saved
        _slabel = "✅ 저장됨" if _is_saved else "💾 저장해!"
        st.markdown('''<style>
        div[data-testid="stColumn"]:last-child button{
            border:2px solid #9aa5b4!important;
            color:#9aa5b4!important;
            background:#0d0d18!important;
            border-radius:50px!important;
            font-size:0.85rem!important;
        }
        div[data-testid="stColumn"]:last-child button p{
            color:#9aa5b4!important;
        }
        </style>''', unsafe_allow_html=True)
        if st.button(_slabel, key=f"sv_{q['id']}_{bi}", use_container_width=True, disabled=_is_saved):
            item = {"id":q["id"],"text":q["text"],"ch":q["ch"],"a":q["a"],"ex":q.get("ex",""),"exk":q.get("exk",""),"cat":q.get("cat",""),"kr":q.get("kr",""),"tp":q.get("tp","grammar")}
            save_to_storage([item])
            st.session_state.br_saved.add(bi)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:#1a1a2a;margin:2px 0;"></div>', unsafe_allow_html=True)

    # 하단 버튼
    st.markdown('''<style>
    .bottom-row [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:8px!important;}
    .bottom-row [data-testid="stHorizontalBlock"] [data-testid="stColumn"]{min-width:0!important;flex:1!important;padding:0!important;}
    .bottom-row button{
        background:transparent!important;
        border:1px solid rgba(255,255,255,0.4)!important;
        color:rgba(255,255,255,0.55)!important;
        font-weight:400!important;
        font-size:0.82rem!important;
        border-radius:8px!important;
        min-height:44px!important;
        box-shadow:none!important;
    }
    .bottom-row button p{
        color:rgba(255,255,255,0.55)!important;
        font-size:0.82rem!important;
        font-weight:400!important;
    }
    </style>''', unsafe_allow_html=True)
    st.markdown('<div class="bottom-row br-size">', unsafe_allow_html=True)
    if was_victory:
        nrd = rn + 1
        _c1, _c2 = st.columns([2,1])
        with _c1:
            if st.button("🔥 오답전장!", use_container_width=True):
                st.switch_page("pages/03_오답전장.py")
        with _c2:
            if st.button("🏠 홈", use_container_width=True):
                st.session_state._p5_just_left = True
                st.session_state.ans = False
                st.session_state["_battle_entry_ans_reset"] = True
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
                st.switch_page("main_hub.py")
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
        st.switch_page("pages/03_오답전장.py")
    st.session_state.phase="lobby"
    if "sel_mode" not in st.session_state: st.session_state.sel_mode=None

    tsec = st.session_state.tsec
    sm = st.session_state.sel_mode
    rn = st.session_state.round_num

    # ─── 밝은 리모컨 CSS ───
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');
.stApp{background:#06060e!important;color:#eeeeff!important;}
section[data-testid="stSidebar"]{display:none!important;}
header[data-testid="stHeader"]{background:transparent!important;height:0!important;min-height:0!important;overflow:hidden!important;}
.block-container{padding-top:0!important;padding-bottom:0!important;margin-top:-8px!important;}
.ah{text-align:center;padding:0 0 0 0;}
.ah h1{font-family:'Orbitron',monospace!important;font-size:2rem;font-weight:900;margin:0;background:linear-gradient(90deg,#00d4ff,#ffffff,#00d4ff);background-size:200%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:titleShine 3s linear infinite;letter-spacing:4px;}
@keyframes titleShine{0%{background-position:200% center}100%{background-position:-200% center}}
@keyframes warningPulse{0%,100%{color:#ff4466;text-shadow:0 0 8px rgba(255,68,102,0.8);}50%{color:#ff8888;text-shadow:0 0 20px rgba(255,68,102,1),0 0 40px rgba(255,0,50,0.6);}}
@keyframes p5bounce{0%,100%{transform:translateY(0);}30%{transform:translateY(-6px);}60%{transform:translateY(-3px);}80%{transform:translateY(-5px);}}
@keyframes p5flash{0%,75%,100%{box-shadow:0 0 12px rgba(0,212,255,0.15);}88%{box-shadow:0 0 45px rgba(0,255,255,1),0 0 90px rgba(0,212,255,0.7);}}
button[kind="primary"],button[kind="secondary"]{background:#0d0d0d!important;color:#fff!important;border:1.5px solid rgba(0,212,255,0.5)!important;border-radius:8px!important;font-size:1.0rem!important;font-weight:500!important;padding:0.35rem 0.8rem!important;text-align:left!important;transition:none!important;animation:none!important;transform:none!important;box-shadow:none!important;min-height:38px!important;}
button[kind="primary"] p,button[kind="secondary"] p{font-size:1.05rem!important;font-weight:700!important;color:#ddd8c8!important;text-align:left!important;}
button[kind="primary"]:hover,button[kind="secondary"]:hover{background:rgba(0,212,255,0.08)!important;border-color:#00d4ff!important;box-shadow:0 0 25px rgba(0,212,255,0.4)!important;transform:none!important;}
.qb{border-radius:12px;padding:0.3rem 0.5rem;margin:0.05rem 0;background:#0d0d0d;}
.qb-g{background:#0d0d0d!important;border:1.5px solid rgba(0,212,255,0.35)!important;border-radius:12px!important;animation:none;}.qb-v{background:#0d0d0d!important;border:1.5px solid rgba(68,136,204,0.35)!important;border-radius:12px!important;animation:none;}
@keyframes borderGlow{0%{box-shadow:0 0 0 2px #00d4ff,0 0 15px rgba(0,212,255,0.4);}50%{box-shadow:0 0 0 2px #fff,0 0 25px rgba(0,212,255,0.6);}100%{box-shadow:0 0 0 2px #00d4ff,0 0 15px rgba(0,212,255,0.4);}}
.qc{font-family:'Orbitron',monospace;font-size:0.72rem;font-weight:400;margin-bottom:0.3rem;letter-spacing:2px;color:#555!important;}
.qc-g,.qc-v{color:#444;text-shadow:none;}
.qt{font-family:'Rajdhani',sans-serif;color:#fff;font-size:0.95rem;font-weight:700;line-height:1.5;word-break:keep-all;}
.qk{color:#00d4ff;font-weight:900;font-size:0.95rem;border-bottom:2px solid #00d4ff;text-shadow:0 0 10px rgba(0,212,255,0.8);}
.bt{display:flex;align-items:center;justify-content:space-between;padding:0.01rem 0.8rem;border-radius:6px;margin-bottom:0;transform:scale(0.85);transform-origin:top center;margin-top:-8px;}
.bt-g,.bt-v{background:#0d0d0d;border:1px solid rgba(0,212,255,0.4);box-shadow:0 0 15px rgba(0,212,255,0.1);}
.bq{font-family:'Orbitron',monospace;font-size:1.6rem;font-weight:900;}
.bq-g,.bq-v{color:#00d4ff;text-shadow:0 0 10px rgba(0,212,255,0.8);}
.bs{font-family:'Orbitron',monospace;font-size:1.1rem;font-weight:800;color:#fff;}
.rd-dots{display:flex;justify-content:center;gap:0.6rem;margin:0 0;}
.rd-dot{width:22px;height:22px;border-radius:50%;border:2px solid #333;display:flex;align-items:center;justify-content:center;font-size:0.7rem;font-weight:900;}
.rd-cur{border-color:#00d4ff!important;color:#00d4ff!important;box-shadow:0 0 10px #00d4ff!important;}
.rd-ok{background:#00d4ff;border-color:#00d4ff;color:#000;}
.rd-no{background:#ff2244;border-color:#ff2244;color:#fff;}
.rd-wait{background:transparent;border-color:#333;color:#444;}
.cg,.cv{border-radius:18px;padding:1.5rem 1.2rem;margin-bottom:0.8rem;min-height:190px;display:flex;flex-direction:column;justify-content:center;animation:none;}
@keyframes fl{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
.cg{background:#0d0d0d;border:1.5px solid rgba(0,212,255,0.3);}
.cv{background:#0d0d0d;border:1.5px solid rgba(0,212,255,0.2);}
.ct{font-size:1.7rem;font-weight:900;margin-bottom:0.4rem;font-family:'Orbitron',monospace;}
.cg .ct{color:#00d4ff;}.cv .ct{color:#88ddff;}
.cd{font-size:1.3rem;font-weight:800;color:#ccc;line-height:1.5;}
.wb{background:#0d0d0d;border-radius:16px;padding:1.8rem 1.5rem;margin:0.5rem 0;border:1px solid rgba(0,212,255,0.3);min-height:250px;}
.wb-qn-ok{color:#00d4ff;}.wb-qn-no{color:#ff2244;}
.wb-s{font-size:2.15rem;font-weight:700;color:#f0f0f0;line-height:2;margin-bottom:1rem;word-break:keep-all;}
.wb-h{color:#00d4ff;font-weight:900;font-size:2.3rem;text-decoration:underline;text-decoration-color:#00d4ff;}
.wb-hn{color:#ff2244;font-weight:900;font-size:2.3rem;text-decoration:underline;text-decoration-color:#ff2244;}
.wb-k{font-size:1.6rem;font-weight:600;color:#ccc;line-height:1.7;}
.wb-e{font-size:1.5rem;color:#aaa;padding:0.6rem 0.8rem;background:rgba(0,212,255,0.06);border-left:4px solid #00d4ff;border-radius:0 10px 10px 0;}
.br-ban-v{border:1.5px solid #00d4ff;color:#00d4ff;}
.br-ban-l{border:1.5px solid #ff2244;color:#ff2244;}
.zl{color:#00d4ff!important;font-family:'Orbitron',monospace!important;letter-spacing:4px!important;}
details{background:rgba(0,212,255,0.03)!important;border-radius:12px!important;}
summary{color:#aaa!important;font-weight:700!important;}
::-webkit-scrollbar{width:4px;}::-webkit-scrollbar-track{background:#0a0a0a;}
::-webkit-scrollbar-thumb{background:rgba(0,212,255,0.4);border-radius:2px;}
</style>
""", unsafe_allow_html=True)

    # ═══ 뮤지컬 3막 로비 CSS ═══
    st.markdown("""<style>
    @keyframes titleGlow{0%,100%{text-shadow:0 0 20px #00d4ff,0 0 40px #00d4ff;}50%{text-shadow:0 0 30px #00ffaa,0 0 60px #00ffaa;}}
    @keyframes stageIn{from{opacity:0;transform:translateY(30px);}to{opacity:1;transform:translateY(0);}}
    @keyframes pulse{0%,100%{box-shadow:0 0 20px rgba(0,212,255,0.4);}50%{box-shadow:0 0 40px rgba(0,212,255,0.8),0 0 60px rgba(0,212,255,0.3);}}
    @keyframes startPulse{0%,100%{box-shadow:0 0 25px rgba(255,136,0,0.6),0 0 50px rgba(255,68,0,0.3);}50%{box-shadow:0 0 40px rgba(255,200,0,0.9),0 0 80px rgba(255,100,0,0.5);}}
    @keyframes navGlow{0%,100%{opacity:0.7;}50%{opacity:1;}}

    .ms-title{text-align:center;padding:18px 8px 8px 8px;animation:stageIn 0.6s ease;}
    .ms-title h1{font-size:2.2rem;font-weight:900;color:#00d4ff;letter-spacing:3px;animation:titleGlow 3s ease infinite;margin:0;}
    .ms-title p{font-size:0.9rem;color:#666;letter-spacing:2px;margin:4px 0 0 0;}

    .stage{animation:stageIn 0.5s ease;border-radius:14px;padding:10px 12px;margin:4px 0;}
    .stage-act{background:linear-gradient(145deg,#050d15,#0a1520);border:2px solid rgba(0,212,255,0.5);box-shadow:0 0 20px rgba(0,212,255,0.1);}
    .stage-dim{background:#050505;border:2px solid #111;opacity:0.3;pointer-events:none;}

    .act-label{font-size:0.7rem;font-weight:900;letter-spacing:3px;color:#00d4ff;margin-bottom:4px;text-align:center;}
    .act-msg{font-size:0.85rem;font-weight:900;color:#fff;text-align:center;margin-bottom:4px;line-height:1.2;}
    .act-msg span.hi{color:#00d4ff;}
    .act-msg span.gold{color:#ffd700;}
    .act-msg span.go{color:#00ff88;}

    .confirmed{text-align:center;padding:8px;margin-bottom:10px;}
    .confirmed span{font-size:1rem;color:#ffd700;font-weight:900;background:rgba(255,215,0,0.1);padding:6px 16px;border-radius:20px;border:1px solid rgba(255,215,0,0.4);}

    button[kind="secondary"]{
        background:#060e18!important;border:2px solid rgba(0,212,255,0.35)!important;
        border-radius:10px!important;font-size:0.85rem!important;font-weight:900!important;
        padding:10px 4px!important;color:#e0e0e0!important;min-height:52px!important;
        animation:none!important;transform:none!important;box-shadow:none!important;
    }
    button[kind="secondary"] p{font-size:0.85rem!important;font-weight:900!important;white-space:pre-line!important;line-height:1.0!important;text-align:center!important;}

    button[data-testid="stBaseButton-primary"]{
        background:linear-gradient(135deg,#ff4400,#ff8800,#ffaa00)!important;
        border:2px solid #ffd700!important;font-size:1.05rem!important;font-weight:900!important;
        padding:0.6rem!important;color:#fff!important;border-radius:12px!important;
        animation:startPulse 1.5s ease infinite!important;
        text-shadow:0 2px 8px rgba(0,0,0,0.5)!important;
    }

    .nav-bar{display:flex;gap:8px;margin-top:16px;padding:12px 4px 4px 4px;border-top:1px solid #111;}
    .nav-bar-label{font-size:0.7rem;color:#333;text-align:center;letter-spacing:3px;margin-bottom:6px;}[data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;}[data-testid="stHorizontalBlock"] [data-testid="stColumn"]{min-width:0!important;flex:1!important;}
    </style>""", unsafe_allow_html=True)

    # 타이틀
    if rn > 1:
        round_txt = f'<p style="color:#cc6600;font-size:0.9rem;font-weight:800;margin:2px 0;">🏆 Round {rn}</p>'
    else:
        round_txt = ''
    st.markdown(f'<div class="ms-title"><h1>⚔️ P5전장</h1><p>TOEIC Part 5 · 문법/어휘 5문제 서바이벌</p>{round_txt}</div>', unsafe_allow_html=True)

    _tsec = st.session_state.get('tsec', 30)
    _tsec_chosen = st.session_state.get('tsec_chosen', False)
    lbl_map={"g1":"⚔️ 문법력","g2":"⚔️ 구조력","g3":"⚔️ 연결력","vocab":"📘 어휘력"}
    mode_map={"g1":("grammar","g1"),"g2":("grammar","g2"),"g3":("grammar","g3"),"vocab":("vocab",None)}

    # ━━━ 1화면 통합 로비 ━━━
    st.markdown('''<style>
    button[kind="secondary"]{
        background:#0a0a14!important;border:1.5px solid #333!important;
        border-radius:10px!important;font-size:1.0rem!important;font-weight:600!important;
        padding:6px!important;color:#aaa!important;min-height:61px!important;
        animation:none!important;transform:none!important;box-shadow:none!important;
    }
    button[kind="secondary"] p{font-size:1.0rem!important;font-weight:600!important;color:#aaa!important;white-space:pre-line!important;line-height:1.2!important;}
    button[data-testid="stBaseButton-primary"]{
        background:#0c0c00!important;border:2px solid #d4af37!important;
        border-left:4px solid #d4af37!important;
        color:#d4af37!important;font-size:1.0rem!important;font-weight:900!important;
        min-height:43px!important;animation:none!important;border-radius:12px!important;
    }
    button[data-testid="stBaseButton-primary"] p{color:#d4af37!important;font-size:1.0rem!important;font-weight:900!important;}
    </style>''', unsafe_allow_html=True)

    st.markdown('''<div style="display:flex;align-items:flex-end;margin-bottom:0;">
        <div style="background:#0c0c1e;border:1.5px solid #9aa5b4;border-bottom:none;border-radius:8px 8px 0 0;padding:3px 12px;font-size:0.72rem;font-weight:900;color:#9aa5b4;">⏱ 시간 선택</div>
    </div>''', unsafe_allow_html=True)
    tc1,tc2,tc3 = st.columns(3)
    with tc1:
        if st.button("🔥 30초", key="t30", use_container_width=True):
            st.session_state.tsec=30; st.session_state.tsec_chosen=True; st.rerun()
    with tc2:
        if st.button("⚡ 40초", key="t40", use_container_width=True):
            st.session_state.tsec=40; st.session_state.tsec_chosen=True; st.rerun()
    with tc3:
        if st.button("✅ 50초", key="t50", use_container_width=True):
            st.session_state.tsec=50; st.session_state.tsec_chosen=True; st.rerun()
    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

    st.markdown('''<div style="display:flex;align-items:flex-end;margin-bottom:0;">
        <div style="background:#140800;border:1.5px solid #cc2244;border-bottom:none;border-radius:8px 8px 0 0;padding:3px 12px;font-size:0.72rem;font-weight:900;color:#ff8800;">⚔️ 전장 선택</div>
    </div>''', unsafe_allow_html=True)
    b1,b2 = st.columns(2)
    with b1:
        if st.button("⚔️ 문법력\n수일치·시제·수동", key="sg1", use_container_width=True):
            st.session_state.sel_mode="g1"; st.rerun()
    with b2:
        if st.button("⚔️ 구조력\n가정법·도치·당위", key="sg2", use_container_width=True):
            st.session_state.sel_mode="g2"; st.rerun()
    b3,b4 = st.columns(2)
    with b3:
        if st.button("⚔️ 연결력\n접속사·관계사·분사", key="sg3", use_container_width=True):
            st.session_state.sel_mode="g3"; st.rerun()
    with b4:
        if st.button("📘 어휘력\n품사·동사·콜로케이션", key="svc", use_container_width=True):
            st.session_state.sel_mode="vocab"; st.rerun()
    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)

    st.markdown('''<div style="background:#0a0500;border:1px solid #441100;border-radius:8px;padding:5px 10px;text-align:center;margin-bottom:6px;">
        <span style="font-size:0.85rem;color:#ff4466;font-weight:900;animation:warningPulse 1.5s ease-in-out infinite;display:inline-block;">💀 생존 규칙: 5문제 중 3개 이상 · 그 이하면 전멸!</span>
    </div>''', unsafe_allow_html=True)

    _ready = _tsec_chosen and sm and sm in ["g1","g2","g3","vocab"]
    if _ready:
        _cat = lbl_map.get(sm,"")
        if st.button("▶ 전투 시작!", key="go_start", type="primary", use_container_width=True):
            md,grp=mode_map[sm]
            st.session_state.mode=md; qs=pick5(md,grp)
            st.session_state.round_qs=qs; st.session_state.cq=qs[0]
            st.session_state.qst=time.time(); st.session_state.phase="battle"; st.rerun()
    else:
        st.markdown('<div style="background:#0a0a14;border:1px solid #222;border-radius:12px;padding:10px;text-align:center;color:#333;font-size:0.9rem;">시간 + 전장을 선택하면 시작!</div>', unsafe_allow_html=True)

    # ━━━ 하단 네비게이션 ━━━
    st.markdown('<div style="height:1px;background:#1a1a2a;margin:2px 0;"></div>', unsafe_allow_html=True)
    st.markdown('<style>div[data-testid="stHorizontalBlock"]:last-of-type button{padding:0.18rem 0.6rem!important;min-height:32px!important;font-size:0.82rem!important;}div[data-testid="stHorizontalBlock"]:last-of-type button p{font-size:0.82rem!important;}</style>', unsafe_allow_html=True)
    nc1,nc2 = st.columns(2)
    with nc1:
        if st.button("🔥 오답전장", key="p5nav1", use_container_width=True):
            st.switch_page("pages/03_오답전장.py")
    with nc2:
        if st.button("🏠 홈", key="p5nav2", use_container_width=True):
            st.session_state._p5_just_left = True
            st.switch_page("main_hub.py")

    import streamlit.components.v1 as _cmp5
    _tsec_v = st.session_state.get("tsec", 30)
    _tc_v = st.session_state.get("tsec_chosen", False)
    _sm_v = st.session_state.get("sel_mode", None) or ""
    _cmp5.html(f'''<script>
    (function(){{
        var selTime = "{_tsec_v if _tc_v else ""}";
        var selMode = "{_sm_v}";
        var timeMap = {{"30":"30초","40":"40초","50":"50초"}};
        var modeMap = {{"g1":"문법력","g2":"구조력","g3":"연결력","vocab":"어휘력"}};
        function styleBtns(){{
            var doc=window.parent.document;
            var btns=doc.querySelectorAll('button[kind="secondary"]');
            btns.forEach(function(b){{
                var t=(b.textContent||"").replace(/\\s+/g," ").trim();
                var isTime=selTime&&t.indexOf(timeMap[selTime])>-1;
                var isMode=selMode&&modeMap[selMode]&&t.indexOf(modeMap[selMode])>-1;
                if(isTime||isMode){{
                    b.style.setProperty("background","#1a1400","important");
                    b.style.setProperty("border","2px solid #d4af37","important");
                    b.querySelectorAll("p").forEach(function(p){{p.style.setProperty("color","#d4af37","important");}});
                }}
            }});
            var rows=doc.querySelectorAll('[data-testid="stHorizontalBlock"]');
            if(!rows.length) return;
            var last=rows[rows.length-1];
            last.querySelectorAll('button').forEach(function(b){{
                b.style.setProperty("animation","none","important");
                b.style.setProperty("border","1.5px solid rgba(255,255,255,0.5)","important");
                b.style.setProperty("background","#0f0f1e","important");
                b.style.setProperty("color","#bbb","important");
            }});
        }}
        setTimeout(styleBtns,100);setTimeout(styleBtns,400);setTimeout(styleBtns,900);
        setInterval(styleBtns,800);
    }})();
    </script>''', height=0)






