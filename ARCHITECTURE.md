# ARCHITECTURE.md — SnapQ TOEIC V3 시스템 아키텍처

> 이 문서는 AI 에이전트와 개발자가 시스템의 전체 구조, 데이터 흐름, 핵심 알고리즘을 빠르게 파악하기 위한 설계 문서입니다.

---

## 1. 시스템 구성도

```
┌─────────────────────────────────────────────────────────┐
│                  Streamlit Cloud                        │
│                                                         │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ main_hub │→ │ 02_Firepower │→ │    03_POW_HQ     │  │
│  │  (허브)   │→ │  (P5 화력전)  │→ │  (포로사령부)     │  │
│  │          │→ │              │→ │                  │  │
│  │          │→ │ 04_Decrypt   │→ │                  │  │
│  │          │→ │  (P7 암호해독) │→ │                  │  │
│  └────┬─────┘  └──────┬───────┘  └────────┬─────────┘  │
│       │               │                   │             │
│  ┌────▼───────────────▼───────────────────▼──────────┐  │
│  │                 _storage.py                        │  │
│  │          (공통 저장소 + Google Sheets 연동)          │  │
│  └────┬───────────────────────────────────────┬──────┘  │
│       │                                       │         │
│  ┌────▼────────┐                    ┌─────────▼──────┐  │
│  │storage_data │                    │ Google Sheets  │  │
│  │   .json     │                    │ (영구 보존)     │  │
│  └─────────────┘                    └────────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │              data/ (JSON 콘텐츠)                  │    │
│  │  firepower/*.json │ passages_*.json │ 기타        │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │              app/core/ (공통 모듈)                 │    │
│  │  access_guard │ pretest_gate │ attendance_engine │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │           _word_family_db.py (어휘 DB)            │    │
│  │     lookup() / find_words_in_sentence()          │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 페이지별 Phase 흐름

### 2-1. main_hub.py (작전사령부)

```
LOGIN → LOBBY
  │
  ├─ require_access()     : 로그인 게이트 (이름 + 전화 뒷4자리 + 월별코드)
  ├─ require_pretest_gate(): 사전검사 게이트 (1~10일/11~24일/25~28일)
  ├─ _calc_stats()        : rt_logs 분석 → 정답률, 무기고 대기 수 계산
  ├─ NPC 오버레이 메시지   : 정답률 기반 개인화 피드백 (80%↑ / 60~79% / 60%↓ / 첫접속)
  └─ 전장 카드 3종         : 화력전 / 암호해독 / 포로사령부
```

### 2-2. 02_Firepower.py (화력전 — P5)

```
LOBBY → BATTLE → BRIEFING → RESULT
  │        │         │
  │        │         └─ 오답 문장 → _prison_from_sentence() → word_prison 저장
  │        │            정답 문장 → 선택적 저장 (📌 정보 포획)
  │        │
  │        ├─ pick5()              : 5문제 선택 (적응형 난이도 적용)
  │        ├─ _calc_adp_level()    : 1문제 결과 → 즉시 난이도 전환
  │        ├─ _classify_error_timing(): 오답 타이밍 3분류 (fast/mid/slow)
  │        └─ rt_logs 저장         : 반응속도 프록시, 정답여부, 문법유형, 난이도
  │
  └─ GAME OVER: 5문제 중 오답 발생 시 (HP 소진), 브리핑은 1문제라도 맞혔으면 진입 가능
```

### 2-3. 04_Decrypt_Op.py (암호해독 — P7)

```
LOBBY → BATTLE → BRIEFING → RESULT
  │        │         │
  │        │         ├─ 오답 문장 → 브리핑 진입 시 자동 저장 (source: "P7 자동")
  │        │         ├─ 정답 문장 → 선택 저장 ("📌 정보 포획!" 버튼)
  │        │         └─ _save_cross_log() : P7↔P5 크로스스킬 전이 감지
  │        │
  │        ├─ pick_passage()       : 난이도별 지문 선택
  │        ├─ _load_passages()     : 4개 JSON 동적 로딩 (signal→cipher→intercept→blackout)
  │        └─ ZPD 즉사 메커니즘    : 3문제 중 1문제라도 틀리면 즉시 LOST ★★★
  │
  └─ LOST에서도 브리핑 진입 가능 (1문제라도 시도했으면)
```

### 2-4. 03_POW_HQ.py (포로사령부)

```
LOBBY → PUZZLE_BATTLE | EXAM | WORD_PRISON | VOCA_EXAM | COMBO_RUSH
  │
  ├─ PUZZLE_BATTLE: 문장 퍼즐 (적응형 blank 레벨 1~3)
  │    └─ 오답/건너뜀 → _prison_from_sentence() → word_prison 저장
  │
  ├─ EXAM: P5 오답 문제 재시험
  │    └─ 오답 → _prison_from_sentence() → word_prison 저장
  │
  ├─ WORD_PRISON: 단어수용소 플립카드 심문
  │    └─ correct_streak 추적 → 망각곡선 데이터 (forget_logs)
  │
  ├─ VOCA_EXAM: 어휘 시험
  │
  └─ COMBO_RUSH: P7 지문 기반 문장 연속 퀴즈
       └─ 오답 → _prison_from_sentence() → word_prison 저장
```

---

## 3. 데이터 흐름

### 3-1. 콘텐츠 입력 (정적 데이터)

```
data/firepower/*.json ──→ 02_Firepower.py (문법/어형/연결어/어휘 문제)
data/passages_*.json  ──→ 04_Decrypt_Op.py (독해 지문 + 3문제)
data/diagnosis_sets.json → app/core/pretest_gate.py (진단 검사)
_word_family_db.py    ──→ 모든 페이지 (어휘 조회, DB 교집합)
```

### 3-2. 학습 데이터 출력 (동적 데이터)

```
storage_data.json
├── saved_questions[]    : 화력전 P5 오답 문제 저장
├── saved_expressions[]  : 정보 포획 표현 저장
├── word_prison[]        : 단어수용소 포로 목록
├── rt_logs[]            : 반응속도 로그 (논문D)
├── p5_logs[]            : P5 세션 결과 로그
├── zpd_logs[]           : ZPD 즉사 로그 (논문A)
├── cross_logs[]         : P7→P5 크로스스킬 전이 로그 (논문B)
├── recon_xyz_logs[]     : X·Y·Z 단계별 정답/시간 로그
├── recon_logs[]         : 정찰 임무 로그
└── forget_logs[]        : 망각곡선 로그 (논문C)
```

### 3-3. Google Sheets 연동 (영구 보존)

`_storage.py`의 `save_to_sheets()` 함수가 모든 로그를 Google Sheets에 이중 저장합니다. Streamlit Cloud 재시작 시에도 연구 데이터가 유실되지 않습니다. 각 로그 유형별로 별도 시트가 자동 생성됩니다.

### 3-4. 출석 데이터

```
data/cohorts/YYYY-MM/
├── attendance.json      : 일별 출석 기록
└── activity.json        : 활동 기록 (전장, 정답률, 소요시간)
```

---

## 4. 핵심 알고리즘

### 4-1. 오답 타이밍 3분류 (논문B 핵심)

**파일:** `02_Firepower.py` → `_classify_error_timing()`

```
타이머 잔여시간 비율 = seconds_remaining / timer_setting

비율 > 2/3  →  fast_wrong   (충동형 오답: 문제를 제대로 읽지 않음)
1/3 ~ 2/3   →  mid_wrong    (표준형 오답: 읽었으나 틀림)
비율 < 1/3  →  slow_wrong   (인지과부하형 오답: 고민했으나 시간 부족)
```

`slow_wrong`만 강제 저장 대상 (논문B 청구항3).

### 4-2. 적응형 난이도 조절 (논문A 핵심)

**파일:** `02_Firepower.py` → `_calc_adp_level()`

```
가장 최근 1문제 결과만 반영:
  정답 → 한 단계 UP  (easy → normal → hard)
  오답 → 한 단계 DOWN (hard → normal → easy)

난이도는 word_count 기준:
  easy:   word_count ≤ 15
  normal: word_count 16~19
  hard:   word_count 20~23

+ hard 모드에서는 고급 문법 카테고리 비율 증가 (가정법, 도치, 분사구문)
+ easy 모드에서는 기초 문법 카테고리 비율 증가 (수일치, 접속사, 관계대명사)
```

### 4-3. ZPD 즉사 메커니즘 (논문A 청구항2)

**파일:** `04_Decrypt_Op.py`

독해 3문제 중 1개라도 틀리면 즉시 LOST 처리. 전통적인 3문제 중 2문제 이상 정답 방식이 아닌, 근접발달영역(ZPD) 경계를 탐지하는 방식. **논문 청구항 핵심이므로 절대 제거 금지.**

### 4-4. DB 교집합 어휘 포획 (논문A 청구항1)

**파일:** `03_POW_HQ.py` → `_prison_from_sentence()`

```
1. 오답 문장에서 영단어 추출
2. _word_family_db.py의 find_words_in_sentence()로 DB 매칭
3. DB에 등록된 단어만 word_prison에 저장
4. 모든 오답 경로(퍼즐 오답, 시험 오답, 콤보러시 오답)가 이 함수를 통과
```

### 4-5. 크로스모듈 어휘 전이 (논문B)

**파일:** `04_Decrypt_Op.py` → `_save_cross_log()`

```
1. P7 독해 지문의 어휘 추출
2. P5 화력전 오답 문제의 어휘와 교집합 계산
3. 겹치는 어휘 수와 ID를 cross_logs에 저장
→ P7 학습이 P5 성적에 미치는 전이 효과 측정
```

### 4-6. 문장 퍼즐 적응형 난이도 (논문A)

**파일:** `03_POW_HQ.py`

```
puzzle_blank_level 1~3:
  레벨 1: 명사만 빈칸
  레벨 2: 명사 + 동사 빈칸
  레벨 3: 명사 + 동사 + 부사 빈칸

연속 정답(puzzle_streak)에 따라 레벨 상승
```

---

## 5. 인증 시스템

**파일:** `app/core/access_guard.py`

```
로그인 3단계:
1. 이름 입력 → nickname 생성
2. 전화번호 뒷 4자리 확인
3. 월별 코드 입력 (MONTHLY_CODES 딕셔너리에서 관리)

월말 잠금: LOCK_DAY(28일) 이후 접속 차단
```

**iOS Safari 세션 가드:**

각 페이지에 `?nick=XXX&ag=1` 쿼리 파라미터로 세션 자동 복원 기능이 있습니다. WebSocket이 끊겨도 세션이 유지됩니다.

---

## 6. 검사 시스템

**파일:** `app/core/pretest_gate.py`

```
매월 3회 자동 검사:
  1차 (1~10일):  사전검사
  2차 (11~24일): 중간검사
  3차 (25~28일): 사후검사

검사 형식: TOEIC P5 형식 10문제, 3분 제한
```

---

## 7. NPC 피드백 시스템

**파일:** `main_hub.py`

메인 허브의 전장 카드에 마우스 호버/터치 시 NPC 캐릭터(해/토리)가 개인화 메시지를 표시합니다.

```
정답률 기반 분기:
  80% 이상  → 칭찬 + 도전 유도
  60~79%   → 격려 + 약점 안내
  60% 미만  → 위로 + 기초 권유
  첫 접속   → 환영 + 튜토리얼
```

---

## 8. 주의사항 (AI 에이전트 필독)

| 항목 | 설명 |
|---|---|
| HTML 문자열 | 반드시 `+` 연결 사용. f-string 멀티라인 시 `</div>`가 리터럴로 렌더링됨 |
| `answer` 필드 | GRM/FORM/LINK는 `"a"` 필드명 사용. `"answer"` 경고는 false positive |
| Streamlit 버전 | 1.44.0 이상 사용 금지 (MPA 방식 변경으로 navigation 오류) |
| `st.switch_page()` | 경로는 `pages/02_Firepower.py` 형식 유지 |
| NPC 메시지 변수 | `_npc_p5_tx` 등은 `_calc_stats()` 이후에 정의됨 (순서 주의) |
| JS 주입 | `components.html(height=0)`으로 레이아웃 영향 없이 주입 |
| JS 타이밍 | `setTimeout` 120ms/450ms 간격 사용 |
