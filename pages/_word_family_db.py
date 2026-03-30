"""
_word_family_db.py — TOEIC 핵심 단어 패밀리 공유 DB
위치: pages/_word_family_db.py
사용: 02_Firepower, 03_POW_HQ, 04_Decrypt_Op에서 import
"""
import re as _re

# ════════════════════════════════════════════════════
# 패밀리 DB: root → {pos: [(word, kr), ...]}
# V=동사 N=명사 ADJ=형용사 ADV=부사
# ════════════════════════════════════════════════════
FAMILY_DB = {
    # ─── EMPLOYMENT & HR ───
    "employ":      {"V":[("employ","고용하다")],"N":[("employee","직원"),("employer","고용주"),("employment","고용"),("unemployment","실업")],"ADJ":[("employed","고용된"),("unemployed","실직한"),("employable","고용 가능한")],"ADV":[]},
    "hire":        {"V":[("hire","고용하다")],"N":[("hire","고용"),("hiring","채용")],"ADJ":[],"ADV":[]},
    "recruit":     {"V":[("recruit","채용하다")],"N":[("recruitment","채용"),("recruiter","채용 담당자"),("recruit","신입")],"ADJ":[],"ADV":[]},
    "retire":      {"V":[("retire","은퇴하다")],"N":[("retirement","은퇴"),("retiree","은퇴자")],"ADJ":[("retired","은퇴한")],"ADV":[]},
    "train":       {"V":[("train","교육하다")],"N":[("training","교육"),("trainer","강사"),("trainee","교육생")],"ADJ":[],"ADV":[]},
    "supervise":   {"V":[("supervise","감독하다")],"N":[("supervisor","감독자"),("supervision","감독")],"ADJ":[("supervisory","감독의")],"ADV":[]},
    "promote":     {"V":[("promote","홍보하다/승진시키다")],"N":[("promotion","홍보/승진"),("promoter","홍보자")],"ADJ":[("promotional","홍보의")],"ADV":[]},
    "compensate":  {"V":[("compensate","보상하다")],"N":[("compensation","보상")],"ADJ":[],"ADV":[]},
    "certify":     {"V":[("certify","증명하다")],"N":[("certification","인증"),("certificate","증명서")],"ADJ":[("certified","인증된")],"ADV":[]},
    "qualify":     {"V":[("qualify","자격 갖추다")],"N":[("qualification","자격"),("qualifier","예선")],"ADJ":[("qualified","자격 있는"),("qualifying","예선의")],"ADV":[]},
    "terminate":   {"V":[("terminate","해고하다/종료하다")],"N":[("termination","해고/종료")],"ADJ":[],"ADV":[]},
    "relocate":    {"V":[("relocate","이전하다")],"N":[("relocation","이전")],"ADJ":[],"ADV":[]},
    "assign":      {"V":[("assign","배정하다")],"N":[("assignment","과제/배정")],"ADJ":[],"ADV":[]},
    "delegate":    {"V":[("delegate","위임하다")],"N":[("delegation","위임"),("delegate","대표")],"ADJ":[],"ADV":[]},
    "resign":      {"V":[("resign","사직하다")],"N":[("resignation","사직")],"ADJ":[],"ADV":[]},
    "apply":       {"V":[("apply","지원하다/적용하다")],"N":[("applicant","지원자"),("application","지원서")],"ADJ":[("applicable","적용 가능한")],"ADV":[]},

    # ─── FINANCE & BUSINESS ───
    "invest":      {"V":[("invest","투자하다")],"N":[("investment","투자"),("investor","투자자")],"ADJ":[],"ADV":[]},
    "finance":     {"V":[("finance","자금 조달하다")],"N":[("finance","재정"),("financing","금융")],"ADJ":[("financial","재정적인")],"ADV":[("financially","재정적으로")]},
    "budget":      {"V":[("budget","예산을 세우다")],"N":[("budget","예산")],"ADJ":[("budgetary","예산의")],"ADV":[]},
    "purchase":    {"V":[("purchase","구매하다")],"N":[("purchase","구매"),("purchaser","구매자")],"ADJ":[],"ADV":[]},
    "acquire":     {"V":[("acquire","취득하다")],"N":[("acquisition","취득")],"ADJ":[],"ADV":[]},
    "audit":       {"V":[("audit","감사하다")],"N":[("audit","감사"),("auditor","감사관")],"ADJ":[],"ADV":[]},
    "reimburse":   {"V":[("reimburse","상환하다")],"N":[("reimbursement","상환")],"ADJ":[],"ADV":[]},
    "estimate":    {"V":[("estimate","추정하다")],"N":[("estimate","견적/추정"),("estimation","추정")],"ADJ":[("estimated","추정된")],"ADV":[]},
    "calculate":   {"V":[("calculate","계산하다")],"N":[("calculation","계산"),("calculator","계산기")],"ADJ":[],"ADV":[]},
    "reduce":      {"V":[("reduce","줄이다")],"N":[("reduction","감소")],"ADJ":[],"ADV":[]},
    "increase":    {"V":[("increase","증가시키다")],"N":[("increase","증가")],"ADJ":[("increased","증가된")],"ADV":[("increasingly","점점 더")]},
    "allocate":    {"V":[("allocate","배분하다")],"N":[("allocation","배분")],"ADJ":[],"ADV":[]},
    "profit":      {"V":[("profit","이익을 얻다")],"N":[("profit","이익"),("profitability","수익성")],"ADJ":[("profitable","수익성 있는")],"ADV":[("profitably","수익성 있게")]},
    "compete":     {"V":[("compete","경쟁하다")],"N":[("competition","경쟁"),("competitor","경쟁자"),("competitiveness","경쟁력")],"ADJ":[("competitive","경쟁적인")],"ADV":[("competitively","경쟁적으로")]},
    "supply":      {"V":[("supply","공급하다")],"N":[("supply","공급"),("supplier","공급업체")],"ADJ":[],"ADV":[]},
    "charge":      {"V":[("charge","청구하다")],"N":[("charge","청구/요금")],"ADJ":[],"ADV":[]},
    "invoice":     {"V":[("invoice","청구서를 보내다")],"N":[("invoice","청구서")],"ADJ":[],"ADV":[]},
    "withdraw":    {"V":[("withdraw","철회하다/인출하다")],"N":[("withdrawal","철회/인출")],"ADJ":[],"ADV":[]},
    "deposit":     {"V":[("deposit","예금하다")],"N":[("deposit","예금/보증금")],"ADJ":[],"ADV":[]},

    # ─── COMMUNICATION & DOCUMENTS ───
    "announce":    {"V":[("announce","발표하다")],"N":[("announcement","발표"),("announcer","아나운서")],"ADJ":[],"ADV":[]},
    "notify":      {"V":[("notify","통지하다")],"N":[("notification","통지")],"ADJ":[],"ADV":[]},
    "inform":      {"V":[("inform","알리다")],"N":[("information","정보")],"ADJ":[("informative","유익한"),("informed","잘 아는")],"ADV":[]},
    "confirm":     {"V":[("confirm","확인하다")],"N":[("confirmation","확인")],"ADJ":[("confirmed","확인된")],"ADV":[]},
    "report":      {"V":[("report","보고하다")],"N":[("report","보고서"),("reporter","기자")],"ADJ":[],"ADV":[]},
    "submit":      {"V":[("submit","제출하다")],"N":[("submission","제출")],"ADJ":[("submitted","제출된")],"ADV":[]},
    "present":     {"V":[("present","발표하다")],"N":[("presentation","발표"),("presenter","발표자")],"ADJ":[("present","현재의")],"ADV":[("presently","현재")]},
    "correspond":  {"V":[("correspond","서신 왕래하다")],"N":[("correspondence","서신"),("correspondent","특파원")],"ADJ":[],"ADV":[]},
    "specify":     {"V":[("specify","명시하다")],"N":[("specification","사양")],"ADJ":[("specific","특정한")],"ADV":[("specifically","특히")]},
    "document":    {"V":[("document","문서화하다")],"N":[("document","문서"),("documentation","문서화")],"ADJ":[],"ADV":[]},
    "respond":     {"V":[("respond","응답하다")],"N":[("response","응답"),("responsibility","책임")],"ADJ":[("responsible","책임 있는"),("responsive","반응하는")],"ADV":[("responsibly","책임감 있게")]},
    "indicate":    {"V":[("indicate","나타내다")],"N":[("indication","표시"),("indicator","지표")],"ADJ":[("indicative","나타내는")],"ADV":[]},
    "clarify":     {"V":[("clarify","명확히 하다")],"N":[("clarification","명확화")],"ADJ":[("clear","명확한")],"ADV":[("clearly","명확히")]},
    "publish":     {"V":[("publish","출판하다")],"N":[("publication","출판"),("publisher","출판사")],"ADJ":[],"ADV":[]},
    "request":     {"V":[("request","요청하다")],"N":[("request","요청")],"ADJ":[],"ADV":[]},
    "communicate": {"V":[("communicate","소통하다")],"N":[("communication","소통"),("communicator","소통자")],"ADJ":[("communicative","소통적인")],"ADV":[]},
    "describe":    {"V":[("describe","묘사하다")],"N":[("description","묘사")],"ADJ":[("descriptive","묘사적인")],"ADV":[]},

    # ─── OPERATIONS & PROCESS ───
    "operate":     {"V":[("operate","운영하다")],"N":[("operation","운영"),("operator","운영자")],"ADJ":[("operational","운영의"),("operative","작동하는")],"ADV":[]},
    "implement":   {"V":[("implement","시행하다")],"N":[("implementation","시행")],"ADJ":[],"ADV":[]},
    "process":     {"V":[("process","처리하다")],"N":[("process","과정"),("processing","처리"),("processor","처리기")],"ADJ":[("processed","처리된")],"ADV":[]},
    "proceed":     {"V":[("proceed","진행하다")],"N":[("procedure","절차"),("proceedings","의사록")],"ADJ":[],"ADV":[]},
    "execute":     {"V":[("execute","실행하다")],"N":[("execution","실행"),("executive","임원")],"ADJ":[("executive","임원의")],"ADV":[]},
    "facilitate":  {"V":[("facilitate","촉진하다")],"N":[("facilitation","촉진"),("facility","시설")],"ADJ":[],"ADV":[]},
    "coordinate":  {"V":[("coordinate","조율하다")],"N":[("coordination","조율"),("coordinator","조율자")],"ADJ":[],"ADV":[]},
    "organize":    {"V":[("organize","조직하다")],"N":[("organization","조직"),("organizer","주최자")],"ADJ":[("organizational","조직의")],"ADV":[]},
    "maintain":    {"V":[("maintain","유지하다")],"N":[("maintenance","유지/관리")],"ADJ":[],"ADV":[]},
    "establish":   {"V":[("establish","설립하다")],"N":[("establishment","설립/기관")],"ADJ":[("established","확립된")],"ADV":[]},
    "develop":     {"V":[("develop","개발하다")],"N":[("development","개발"),("developer","개발자")],"ADJ":[("developed","선진의"),("developing","개발 중인")],"ADV":[]},
    "improve":     {"V":[("improve","개선하다")],"N":[("improvement","개선")],"ADJ":[("improved","개선된")],"ADV":[]},
    "enhance":     {"V":[("enhance","향상시키다")],"N":[("enhancement","향상")],"ADJ":[],"ADV":[]},
    "optimize":    {"V":[("optimize","최적화하다")],"N":[("optimization","최적화")],"ADJ":[("optimal","최적의"),("optimum","최적")],"ADV":[]},
    "standardize": {"V":[("standardize","표준화하다")],"N":[("standardization","표준화"),("standard","기준")],"ADJ":[("standard","표준의"),("standardized","표준화된")],"ADV":[]},
    "integrate":   {"V":[("integrate","통합하다")],"N":[("integration","통합")],"ADJ":[("integrated","통합된")],"ADV":[]},
    "consolidate": {"V":[("consolidate","통합하다")],"N":[("consolidation","통합")],"ADJ":[("consolidated","통합된")],"ADV":[]},
    "restructure": {"V":[("restructure","구조조정하다")],"N":[("restructuring","구조조정")],"ADJ":[],"ADV":[]},
    "upgrade":     {"V":[("upgrade","업그레이드하다")],"N":[("upgrade","업그레이드")],"ADJ":[],"ADV":[]},
    "modify":      {"V":[("modify","수정하다")],"N":[("modification","수정")],"ADJ":[("modified","수정된")],"ADV":[]},
    "manage":      {"V":[("manage","관리하다")],"N":[("manager","관리자"),("management","관리")],"ADJ":[("managerial","관리의")],"ADV":[]},

    # ─── LEGAL & COMPLIANCE ───
    "authorize":   {"V":[("authorize","승인하다")],"N":[("authorization","승인")],"ADJ":[("authorized","승인된")],"ADV":[]},
    "approve":     {"V":[("approve","승인하다"),("disapprove","반대하다")],"N":[("approval","승인"),("disapproval","불승인")],"ADJ":[("approved","승인된")],"ADV":[]},
    "comply":      {"V":[("comply","준수하다")],"N":[("compliance","준수")],"ADJ":[("compliant","순응하는")],"ADV":[]},
    "regulate":    {"V":[("regulate","규제하다")],"N":[("regulation","규정"),("regulator","규제기관")],"ADJ":[("regulatory","규제의")],"ADV":[]},
    "prohibit":    {"V":[("prohibit","금지하다")],"N":[("prohibition","금지")],"ADJ":[("prohibited","금지된")],"ADV":[]},
    "permit":      {"V":[("permit","허가하다")],"N":[("permit","허가증"),("permission","허가")],"ADJ":[("permissible","허용 가능한"),("permitted","허용된")],"ADV":[]},
    "restrict":    {"V":[("restrict","제한하다")],"N":[("restriction","제한")],"ADJ":[("restricted","제한된"),("restrictive","제한적인")],"ADV":[]},
    "enforce":     {"V":[("enforce","집행하다")],"N":[("enforcement","집행")],"ADJ":[("enforceable","집행 가능한")],"ADV":[]},
    "verify":      {"V":[("verify","확인하다")],"N":[("verification","확인")],"ADJ":[("verified","확인된")],"ADV":[]},
    "mandate":     {"V":[("mandate","의무화하다")],"N":[("mandate","위임/명령")],"ADJ":[("mandatory","의무적인")],"ADV":[]},
    "consent":     {"V":[("consent","동의하다")],"N":[("consent","동의")],"ADJ":[],"ADV":[]},
    "license":     {"V":[("license","허가하다")],"N":[("license","면허/허가증"),("licensing","허가")],"ADJ":[("licensed","허가된")],"ADV":[]},

    # ─── PROJECT & SCHEDULING ───
    "schedule":    {"V":[("schedule","일정 잡다")],"N":[("schedule","일정")],"ADJ":[("scheduled","예정된")],"ADV":[]},
    "complete":    {"V":[("complete","완료하다")],"N":[("completion","완료")],"ADJ":[("complete","완전한")],"ADV":[("completely","완전히")]},
    "extend":      {"V":[("extend","연장하다")],"N":[("extension","연장")],"ADJ":[("extensive","광범위한"),("extended","연장된")],"ADV":[("extensively","광범위하게")]},
    "revise":      {"V":[("revise","수정하다")],"N":[("revision","수정")],"ADJ":[("revised","수정된")],"ADV":[]},
    "deliver":     {"V":[("deliver","배송하다")],"N":[("delivery","배송"),("deliverable","산출물")],"ADJ":[],"ADV":[]},
    "install":     {"V":[("install","설치하다")],"N":[("installation","설치")],"ADJ":[],"ADV":[]},
    "replace":     {"V":[("replace","교체하다")],"N":[("replacement","교체")],"ADJ":[],"ADV":[]},
    "transfer":    {"V":[("transfer","이전하다")],"N":[("transfer","이전")],"ADJ":[("transferable","이전 가능한")],"ADV":[]},
    "access":      {"V":[("access","접근하다")],"N":[("access","접근")],"ADJ":[("accessible","접근 가능한"),("inaccessible","접근 불가한")],"ADV":[]},
    "advance":     {"V":[("advance","진전하다")],"N":[("advance","진전"),("advancement","발전")],"ADJ":[("advanced","고급의")],"ADV":[]},
    "finalize":    {"V":[("finalize","마무리하다")],"N":[("finalization","마무리")],"ADJ":[],"ADV":[]},
    "launch":      {"V":[("launch","출시하다")],"N":[("launch","출시")],"ADJ":[],"ADV":[]},
    "initiate":    {"V":[("initiate","시작하다")],"N":[("initiation","시작"),("initiative","주도권")],"ADJ":[],"ADV":[]},
    "postpone":    {"V":[("postpone","연기하다")],"N":[("postponement","연기")],"ADJ":[],"ADV":[]},
    "cancel":      {"V":[("cancel","취소하다")],"N":[("cancellation","취소")],"ADJ":[("cancelled","취소된")],"ADV":[]},
    "renew":       {"V":[("renew","갱신하다")],"N":[("renewal","갱신")],"ADJ":[("renewed","갱신된")],"ADV":[]},

    # ─── ANALYSIS & RESEARCH ───
    "analyze":     {"V":[("analyze","분석하다")],"N":[("analysis","분석"),("analyst","분석가")],"ADJ":[("analytical","분석적인")],"ADV":[("analytically","분석적으로")]},
    "assess":      {"V":[("assess","평가하다")],"N":[("assessment","평가")],"ADJ":[],"ADV":[]},
    "investigate": {"V":[("investigate","조사하다")],"N":[("investigation","조사"),("investigator","조사관")],"ADJ":[],"ADV":[]},
    "identify":    {"V":[("identify","식별하다")],"N":[("identification","식별"),("identity","신분")],"ADJ":[("identifiable","식별 가능한")],"ADV":[]},
    "measure":     {"V":[("measure","측정하다")],"N":[("measurement","측정"),("measure","조치")],"ADJ":[("measurable","측정 가능한")],"ADV":[]},
    "compare":     {"V":[("compare","비교하다")],"N":[("comparison","비교")],"ADJ":[("comparable","비교 가능한"),("comparative","비교의")],"ADV":[("comparatively","비교적으로")]},
    "survey":      {"V":[("survey","조사하다")],"N":[("survey","설문조사")],"ADJ":[],"ADV":[]},
    "monitor":     {"V":[("monitor","모니터링하다")],"N":[("monitoring","모니터링"),("monitor","모니터")],"ADJ":[],"ADV":[]},
    "predict":     {"V":[("predict","예측하다")],"N":[("prediction","예측")],"ADJ":[("predictable","예측 가능한")],"ADV":[("predictably","예측 가능하게")]},
    "examine":     {"V":[("examine","조사하다")],"N":[("examination","검사/시험"),("examiner","검사관")],"ADJ":[],"ADV":[]},
    "review":      {"V":[("review","검토하다")],"N":[("review","검토"),("reviewer","검토자")],"ADJ":[],"ADV":[]},

    # ─── GENERAL BUSINESS ───
    "require":     {"V":[("require","요구하다")],"N":[("requirement","요구사항")],"ADJ":[("required","필수의")],"ADV":[]},
    "provide":     {"V":[("provide","제공하다")],"N":[("provision","제공"),("provider","제공자")],"ADJ":[],"ADV":[]},
    "consider":    {"V":[("consider","고려하다")],"N":[("consideration","고려")],"ADJ":[("considerable","상당한"),("considerate","사려 깊은")],"ADV":[("considerably","상당히")]},
    "conduct":     {"V":[("conduct","수행하다")],"N":[("conduct","행동"),("conductor","지휘자")],"ADJ":[],"ADV":[]},
    "achieve":     {"V":[("achieve","달성하다")],"N":[("achievement","업적/달성")],"ADJ":[],"ADV":[]},
    "prepare":     {"V":[("prepare","준비하다")],"N":[("preparation","준비")],"ADJ":[("prepared","준비된")],"ADV":[]},
    "select":      {"V":[("select","선택하다")],"N":[("selection","선택")],"ADJ":[("selective","선택적인"),("selected","선택된")],"ADV":[]},
    "propose":     {"V":[("propose","제안하다")],"N":[("proposal","제안")],"ADJ":[],"ADV":[]},
    "recommend":   {"V":[("recommend","추천하다")],"N":[("recommendation","추천")],"ADJ":[],"ADV":[]},
    "resolve":     {"V":[("resolve","해결하다")],"N":[("resolution","해결")],"ADJ":[("resolved","해결된")],"ADV":[]},
    "retain":      {"V":[("retain","보유하다")],"N":[("retention","보유")],"ADJ":[],"ADV":[]},
    "register":    {"V":[("register","등록하다")],"N":[("registration","등록"),("registrant","등록자")],"ADJ":[],"ADV":[]},
    "contact":     {"V":[("contact","연락하다")],"N":[("contact","연락"),("contractor","계약자")],"ADJ":[],"ADV":[]},
    "accept":      {"V":[("accept","수락하다")],"N":[("acceptance","수락")],"ADJ":[("acceptable","수락 가능한"),("unacceptable","수락 불가한")],"ADV":[("acceptably","허용 가능하게")]},
    "assist":      {"V":[("assist","도와주다")],"N":[("assistance","도움"),("assistant","보조")],"ADJ":[],"ADV":[]},
    "expand":      {"V":[("expand","확장하다")],"N":[("expansion","확장")],"ADJ":[("expandable","확장 가능한")],"ADV":[]},
    "attend":      {"V":[("attend","참석하다")],"N":[("attendance","참석"),("attendee","참석자"),("attendant","안내원")],"ADJ":[],"ADV":[]},
    "produce":     {"V":[("produce","생산하다")],"N":[("production","생산"),("producer","생산자"),("product","제품"),("productivity","생산성")],"ADJ":[("productive","생산적인")],"ADV":[("productively","생산적으로")]},
    "negotiate":   {"V":[("negotiate","협상하다")],"N":[("negotiation","협상"),("negotiator","협상가")],"ADJ":[],"ADV":[]},
    "inspect":     {"V":[("inspect","검사하다")],"N":[("inspection","검사"),("inspector","검사관")],"ADJ":[],"ADV":[]},
    "renovate":    {"V":[("renovate","개조하다")],"N":[("renovation","개조")],"ADJ":[],"ADV":[]},
    "distribute":  {"V":[("distribute","배포하다")],"N":[("distribution","배포"),("distributor","배포자")],"ADJ":[],"ADV":[]},
    "participate": {"V":[("participate","참가하다")],"N":[("participation","참가"),("participant","참가자")],"ADJ":[],"ADV":[]},
    "contribute":  {"V":[("contribute","기여하다")],"N":[("contribution","기여"),("contributor","기여자")],"ADJ":[],"ADV":[]},
    "perform":     {"V":[("perform","수행하다")],"N":[("performance","성과"),("performer","수행자")],"ADJ":[],"ADV":[]},
    "secure":      {"V":[("secure","확보하다")],"N":[("security","보안")],"ADJ":[("secure","안전한")],"ADV":[("securely","안전하게")]},
    "update":      {"V":[("update","업데이트하다")],"N":[("update","업데이트")],"ADJ":[("updated","업데이트된")],"ADV":[]},
    "utilize":     {"V":[("utilize","활용하다")],"N":[("utilization","활용"),("utility","유틸리티")],"ADJ":[("useful","유용한")],"ADV":[]},
    "validate":    {"V":[("validate","유효화하다")],"N":[("validation","유효성 검사")],"ADJ":[("valid","유효한"),("invalid","무효한")],"ADV":[]},
    "release":     {"V":[("release","출시하다/석방하다")],"N":[("release","출시/석방")],"ADJ":[],"ADV":[]},
    "exceed":      {"V":[("exceed","초과하다")],"N":[("excess","초과")],"ADJ":[("excessive","과도한")],"ADV":[("excessively","과도하게")]},
    "acquire":     {"V":[("acquire","취득하다")],"N":[("acquisition","취득")],"ADJ":[],"ADV":[]},
    "acknowledge": {"V":[("acknowledge","인정하다")],"N":[("acknowledgment","인정")],"ADJ":[],"ADV":[]},
    "adapt":       {"V":[("adapt","적응하다")],"N":[("adaptation","적응")],"ADJ":[("adaptable","적응 가능한")],"ADV":[]},
    "adjust":      {"V":[("adjust","조정하다")],"N":[("adjustment","조정")],"ADJ":[("adjustable","조정 가능한")],"ADV":[]},
    "collaborate": {"V":[("collaborate","협력하다")],"N":[("collaboration","협력"),("collaborator","협력자")],"ADJ":[("collaborative","협력적인")],"ADV":[]},
    "demonstrate": {"V":[("demonstrate","시연하다")],"N":[("demonstration","시연")],"ADJ":[],"ADV":[]},
    "designate":   {"V":[("designate","지정하다")],"N":[("designation","지정")],"ADJ":[("designated","지정된")],"ADV":[]},
    "determine":   {"V":[("determine","결정하다")],"N":[("determination","결정")],"ADJ":[("determined","결심한")],"ADV":[]},
    "distinguish": {"V":[("distinguish","구분하다")],"N":[("distinction","구분")],"ADJ":[("distinct","뚜렷한"),("distinctive","독특한")],"ADV":[("distinctly","뚜렷하게")]},
    "eliminate":   {"V":[("eliminate","제거하다")],"N":[("elimination","제거")],"ADJ":[],"ADV":[]},
    "encourage":   {"V":[("encourage","장려하다")],"N":[("encouragement","장려")],"ADJ":[("encouraging","고무적인")],"ADV":[]},
    "ensure":      {"V":[("ensure","보장하다")],"N":[],"ADJ":[],"ADV":[]},
    "generate":    {"V":[("generate","생성하다")],"N":[("generation","생성")],"ADJ":[("generated","생성된")],"ADV":[]},
    "incorporate": {"V":[("incorporate","통합하다")],"N":[("incorporation","통합")],"ADJ":[("incorporated","통합된")],"ADV":[]},
    "issue":       {"V":[("issue","발행하다")],"N":[("issue","문제/발행")],"ADJ":[],"ADV":[]},
    "justify":     {"V":[("justify","정당화하다")],"N":[("justification","정당화")],"ADJ":[("justified","정당화된")],"ADV":[]},
    "obtain":      {"V":[("obtain","얻다")],"N":[],"ADJ":[("obtainable","얻을 수 있는")],"ADV":[]},
    "prioritize":  {"V":[("prioritize","우선순위 두다")],"N":[("priority","우선순위")],"ADJ":[("prior","사전의")],"ADV":[]},
    "migrate":     {"V":[("migrate","이주하다")],"N":[("migration","이주")],"ADJ":[],"ADV":[]},
    "minimize":    {"V":[("minimize","최소화하다")],"N":[("minimum","최솟값")],"ADJ":[("minimal","최소의"),("minimum","최소의")],"ADV":[]},
    "maximize":    {"V":[("maximize","최대화하다")],"N":[("maximum","최댓값")],"ADJ":[("maximum","최대의")],"ADV":[]},
    "simplify":    {"V":[("simplify","단순화하다")],"N":[("simplification","단순화")],"ADJ":[("simple","단순한")],"ADV":[("simply","단순히")]},
    "summarize":   {"V":[("summarize","요약하다")],"N":[("summary","요약")],"ADJ":[],"ADV":[]},
    "accumulate":  {"V":[("accumulate","축적하다")],"N":[("accumulation","축적")],"ADJ":[("accumulated","축적된")],"ADV":[]},
    "exchange":    {"V":[("exchange","교환하다")],"N":[("exchange","교환")],"ADJ":[],"ADV":[]},

    # ─── ADJ/ADV-ROOT (품사 파생형이 핵심인 단어들) ───
    "significance":{"V":[],"N":[("significance","중요성")],"ADJ":[("significant","중요한")],"ADV":[("significantly","상당히")]},
    "efficiency":  {"V":[],"N":[("efficiency","효율성")],"ADJ":[("efficient","효율적인")],"ADV":[("efficiently","효율적으로")]},
    "sufficiency": {"V":[],"N":[("sufficiency","충분함")],"ADJ":[("sufficient","충분한")],"ADV":[("sufficiently","충분히")]},
    "convenience": {"V":[],"N":[("convenience","편의")],"ADJ":[("convenient","편리한")],"ADV":[("conveniently","편리하게")]},
    "availability":{"V":[],"N":[("availability","가용성")],"ADJ":[("available","이용 가능한")],"ADV":[]},
    "relevance":   {"V":[],"N":[("relevance","관련성")],"ADJ":[("relevant","관련 있는")],"ADV":[]},
    "appropriateness":{"V":[],"N":[],"ADJ":[("appropriate","적절한")],"ADV":[("appropriately","적절히")]},
    "potential":   {"V":[],"N":[("potential","잠재력")],"ADJ":[("potential","잠재적인")],"ADV":[("potentially","잠재적으로")]},
    "addition":    {"V":[("add","추가하다")],"N":[("addition","추가")],"ADJ":[("additional","추가적인")],"ADV":[("additionally","추가로")]},
    "permanence":  {"V":[],"N":[("permanence","영속성")],"ADJ":[("permanent","영구적인")],"ADV":[("permanently","영구적으로")]},
    "immediacy":   {"V":[],"N":[],"ADJ":[("immediate","즉각적인")],"ADV":[("immediately","즉시")]},
    "effectiveness":{"V":[],"N":[("effectiveness","효과")],"ADJ":[("effective","효과적인")],"ADV":[("effectively","효과적으로")]},
    "accuracy":    {"V":[],"N":[("accuracy","정확도")],"ADJ":[("accurate","정확한")],"ADV":[("accurately","정확히")]},
    "temporary":   {"V":[],"N":[],"ADJ":[("temporary","임시의")],"ADV":[("temporarily","일시적으로")]},
    "responsibility":{"V":[("respond","응답하다")],"N":[("responsibility","책임")],"ADJ":[("responsible","책임 있는")],"ADV":[("responsibly","책임감 있게")]},
    "comprehension":{"V":[("comprehend","이해하다")],"N":[("comprehension","이해")],"ADJ":[("comprehensive","포괄적인")],"ADV":[("comprehensively","포괄적으로")]},
    "approval":    {"V":[("approve","승인하다")],"N":[("approval","승인")],"ADJ":[("approved","승인된")],"ADV":[]},
}

# ════════════════════════════════════════════════════
# 역방향 인덱스 자동 생성: word → {root, kr, pos}
# ════════════════════════════════════════════════════
WORD_INDEX = {}
for _root, _fam in FAMILY_DB.items():
    for _pos, _members in _fam.items():
        for _word, _kr in _members:
            _wl = _word.lower()
            if _wl not in WORD_INDEX:
                WORD_INDEX[_wl] = {"root": _root, "kr": _kr, "pos": _pos}
    # root 자체도 등록 (동사형이 없는 경우 대비)
    if _root not in WORD_INDEX:
        WORD_INDEX[_root] = {"root": _root, "kr": "", "pos": "V"}


def _normalize(word):
    """inflected → base 후보 리스트 반환"""
    w = word.lower().strip(".,;:!?\"'()")
    candidates = [w]
    # -ing 제거
    if w.endswith("ing") and len(w) > 5:
        candidates.append(w[:-3])          # removing → remov
        candidates.append(w[:-3] + "e")    # removing → remove
    # -ed 제거
    if w.endswith("ed") and len(w) > 4:
        candidates.append(w[:-2])          # employed → employ (close enough)
        candidates.append(w[:-1])          # trained → traine (fallback)
        candidates.append(w[:-2] + "e")    # managed → manage
    # -s/-es 제거
    if w.endswith("ies") and len(w) > 4:
        candidates.append(w[:-3] + "y")    # identifies → identify
    elif w.endswith("es") and len(w) > 4:
        candidates.append(w[:-2])          # processes → process
    elif w.endswith("s") and len(w) > 4:
        candidates.append(w[:-1])          # managers → manager
    # -ly 제거
    if w.endswith("ly") and len(w) > 5:
        candidates.append(w[:-2])          # effectively → effective
        candidates.append(w[:-2] + "e")
    # -ion / -tion 제거
    if w.endswith("tion") and len(w) > 6:
        candidates.append(w[:-4])
        candidates.append(w[:-4] + "e")
    if w.endswith("ation") and len(w) > 7:
        candidates.append(w[:-5])
        candidates.append(w[:-5] + "e")
    return candidates


def lookup(word):
    """단어 → {root, kr, pos} 반환, 없으면 None"""
    for candidate in _normalize(word):
        if candidate in WORD_INDEX:
            return WORD_INDEX[candidate]
    return None


def get_family(word):
    """단어 → 패밀리 dict {V:[...], N:[...], ADJ:[...], ADV:[...]} 반환"""
    info = lookup(word)
    if not info:
        return {}
    return FAMILY_DB.get(info["root"], {})


def find_words_in_sentence(sentence, max_words=3):
    """
    문장에서 DB에 있는 단어 추출.
    반환: [{"word":w, "kr":kr, "pos":pos, "family_root":root}, ...]
    토익 핵심 어휘 우선, 중복 root 제거, max_words 개 반환
    """
    if not sentence:
        return []
    tokens = _re.findall(r"[A-Za-z]{3,}", sentence)
    seen_roots = set()
    results = []
    # 긴 단어 우선 (핵심어일 가능성 높음)
    tokens_sorted = sorted(set(t.lower() for t in tokens), key=len, reverse=True)
    # 기능어 제외
    _STOP = {
        "the","and","for","are","was","were","has","have","had","been","being",
        "that","this","with","they","them","their","from","will","would","could",
        "should","shall","which","what","when","where","who","whom","whose","how",
        "not","but","its","his","her","our","your","all","any","each","both",
        "more","most","such","only","just","also","even","still","very","much",
        "into","onto","upon","over","under","after","before","since","until",
        "about","above","below","along","among","between","through","during",
        "these","those","here","there","now","then","thus","however","therefore",
        "although","because","whether","whereas","while","although","unless",
        "either","neither","nor","yet","though","once","already","always","never",
    }
    for token in tokens_sorted:
        if token in _STOP or len(token) < 4:
            continue
        info = lookup(token)
        if info and info["root"] not in seen_roots:
            seen_roots.add(info["root"])
            results.append({
                "word":        token,
                "kr":          info["kr"],
                "pos":         info["pos"],
                "family_root": info["root"],
            })
            if len(results) >= max_words:
                break
    return results


# ════════════════════════════════════════════════════
# 통계 (확인용)
# ════════════════════════════════════════════════════
TOTAL_ROOTS = len(FAMILY_DB)
TOTAL_WORDS = len(WORD_INDEX)
