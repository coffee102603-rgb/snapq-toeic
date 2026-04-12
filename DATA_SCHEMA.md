# DATA_SCHEMA.md — SnapQ TOEIC V3 데이터 스키마 명세

> 이 문서는 플랫폼에서 사용하는 모든 JSON 데이터의 스키마를 정의합니다.  
> AI 에이전트가 새 문제를 생성하거나 데이터를 분석할 때 이 문서를 참조하세요.

---

## 1. P5 화력전 문제 (data/firepower/)

### 파일 구조

| 파일 패턴 | 카테고리 | 수량 |
|---|---|---|
| `firepower_grammar_batch1~8.json` | GRM (문법) | 1,000문제 |
| `firepower_form_batch1~8.json` | FORM (어형) | 1,000문제 |
| `firepower_link_batch1~8.json` | LINK (연결어) | 969문제 |
| `firepower_vocab_batch1~8.json` | VOCAB (어휘) | 1,000문제 |

각 파일은 JSON 배열이며, 배치당 약 125문제입니다.

### 문제 스키마

```json
{
  "id":              "GRM_001",              // 고유 ID (GRM_/FORM_/LINK_/VOCAB_ + 3자리)
  "category":        "GRAMMAR",              // 대분류: GRAMMAR | FORM | LINK | VOCAB
  "cat":             "수동태",               // 소분류 (한국어 문법 카테고리)
  "word_count":      8,                      // 문장 단어 수 (난이도 기준)
  "diff":            "easy",                 // 난이도: easy | normal | hard
  "sentence":        "The report _______ by the board.", // 문제 문장 (빈칸 포함)
  "choices":         ["(A) was reviewed", ...], // 4지선다
  "answer":          0,                      // 정답 인덱스 (0-based)
  "answer_word":     "was reviewed",         // 정답 단어/구
  "explanation":     "주어 + 수동 + 과거...", // 해설 (한국어)
  "explanation_kr":  "보고서가 직접 검토해?!...", // 해설 (구어체 한국어, 티칭 톤)
  "kr":              "연례 보고서가 이사회에 의해...", // 문장 한국어 번역
  "expressions": [                           // 학습 표현 목록
    {
      "expr":    "was reviewed",
      "meaning": "검토되었다",
      "pos":     "verb phrase"
    }
  ]
}
```

### 난이도 분포 기준

| 난이도 | word_count 기준 | 비율 |
|---|---|---|
| easy | ≤ 15 | ~40% |
| normal | 16~19 | ~40% |
| hard | 20~23 | ~20% |

### VOCAB cat 분류 기준 (엄격 적용)

| cat | 비율 | 설명 |
|---|---|---|
| 문맥어휘 | ~77% | 문맥에서 적절한 어휘 선택 |
| 콜로케이션 | ~15% | 함께 자주 쓰이는 단어 조합 |
| 혼동어휘 | ~7% | 형태가 유사한 어휘 구별 |

**주의:** VOCAB에는 동의어(synonym) 문제를 포함하지 않습니다.

### GRM cat 소분류 (문법 카테고리)

수일치, 수동태, 수동태/수일치, 시제, 접속사, 관계대명사, 전치사, 가정법, 가정법/당위, 도치, 분사구문, to부정사/동명사 등

### `answer` 필드 주의사항

GRM, FORM, LINK 카테고리의 일부 문제는 `"answer"` 대신 `"a"` 필드명을 사용합니다. 플랫폼 코드는 `q.get("answer", q.get("a", 0))` 방식으로 둘 다 처리합니다. **이 경고는 false positive이며 수정 불필요합니다.**

---

## 2. P7 독해 지문 (data/passages_*.json)

### 파일 구조

| 파일 | 난이도 | 지문 수 |
|---|---|---|
| `passages_signal.json` | SIGNAL (쉬움) | 40편 |
| `passages_cipher.json` | CIPHER (보통) | 40편 |
| `passages_intercept.json` | INTERCEPT (어려움) | 40편 |
| `passages_blackout.json` | BLACKOUT (최상) | 40편 |
| `passages_recon.json` | RECON (정찰) | 100편 |

### 지문 스키마

```json
{
  "title": "📢 SIGNAL",
  "steps": [
    {
      "q_type":      "purpose",              // 문제 유형: purpose | detail | inference
      "sentences":   [                       // 지문 문장 배열
        "Greenfield Bakery is now hiring...",
        "Applicants must be available..."
      ],
      "question":    "What is the purpose...?",   // 영어 질문
      "question_kr": "이 광고의 목적은 무엇인가?", // 한국어 질문
      "choices":     ["(A) To recruit...", ...],   // 4지선다
      "choices_kr":  ["(A) 파트타임 직원 채용", ...], // 한국어 선지
      "answer":      0,                      // 정답 인덱스 (0-based)
      "kr":          "전체 지문 한국어 번역",
      "expressions": [                       // 학습 표현 목록
        {
          "expr":    "part-time staff",
          "meaning": "파트타임 직원"
        }
      ]
    }
    // steps[0], steps[1], steps[2] — 총 3문제 (X·Y·Z 스캐폴딩)
  ]
}
```

### X·Y·Z 스캐폴딩 구조

각 지문의 3문제(`steps[0]`, `steps[1]`, `steps[2]`)는 X·Y·Z 단계로 나뉩니다:
- **X (1단계):** 지문 직접 언급 (detail/purpose)
- **Y (2단계):** 지문 기반 추론 (inference)
- **Z (3단계):** 심화 추론 또는 종합

---

## 3. 저장소 데이터 (storage_data.json)

### 최상위 구조

```json
{
  "saved_questions":    [],   // P5 오답 문제 저장
  "saved_expressions":  [],   // 정보 포획 표현
  "word_prison":        [],   // 단어수용소 포로
  "rt_logs":            [],   // 반응속도 로그
  "p5_logs":            [],   // P5 세션 결과
  "zpd_logs":           [],   // ZPD 즉사 로그
  "cross_logs":         [],   // 크로스스킬 전이 로그
  "recon_xyz_logs":     [],   // X·Y·Z 단계 로그
  "recon_logs":         [],   // 정찰 임무 로그
  "forget_logs":        []    // 망각곡선 로그
}
```

### 3-1. saved_questions (P5 오답 저장)

```json
{
  "id":   "GRM_042",
  "text": "The report _______ by the board.",
  "ch":   ["(A) was reviewed", "(B) is reviewing", ...],
  "a":    0,
  "ex":   "해설 텍스트",
  "exk":  "구어체 해설",
  "cat":  "수동태",
  "kr":   "한국어 번역",
  "tp":   "grammar"
}
```

### 3-2. word_prison (단어수용소)

```json
{
  "word":            "comprehensive",
  "kr":              "종합적인",
  "pos":             "adjective",
  "family_root":     "comprehend",
  "source":          "P5 시험 오답",        // 출처 식별자
  "sentence":        "원본 문장",
  "captured_date":   "2026-04-12",
  "correct_streak":  0,                    // 연속 정답 횟수 (망각곡선)
  "last_reviewed":   null,                 // 마지막 복습 날짜
  "cat":             "수동태"
}
```

**source 필드 값:**
- `"P5 시험 오답"` — 포로사령부 시험에서 오답
- `"퍼즐 오답"` — 문장 퍼즐에서 오답
- `"퍼즐 건너뜀"` — 문장 퍼즐에서 건너뜀
- `"P7 자동"` — 암호해독 오답 자동 저장
- `"P7 콤보러시 오답"` — 콤보러시에서 오답

### 3-3. rt_logs (반응속도 로그 — 논문D)

```json
{
  "timestamp":          "2026-04-12T14:30:00",
  "user_id":            "홍길동_1234",
  "question_id":        "GRM_042",
  "is_correct":         true,
  "seconds_remaining":  12.5,              // 타이머 잔여 시간
  "timer_setting":      40,                // 타이머 총 시간
  "rt_proxy":           27.5,              // 반응시간 프록시 (timer - remaining)
  "grammar_type":       "GRM",
  "cat":                "수동태",
  "diff":               "normal",
  "adp_level":          "normal",          // 적응형 난이도 레벨
  "session_no":         3,
  "week":               2,                 // 학습 주차
  "error_timing_type":  null,              // 오답 시: fast_wrong | mid_wrong | slow_wrong
  "research_phase":     "pre_irb"
}
```

### 3-4. cross_logs (크로스스킬 전이 로그 — 논문B)

```json
{
  "timestamp":       "2026-04-12T15:00:00",
  "user_id":         "홍길동_1234",
  "p7_passage_id":   "SIGNAL_003",
  "p5_matched_ids":  ["GRM_042", "FORM_101"],  // P5에서 매칭된 문제 ID
  "match_count":     5,                         // 겹치는 어휘 수
  "week":            2,
  "research_phase":  "pre_irb"
}
```

### 3-5. recon_xyz_logs (X·Y·Z 단계 로그)

```json
{
  "timestamp":    "2026-04-12T15:10:00",
  "user_id":      "홍길동_1234",
  "passage_id":   "SIGNAL_003",
  "x_correct":    true,                // X단계 정답여부
  "y_correct":    true,                // Y단계 정답여부
  "z_correct":    false,               // Z단계 정답여부
  "x_sec":        15.3,                // X단계 소요시간(초)
  "y_sec":        22.1,                // Y단계 소요시간(초)
  "z_sec":        35.8,                // Z단계 소요시간(초)
  "total_score":  2,
  "session_no":   1,
  "week":         2,
  "research_phase": "pre_irb"
}
```

### 3-6. forget_logs (망각곡선 로그 — 논문C)

```json
{
  "timestamp":       "2026-04-12T16:00:00",
  "user_id":         "홍길동_1234",
  "problem_id":      "GRM_042",
  "grammar_type":    "GRM",
  "source":          "P5 시험 오답",
  "first_wrong_date":"2026-04-01",
  "revisit_date":    "2026-04-12",
  "interval_days":   11,               // 첫 오답 → 재방문 간격
  "re_wrong":        false,            // 재방문 시 또 틀렸는지
  "revisit_count":   2,
  "finally_correct": true,             // 최종 정답 여부
  "days_to_overcome":11,               // 극복까지 소요일
  "week":            2,
  "research_phase":  "pre_irb"
}
```

---

## 4. 출석 데이터 (data/cohorts/)

### attendance.json

```json
{
  "홍길동_1234": {
    "days": ["2026-04-01", "2026-04-02", "2026-04-05"],
    "last_ts": "2026-04-05T08:30:00"
  }
}
```

---

## 5. 진단 검사 (data/diagnosis_sets.json)

```json
{
  "day1":  [...],   // 1차 사전검사 문제 세트
  "day10": [...],   // 2차 중간검사 문제 세트
  "day20": [...]    // 3차 사후검사 문제 세트
}
```

---

## 6. Google Sheets 스키마

`_storage.py`의 `_SHEETS_HEADERS` 딕셔너리에 정의되어 있으며, 각 시트의 컬럼 구조는 위 로그 스키마의 키와 동일합니다.

| 시트명 | 대응 로그 |
|---|---|
| `rt_logs` | 반응속도 로그 |
| `p5_logs` | P5 세션 결과 |
| `zpd_logs` | ZPD 즉사 로그 |
| `forget_logs` | 망각곡선 로그 |
| `cross_logs` | 크로스스킬 전이 로그 |
| `recon_xyz_logs` | X·Y·Z 단계 로그 |
| `activity` | 활동 기록 |
| `attendance` | 출석 기록 |

---

## 7. _word_family_db.py (어휘 DB)

### 주요 API

```python
from _word_family_db import lookup, find_words_in_sentence, WORD_INDEX

# 단일 단어 조회
info = lookup("comprehensive")
# → {"word": "comprehensive", "kr": "종합적인", "pos": "adjective", "family_root": "comprehend"}

# 문장에서 DB 매칭 단어 추출
matched = find_words_in_sentence("The comprehensive report was reviewed.", max_words=3)
# → [{"word": "comprehensive", "kr": "종합적인", ...}, {"word": "report", ...}]
```

이 DB는 플랫폼 전용이며, `_prison_from_sentence()`에서 오답 문장의 DB 교집합 어휘를 추출하는 데 사용됩니다.
