# -*- coding: utf-8 -*-
"""
SnapQ v11 — 모닝팩 P5 개편 (2026-04-24)
═══════════════════════════════════════════════════════════

변경:
  ✅ 레이블: "🌅 오늘의 워밍업" → "🌅 모닝팩 P5" (2곳)
  ✅ 시간: 데일리 120초 → 33초 (속도 훈련, 선생님 수업 용어)
  ✅ 문항 풀: 새 30문항 (정기 TOEIC P5 수준, 각 15-18단어)
      - 어법 15문항 (D001~D015)
      - 어휘 15문항 (D016~D030)
  ✅ 정답 인덱스 균형 배치 (0/1/2/3 골고루)

실행:
    cd C:\\Users\\최정은\\Desktop\\snapq_toeic_V3
    python apply_patch_v11.py
"""
import shutil, sys
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

FILE = Path("app/core/pretest_gate.py")
BACKUP_DIR = Path("backup_2026-04-27")
BACKUP_DIR.mkdir(exist_ok=True)

if not FILE.exists():
    print(f"❌ 파일 없음: {FILE.resolve()}")
    sys.exit(1)

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"pretest_gate.py.v11_p5.{stamp}.bak"
shutil.copy(FILE, backup)
print(f"✅ 백업: {backup}")

raw = FILE.read_bytes()
had_bom = raw.startswith(b"\xef\xbb\xbf")
if had_bom:
    raw = raw[3:]
text = raw.decode("utf-8")
orig_crlf = "\r\n" in text
content = text.replace("\r\n", "\n")
original = content
patches = 0

# ═══════════════════════════════════════════════════════════
# 패치 ① : DAILY_GATE_TIME_SEC 120 → 33
# ═══════════════════════════════════════════════════════════
old_1 = "DAILY_GATE_TIME_SEC      = 120   # ⭐ 데일리 총 제한: 2분"
new_1 = "DAILY_GATE_TIME_SEC      = 33    # ⭐ 모닝팩 P5: 5문제 33초 (속도 훈련)"
if old_1 in content:
    content = content.replace(old_1, new_1)
    print("✅ 패치 ①: DAILY_GATE_TIME_SEC 120 → 33")
    patches += 1
else:
    print("⚠️  패치 ①: 상수 원본 못 찾음")

# ═══════════════════════════════════════════════════════════
# 패치 ② : "오늘의 워밍업 완료!" → "모닝팩 P5 완료!"
# ═══════════════════════════════════════════════════════════
old_2 = "오늘의 워밍업 완료!"
new_2 = "모닝팩 P5 완료!"
count_2 = content.count(old_2)
if count_2 > 0:
    content = content.replace(old_2, new_2)
    print(f"✅ 패치 ②: '워밍업 완료' → '모닝팩 P5 완료' ({count_2}곳)")
    patches += 1
else:
    print("⚠️  패치 ②: '워밍업 완료' 못 찾음")

# ═══════════════════════════════════════════════════════════
# 패치 ③ : "🌅 오늘의 워밍업 · Day {day}" → "🌅 모닝팩 P5 · Day {day}"
# ═══════════════════════════════════════════════════════════
old_3 = "🌅 오늘의 워밍업 · Day {day}"
new_3 = "🌅 모닝팩 P5 · Day {day}"
count_3 = content.count(old_3)
if count_3 > 0:
    content = content.replace(old_3, new_3)
    print(f"✅ 패치 ③: 헤더 타이틀 '워밍업' → '모닝팩 P5' ({count_3}곳)")
    patches += 1
else:
    print("⚠️  패치 ③: 헤더 원본 못 찾음")

# ═══════════════════════════════════════════════════════════
# 패치 ④ : _BUILTIN_DAILY_POOL 전체 교체 (신규 30문항)
# ═══════════════════════════════════════════════════════════
start = content.find("_BUILTIN_DAILY_POOL = [")
end = content.find("\ndef require_pretest_gate", start)
if start < 0 or end < 0:
    print("⚠️  패치 ④: _BUILTIN_DAILY_POOL 위치 못 찾음")
else:
    new_pool = '''_BUILTIN_DAILY_POOL = [
    # ═══ 어법 15문항 (TOEIC P5 수준, 15-18단어) ═══
    {"id":"D001","type":"grammar","diff":"medium",
     "question":"The manager announced that the quarterly report ___ by the accounting department before Friday.",
     "choices":["completing","completed","will be completed","was completing"],"answer_idx":2},
    {"id":"D002","type":"grammar","diff":"easy",
     "question":"All documents submitted to the legal department must be ___ reviewed before the signing ceremony.",
     "choices":["thorough","thoroughly","thoroughness","more thorough"],"answer_idx":1},
    {"id":"D003","type":"grammar","diff":"medium",
     "question":"The new marketing strategy ___ last month has already increased sales by over twenty percent.",
     "choices":["implement","implemented","implementing","to implement"],"answer_idx":1},
    {"id":"D004","type":"grammar","diff":"hard",
     "question":"Unless the proposal ___ by the board next week, the project will be postponed indefinitely.",
     "choices":["approved","approves","is approved","approving"],"answer_idx":2},
    {"id":"D005","type":"grammar","diff":"medium",
     "question":"The senior engineers ___ on the new prototype have requested additional funding from the director this month.",
     "choices":["work","works","working","worked"],"answer_idx":2},
    {"id":"D006","type":"grammar","diff":"easy",
     "question":"Mr. Chen, ___ has been with the company for fifteen years, will retire this December.",
     "choices":["who","whom","which","whose"],"answer_idx":0},
    {"id":"D007","type":"grammar","diff":"medium",
     "question":"The training session will begin promptly at nine AM ___ all participants arrive on time.",
     "choices":["as long as","in spite of","because of","due to"],"answer_idx":0},
    {"id":"D008","type":"grammar","diff":"hard",
     "question":"Not only ___ the annual revenue exceeded expectations, but customer satisfaction also improved quite significantly.",
     "choices":["have","has","did","does"],"answer_idx":1},
    {"id":"D009","type":"grammar","diff":"medium",
     "question":"The company's decision to expand into Asian markets ___ by many analysts as highly strategic.",
     "choices":["views","viewing","viewed","is viewed"],"answer_idx":3},
    {"id":"D010","type":"grammar","diff":"easy",
     "question":"Before finalizing the annual budget, the finance team consulted with senior management for three days.",
     "choices":["Before","While","During","Since"],"answer_idx":0},
    {"id":"D011","type":"grammar","diff":"hard",
     "question":"Had the contract been signed yesterday afternoon, the project ___ started on schedule this morning.",
     "choices":["will","would","would have","had"],"answer_idx":2},
    {"id":"D012","type":"grammar","diff":"medium",
     "question":"The research findings, ___ were published last month, have attracted significant attention from industry experts.",
     "choices":["who","which","that","what"],"answer_idx":1},
    {"id":"D013","type":"grammar","diff":"easy",
     "question":"The newly released software is significantly faster ___ the previous version in almost every aspect.",
     "choices":["as","than","to","from"],"answer_idx":1},
    {"id":"D014","type":"grammar","diff":"medium",
     "question":"Employees ___ training programs regularly tend to show higher productivity than those who do not.",
     "choices":["attend","attending","attended","have attended"],"answer_idx":1},
    {"id":"D015","type":"grammar","diff":"hard",
     "question":"Please ensure that all visitors ___ at the reception desk immediately upon entering the building.",
     "choices":["register","registers","to register","registered"],"answer_idx":0},

    # ═══ 어휘 15문항 (TOEIC P5 수준, 15-18단어) ═══
    {"id":"D016","type":"vocab","diff":"easy",
     "question":"The board of directors will ___ the new proposal during tomorrow's executive meeting at headquarters.",
     "choices":["retain","replace","reject","review"],"answer_idx":3},
    {"id":"D017","type":"vocab","diff":"medium",
     "question":"Customer complaints have ___ quite significantly after the implementation of the new quality control system.",
     "choices":["increased","released","decreased","expressed"],"answer_idx":2},
    {"id":"D018","type":"vocab","diff":"medium",
     "question":"The company's financial position has become much more ___ since the merger was completed last year.",
     "choices":["stabled","stable","stability","stably"],"answer_idx":1},
    {"id":"D019","type":"vocab","diff":"hard",
     "question":"Please kindly ___ from using mobile devices during the presentation in the main conference hall.",
     "choices":["refrain","refer","refresh","reduce"],"answer_idx":0},
    {"id":"D020","type":"vocab","diff":"medium",
     "question":"The marketing team will ___ a comprehensive new strategy to attract international clients next quarter.",
     "choices":["divide","deliver","decline","devise"],"answer_idx":3},
    {"id":"D021","type":"vocab","diff":"medium",
     "question":"The factory's production capacity has already ___ the limit set by current industry regulations this month.",
     "choices":["exhausted","extracted","exceeded","extended"],"answer_idx":2},
    {"id":"D022","type":"vocab","diff":"hard",
     "question":"All staff members are expected to ___ to the company's strict code of conduct at all times.",
     "choices":["adhere","adjust","address","admit"],"answer_idx":0},
    {"id":"D023","type":"vocab","diff":"medium",
     "question":"The CEO expressed her ___ for the team's outstanding performance during the difficult economic period.",
     "choices":["hesitation","explanation","appreciation","limitation"],"answer_idx":2},
    {"id":"D024","type":"vocab","diff":"easy",
     "question":"The supplier failed to ___ the shipment as promised, causing significant delays in our production schedule.",
     "choices":["divide","deliver","declare","devote"],"answer_idx":1},
    {"id":"D025","type":"vocab","diff":"hard",
     "question":"The new company policy will ___ every employee across all departments starting from next Monday.",
     "choices":["effect","infect","reflect","affect"],"answer_idx":3},
    {"id":"D026","type":"vocab","diff":"medium",
     "question":"The conference attendees ___ from various industries around the world gathered for the keynote speech.",
     "choices":["representing","represented","represent","representation"],"answer_idx":0},
    {"id":"D027","type":"vocab","diff":"medium",
     "question":"The research team will need to ___ the data very carefully before publishing the final findings.",
     "choices":["apologize","announce","analyze","anticipate"],"answer_idx":2},
    {"id":"D028","type":"vocab","diff":"easy",
     "question":"The proposal submitted by our competitor is ___ to ours in terms of technical specifications.",
     "choices":["simulated","similar","stimulating","strategic"],"answer_idx":1},
    {"id":"D029","type":"vocab","diff":"hard",
     "question":"The client's detailed requirements have been clearly ___ in the technical specifications document distributed last Friday.",
     "choices":["outlined","outlaid","outsourced","outlawed"],"answer_idx":0},
    {"id":"D030","type":"vocab","diff":"medium",
     "question":"Due to unexpected circumstances, the launch event has been ___ until further notice from management.",
     "choices":["postponed","prospected","promoted","preserved"],"answer_idx":0},
]

'''
    content = content[:start] + new_pool + content[end+1:]
    print("✅ 패치 ④: _BUILTIN_DAILY_POOL 30문항 교체 (TOEIC P5 15-18단어)")
    patches += 1

# ═══════════════════════════════════════════════════════════
# 저장
# ═══════════════════════════════════════════════════════════
if content == original:
    print("❌ 변경 없음")
    sys.exit(1)

if orig_crlf:
    content = content.replace("\n", "\r\n")
out = content.encode("utf-8")
if had_bom:
    out = b"\xef\xbb\xbf" + out
FILE.write_bytes(out)

print(f"\n✅ 저장 완료 ({patches}/4 패치 적용)")
print(f"📁 백업: {backup}")
print("")
print("📝 최종 사양:")
print("   - 이름: 🌅 모닝팩 P5 (모닝 임팩트)")
print("   - 시간: 5문제 33초 (속도 훈련)")
print("   - 난이도: 정기 TOEIC P5 수준 (15-18단어)")
print("   - 구성: 어법 15 + 어휘 15 = 30문항 풀")
print("")
print("🧪 다음 단계:")
print("   git add app/core/pretest_gate.py apply_patch_v11.py")
print('   git commit -m "feat: v11 모닝팩 P5 - 33초 + TOEIC 정기시험 수준 30문항"')
print("   git push")
print("")
print("📱 모바일: https://snapq-toeic.streamlit.app?v=11")
