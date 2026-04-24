# -*- coding: utf-8 -*-
"""
SnapQ 설문 문항 재설계 v3 (2026-04-24)
═══════════════════════════════════════════════════════════

변경 내용:
  ① 리커트 24문항 (A~F) → 26문항 (TH/AL/EF/MG/MO/GA) 재구조화
  ② 기초변수 2개 추가 (Q_LEVEL, Q_YEARS) — 종단분석 공변량
  ③ 사전 주관식 G0_open 추가 — 자기문화기술지 pre-post 쌍
  ④ _render_survey 함수 교체 — 카테고리 prefix 매핑 + 선택형 UI

실행:
    cd C:\\Users\\최정은\\Desktop\\snapq_toeic_V3
    python apply_patch_v3.py
"""
import shutil
import sys
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
backup_path = BACKUP_DIR / f"pretest_gate.py.v3_survey.{stamp}.bak"
shutil.copy(FILE, backup_path)
print(f"✅ 백업: {backup_path}")

# ━━━ 파일 읽기 ━━━
raw = FILE.read_bytes()
had_bom = raw.startswith(b"\xef\xbb\xbf")
if had_bom:
    raw = raw[3:]
text = raw.decode("utf-8")
original_crlf = "\r\n" in text
content = text.replace("\r\n", "\n")
original = content
patches = 0

# ═══════════════════════════════════════════════════════════
# 패치 ① : SURVEY_ITEMS + SURVEY_POST_ONLY + 부속 상수 블록 전체 교체
# ═══════════════════════════════════════════════════════════
old_1 = """SURVEY_ITEMS = {
    # ── A. 영어 학습 동기·태도 → ①⑤⑩⑪ ──
    "A1": "영어 문법 공부가 재미있다",
    "A2": "TOEIC 점수를 올리고 싶은 마음이 강하다",
    "A3": "혼자서도 영어 공부를 꾸준히 할 수 있다",
    "A4": "영어 공부에 자신감이 있다",
    # ── B. 게이미피케이션·임계값 인식 → ①②⑤⑩ ── ★ THRESHOLD CORE
    "B1": "게임처럼 점수·랭킹이 있으면 더 열심히 공부한다",
    "B2": "시간 제한이 있으면 더 집중된다",
    "B3": "틀린 문제를 다시 풀면 실력이 오를 것 같다",          # 재도전 임계값
    "B4": "도전적인 목표가 있으면 더 몰입한다",                 # 목표 임계값
    # ── C. AI·기술 학습 환경 인식 → ⑤⑧⑨⑪ ──
    "C1": "AI가 내 수준에 맞춰주면 더 효과적일 것 같다",
    "C2": "앱이나 웹으로 공부하는 것이 교재보다 편하다",
    "C3": "AI가 내 약점을 알려주면 도움이 될 것 같다",
    "C4": "기술(앱/AI)을 활용한 학습에 거부감이 없다",
    # ── D. 자기 효능감 → ④⑦⑩⑪ ── ★ THRESHOLD CORE
    "D1": "나는 TOEIC P5 문법 문제를 잘 풀 수 있다",
    "D2": "어려운 문법이라도 연습하면 이해할 수 있다",
    "D3": "영어 독해 지문을 정확히 읽을 수 있다",
    "D4": "시간 압박 속에서도 정답을 고를 수 있다",              # RT 임계값 효능감
    # ── E. 학습 전략·습관 → ⑤⑥⑦ ── ★ THRESHOLD CORE
    "E1": "모르는 단어를 만나면 바로 찾아보는 편이다",
    "E2": "틀린 문제를 반드시 다시 확인한다",                    # 망각곡선 임계값
    "E3": "문법 문제를 풀 때 문장 전체를 읽고 푼다",
    "E4": "독해에서 배운 표현을 문법에 적용해본 적이 있다",      # 크로스스킬
    # ── F. 몰입·지속 의향 → ②⑤⑩⑪ ──
    "F1": "한 번 시작하면 쉽게 멈추기 어렵다",
    "F2": "매일 조금씩이라도 영어 공부를 하고 싶다",
    "F3": "이런 학습 앱을 계속 사용하고 싶다",
    "F4": "친구에게도 추천하고 싶다",
}

# 사후 전용 (G) — 리커트 4문항 + 주관식 1문항
SURVEY_POST_ONLY = {
    "G1": "SnapQ가 영어 실력 향상에 도움이 되었다",
    "G2_choice": "가장 도움이 된 모드는?",  # 선택형
    "G3": "난이도가 자동으로 바뀌는 것이 도움이 되었다",        # 논문 ⑦
    "G4": "NPC(토리/해이) 메시지가 동기부여에 도움이 되었다",   # 논문 ⑧
    "G5_open": "한 줄 소감을 자유롭게 적어주세요",               # 질적 데이터
}

LIKERT_OPTIONS = ["전혀 아니다", "아니다", "보통이다", "그렇다", "매우 그렇다"]
G2_CHOICES = ["⚡ 화력전 (문법 5문제)", "📡 암호해독 (독해 3문제)", "💀 포로사령부 (오답 복습)"]"""

new_1 = '''# ═════════════════════════════════════════════════════════════════
# 설문 문항 v3 — 재구조화 2026.04.24 (PPT 대서사시 × 11개 논문 매핑)
# ═════════════════════════════════════════════════════════════════
# 🔥 TH (7) · 임계값 지향 ← 박사논문 철학 핵심, ★★★
# 🤖 AL (4) · AI 알고리즘 수용 ← Layer 1+2 · 논문 ④⑤⑥
# 💪 EF (4) · 자기 효능감 ← Bandura · 논문 ④⑦⑩⑪
# 🧠 MG (3) · 메타인지·전략 ← Layer 1 · 논문 ⑤⑥
# ⚡ MO (5) · 동기·몰입 ← Flow+ARCS+SDT+Grit+NPS
# 🎮 GA (3) · 게이미피케이션 반응 ← Layer 4 · 논문 ①②⑩
# 합계: 리커트 26
# ═════════════════════════════════════════════════════════════════
SURVEY_ITEMS = {
    # ── 🔥 TH · 임계값 지향 (7) ── ★★★ 박사논문 축
    "TH1": "나는 지금 내 실력보다 조금 어려운 문제를 푸는 것이 좋다",    # ZPD
    "TH2": "틀린 문제를 다시 풀면 실력이 한 단계 오를 것 같다",          # 재도전 임계
    "TH3": "도전적인 목표가 있으면 더 몰입해서 공부한다",                # Flow Challenge
    "TH4": "시간 압박 속에서도 집중해서 정답을 고를 수 있다",            # RT 효능
    "TH5": "레벨·단계가 올라가는 느낌이 있으면 계속하고 싶다",           # Mastery
    "TH6": "실력이 확 늘었을 때의 뿌듯함을 생생히 기억한다",             # Bandura 성공경험
    "TH7": "쉬운 문제만 반복하는 것보다 도전하다 틀리는 게 낫다",        # 성장 마인드셋
    # ── 🤖 AL · AI 알고리즘 수용 (4) ──
    "AL1": "내가 얼마나 빨리 푸는지 기록되는 것에 거부감이 없다",        # 논문 ④
    "AL2": "AI가 내 약점을 스스로 찾아서 알려주면 도움이 될 것 같다",     # 논문 ④⑥
    "AL3": "내 학습 기록이 쌓이면 내 실력 변화를 볼 수 있을 것 같다",     # 논문 ⑤
    "AL4": "AI가 다음 문제를 알아서 골라주는 방식을 신뢰한다",           # 논문 ④⑥⑨
    # ── 💪 EF · 자기 효능감 (4) ──
    "EF1": "나는 TOEIC 문법 문제를 대체로 잘 풀 수 있다",               # 문법 효능
    "EF2": "어려운 문법이라도 연습하면 이해할 수 있다",                  # 숙달 효능
    "EF3": "모르는 단어가 많아도 문장 의미를 추측할 수 있다",            # 독해 전략 효능
    "EF4": "시험에서 긴장되어도 실력을 발휘할 수 있다",                  # 심리생리 효능
    # ── 🧠 MG · 메타인지·전략 (3) ──
    "MG1": "틀린 문제는 반드시 다시 확인하고 넘어간다",                  # 망각곡선 임계
    "MG2": "문법·독해·어휘를 서로 연결해서 공부한다",                    # 크로스스킬
    "MG3": "문제를 풀 때 왜 틀렸는지 스스로 분석한다",                   # 메타인지
    # ── ⚡ MO · 동기·몰입 (5) ──
    "MO1": "영어 문법을 새로 배울 때 흥미를 느낀다",                     # 내재동기
    "MO2": "TOEIC 점수 목표를 꼭 달성하고 싶다",                        # 외재동기 (공변량)
    "MO3": "공부하다 시간 가는 줄 모를 때가 있다",                       # Flow 시간왜곡
    "MO4": "매일 조금씩이라도 꾸준히 공부하고 싶다",                     # Grit
    "MO5": "이 앱을 친구에게 추천하고 싶다",                            # NPS
    # ── 🎮 GA · 게이미피케이션 반응 (3) ──
    "GA1": "점수·포인트가 있으면 더 열심히 하게 된다",                   # Points
    "GA2": "캐릭터·스토리가 있으면 몰입이 잘 된다",                      # Narrative (TORI/HAE)
    "GA3": "다른 사람과 경쟁·비교하는 것이 동기부여가 된다",             # Leaderboard
}

# ── 📋 기초 변수 (사전만, 선택형) — 종단분석 공변량 ──
BASE_VARS = {
    "Q_LEVEL": "현재 예상 TOEIC 점수대는?",
    "Q_YEARS": "영어 학습 기간은?",
}
Q_LEVEL_CHOICES = ["400점 이하", "400~600점", "600~800점", "800점 이상", "잘 모르겠어요"]
Q_YEARS_CHOICES = ["1년 미만", "1~3년", "3~5년", "5년 이상"]

# ── 🖊 사전 추가 주관식 (선택 입력) — 논문 ⑪ 자기문화기술지 pre-post 쌍 ──
SURVEY_PRE_EXTRA = {
    "G0_open": "지금 TOEIC 공부에서 가장 막히는 부분이나 어려운 점을 한 문장으로 적어주세요. (선택 입력)",
}

# ── 📝 사후 전용 (G) ──
SURVEY_POST_ONLY = {
    "G1": "SnapQ가 영어 실력 향상에 도움이 되었다",
    "G2_choice": "가장 도움이 된 모드는?",
    "G3": "난이도가 자동으로 바뀌는 것이 도움이 되었다",        # 논문 ⑦
    "G4": "NPC(토리/해이) 메시지가 동기부여에 도움이 되었다",   # 논문 ⑧
    "G5_open": "한 줄 소감을 자유롭게 적어주세요",               # 질적 데이터
}

LIKERT_OPTIONS = ["전혀 아니다", "아니다", "보통이다", "그렇다", "매우 그렇다"]
G2_CHOICES = ["⚡ 화력전 (문법 5문제)", "📡 암호해독 (독해 3문제)", "💀 포로사령부 (오답 복습)"]

# ── 카테고리 prefix → 한글 이름 매핑 (명시적 순서 = G0 먼저 매치) ──
CATEGORY_NAMES = [
    ("Q_",  "📋 기초 정보"),
    ("TH",  "🔥 도전과 성장"),
    ("AL",  "🤖 AI 학습"),
    ("EF",  "💪 자기 효능감"),
    ("MG",  "🧠 학습 전략"),
    ("MO",  "⚡ 학습 동기"),
    ("GA",  "🎮 게임 요소"),
    ("G0",  "🖊 자유 응답"),
    ("G5",  "🖊 자유 응답"),
    ("G2",  "📝 사용 경험"),
    ("G1",  "📝 사용 경험"),
    ("G3",  "📝 사용 경험"),
    ("G4",  "📝 사용 경험"),
]

def _get_category_name(key: str) -> str:
    """설문 key의 prefix에 따라 카테고리 이름 반환"""
    for prefix, name in CATEGORY_NAMES:
        if key.startswith(prefix):
            return name
    return "설문"'''

if old_1 in content:
    content = content.replace(old_1, new_1)
    print("✅ 패치 ①: SURVEY_ITEMS 26문항 + 기초변수 + G0 + 카테고리 매핑")
    patches += 1
else:
    print("⚠️  패치 ①: 원본 못 찾음")

# ═══════════════════════════════════════════════════════════
# 패치 ② : _render_survey items 구성 로직
# ═══════════════════════════════════════════════════════════
old_2 = """    # 문항 리스트 구성
    items = list(SURVEY_ITEMS.items())
    if survey_type == "post":
        items += list(SURVEY_POST_ONLY.items())
    total = len(items)
    qi = st.session_state.survey_qi"""

new_2 = """    # 문항 리스트 구성 — v3 재설계
    if survey_type == "pre":
        # 사전: 기초변수 2개 → 리커트 26 → 사전 주관식 1 = 29문항
        items = list(BASE_VARS.items()) + list(SURVEY_ITEMS.items()) + list(SURVEY_PRE_EXTRA.items())
    else:
        # 사후: 리커트 26 → 사후 G 5개 = 31문항
        items = list(SURVEY_ITEMS.items()) + list(SURVEY_POST_ONLY.items())
    total = len(items)
    qi = st.session_state.survey_qi"""

if old_2 in content:
    content = content.replace(old_2, new_2)
    print("✅ 패치 ②: 사전 items 구성 (기초변수 + 리커트26 + G0)")
    patches += 1
else:
    print("⚠️  패치 ②: 원본 못 찾음")

# ═══════════════════════════════════════════════════════════
# 패치 ③ : cat_letter 로직 → CATEGORY_NAMES 매핑
# ═══════════════════════════════════════════════════════════
old_3 = """    key, text = items[qi]
    cat_letter = key[0]
    cat_names = {"A": "영어 학습 동기", "B": "게이미피케이션 인식",
                 "C": "AI 학습 환경", "D": "자기 효능감",
                 "E": "학습 전략", "F": "몰입·지속", "G": "사용 경험"}
    cat_name = cat_names.get(cat_letter, "설문")"""

new_3 = """    key, text = items[qi]
    cat_name = _get_category_name(key)"""

if old_3 in content:
    content = content.replace(old_3, new_3)
    print("✅ 패치 ③: cat_letter → CATEGORY_NAMES 매핑")
    patches += 1
else:
    print("⚠️  패치 ③: 원본 못 찾음")

# ═══════════════════════════════════════════════════════════
# 패치 ④ : 응답 UI 분기 — Q_LEVEL, Q_YEARS, G0_open 추가
# ═══════════════════════════════════════════════════════════
old_4 = '''    # 응답 UI
    if key == "G2_choice":
        # 선택형 (가장 도움이 된 모드)
        for ci, choice in enumerate(G2_CHOICES):
            if st.button(choice, key=f"sv_{qi}_{ci}", use_container_width=True):
                st.session_state.survey_responses[key] = choice
                st.session_state.survey_qi = qi + 1
                st.rerun()

    elif key == "G5_open":
        # 주관식
        answer = st.text_area("", placeholder="자유롭게 적어주세요 (선택사항)",
                              key=f"sv_open_{qi}", height=100)
        if st.button("✅ 제출하기", key=f"sv_submit_{qi}", use_container_width=True):
            st.session_state.survey_responses[key] = answer.strip() if answer else ""
            st.session_state.survey_qi = qi + 1
            st.rerun()

    else:
        # 5점 리커트
        cols = st.columns(5)
        for li, label in enumerate(LIKERT_OPTIONS):
            score = li + 1  # 1~5
            with cols[li]:
                if st.button(f"{score}\\n{label}", key=f"sv_{qi}_{li}",
                             use_container_width=True):
                    st.session_state.survey_responses[key] = score
                    st.session_state.survey_qi = qi + 1
                    st.rerun()'''

new_4 = '''    # 응답 UI — v3 재설계 (기초변수 Q_LEVEL, Q_YEARS + 주관식 G0/G5 통합)
    if key == "Q_LEVEL":
        # 선택형: TOEIC 점수대
        for ci, choice in enumerate(Q_LEVEL_CHOICES):
            if st.button(choice, key=f"sv_{qi}_{ci}", use_container_width=True):
                st.session_state.survey_responses[key] = choice
                st.session_state.survey_qi = qi + 1
                st.rerun()

    elif key == "Q_YEARS":
        # 선택형: 영어 학습 기간
        for ci, choice in enumerate(Q_YEARS_CHOICES):
            if st.button(choice, key=f"sv_{qi}_{ci}", use_container_width=True):
                st.session_state.survey_responses[key] = choice
                st.session_state.survey_qi = qi + 1
                st.rerun()

    elif key == "G2_choice":
        # 선택형: 가장 도움이 된 모드
        for ci, choice in enumerate(G2_CHOICES):
            if st.button(choice, key=f"sv_{qi}_{ci}", use_container_width=True):
                st.session_state.survey_responses[key] = choice
                st.session_state.survey_qi = qi + 1
                st.rerun()

    elif key.endswith("_open"):
        # 주관식 (G0_open 사전 · G5_open 사후 모두 해당)
        placeholder_text = "자유롭게 적어주세요 (선택 입력 — 생략 가능)"
        answer = st.text_area("", placeholder=placeholder_text,
                              key=f"sv_open_{qi}", height=100)
        btn_label = "⏭ 건너뛰기" if not answer.strip() else "✅ 제출하기"
        if st.button(btn_label, key=f"sv_submit_{qi}", use_container_width=True):
            st.session_state.survey_responses[key] = answer.strip() if answer else ""
            st.session_state.survey_qi = qi + 1
            st.rerun()

    else:
        # 5점 리커트
        cols = st.columns(5)
        for li, label in enumerate(LIKERT_OPTIONS):
            score = li + 1  # 1~5
            with cols[li]:
                if st.button(f"{score}\\n{label}", key=f"sv_{qi}_{li}",
                             use_container_width=True):
                    st.session_state.survey_responses[key] = score
                    st.session_state.survey_qi = qi + 1
                    st.rerun()'''

if old_4 in content:
    content = content.replace(old_4, new_4)
    print("✅ 패치 ④: 응답 UI 분기 (Q_LEVEL + Q_YEARS + 주관식 확장)")
    patches += 1
else:
    print("⚠️  패치 ④: 원본 못 찾음")

# ═══════════════════════════════════════════════════════════
# 저장
# ═══════════════════════════════════════════════════════════
print("")
if content == original:
    print("❌ 변경 내용 없음. 원본 유지.")
    sys.exit(1)

if original_crlf:
    content = content.replace("\n", "\r\n")

out_bytes = content.encode("utf-8")
if had_bom:
    out_bytes = b"\xef\xbb\xbf" + out_bytes

FILE.write_bytes(out_bytes)
print(f"✅ 저장 완료 ({patches}/4 패치 적용)")
print(f"📁 백업: {backup_path}")
print("")
print("🧪 다음 단계:")
print("   1. git add app/core/pretest_gate.py apply_patch_v3.py")
print('   2. git commit -m "feat: 설문 재설계 v3 — TH/AL/EF/MG/MO/GA 26문항 + 기초변수 + G0"')
print("   3. git push")
print("   4. 모바일 재테스트 (새 별명!)")
