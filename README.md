# SnapQ TOEIC V3 — 게이미피케이션 기반 TOEIC 학습 플랫폼

> **개발자:** 최정은 (대구교육대학교 AI교육학과 박사과정)  
> **목적:** 학술 연구용 (6개월 이상 장기 사용 설계)  
> **특허:** 출원 예정  
> **배포:** [Streamlit Cloud](https://snapq-toeic.streamlit.app)

---

## 프로젝트 개요

SnapQ TOEIC은 25년 영어 강의 노하우를 바탕으로 설계된 **모바일 퍼스트 TOEIC 학습 플랫폼**입니다. 군사/심문 테마의 게이미피케이션 요소를 활용하며, 모든 학습 데이터를 연구 논문용으로 자동 수집합니다.

### 핵심 독창 기술

- **오답 타이밍 3분류 시스템** — 응답 속도에 따라 충동형/표준형/인지과부하형 오답을 자동 분류
- **ZPD 즉사 메커니즘** — 독해 3문제 중 1개라도 틀리면 즉시 LOST (근접발달영역 경계 탐지)
- **DB 교집합 어휘 포획** — 오답 문장에서 플랫폼 DB에 등록된 단어만 추출하여 저장
- **적응형 난이도 조절** — 1문제 결과에 따라 즉시 난이도 전환 (easy ↔ normal ↔ hard)
- **크로스모듈 어휘 전이 감지** — P7(독해)과 P5(문법) 간 공통 어휘 자동 탐지 및 로깅

---

## 기술 스택

| 구성 | 기술 |
|---|---|
| 프론트엔드 | Streamlit (< 1.44.0), HTML/CSS/JS 인라인 |
| 백엔드 | Python 3 |
| 데이터 저장 | JSON 파일 (storage_data.json), Google Sheets (논문 데이터 영구 보존) |
| AI 번역 | Anthropic Claude API (문장 한국어 번역) |
| 배포 | Streamlit Cloud (git push 자동 배포) |
| 버전관리 | Git / GitHub |

---

## 디렉토리 구조

```
snapq-toeic/
│
├── main_hub.py                  # 메인 허브 (로그인·스탯·NPC 피드백·전장 선택)
│
├── pages/
│   ├── 01_Admin.py              # 관리자 페이지
│   ├── 02_Firepower.py          # 화력전 — P5 문법·어휘 5문제 서바이벌
│   ├── 03_POW_HQ.py             # 포로사령부 — 오답 관리 (학습·시험·수용소)
│   ├── 04_Decrypt_Op.py         # 암호해독 — P7 독해 3문제 전투
│   ├── 99_Test.py               # 테스트 페이지
│   ├── _storage.py              # 공통 저장소 모듈
│   ├── _word_family_db.py       # 플랫폼 전용 어휘 DB (5,987줄)
│   └── _responsive_css.py       # 공유 반응형 CSS
│
├── app/core/
│   ├── access_guard.py          # 로그인 게이트 (이름+전화+월별코드)
│   ├── pretest_gate.py          # 사전/중간/사후 검사 게이트
│   ├── battle_state.py          # 학생 프로필 로드
│   └── attendance_engine.py     # 출석 자동 기록
│
├── config/
│   └── settings.py              # 전역 설정 (타이머, HP, 점수)
│
├── data/
│   ├── firepower/               # P5 문제 데이터 (32개 JSON, 총 3,969문제)
│   │   ├── firepower_grammar_batch1~8.json   # 문법 1,000문제
│   │   ├── firepower_form_batch1~8.json      # 어형 1,000문제
│   │   ├── firepower_link_batch1~8.json      # 연결어 969문제
│   │   └── firepower_vocab_batch1~8.json     # 어휘 1,000문제
│   │
│   ├── passages_signal.json     # P7 독해 지문 — SIGNAL (쉬움, 40편)
│   ├── passages_cipher.json     # P7 독해 지문 — CIPHER (보통, 40편)
│   ├── passages_intercept.json  # P7 독해 지문 — INTERCEPT (어려움, 40편)
│   ├── passages_blackout.json   # P7 독해 지문 — BLACKOUT (최상, 40편)
│   ├── passages_recon.json      # P7 독해 지문 — RECON (정찰, 100편)
│   │
│   ├── diagnosis_sets.json      # 진단 검사 세트 (day1/day10/day20)
│   ├── armory/                  # 무기고 데이터
│   ├── cohorts/                 # 월별 출석·활동 데이터
│   └── stats/                   # 통계 데이터
│
├── assets/                      # 캐릭터 이미지 (해·토리)
├── styles/                      # 전역 CSS 파일
├── storage_data.json            # 메인 저장소 (서버 재시작에도 유지)
├── requirements.txt             # 의존성 (Streamlit < 1.44.0 필수)
└── render.yaml                  # Render 배포 설정
```

---

## 페이지 흐름

```
로그인(main_hub.py)
  └─→ LOBBY (NPC 피드백 + 전장 선택)
        ├─→ 화력전 (02_Firepower.py)
        │     LOBBY → BATTLE → BRIEFING → RESULT
        │
        ├─→ 암호해독 (04_Decrypt_Op.py)
        │     LOBBY → BATTLE → BRIEFING → RESULT
        │
        └─→ 포로사령부 (03_POW_HQ.py)
              LOBBY → PUZZLE_BATTLE | EXAM | WORD_PRISON | VOCA_EXAM
```

---

## 배포 방법

```bash
git add .
git commit -m "설명"
git push origin main
# → Streamlit Cloud 자동 배포
```

**⚠️ 중요:** `storage_data.json`은 Streamlit Cloud에서 앱 재시작 시에도 유지됩니다.

---

## 관련 문서

- [ARCHITECTURE.md](ARCHITECTURE.md) — 시스템 설계 및 데이터 흐름
- [DATA_SCHEMA.md](DATA_SCHEMA.md) — 모든 JSON 데이터 스키마 명세
- [PATENT_CLAIMS.md](PATENT_CLAIMS.md) — 특허 청구항과 코드 매핑

---

## AI 에이전트 가이드

이 프로젝트를 수정할 때 반드시 지켜야 할 규칙:

1. **HTML은 문자열 연결(`+`)로 처리** — f-string 멀티라인은 `</div>`가 리터럴 텍스트로 렌더링됨
2. **`answer` 필드 경고는 false positive** — GRM/FORM/LINK는 `"a"` 필드명을 사용하며, 플랫폼이 둘 다 처리함
3. **ZPD 즉사 메커니즘 유지 필수** — 논문 청구항 핵심이므로 절대 제거하지 말 것
4. **`_prison_from_sentence()` 우회 금지** — 모든 오답 저장 경로는 반드시 이 함수를 통과해야 함
5. **Streamlit 1.44.0 이상 사용 금지** — MPA 방식 변경으로 navigation 오류 발생
