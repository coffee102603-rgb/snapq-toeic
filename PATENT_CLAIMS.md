# PATENT_CLAIMS.md — 특허 청구항 ↔ 코드 매핑

> 이 문서는 SnapQ TOEIC 플랫폼의 특허 청구항이 코드의 어떤 파일, 어떤 함수에 구현되어 있는지를 매핑합니다.
> 특허 출원 및 심사 시 기술 구현의 증거 자료로 활용할 수 있습니다.

---

## 논문 A — 적응형 난이도 & DB 교집합 어휘 시스템

### 청구항 A-1: DB 교집합 어휘 자동 포획

**핵심 개념:** 학습자가 오답을 낸 문장에서, 플랫폼이 보유한 어휘 데이터베이스에 등록된 단어만 자동 추출하여 개인별 단어수용소에 저장하는 시스템.

| 항목 | 위치 |
|---|---|
| 핵심 함수 | `pages/03_POW_HQ.py` → `_prison_from_sentence()` (174번째 줄) |
| DB 매칭 | `pages/_word_family_db.py` → `find_words_in_sentence()` |
| 개별 저장 | `pages/03_POW_HQ.py` → `_add_to_prison()` (137번째 줄) |
| 데이터 출력 | `storage_data.json` → `word_prison[]` |

**동작 흐름:**
```
오답 발생 → 오답 문장 추출
  → find_words_in_sentence(sentence)로 DB 매칭
  → 매칭된 단어만 word_prison에 저장 (중복 제외)
  → source 필드로 포획 경로 식별
```

**모든 오답 경로가 이 함수를 통과:**
- 화력전 P5 브리핑 오답 (`02_Firepower.py`)
- 포로사령부 퍼즐 오답/건너뜀 (`03_POW_HQ.py`)
- 포로사령부 시험 오답 (`03_POW_HQ.py`)
- 콤보러시 오답 (`03_POW_HQ.py`)
- 암호해독 P7 오답 (`04_Decrypt_Op.py`)

### 청구항 A-2: ZPD 즉사 메커니즘

**핵심 개념:** 독해 전장에서 3문제 중 1개라도 오답이면 즉시 전투 종료(LOST)하는 시스템. 전통적인 부분 점수 방식과 달리, 학습자의 근접발달영역(ZPD) 경계를 실시간으로 탐지.

| 항목 | 위치 |
|---|---|
| 구현 위치 | `pages/04_Decrypt_Op.py` (BATTLE 페이즈 내 오답 판정 로직) |
| 로그 출력 | `storage_data.json` → `zpd_logs[]` |
| 로그 저장 | `pages/_storage.py` → `append_log("zpd_logs", ...)` |

**⚠️ 절대 제거 금지** — 논문 핵심 청구항이므로 이 메커니즘의 동작을 변경하면 안 됩니다.

### 청구항 A-3: 적응형 난이도 즉시 전환

**핵심 개념:** 가장 최근 1문제의 정답/오답 결과만으로 다음 문제의 난이도를 즉시 조정하는 시스템.

| 항목 | 위치 |
|---|---|
| 난이도 계산 | `pages/02_Firepower.py` → `_calc_adp_level()` (459번째 줄) |
| 문제 선택 | `pages/02_Firepower.py` → `pick5()` (479번째 줄) |
| 로그 기록 | `pages/_storage.py` → `save_rt_log()` (adp_level 필드) |

**난이도 전환 규칙:**
```
정답 → easy→normal→hard (한 단계 UP)
오답 → hard→normal→easy (한 단계 DOWN)
```

**난이도 적용 기준:**
- 1차: `word_count` 기반 (`diff` 필드: easy/normal/hard)
- 2차: 문법 카테고리 비율 조정 (hard 모드 → 가정법/도치 비율↑)

---

## 논문 B — 오답 타이밍 분류 & 크로스모듈 전이

### 청구항 B-1: X·Y·Z 스캐폴딩 효과 측정

**핵심 개념:** 독해 지문의 3문제를 X(직접)·Y(추론)·Z(심화) 단계로 설계하고, 각 단계별 정답률과 소요시간을 개별 측정하는 시스템.

| 항목 | 위치 |
|---|---|
| X·Y·Z 로그 저장 | `pages/04_Decrypt_Op.py` → `_save_recon_xyz_log()` (164번째 줄) |
| 데이터 출력 | `storage_data.json` → `recon_xyz_logs[]` |
| 지문 구조 | `data/passages_*.json` → `steps[0]`(X), `steps[1]`(Y), `steps[2]`(Z) |

**로그 필드:**
- `x_correct`, `y_correct`, `z_correct` — 단계별 정답여부
- `x_sec`, `y_sec`, `z_sec` — 단계별 소요시간(초)
- `total_score` — 총 정답 수

### 청구항 B-2: 크로스모듈 어휘 전이 자동 감지

**핵심 개념:** P7(독해)에서 학습한 어휘가 P5(문법) 전장의 오답 어휘와 겹치는 정도를 자동 감지하여, 모듈 간 학습 전이 효과를 측정하는 시스템.

| 항목 | 위치 |
|---|---|
| 크로스 로그 저장 | `pages/04_Decrypt_Op.py` → `_save_cross_log()` (128번째 줄) |
| 공통 저장 | `pages/_storage.py` → `save_cross_log()` |
| 데이터 출력 | `storage_data.json` → `cross_logs[]` |

**동작 흐름:**
```
P7 지문 완료 → P7 지문 어휘 추출
  → P5 오답 문제(saved_questions) 어휘 추출
  → 교집합 계산 (4글자 이상 영단어)
  → match_count, matched_ids 저장
```

### 청구항 B-3: 오답 타이밍 3분류 시스템

**핵심 개념:** 학습자가 오답을 냈을 때, 남은 시간 비율에 따라 오답 유형을 자동 분류하는 시스템.

| 항목 | 위치 |
|---|---|
| 분류 함수 | `pages/02_Firepower.py` → `_classify_error_timing()` (89번째 줄) |
| 로그 기록 | `pages/_storage.py` → `save_rt_log()` (error_timing_type 필드) |

**분류 기준:**
```
잔여시간/총시간 > 2/3  →  fast_wrong   (충동형: 문제를 읽지 않고 답함)
1/3 ~ 2/3              →  mid_wrong    (표준형: 읽었으나 이해 부족)
< 1/3                  →  slow_wrong   (인지과부하형: 오래 고민했으나 실패)
```

**`slow_wrong`만 강제 저장 대상** — 인지과부하형 오답은 학습자가 실제로 노력했으나 실패한 경우이므로, 이후 집중 복습 대상으로 자동 분류됩니다.

---

## 논문 C — 망각곡선 추적

### 청구항 C-1: 개인별 망각곡선 자동 추적

**핵심 개념:** 학습자가 처음 틀린 문제를 나중에 다시 만났을 때의 정답여부와 간격(일)을 자동 기록하여 개인별 망각곡선을 구축하는 시스템.

| 항목 | 위치 |
|---|---|
| 로그 출력 | `storage_data.json` → `forget_logs[]` |
| 로그 저장 | `pages/_storage.py` → `append_log("forget_logs", ...)` |
| 복습 UI | `pages/03_POW_HQ.py` → WORD_PRISON (플립카드 심문) |

**추적 필드:**
- `first_wrong_date` — 최초 오답 날짜
- `revisit_date` — 재방문 날짜
- `interval_days` — 간격(일)
- `re_wrong` — 재방문 시 또 틀렸는지
- `revisit_count` — 총 재방문 횟수
- `finally_correct` — 최종 정답 달성 여부
- `days_to_overcome` — 극복까지 소요일

---

## 논문 D — 반응속도 프록시 분석

### 청구항 D-1: 타이머 기반 반응속도 프록시

**핵심 개념:** 별도의 하드웨어 없이, 문제 풀이 제한시간(타이머)과 남은 시간의 차이를 반응속도의 대리 변수(proxy)로 활용하는 시스템.

| 항목 | 위치 |
|---|---|
| 반응속도 계산 | `pages/_storage.py` → `save_rt_log()` (rt_proxy 필드) |
| 타이머 설정 | `config/settings.py` → `TIMER_SETTINGS` |
| NPC 피드백 | `main_hub.py` → `_calc_stats()` (198번째 줄) |

**계산:**
```
rt_proxy = timer_setting - seconds_remaining
```

### 청구항 D-2: NPC 개인화 피드백

**핵심 개념:** 반응속도 로그와 정답률을 분석하여 NPC 캐릭터가 학습자별 맞춤 피드백을 제공하는 시스템.

| 항목 | 위치 |
|---|---|
| 스탯 계산 | `main_hub.py` → `_calc_stats()` (198번째 줄) |
| 피드백 생성 | `main_hub.py` → `_npc_p5_tx`, `_npc_p7_tx`, `_npc_pow_tx` 변수 |
| 피드백 분기 | 정답률 80%↑ / 60~79% / 60%↓ / 첫접속 |

---

## 통합 시스템 — 플랫폼 아키텍처 청구항

### 청구항 S-1: 게이미피케이션 기반 통합 학습 플랫폼

**핵심 개념:** 문법(P5), 독해(P7), 오답 복습을 군사 테마 게임으로 통합하고, 모든 학습 데이터를 자동 수집하는 플랫폼.

| 전장 | 파일 | 역할 |
|---|---|---|
| 화력전 | `02_Firepower.py` | P5 문법·어휘 서바이벌 |
| 암호해독 | `04_Decrypt_Op.py` | P7 독해 전투 |
| 포로사령부 | `03_POW_HQ.py` | 오답 관리·복습 허브 |
| 작전사령부 | `main_hub.py` | 메인 허브·NPC 피드백 |

### 청구항 S-2: 이중 저장 시스템

**핵심 개념:** 로컬 JSON 파일과 Google Sheets에 학습 데이터를 이중 저장하여 데이터 유실을 방지하는 시스템.

| 항목 | 위치 |
|---|---|
| 로컬 저장 | `pages/_storage.py` → `save()` |
| Sheets 저장 | `pages/_storage.py` → `save_to_sheets()` |
| 스키마 정의 | `pages/_storage.py` → `_SHEETS_HEADERS` |

### 청구항 S-3: 월별 코호트 관리 시스템

**핵심 개념:** 월별 접속 코드와 자동 잠금 시스템으로 연구 코호트를 관리하는 시스템.

| 항목 | 위치 |
|---|---|
| 월별 코드 | `app/core/access_guard.py` → `MONTHLY_CODES` |
| 잠금 설정 | `app/core/access_guard.py` → `LOCK_DAY = 28` |
| 검사 게이트 | `app/core/pretest_gate.py` → 1차/2차/3차 검사 일정 |
| 출석 기록 | `app/core/attendance_engine.py` → `mark_attendance_once()` |

---

## 특허 증거 요약표

| 기술 | 파일 | 함수/변수 | 줄 번호 |
|---|---|---|---|
| DB 교집합 포획 | `03_POW_HQ.py` | `_prison_from_sentence()` | 174 |
| ZPD 즉사 | `04_Decrypt_Op.py` | BATTLE 페이즈 오답 판정 | — |
| 적응형 난이도 | `02_Firepower.py` | `_calc_adp_level()` | 459 |
| 문제 선택 | `02_Firepower.py` | `pick5()` | 479 |
| 오답 타이밍 3분류 | `02_Firepower.py` | `_classify_error_timing()` | 89 |
| X·Y·Z 로그 | `04_Decrypt_Op.py` | `_save_recon_xyz_log()` | 164 |
| 크로스모듈 전이 | `04_Decrypt_Op.py` | `_save_cross_log()` | 128 |
| 반응속도 프록시 | `_storage.py` | `save_rt_log()` | — |
| NPC 피드백 | `main_hub.py` | `_calc_stats()` | 198 |
| 망각곡선 추적 | `_storage.py` | `append_log("forget_logs")` | — |
| 월별 코호트 | `access_guard.py` | `MONTHLY_CODES` | — |
| 검사 게이트 | `pretest_gate.py` | `STAGE_1/2/3_DAYS` | — |
| 이중 저장 | `_storage.py` | `save_to_sheets()` | — |
