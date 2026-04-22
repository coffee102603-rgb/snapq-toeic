# SnapQ TOEIC V3 — 코드 수정 변경 로그
## 날짜: 2026-04-23 | 세션 목표: 데이터 수집 보장 (STAGE 1 논문 ①②⑤)

---

## 🔍 사전 진단 결과

로그설계 문서 v2.0과 코드를 교차 점검한 결과:

| 항목 | 문서 예상 | 실제 코드 | 상태 |
|------|-----------|-----------|------|
| 03, 04 `record_activity()` | ❌ 호출 누락 | ✅ 이미 구현됨 | 문서보다 코드가 앞서 있었음 |
| zpd_logs Sheets 저장 | 필요 | ❌ 로컬 JSON만 | **수정 완료** |
| p5_logs Sheets 저장 | 필요 | ❌ 로컬 JSON만 | **수정 완료** |
| 04 save_to_sheets 인증 | 통일 필요 | ❌ gspread.authorize (구 방식) | **수정 완료** |
| research_phase 필드 | 필수 | ❌ zpd/p5 logs에 미포함 | **수정 완료** |

---

## ✅ 수정 1: 02_Firepower.py

### 변경 내용
- **VICTORY 블록** (line ~940): zpd_logs + p5_logs에 `_storage.save_to_sheets()` 호출 추가
- **GAME_OVER 블록** (line ~1176): 동일하게 Sheets 이중저장 추가
- 모든 entry에 `research_phase` 필드 추가

### 수정 원칙
- 기존 로컬 JSON 저장 코드 **일체 변경 없음** (안전)
- `_storage.save(_st2)` 호출 **아래에** Sheets 저장 추가 (추가 only)
- Sheets 저장 실패해도 `try/except pass`로 게임 계속 (원칙 5)
- AI agent 주석에 PAPER 번호, STORAGE 방식, SAFETY 사항 명시

### 영향받는 논문
- ⑤ 탐색적 로그 분석: p5_logs 세션 요약이 Sheets에 영구 보존
- ⑦ ZPD 스캐폴딩: zpd_logs VICTORY/GAME_OVER가 Sheets에 영구 보존

---

## ✅ 수정 2: 04_Decrypt_Op.py

### 변경 내용 A — save_to_sheets 인증 방식 통일
- `gspread.authorize()` + `Credentials.from_service_account_info()` (구 방식)
- → `gspread.service_account_from_dict()` (gspread 6.x, _storage.py와 동일)
- `st.error()` 제거 → 학생에게 Sheets 오류 노출 방지
- AI-AGENT NOTE 추가: 이 함수가 왜 _storage.py와 별도로 존재하는지 설명

### 변경 내용 B — P7 zpd_logs Sheets 이중저장
- LOST (즉사) 시 zpd_logs entry를 Sheets에도 저장
- VICTORY (3문제 전부 정답) 시 zpd_logs entry를 Sheets에도 저장
- 모든 entry에 `research_phase` 필드 추가

### 수정 원칙
- P7 세션 레코드 형식 (step1/step2/step3)은 스키마가 다르므로 함수 유지
- 인증 방식만 통일 (보안·호환성)
- 기존 로컬 JSON 저장 코드 변경 없음

### 영향받는 논문
- ⑦ ZPD 스캐폴딩: P7 즉사 지점 데이터가 Sheets에 영구 보존
- ④ AI 자동 분류: P7 RT 데이터 Sheets 저장 안정성 향상

---

## 📊 수정 후 데이터 흐름 요약

```
학생 플레이
    ↓
02_Firepower.py (P5 화력전)
    ├── rt_logs     → _storage.append_log() → 로컬 + Sheets ✅ (기존)
    ├── p5_logs     → _storage.save() + save_to_sheets() → 로컬 + Sheets ✅ (신규)
    ├── zpd_logs    → _storage.save() + save_to_sheets() → 로컬 + Sheets ✅ (신규)
    └── activity    → record_activity() → 로컬 + Sheets ✅ (기존)

03_POW_HQ.py (포로사령부)
    ├── forget_logs → _storage.append_log() → 로컬 + Sheets ✅ (기존)
    └── activity    → record_activity() → 로컬 + Sheets ✅ (기존)

04_Decrypt_Op.py (P7 암호해독)
    ├── P7 세션     → save_to_sheets() → Sheets ✅ (인증 통일)
    ├── cross_logs  → _storage.save_cross_log() → 로컬 + Sheets ✅ (기존)
    ├── recon_xyz   → _storage.save_recon_xyz_log() → 로컬 + Sheets ✅ (기존)
    ├── zpd_logs    → 로컬 + save_to_sheets() → 로컬 + Sheets ✅ (신규)
    └── activity    → record_activity() → 로컬 + Sheets ✅ (기존)
```

---

## ⏭️ 다음 작업 (이 세션 계속)

1. 코드 감사 문서 v2 업데이트

---

## ✅ 수정 4: 02_Firepower.py — P5 로비 리모컨 UI 마무리

### 현재 상태 재확인
- 개별 버튼 색상(fp-t30/t40/t50, fp-g1/g2/g3/vc)은 **이미 구현 완료**
- 선택 상태 글로우(fp-sel)도 작동 중
- JS 클래스 주입 방식 = main_hub.py보다 더 우아한 해결

### 추가 구현 (리모컨 3구역 시각적 분리)
- **⚡ COMBAT TIME** 구역: 네이비 배경 (linear-gradient #0a1628→#0d1a30)
- **🎯 MISSION SELECT** 구역: 다크레드 배경 (#1a0810→#200c14)
- **🧭 NAVIGATE** 구역: 다크그린 배경 (#081a0e→#0c200f) + 라벨 신규 추가
- 네비 버튼 색상: 무채색 → 그린 계열 (#448855) + hover 글로우
- JS `applyZones()` 함수: 런타임에 구역 라벨을 찾아 배경 스타일 동적 주입
- `el.dataset.zoned` 플래그로 중복 적용 방지

### 수정 원칙
- 기존 버튼 동작 코드 **변경 없음**
- CSS 추가 + JS 함수 추가만 (추가 only)
- 구역 라벨을 못 찾으면 아무것도 안 함 (안전 fallback)

---

## ✅ 수정 3: 01_Admin.py — 전면 재작성

### 문제
- 기존: `data/research_logs/*.jsonl`에서 읽음
- 실제 데이터: Google Sheets에 저장됨
- 결과: **대시보드 항상 빈 화면** ("아직 수집된 데이터가 없습니다")

### 수정 내용
- `gspread.service_account_from_dict()`로 Sheets 직접 읽기
- `st.cache_data(ttl=300)` → 5분 캐싱으로 API 절약
- 8개 시트 동시 로드: rt_logs, p5_logs, zpd_logs, activity, attendance, forget_logs, cross_logs, session_events
- 로컬 `storage_data.json` fallback (Sheets 완전 실패 시)
- 6개 탭 구성: 학생 현황 / 학습 분석 / 게이미피케이션 / 논문별 로그 / 세션 이벤트 / 내보내기
- 논문별 로그 현황 탭 신규 추가 (각 시트 행 수 + 논문 번호 표시)
- `is_correct` 문자열 → boolean 자동 변환 (Sheets에서 "True"/"False" 문자열로 올 수 있음)
- 데이터 소스 배지 표시 (📡 Sheets / 💾 로컬)

### 영향받는 논문
- ⑤ 탐색적 로그 분석: 실시간 데이터 시각화 가능
- 전체: 연구자가 수집 상태를 즉시 확인 가능

### 배포 경로
```
01_Admin.py → snapq_toeic_V2/pages/01_Admin.py
```
