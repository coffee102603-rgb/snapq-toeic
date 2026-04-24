# -*- coding: utf-8 -*-
"""
SnapQ v12 — 관문검사 개편 (2026-04-24)
═══════════════════════════════════════════════════════════

선생님 예측 기반 설계 (100명 기준):
  - 만점: 3명 (3%)
  - 20-29점: 47명 (47%)
  - 0-15점: 50명 (50%)
  → IRT 예상 평균 59.5% (baseline 이상적 범위)

변경:
  ✅ MILESTONE_GATE_TIME_SEC: 900 → 600 (15분 → 10분)
  ✅ TEST_QUESTIONS 전체 교체 (30문항, 각 20-25단어)
  ✅ 난이도 분포:
     어법 20 = 쉬움 6 + 중간 8 + 어려움 6
     어휘 10 = 쉬움 3 + 중간 4 + 어려움 3
  ✅ 모닝팩 P5와 문항 완전 분리 (중복 없음)

실행:
    cd C:\\Users\\최정은\\Desktop\\snapq_toeic_V3
    python apply_patch_v12.py
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
backup = BACKUP_DIR / f"pretest_gate.py.v12_milestone.{stamp}.bak"
shutil.copy(FILE, backup)
print(f"✅ 백업: {backup}")

raw = FILE.read_bytes()
had_bom = raw.startswith(b"\xef\xbb\xbf")
if had_bom:
    raw = raw[3:]
text = raw.decode("utf-8")
orig_crlf = "\r\n" in text
content = text.replace("\n", "\n").replace("\r\n", "\n")
original = content
patches = 0

# ═══════════════════════════════════════════════════════════
# 패치 ① : MILESTONE_GATE_TIME_SEC 900 → 600
# ═══════════════════════════════════════════════════════════
old_1 = "MILESTONE_GATE_TIME_SEC  = 900   # ⭐ 관문검사 총 제한: 15분"
new_1 = "MILESTONE_GATE_TIME_SEC  = 600   # ⭐ 관문검사: 30문항 10분 (정기토익 속도)"
if old_1 in content:
    content = content.replace(old_1, new_1)
    print("✅ 패치 ①: MILESTONE_GATE_TIME_SEC 900 → 600 (10분)")
    patches += 1
else:
    print("⚠️  패치 ①: 상수 원본 못 찾음")

# ═══════════════════════════════════════════════════════════
# 패치 ② : TEST_QUESTIONS 전체 교체 (30문항 20-25단어)
# ═══════════════════════════════════════════════════════════
start = content.find("TEST_QUESTIONS = [")
end = content.find("\n]\n", start)
if start < 0 or end < 0:
    print("⚠️  패치 ②: TEST_QUESTIONS 위치 못 찾음")
else:
    end += 3  # '\n]\n' 포함
    new_questions = '''TEST_QUESTIONS = [
    # ═══ 어법 20문항 (TOEIC 정기시험 수준, 20단어) ═══

    # --- 쉬움 6문항 (정답률 85%+ 기대) ---
    {"id": "T1", "text": "The detailed quarterly sales report _______ to all department heads before tomorrow's management meeting scheduled at the main office.",
     "ch": ["(A) distributes", "(B) distributing", "(C) will be distributed", "(D) has distributed"], "a": 2, "cat": "수동태·시제"},
    {"id": "T2", "text": "The new employees have been working very _______ to complete the training program before the end of the month.",
     "ch": ["(A) diligent", "(B) diligently", "(C) diligence", "(D) most diligent"], "a": 1, "cat": "품사/수식"},
    {"id": "T3", "text": "Ms. Rodriguez, _______ has been promoted to senior vice president, will oversee the Asia-Pacific division starting next January.",
     "ch": ["(A) who", "(B) whom", "(C) whose", "(D) which"], "a": 0, "cat": "관계절"},
    {"id": "T4", "text": "Employees currently _______ in the new wellness program have reported significantly improved energy levels and overall workplace satisfaction.",
     "ch": ["(A) participate", "(B) participating", "(C) participated", "(D) to participate"], "a": 1, "cat": "분사구"},
    {"id": "T5", "text": "All conference participants must register _______ the main reception desk at least thirty minutes before the keynote speech begins.",
     "ch": ["(A) to", "(B) at", "(C) in", "(D) on"], "a": 1, "cat": "전치사"},
    {"id": "T6", "text": "Sales performance this quarter has been considerably _______ than last quarter due to the new integrated marketing campaign strategies.",
     "ch": ["(A) good", "(B) better", "(C) best", "(D) well"], "a": 1, "cat": "비교급"},

    # --- 중간 8문항 (정답률 55-65% 기대) ---
    {"id": "T7", "text": "Rarely _______ the finance department encountered such significant discrepancies in the annual audit report submitted just last week.",
     "ch": ["(A) have", "(B) has", "(C) did", "(D) does"], "a": 1, "cat": "도치"},
    {"id": "T8", "text": "The committee members strongly recommended that the current proposal _______ thoroughly before the final decision is made at headquarters.",
     "ch": ["(A) reconsiders", "(B) reconsidered", "(C) be reconsidered", "(D) is reconsidered"], "a": 2, "cat": "가정법/주장동사"},
    {"id": "T9", "text": "By the time the merger is finalized, the negotiation team _______ the details for over six months straight.",
     "ch": ["(A) discusses", "(B) has discussed", "(C) will have been discussing", "(D) was discussing"], "a": 2, "cat": "시제"},
    {"id": "T10", "text": "_______ by the chief executive officer, the new company policy will take effect at the beginning of next month.",
     "ch": ["(A) Approve", "(B) Approved", "(C) Approving", "(D) Having approved"], "a": 1, "cat": "분사구문"},
    {"id": "T11", "text": "The important clients were quite satisfied with the proposal _______ they had initially requested several additional features for the platform.",
     "ch": ["(A) although", "(B) because", "(C) unless", "(D) whereas"], "a": 0, "cat": "접속사"},
    {"id": "T12", "text": "The confidential financial documents need _______ by the external auditor before the board meeting scheduled for next Friday afternoon.",
     "ch": ["(A) reviewing", "(B) to review", "(C) to be reviewed", "(D) reviewed"], "a": 2, "cat": "부정사/수동"},
    {"id": "T13", "text": "The conference room _______ we held the last strategy meeting has recently been equipped with advanced audiovisual technology equipment.",
     "ch": ["(A) which", "(B) where", "(C) that", "(D) when"], "a": 1, "cat": "관계부사"},
    {"id": "T14", "text": "Each of the department managers, along with their personal assistants, _______ required to attend the quarterly strategic planning session.",
     "ch": ["(A) is", "(B) are", "(C) have", "(D) being"], "a": 0, "cat": "주어동사 일치"},

    # --- 어려움 6문항 (정답률 30-40% 기대) ---
    {"id": "T15", "text": "Had the company _______ the innovative technology earlier, the market share would have increased by at least thirty percent.",
     "ch": ["(A) adopt", "(B) adopted", "(C) adopts", "(D) adopting"], "a": 1, "cat": "가정법 도치"},
    {"id": "T16", "text": "The consulting firm presented exactly _______ they claimed would be the most profitable investment strategy for our overseas expansion.",
     "ch": ["(A) that", "(B) which", "(C) what", "(D) whose"], "a": 2, "cat": "관계대명사 what"},
    {"id": "T17", "text": "The complicated negotiations took much longer than expected, _______ a significant delay in the project's originally planned completion date.",
     "ch": ["(A) cause", "(B) caused", "(C) causing", "(D) to cause"], "a": 2, "cat": "분사구문"},
    {"id": "T18", "text": "So rapidly _______ the entire technology sector evolved that traditional business models have become obsolete within just a few years.",
     "ch": ["(A) has", "(B) have", "(C) had", "(D) does"], "a": 0, "cat": "도치"},
    {"id": "T19", "text": "_______ any further assistance be required at any stage of the process, please do not hesitate to contact our team.",
     "ch": ["(A) If", "(B) Should", "(C) Were", "(D) Had"], "a": 1, "cat": "가정법 도치"},
    {"id": "T20", "text": "The new CEO has introduced innovative policies that prioritize not only increased efficiency _______ also enhanced employee satisfaction and retention.",
     "ch": ["(A) and", "(B) or", "(C) but", "(D) with"], "a": 2, "cat": "상관접속사"},

    # ═══ 어휘 10문항 (TOEIC 정기시험 수준, 20단어) ═══

    # --- 쉬움 3문항 ---
    {"id": "T21", "text": "The annual financial report indicates that our company has achieved _______ growth in all three major international markets this year.",
     "ch": ["(A) substantial", "(B) substantive", "(C) subsequent", "(D) subjective"], "a": 0, "cat": "어휘"},
    {"id": "T22", "text": "All department heads must _______ their quarterly budget proposal to the finance committee by the end of next week.",
     "ch": ["(A) submit", "(B) subject", "(C) submerge", "(D) subside"], "a": 0, "cat": "어휘"},
    {"id": "T23", "text": "The new marketing strategy requires a detailed _______ of consumer behavior patterns across different demographic segments and regional markets.",
     "ch": ["(A) analysis", "(B) anxiety", "(C) amnesty", "(D) ambition"], "a": 0, "cat": "어휘"},

    # --- 중간 4문항 ---
    {"id": "T24", "text": "The CEO's inspiring speech at the annual company conference had a _______ impact on employee morale throughout the entire organization.",
     "ch": ["(A) productive", "(B) profound", "(C) protective", "(D) provocative"], "a": 1, "cat": "어휘"},
    {"id": "T25", "text": "Due to unforeseen global economic circumstances, the senior management team has decided to _______ all non-essential expenditures until further notice.",
     "ch": ["(A) postpone", "(B) promote", "(C) preserve", "(D) predict"], "a": 0, "cat": "어휘"},
    {"id": "T26", "text": "The conference venue was booked for our industry event, making it necessary to find a _______ location on short notice.",
     "ch": ["(A) alternate", "(B) alternative", "(C) alternating", "(D) alternation"], "a": 1, "cat": "어휘"},
    {"id": "T27", "text": "The research team will need to very carefully _______ the experimental data before drawing any definitive conclusions from the study.",
     "ch": ["(A) examine", "(B) exempt", "(C) exceed", "(D) exclaim"], "a": 0, "cat": "어휘"},

    # --- 어려움 3문항 ---
    {"id": "T28", "text": "The strict regulatory changes announced last month will _______ a significant shift in how financial institutions manage their investment portfolios.",
     "ch": ["(A) necessitate", "(B) negotiate", "(C) neutralize", "(D) nominate"], "a": 0, "cat": "어휘"},
    {"id": "T29", "text": "Despite the initial setbacks, the entire project team demonstrated remarkable _______ by successfully meeting all critical milestones ahead of schedule.",
     "ch": ["(A) resilience", "(B) reluctance", "(C) reverence", "(D) redundancy"], "a": 0, "cat": "어휘"},
    {"id": "T30", "text": "The new merger agreement _______ all parties involved to strict confidentiality clauses regarding the financial details of the transaction.",
     "ch": ["(A) subjects", "(B) subjugates", "(C) submits", "(D) subscribes"], "a": 0, "cat": "어휘"},
]
'''
    content = content[:start] + new_questions + content[end:]
    print("✅ 패치 ②: TEST_QUESTIONS 30문항 교체 (정기토익 수준 20단어)")
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

print(f"\n✅ 저장 완료 ({patches}/2 패치 적용)")
print(f"📁 백업: {backup}")
print("")
print("📝 최종 관문검사 사양:")
print("   - 시점: Day 2 / Day 11 / Day 20 (월 3회)")
print("   - 문항: 30개 (어법 20 + 어휘 10)")
print("   - 시간: 10분 (600초)")
print("   - 문항 길이: 각 20단어 (정기 TOEIC 실전)")
print("   - 난이도: 쉬움 9 + 중간 12 + 어려움 9")
print("   - 예상 Day 2 평균: 59% (baseline)")
print("   - Day 20 목표 평균: 75%+ (성장 검증)")
print("")
print("🧪 다음 단계:")
print("   git add app/core/pretest_gate.py apply_patch_v12.py")
print('   git commit -m "feat: v12 관문검사 개편 - 10분 + 30문항 TOEIC 정기시험 수준"')
print("   git push")
print("")
print("📱 모바일: https://snapq-toeic.streamlit.app?v=12")
