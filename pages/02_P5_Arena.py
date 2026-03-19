"""P5 Arena v13b — 로비 구역별 색감 적용 (틸/핑크오렌지에메랄드인디고/포레스트)"""
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import random, time, json, os

st.set_page_config(page_title="P5 Arena ⚔️", page_icon="⚔️", layout="wide", initial_sidebar_state="collapsed")

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
.stApp{background:linear-gradient(rgba(0,212,255,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(0,212,255,0.03) 1px,transparent 1px),#0a0a0a!important;background-size:40px 40px,40px 40px,100% 100%!important;color:#f0f0f0!important;}
section[data-testid="stSidebar"]{display:none!important;}
header[data-testid="stHeader"]{background:transparent!important;}
.block-container{padding-top:0.7rem!important;padding-bottom:1rem!important;}
.ah{text-align:center;padding:0.6rem 0 0.2rem 0;}
.ah h1{font-family:'Orbitron',monospace!important;font-size:2rem;font-weight:900;margin:0;background:linear-gradient(90deg,#00d4ff,#ffffff,#00d4ff);background-size:200%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:titleShine 3s linear infinite;letter-spacing:4px;}
@keyframes titleShine{0%{background-position:200% center}100%{background-position:-200% center}}
button[kind="primary"],button[kind="secondary"]{background:#0d0d0d!important;color:#fff!important;border:1.5px solid rgba(0,212,255,0.5)!important;border-radius:8px!important;font-family:'Rajdhani',sans-serif!important;font-size:2.1rem!important;font-weight:700!important;padding:1.2rem 1.4rem!important;box-shadow:0 0 12px rgba(0,212,255,0.15)!important;text-align:center!important;transition:all 0.15s!important;}
button[kind="primary"] p,button[kind="primary"] span,button[kind="secondary"] p,button[kind="secondary"] span{font-family:'Rajdhani',sans-serif!important;font-size:2.1rem!important;font-weight:700!important;text-align:center!important;}
button[kind="primary"]:hover,button[kind="secondary"]:hover{background:rgba(0,212,255,0.08)!important;border-color:#00d4ff!important;box-shadow:0 0 25px rgba(0,212,255,0.4)!important;transform:translateY(-2px)!important;}
.qb{border-radius:18px;padding:1.8rem 1.5rem;margin:0.2rem 0 0.6rem 0;background:#0d0d0d;}
.qb-g,.qb-v{background:#0d0d0d!important;border:none!important;animation:borderGlow 3s linear infinite;}
@keyframes borderGlow{0%{box-shadow:0 0 0 2px #00d4ff,0 0 15px rgba(0,212,255,0.4);}50%{box-shadow:0 0 0 2px #fff,0 0 25px rgba(0,212,255,0.6);}100%{box-shadow:0 0 0 2px #00d4ff,0 0 15px rgba(0,212,255,0.4);}}
.qc{font-family:'Orbitron',monospace;font-size:1.05rem;font-weight:800;margin-bottom:0.8rem;letter-spacing:3px;}
.qc-g,.qc-v{color:#00d4ff;text-shadow:0 0 8px rgba(0,212,255,0.6);}
.qt{font-family:'Rajdhani',sans-serif;color:#fff;font-size:2.4rem;font-weight:700;line-height:2;word-break:keep-all;}
.qk{color:#00d4ff;font-weight:900;font-size:2.6rem;border-bottom:3px solid #00d4ff;text-shadow:0 0 15px rgba(0,212,255,0.8);}
.bt{display:flex;align-items:center;justify-content:space-between;padding:0.7rem 1rem;border-radius:14px;margin-bottom:0.2rem;}
.bt-g,.bt-v{background:#0d0d0d;border:1px solid rgba(0,212,255,0.4);box-shadow:0 0 15px rgba(0,212,255,0.1);}
.bq{font-family:'Orbitron',monospace;font-size:1.6rem;font-weight:900;}
.bq-g,.bq-v{color:#00d4ff;text-shadow:0 0 10px rgba(0,212,255,0.8);}
.bs{font-family:'Orbitron',monospace;font-size:1.1rem;font-weight:800;color:#fff;}
.rd-dots{display:flex;justify-content:center;gap:0.6rem;margin:0.3rem 0;}
.rd-dot{width:22px;height:22px;border-radius:50%;border:2px solid #333;display:flex;align-items:center;justify-content:center;font-size:0.7rem;font-weight:900;}
.rd-cur{border-color:#00d4ff!important;color:#00d4ff!important;box-shadow:0 0 10px #00d4ff!important;}
.rd-ok{background:#00d4ff;border-color:#00d4ff;color:#000;}
.rd-no{background:#ff2244;border-color:#ff2244;color:#fff;}
.rd-wait{background:transparent;border-color:#333;color:#444;}
.cg,.cv{border-radius:18px;padding:1.5rem 1.2rem;margin-bottom:0.8rem;min-height:190px;display:flex;flex-direction:column;justify-content:center;animation:fl 3s ease-in-out infinite;}
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

# 외부에서 진입 시 게임 종료 상태면 lobby로 리셋
if st.session_state.phase in ("lost", "victory", "briefing") and not st.session_state.get("_p5_active", False):
    st.session_state.phase = "lobby"
    for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results"]:
        if k in D: st.session_state[k] = D[k]
st.session_state._p5_active = True

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
    ej="🔴" if ig else "🔵"; tn="어법" if ig else "어휘"

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
        *{{margin:0;padding:0;}}body{{background:transparent;overflow:hidden;font-family:sans-serif;}}
        #w{{text-align:center;}}
        #n{{font-size:5rem;font-weight:900;animation:p 1s ease-in-out infinite;}}
        #bw{{background:#1a1a2e;border-radius:10px;height:14px;margin:0.2rem 0.5rem;overflow:hidden;border:1px solid #333;}}
        #b{{height:100%;border-radius:10px;transition:width 1s linear;}}
        .safe{{color:#44ff88;text-shadow:0 0 20px #44ff88;}}
        .warn{{color:#ffcc00;text-shadow:0 0 25px #ffcc00;}}
        .danger{{color:#ff4444;text-shadow:0 0 35px #ff4444;}}
        .critical{{color:#ff0000;text-shadow:0 0 50px #ff0000;font-size:6rem!important;}}
        .bs{{background:linear-gradient(90deg,#22cc66,#44ff88);box-shadow:0 0 10px #44ff88;}}
        .bw{{background:linear-gradient(90deg,#cc8800,#ffcc00);box-shadow:0 0 10px #ffcc00;}}
        .bd{{background:linear-gradient(90deg,#cc2200,#ff4444);box-shadow:0 0 15px #ff4444;animation:bp 0.5s infinite;}}
        .bc{{background:linear-gradient(90deg,#ff0000,#ff4444);box-shadow:0 0 25px #ff0000;animation:bp 0.25s infinite;}}
        @keyframes p{{0%,100%{{transform:scale(1);opacity:1}}50%{{transform:scale(1.07);opacity:0.8}}}}
        @keyframes bp{{0%,100%{{opacity:1}}50%{{opacity:0.4}}}}
        </style>
        <div id="w"><div id="n" class="{tcl}">{rem}</div>
        <div id="bw"><div id="b" class="b{'s' if tcl=='safe' else 'w' if tcl=='warn' else 'd' if tcl=='danger' else 'c'}" style="width:{pct}%"></div></div></div>
        <script>
        var l={rem},t={total};var e=document.getElementById("n"),b=document.getElementById("b");
        setInterval(function(){{l--;if(l<0)l=0;e.textContent=l;var r=l/t;
        var c=r>0.6?"safe":r>0.35?"warn":r>0.15?"danger":"critical";e.className=c;
        b.className="b"+(r>0.6?"s":r>0.35?"w":r>0.15?"d":"c");b.style.width=(r*100)+"%";}},1000);
        </script>""", height=120)

        # 시간초과 → YOU LOST
        if rem<=0:
            st.session_state.phase="lost"; st.rerun()

    # 문제
    st.markdown(f'<div class="qb qb-{th}"><div class="qc qc-{th}">{ej} {tn} · {q.get("cat","")}</div><div class="qt">{fq(q["text"])}</div></div>', unsafe_allow_html=True)

    # 선택지
    if not st.session_state.ans:
        cc=st.columns(2)
        for i,ch in enumerate(q["ch"]):
            with cc[i%2]:
                if st.button(ch,key=f"c{i}",type=bt,use_container_width=True):
                    # 시간초과 재확인
                    if time.time()-st.session_state.qst>st.session_state.tsec:
                        st.session_state.phase="lost"; st.rerun()
                    st.session_state.ans=True; st.session_state.sel=i
                    ok=i==q["a"]
                    st.session_state.round_results.append(ok)
                    if ok: st.session_state.sc+=1
                    else: st.session_state.wrong+=1
                    st.session_state.ta+=1
                    try:
                        import sys as _sys, os as _os; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(__file__)))
                        from data_collector import DataCollector as _DC
                        _DC(st.session_state.get('nickname','guest')).log_activity('P5', q.get('id','?'), i, ok, round(time.time()-st.session_state.qst,2))
                    except: pass

                    # 2문제 틀림 → 즉시 LOST
                    if st.session_state.wrong>=2:
                        st.session_state.phase="lost"; st.rerun()

                    # 5문제 완료 체크 (마지막 문제였으면 결과로)
                    if st.session_state.qi>=4:  # 0-indexed, 마지막 문제
                        if st.session_state.sc>=4:
                            st.session_state.phase="victory"
                        else:
                            st.session_state.phase="lost"
                        st.rerun()

                    # 다음 문제로 (qi가 4 미만일 때만 도달)
                    nqi = st.session_state.qi + 1
                    if nqi < len(st.session_state.round_qs):
                        st.session_state.qi = nqi
                        st.session_state.cq=st.session_state.round_qs[nqi]
                        st.session_state.ans=False; st.session_state.sel=None
                    else:
                        # 안전장치: 범위 초과 시 결과로
                        if st.session_state.sc>=4:
                            st.session_state.phase="victory"
                        else:
                            st.session_state.phase="lost"
                    st.rerun()
# ════════════════════════════════════════
elif st.session_state.phase=="victory":
    components.html("""
    <style>
    *{margin:0;padding:0;}body{background:#000;overflow:hidden;display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;}
    .v{text-align:center;animation:vi 0.8s ease-out;}
    .v h1{font-size:5rem;font-weight:900;color:#ffcc00;text-shadow:0 0 40px #ffcc00,0 0 80px #ff8800,0 0 120px #ff4400;animation:glow 1.5s ease-in-out infinite alternate;}
    .v p{font-size:1.5rem;color:#44ff88;font-weight:700;margin-top:0.5rem;}
    .stars{position:absolute;width:100%;height:100%;}
    .star{position:absolute;background:#ffcc00;border-radius:50%;animation:twinkle 1s ease-in-out infinite;}
    @keyframes vi{0%{transform:scale(0);opacity:0}100%{transform:scale(1);opacity:1}}
    @keyframes glow{0%{text-shadow:0 0 40px #ffcc00,0 0 80px #ff8800}100%{text-shadow:0 0 60px #ffcc00,0 0 120px #ff8800,0 0 180px #ff4400}}
    @keyframes twinkle{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.3;transform:scale(0.5)}}
    </style>
    <div class="stars">
    """ + "".join([f'<div class="star" style="left:{random.randint(5,95)}%;top:{random.randint(5,95)}%;width:{random.randint(3,8)}px;height:{random.randint(3,8)}px;animation-delay:{random.random():.1f}s;"></div>' for _ in range(30)]) + """
    </div>
    <div class="v"><h1>⚔️ VICTORY ⚔️</h1><p>라운드 클리어!</p></div>
    """, height=350)

    st.markdown("")
    vc=st.columns(2)
    with vc[0]:
        if st.button("📋 브리핑 보기", type="primary", use_container_width=True):
            st.session_state.phase="briefing"; st.rerun()
    with vc[1]:
        if st.button("🏠 메인", type="secondary", use_container_width=True):
            st.session_state._p5_active = False
            st.session_state.ans = False
            st.session_state["_battle_entry_ans_reset"] = True
            st.switch_page("main_hub.py")

# ════════════════════════════════════════
# PHASE: YOU LOST
# ════════════════════════════════════════
elif st.session_state.phase=="lost":
    reason = "⏰ 시간 초과!" if (time.time()-st.session_state.qst>st.session_state.tsec) else f"💀 오답 {st.session_state.wrong}개!"
    components.html(f"""
    <style>
    *{{margin:0;padding:0;}}body{{background:#000;overflow:hidden;display:flex;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;}}
    .l{{text-align:center;animation:li 0.6s ease-out;}}
    .l h1{{font-size:5rem;font-weight:900;color:#ff0000;text-shadow:0 0 40px #ff0000,0 0 80px #cc0000,0 0 120px #880000;animation:shake 0.5s ease-in-out infinite;}}
    .l p{{font-size:1.5rem;color:#ff6666;font-weight:700;margin-top:0.5rem;}}
    @keyframes li{{0%{{transform:scale(3);opacity:0}}100%{{transform:scale(1);opacity:1}}}}
    @keyframes shake{{0%,100%{{transform:translateX(0)}}25%{{transform:translateX(-5px)}}75%{{transform:translateX(5px)}}}}
    .embers{{position:absolute;width:100%;height:100%;}}
    .ember{{position:absolute;background:#ff4400;border-radius:50%;animation:rise 2s ease-in infinite;}}
    @keyframes rise{{0%{{opacity:1;transform:translateY(0)}}100%{{opacity:0;transform:translateY(-200px)}}}}
    </style>
    <div class="embers">
    """ + "".join([f'<div class="ember" style="left:{random.randint(5,95)}%;bottom:{random.randint(0,30)}%;width:{random.randint(3,6)}px;height:{random.randint(3,6)}px;animation-delay:{random.random():.1f}s;"></div>' for _ in range(25)]) + f"""
    </div>
    <div class="l"><h1>💀 YOU LOST 💀</h1><p>{reason}</p></div>
    """, height=350)

    st.markdown("")
    bc=st.columns(3)
    with bc[0]:
        if st.button("📋 브리핑 보기", type="primary", use_container_width=True):
            st.session_state.phase="briefing"; st.rerun()
    with bc[1]:
        if st.button("🔄 재도전", type="secondary", use_container_width=True):
            st.session_state.phase="lobby"
            for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results"]:
                st.session_state[k]=D[k]
            st.rerun()
    with bc[2]:
        if st.button("🏠 메인", type="secondary", use_container_width=True):
            st.session_state._p5_active = False
            st.session_state.ans = False
            st.session_state["_battle_entry_ans_reset"] = True
            st.switch_page("main_hub.py")

# ════════════════════════════════════════
# PHASE: BRIEFING
# ════════════════════════════════════════
elif st.session_state.phase=="briefing":
    # 브리핑 하단 버튼 10% 작게 + 화살표 작게
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');
.stApp{background:linear-gradient(rgba(0,212,255,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(0,212,255,0.03) 1px,transparent 1px),#0a0a0a!important;background-size:40px 40px,40px 40px,100% 100%!important;color:#f0f0f0!important;}
section[data-testid="stSidebar"]{display:none!important;}
header[data-testid="stHeader"]{background:transparent!important;}
.block-container{padding-top:0.7rem!important;padding-bottom:1rem!important;}
.ah{text-align:center;padding:0.6rem 0 0.2rem 0;}
.ah h1{font-family:'Orbitron',monospace!important;font-size:2rem;font-weight:900;margin:0;background:linear-gradient(90deg,#00d4ff,#ffffff,#00d4ff);background-size:200%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:titleShine 3s linear infinite;letter-spacing:4px;}
@keyframes titleShine{0%{background-position:200% center}100%{background-position:-200% center}}
button[kind="primary"],button[kind="secondary"]{background:#0d0d0d!important;color:#fff!important;border:1.5px solid rgba(0,212,255,0.5)!important;border-radius:8px!important;font-family:'Rajdhani',sans-serif!important;font-size:2.1rem!important;font-weight:700!important;padding:1.2rem 1.4rem!important;box-shadow:0 0 12px rgba(0,212,255,0.15)!important;text-align:center!important;transition:all 0.15s!important;}
button[kind="primary"] p,button[kind="primary"] span,button[kind="secondary"] p,button[kind="secondary"] span{font-family:'Rajdhani',sans-serif!important;font-size:2.1rem!important;font-weight:700!important;text-align:center!important;}
button[kind="primary"]:hover,button[kind="secondary"]:hover{background:rgba(0,212,255,0.08)!important;border-color:#00d4ff!important;box-shadow:0 0 25px rgba(0,212,255,0.4)!important;transform:translateY(-2px)!important;}
.qb{border-radius:18px;padding:1.8rem 1.5rem;margin:0.2rem 0 0.6rem 0;background:#0d0d0d;}
.qb-g,.qb-v{background:#0d0d0d!important;border:none!important;animation:borderGlow 3s linear infinite;}
@keyframes borderGlow{0%{box-shadow:0 0 0 2px #00d4ff,0 0 15px rgba(0,212,255,0.4);}50%{box-shadow:0 0 0 2px #fff,0 0 25px rgba(0,212,255,0.6);}100%{box-shadow:0 0 0 2px #00d4ff,0 0 15px rgba(0,212,255,0.4);}}
.qc{font-family:'Orbitron',monospace;font-size:1.05rem;font-weight:800;margin-bottom:0.8rem;letter-spacing:3px;}
.qc-g,.qc-v{color:#00d4ff;text-shadow:0 0 8px rgba(0,212,255,0.6);}
.qt{font-family:'Rajdhani',sans-serif;color:#fff;font-size:2.4rem;font-weight:700;line-height:2;word-break:keep-all;}
.qk{color:#00d4ff;font-weight:900;font-size:2.6rem;border-bottom:3px solid #00d4ff;text-shadow:0 0 15px rgba(0,212,255,0.8);}
.bt{display:flex;align-items:center;justify-content:space-between;padding:0.7rem 1rem;border-radius:14px;margin-bottom:0.2rem;}
.bt-g,.bt-v{background:#0d0d0d;border:1px solid rgba(0,212,255,0.4);box-shadow:0 0 15px rgba(0,212,255,0.1);}
.bq{font-family:'Orbitron',monospace;font-size:1.6rem;font-weight:900;}
.bq-g,.bq-v{color:#00d4ff;text-shadow:0 0 10px rgba(0,212,255,0.8);}
.bs{font-family:'Orbitron',monospace;font-size:1.1rem;font-weight:800;color:#fff;}
.rd-dots{display:flex;justify-content:center;gap:0.6rem;margin:0.3rem 0;}
.rd-dot{width:22px;height:22px;border-radius:50%;border:2px solid #333;display:flex;align-items:center;justify-content:center;font-size:0.7rem;font-weight:900;}
.rd-cur{border-color:#00d4ff!important;color:#00d4ff!important;box-shadow:0 0 10px #00d4ff!important;}
.rd-ok{background:#00d4ff;border-color:#00d4ff;color:#000;}
.rd-no{background:#ff2244;border-color:#ff2244;color:#fff;}
.rd-wait{background:transparent;border-color:#333;color:#444;}
.cg,.cv{border-radius:18px;padding:1.5rem 1.2rem;margin-bottom:0.8rem;min-height:190px;display:flex;flex-direction:column;justify-content:center;animation:fl 3s ease-in-out infinite;}
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
    was_victory = st.session_state.sc>=4
    if "br_idx" not in st.session_state: st.session_state.br_idx=0
    bi = st.session_state.br_idx
    rqs = st.session_state.round_qs
    rrs = st.session_state.round_results
    num_qs = min(len(rqs), len(rrs))
    if bi >= num_qs: bi = num_qs - 1
    if bi < 0: bi = 0

    def full_sent(qq, is_ok):
        ans = qq["ch"][qq["a"]]
        clean = ans.split(") ",1)[-1] if ") " in ans else ans
        cls = "wb-h" if is_ok else "wb-hn"
        return qq["text"].replace("_______", '<span class="'+cls+'">'+clean+'</span>')

    rn = st.session_state.round_num
    sc_v = st.session_state.sc
    wr_v = st.session_state.wrong
    v_cls = "br-ban-v" if was_victory else "br-ban-l"
    v_label = "VICTORY!" if was_victory else "YOU LOST"
    ban_emoji = "\U0001f3c6"
    st.markdown(f'<div class="br-ban {v_cls}">{ban_emoji} \ub77c\uc6b4\ub4dc {rn} \u2014 {v_label} \u2705{sc_v} \u274c{wr_v}</div>', unsafe_allow_html=True)

    nc1, nc2, nc3 = st.columns([0.7, 8, 0.7])
    with nc1:
        if st.button("\u25c0", key="br_p", disabled=bi<=0, use_container_width=True):
            st.session_state.br_idx = bi - 1; st.rerun()
    with nc2:
        dots = ""
        for i in range(num_qs):
            dcls = "br-dot-ok" if rrs[i] else "br-dot-no"
            if i == bi: dcls += " br-dot-cur"
            dots += '<div class="br-dot '+dcls+'"></div>'
        st.markdown('<div class="br-nav">'+dots+'</div>', unsafe_allow_html=True)
    with nc3:
        if st.button("\u25b6", key="br_n", disabled=bi>=num_qs-1, use_container_width=True):
            st.session_state.br_idx = bi + 1; st.rerun()

    q = rqs[bi]
    ok = rrs[bi]
    ncls = "wb-qn-ok" if ok else "wb-qn-no"
    sym = "\u2705" if ok else "\u274c"
    sent = full_sent(q, ok)
    kr = q.get("kr","")
    exk = q.get("exk","")

    wb = f'<div class="wb">'
    wb += f'<div class="wb-qn {ncls}">{sym} Q{bi+1} / {num_qs}</div>'
    wb += f'<div class="wb-s">{sent}</div>'
    wb += f'<div class="wb-d"></div>'
    wb += f'<div class="wb-k">\U0001f4d6 {kr}</div>'
    wb += f'<div class="wb-e">\U0001f4a1 {exk}</div>'
    wb += f'</div>'
    st.markdown(wb, unsafe_allow_html=True)

    sv_c1, sv_c2, sv_c3 = st.columns([1, 2, 1])
    with sv_c2:
        if st.button("\U0001f4be \uc774 \ubb38\uc81c \uc800\uc7a5", key=f"sv_{q['id']}_{bi}", type="primary", use_container_width=True):
            item = {"id":q["id"],"text":q["text"],"ch":q["ch"],"a":q["a"],"ex":q.get("ex",""),"exk":q.get("exk",""),"cat":q.get("cat",""),"kr":q.get("kr",""),"tp":q.get("tp","grammar")}
            save_to_storage([item])
            st.success("\u2705 \uc800\uc7a5 \uc644\ub8cc!")

    dot_cols = st.columns(num_qs)
    for i in range(num_qs):
        with dot_cols[i]:
            oi = rrs[i]
            si = "\u2705" if oi else "\u274c"
            bt = "primary" if i == bi else "secondary"
            if st.button(f"{si}{i+1}", key=f"brd_{i}", type=bt, use_container_width=True):
                st.session_state.br_idx = i; st.rerun()

    st.markdown("---")
    if was_victory:
        bc = st.columns(3)
        with bc[0]:
            nrd = st.session_state.round_num + 1
            if st.button(f"\u2694\ufe0f \ub77c\uc6b4\ub4dc {nrd}!", type="primary", use_container_width=True):
                st.session_state.round_num += 1
                for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx"]:
                    if k in st.session_state: del st.session_state[k]
                for k,v in D.items():
                    if k not in st.session_state: st.session_state[k]=v
                qs = pick5(st.session_state.mode)
                st.session_state.round_qs = qs; st.session_state.cq = qs[0]
                st.session_state.qst = time.time(); st.session_state.phase = "battle"; st.rerun()
        with bc[1]:
            if st.button("\U0001f3e0 \ub85c\ube44", type="secondary", use_container_width=True):
                for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx"]:
                    if k in st.session_state: del st.session_state[k]
                for k,v in D.items():
                    if k not in st.session_state: st.session_state[k]=v
                st.session_state.phase = "lobby"; st.rerun()
        with bc[2]:
            if st.button("\U0001f30d \uba54\uc778\ud5c8\ube0c", type="secondary", use_container_width=True):
                st.session_state._p5_active = False
                st.session_state.ans = False
                st.session_state["_battle_entry_ans_reset"] = True
                st.switch_page("main_hub.py")
    else:
        bc = st.columns(3)
        with bc[0]:
            if st.button("\U0001f504 \uc7ac\ub3c4\uc804", type="primary", use_container_width=True):
                for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx"]:
                    if k in st.session_state: del st.session_state[k]
                for k,v in D.items():
                    if k not in st.session_state: st.session_state[k]=v
                qs = pick5(st.session_state.mode)
                st.session_state.round_qs = qs; st.session_state.cq = qs[0]
                st.session_state.qst = time.time(); st.session_state.phase = "battle"; st.rerun()
        with bc[1]:
            if st.button("\U0001f3e0 \ub85c\ube44", type="secondary", use_container_width=True):
                for k in ["cq","qi","sc","wrong","ta","ans","sel","round_qs","round_results","br_idx"]:
                    if k in st.session_state: del st.session_state[k]
                for k,v in D.items():
                    if k not in st.session_state: st.session_state[k]=v
                st.session_state.phase = "lobby"; st.rerun()
        with bc[2]:
            if st.button("\U0001f30d \uba54\uc778\ud5c8\ube0c", type="secondary", use_container_width=True):
                st.session_state._p5_active = False
                st.session_state.ans = False
                st.session_state["_battle_entry_ans_reset"] = True
                st.switch_page("main_hub.py")

# PHASE: LOBBY
# ════════════════════════════════════════
else:
    st.session_state.phase="lobby"
    if "sel_mode" not in st.session_state: st.session_state.sel_mode=None

    tsec = st.session_state.tsec
    sm = st.session_state.sel_mode
    rn = st.session_state.round_num

    # ─── 밝은 리모컨 CSS ───
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@600;700&display=swap');
.stApp{background:linear-gradient(rgba(0,212,255,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(0,212,255,0.03) 1px,transparent 1px),#0a0a0a!important;background-size:40px 40px,40px 40px,100% 100%!important;color:#f0f0f0!important;}
section[data-testid="stSidebar"]{display:none!important;}
header[data-testid="stHeader"]{background:transparent!important;}
.block-container{padding-top:0.7rem!important;padding-bottom:1rem!important;}
.ah{text-align:center;padding:0.6rem 0 0.2rem 0;}
.ah h1{font-family:'Orbitron',monospace!important;font-size:2rem;font-weight:900;margin:0;background:linear-gradient(90deg,#00d4ff,#ffffff,#00d4ff);background-size:200%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:titleShine 3s linear infinite;letter-spacing:4px;}
@keyframes titleShine{0%{background-position:200% center}100%{background-position:-200% center}}
button[kind="primary"],button[kind="secondary"]{background:#0d0d0d!important;color:#fff!important;border:1.5px solid rgba(0,212,255,0.5)!important;border-radius:8px!important;font-family:'Rajdhani',sans-serif!important;font-size:2.1rem!important;font-weight:700!important;padding:1.2rem 1.4rem!important;box-shadow:0 0 12px rgba(0,212,255,0.15)!important;text-align:center!important;transition:all 0.15s!important;}
button[kind="primary"] p,button[kind="primary"] span,button[kind="secondary"] p,button[kind="secondary"] span{font-family:'Rajdhani',sans-serif!important;font-size:2.1rem!important;font-weight:700!important;text-align:center!important;}
button[kind="primary"]:hover,button[kind="secondary"]:hover{background:rgba(0,212,255,0.08)!important;border-color:#00d4ff!important;box-shadow:0 0 25px rgba(0,212,255,0.4)!important;transform:translateY(-2px)!important;}
.qb{border-radius:18px;padding:1.8rem 1.5rem;margin:0.2rem 0 0.6rem 0;background:#0d0d0d;}
.qb-g,.qb-v{background:#0d0d0d!important;border:none!important;animation:borderGlow 3s linear infinite;}
@keyframes borderGlow{0%{box-shadow:0 0 0 2px #00d4ff,0 0 15px rgba(0,212,255,0.4);}50%{box-shadow:0 0 0 2px #fff,0 0 25px rgba(0,212,255,0.6);}100%{box-shadow:0 0 0 2px #00d4ff,0 0 15px rgba(0,212,255,0.4);}}
.qc{font-family:'Orbitron',monospace;font-size:1.05rem;font-weight:800;margin-bottom:0.8rem;letter-spacing:3px;}
.qc-g,.qc-v{color:#00d4ff;text-shadow:0 0 8px rgba(0,212,255,0.6);}
.qt{font-family:'Rajdhani',sans-serif;color:#fff;font-size:2.4rem;font-weight:700;line-height:2;word-break:keep-all;}
.qk{color:#00d4ff;font-weight:900;font-size:2.6rem;border-bottom:3px solid #00d4ff;text-shadow:0 0 15px rgba(0,212,255,0.8);}
.bt{display:flex;align-items:center;justify-content:space-between;padding:0.7rem 1rem;border-radius:14px;margin-bottom:0.2rem;}
.bt-g,.bt-v{background:#0d0d0d;border:1px solid rgba(0,212,255,0.4);box-shadow:0 0 15px rgba(0,212,255,0.1);}
.bq{font-family:'Orbitron',monospace;font-size:1.6rem;font-weight:900;}
.bq-g,.bq-v{color:#00d4ff;text-shadow:0 0 10px rgba(0,212,255,0.8);}
.bs{font-family:'Orbitron',monospace;font-size:1.1rem;font-weight:800;color:#fff;}
.rd-dots{display:flex;justify-content:center;gap:0.6rem;margin:0.3rem 0;}
.rd-dot{width:22px;height:22px;border-radius:50%;border:2px solid #333;display:flex;align-items:center;justify-content:center;font-size:0.7rem;font-weight:900;}
.rd-cur{border-color:#00d4ff!important;color:#00d4ff!important;box-shadow:0 0 10px #00d4ff!important;}
.rd-ok{background:#00d4ff;border-color:#00d4ff;color:#000;}
.rd-no{background:#ff2244;border-color:#ff2244;color:#fff;}
.rd-wait{background:transparent;border-color:#333;color:#444;}
.cg,.cv{border-radius:18px;padding:1.5rem 1.2rem;margin-bottom:0.8rem;min-height:190px;display:flex;flex-direction:column;justify-content:center;animation:fl 3s ease-in-out infinite;}
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

    # ═══ 리모컨 상단 ═══
    st.markdown('<div class="rmt"><div class="rmt-t">⚔️ P5 ARENA ⚔️</div><div class="rmt-s">TOEIC Part 5 · 5문제 서바이벌</div><div class="rmt-ir"></div></div>', unsafe_allow_html=True)
    if rn > 1:
        st.markdown(f'<div style="text-align:center;color:#cc6600;font-size:1rem;font-weight:800;margin:4px 0;">🏆 Round {rn}</div>', unsafe_allow_html=True)

    # ═══ TIMER ═══
    st.markdown('<div class="zn zn-t"><div class="zl zl-t">⏱ T I M E R</div></div>', unsafe_allow_html=True)
    tc1,tc2,tc3 = st.columns(3)
    with tc1:
        if st.button("🔥 30초", key="t30", type="secondary", use_container_width=True):
            st.session_state.tsec=30; st.rerun()
    with tc2:
        if st.button("⚡ 40초", key="t40", type="secondary", use_container_width=True):
            st.session_state.tsec=40; st.rerun()
    with tc3:
        if st.button("✅ 50초", key="t50", type="secondary", use_container_width=True):
            st.session_state.tsec=50; st.rerun()

    # ═══ BATTLE ═══
    st.markdown('<div class="zn zn-b"><div class="zl zl-b">🎮 P 5  B A T T L E</div></div>', unsafe_allow_html=True)
    b1,b2 = st.columns(2)
    with b1:
        if st.button("⚔ 문법력\n수일치·시제·수동", key="sg1", type="secondary", use_container_width=True):
            st.session_state.sel_mode="g1"; st.rerun()
    with b2:
        if st.button("⚔ 구조력\n가정법·도치·당위", key="sg2", type="secondary", use_container_width=True):
            st.session_state.sel_mode="g2"; st.rerun()
    b3,b4 = st.columns(2)
    with b3:
        if st.button("⚔ 연결력\n접속사·관계사·분사", key="sg3", type="secondary", use_container_width=True):
            st.session_state.sel_mode="g3"; st.rerun()
    with b4:
        if st.button("📘 어휘력\n품사·동사·콜로케이션", key="svc", type="secondary", use_container_width=True):
            st.session_state.sel_mode="vocab"; st.rerun()

    # ═══ START ═══
    if sm and sm in ["g1","g2","g3","vocab"]:
        mode_map={"g1":("grammar","g1"),"g2":("grammar","g2"),"g3":("grammar","g3"),"vocab":("vocab",None)}
        lbl_map={"g1":"⚔️ 문법력 전투!","g2":"⚔️ 구조력 전투!","g3":"⚔️ 연결력 전투!","vocab":"📘 어휘력 전투!"}
        if st.button(lbl_map.get(sm,"START"), key="go_start", type="primary", use_container_width=True):
            md,grp=mode_map[sm]
            st.session_state.mode=md; qs=pick5(md,grp)
            st.session_state.round_qs=qs; st.session_state.cq=qs[0]
            st.session_state.qst=time.time(); st.session_state.phase="battle"; st.rerun()
    else:
        st.markdown('<div class="dis-start">▶ START</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;color:#999;font-size:0.95rem;font-weight:700;margin:6px 0;">↑ 모드를 선택하세요!</div>', unsafe_allow_html=True)

    # ═══ NAVIGATE ═══
    st.markdown('<div class="zn zn-n"><div class="zl zl-n">🧭 N A V I G A T E</div></div>', unsafe_allow_html=True)
    nc1,nc2 = st.columns(2)
    with nc1:
        if st.button("📦 저장고", key="nav_stg", type="secondary", use_container_width=True):
            st.switch_page("pages/03_저장고.py")
    with nc2:
        if st.button("🏠 메인", key="nav_hub", type="secondary", use_container_width=True):
            st.session_state._p5_active = False
            st.session_state.ans = False
            st.session_state["_battle_entry_ans_reset"] = True
            st.switch_page("main_hub.py")

    # 하단 장식
    st.markdown('<div class="rmt-end"><div class="rmt-sp"><div class="rmt-sl"></div><div class="rmt-sl"></div><div class="rmt-sl"></div><div class="rmt-sl"></div><div class="rmt-sl"></div></div></div>', unsafe_allow_html=True)

    # ═══ JavaScript 버튼 색상 (밝고 화사한 버전) ═══
    import streamlit.components.v1 as components
    _sel30 = "border:4px solid #fff;box-shadow:0 0 20px rgba(255,255,255,0.6),0 6px 20px rgba(0,150,180,0.5);" if tsec==30 else ""
    _sel40 = "border:4px solid #fff;box-shadow:0 0 20px rgba(255,255,255,0.6),0 6px 20px rgba(0,120,200,0.5);" if tsec==40 else ""
    _sel50 = "border:4px solid #fff;box-shadow:0 0 20px rgba(255,255,255,0.6),0 6px 20px rgba(0,100,180,0.5);" if tsec==50 else ""
    _selg1 = "border:4px solid #fff;box-shadow:0 0 20px rgba(255,255,255,0.6),0 6px 20px rgba(255,17,102,0.5);" if sm=="g1" else ""
    _selg2 = "border:4px solid #fff;box-shadow:0 0 20px rgba(255,255,255,0.6),0 6px 20px rgba(255,136,17,0.5);" if sm=="g2" else ""
    _selg3 = "border:4px solid #fff;box-shadow:0 0 20px rgba(255,255,255,0.6),0 6px 20px rgba(0,204,119,0.5);" if sm=="g3" else ""
    _selvc = "border:4px solid #fff;box-shadow:0 0 20px rgba(255,255,255,0.6),0 6px 20px rgba(85,68,204,0.5);" if sm=="vocab" else ""




