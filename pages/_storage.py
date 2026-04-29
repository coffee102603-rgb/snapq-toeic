"""
FILE: _storage.py
ROLE: 공통 저장소 모듈
"""
import os, json, threading
from datetime import datetime
import streamlit as st

STORAGE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage_data.json")
RESEARCH_PHASE = "pre_irb"

def load():
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if not content: return _empty()
            d = json.loads(content)
            if isinstance(d, list): return {"saved_questions": d, "saved_expressions": []}
            return _ensure(d)
        except: return _empty()
    return _empty()

def save(data):
    try:
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except: return False

def append_log(key, entry):
    threading.Thread(target=save_to_sheets, args=(key, entry), daemon=True).start()
    try:
        d = load()
        if key not in d: d[key] = []
        d[key].append(entry)
        return save(d)
    except: return False

def get_uid():
    for k in ["nickname", "battle_nickname", "p7_player_id"]:
        v = st.session_state.get(k, "")
        if v and str(v).strip(): return str(v).strip()
    return "guest"

def get_week(uid):
    try:
        d = load()
        key = f"{uid}_start_date"
        today = datetime.now().strftime("%Y-%m-%d")
        if key not in d: d[key] = today; save(d)
        delta = (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(d[key], "%Y-%m-%d")).days
        return delta // 7 + 1
    except: return 1

def save_rt_log(q, is_correct, seconds_remaining, timer_setting, session_no, adp_level,
                error_timing_type=None,
                answer_changes=0,           # ★ 신규: 답 변경 횟수 (기본 0)
                hesitation_ms=0):           # ★ 신규: 망설임 시간 ms (기본 0)
    """
    문항 응답 기록 — rt_logs 시트.

    PARAMS:
        q:                문항 dict (id, tp, cat, diff 포함)
        is_correct:       정답 여부
        seconds_remaining: 남은 시간 (초)
        timer_setting:    제한 시간 설정 (초)
        session_no:       세션 번호
        adp_level:        적응형 난이도 레벨
        error_timing_type: 오답 타이밍 분류 (선택)
        answer_changes:   답 변경 횟수 (논문 ④ 신중도 분석용)
        hesitation_ms:    첫 상호작용~제출 시간 ms (논문 ④ 망설임 분석용)

    DEVICE INFO (자동 수집):
        session_state에서 device_type, viewport_w/h 자동 추출.
        값은 main_hub.py에서 JS로 수집하여 session_state에 저장.
        수집 안 된 경우 빈 값으로 기록.

    PAPER:
        ④ AI 자동 분류: 답변경·망설임은 자신감 클러스터링 핵심 변수
        ⑤ 탐색적 로그 분석: device_type은 모바일·PC 학습 패턴 차이
        ⑦ ZPD 스캐폴딩: 기본 rt_logs 확장의 상위 집합
    """
    uid = get_uid()
    gmap = {"grammar":"GRM","g1":"GRM","form":"FORM","g2":"FORM","link":"LINK","g3":"LINK","vocab":"VOCAB"}
    return append_log("rt_logs", {
        "timestamp": datetime.now().isoformat(), "user_id": uid,
        "question_id": q.get("id",""), "is_correct": is_correct,
        "seconds_remaining": round(max(0, seconds_remaining), 2),
        "timer_setting": timer_setting,
        "rt_proxy": round(max(0, timer_setting - seconds_remaining), 2),
        "grammar_type": gmap.get(q.get("tp","grammar"),"GRM"),
        "cat": q.get("cat",""), "diff": q.get("diff",""),
        "adp_level": adp_level, "session_no": session_no,
        "week": get_week(uid), "research_phase": RESEARCH_PHASE,
        "error_timing_type": error_timing_type if not is_correct else None,
        # ── 대서사시 v7 확장 필드 (2026.04) ──
        "answer_changes":  int(answer_changes) if answer_changes else 0,
        "hesitation_ms":   int(hesitation_ms) if hesitation_ms else 0,
        "device_type":     st.session_state.get("_dev_device_type", ""),
        "viewport_w":      st.session_state.get("_dev_vw", ""),
        "viewport_h":      st.session_state.get("_dev_vh", ""),
    })

# ═══ 옵션 A: 게이트 로그 저장 함수 ════════════════════════════
def save_gate_daily_log(user_id, personal_day, q_id, is_correct,
                        response_time_ms, q_type="grammar", difficulty=""):
    """
    데일리 게이트 문항별 로그 저장.

    PAPER:
        ⑤ 탐색적 분석: 일일 정답률·반응시간 미세 궤적
        ⑦ ZPD: 반응시간 단축 = 자동화 진전
        ⑪ 자기문화기술지: 학생 행동 패턴 증거
    """
    return append_log("gate_daily_logs", {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "personal_day": personal_day,
        "q_id": q_id,
        "is_correct": bool(is_correct),
        "response_time_ms": int(response_time_ms) if response_time_ms else 0,
        "q_type": q_type,
        "difficulty": difficulty,
        "research_phase": RESEARCH_PHASE,
    })


def save_gate_milestone_log(user_id, personal_day, milestone_round,
                            q_id, is_correct, response_time_ms,
                            q_type="grammar", difficulty=""):
    """
    관문검사 문항별 로그 저장.

    PAPER:
        ① 설계원리: 임계값 돌파 증거
        ⑤ 탐색적 분석: 10일 단위 변화량
        ⑩ SSCI: 사전·중간·사후 심화 측정
    """
    return append_log("gate_milestone_logs", {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "personal_day": personal_day,
        "milestone_round": milestone_round,
        "q_id": q_id,
        "is_correct": bool(is_correct),
        "response_time_ms": int(response_time_ms) if response_time_ms else 0,
        "q_type": q_type,
        "difficulty": difficulty,
        "research_phase": RESEARCH_PHASE,
    })


def save_gate_milestone_summary(user_id, personal_day, milestone_round,
                                 total_questions, correct_count,
                                 avg_response_time_ms, duration_sec):
    """
    관문검사 세션 요약 저장 (분석 편의용).

    PAPER:
        모든 논문 분석의 기본 지표
        (1 session = 1 row, 성장곡선 모형 입력 데이터)
    """
    accuracy = (correct_count / total_questions * 100) if total_questions else 0
    return append_log("gate_milestone_summary", {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "personal_day": personal_day,
        "milestone_round": milestone_round,
        "total_questions": total_questions,
        "correct_count": correct_count,
        "accuracy_pct": round(accuracy, 1),
        "avg_response_time_ms": int(avg_response_time_ms) if avg_response_time_ms else 0,
        "duration_sec": int(duration_sec) if duration_sec else 0,
        "research_phase": RESEARCH_PHASE,
    })


def save_cross_log(p7_passage_id, p5_matched_ids, match_count):
    uid = get_uid()
    return append_log("cross_logs", {
        "timestamp": datetime.now().isoformat(), "user_id": uid,
        "p7_passage_id": p7_passage_id, "p5_matched_ids": p5_matched_ids,
        "match_count": match_count, "week": get_week(uid),
        "research_phase": RESEARCH_PHASE,
    })

def save_recon_xyz_log(passage_id, step_results, step_times, session_no):
    uid = get_uid()
    return append_log("recon_xyz_logs", {
        "timestamp": datetime.now().isoformat(), "user_id": uid,
        "passage_id": passage_id,
        "x_correct": step_results[0] if len(step_results)>0 else None,
        "y_correct": step_results[1] if len(step_results)>1 else None,
        "z_correct": step_results[2] if len(step_results)>2 else None,
        "x_sec": step_times[0] if len(step_times)>0 else None,
        "y_sec": step_times[1] if len(step_times)>1 else None,
        "z_sec": step_times[2] if len(step_times)>2 else None,
        "total_score": sum(1 for r in step_results if r),
        "session_no": session_no, "week": get_week(uid),
        "research_phase": RESEARCH_PHASE,
    })

def _empty():
    return {"saved_questions":[],"saved_expressions":[],"rt_logs":[],"p5_logs":[],
            "zpd_logs":[],"cross_logs":[],"recon_xyz_logs":[],"recon_logs":[],
            "forget_logs":[],"word_prison":[]}

def _ensure(d):
    for k,v in _empty().items():
        if k not in d: d[k] = v
    return d


# ═══ Google Sheets 저장 (논문 데이터 영구 보존) ════════════════
# AI-AGENT NOTE:
#   - gspread 6.x 호환: service_account_from_dict() 사용
#   - 실패해도 게임 계속 (try/except)
#   - 시트 없으면 자동 생성 + 헤더 추가
#   - SPREADSHEET_ID: Streamlit secrets에 저장

# 논문별 로그 스키마 정의
_SHEETS_HEADERS = {
    "rt_logs":       ["timestamp","user_id","question_id","is_correct",
                      "seconds_remaining","timer_setting","rt_proxy",
                      "grammar_type","cat","diff","adp_level","session_no",
                      "week","error_timing_type","research_phase",
                      # ── 대서사시 v7 확장 필드 (2026.04) ──
                      # PAPER ④: 답 변경 횟수 (신중도·자신감 분류)
                      "answer_changes",
                      # PAPER ④: 첫 상호작용~제출 시간 (ms) — 망설임 정도
                      "hesitation_ms",
                      # PAPER ⑤: 디바이스·뷰포트 (모바일·PC 학습 패턴 차이)
                      "device_type","viewport_w","viewport_h"],
    "p5_logs":       ["timestamp","user_id","session_no","result",
                      "correct_count","wrong_count","timer_selected","mode",
                      "week","research_phase"],
    "zpd_logs":      ["timestamp","user_id","session_no","arena",
                      "timer_setting","result","game_over_q_no",
                      "max_q_reached","week","research_phase",
                      # ── 대서사시 v7 쟁점 A·B 대응 (2026.04) ──
                      # PAPER ⑦: 임계값 돌파 이벤트 추적
                      "threshold_event",      # T_target_met / level_up / reset
                      "current_level",        # 상승된 난이도 레벨
                      "rt_recent_mean",       # 최근 RT 평균 (T_target 계산 기준)
                      "rt_target",            # 목표 RT (T_target)
                      "consecutive_correct",  # 연속 정답 수
                      "is_correct_at_speed"], # 5문항 연속 정답+T_target 이하 여부
    "forget_logs":   ["timestamp","user_id","problem_id","grammar_type",
                      "source","first_wrong_date","revisit_date",
                      "interval_days","re_wrong","revisit_count",
                      "finally_correct","days_to_overcome","week","research_phase"],
    "cross_logs":    ["timestamp","user_id","p7_passage_id","p5_matched_ids",
                      "match_count","week","research_phase"],
    "recon_xyz_logs":["timestamp","user_id","passage_id",
                      "x_correct","y_correct","z_correct",
                      "x_sec","y_sec","z_sec","total_score",
                      "session_no","week","research_phase"],
    "activity":      ["date","month","nickname","arena","duration_sec",
                      "acc","completed","ts"],
    # ── 대서사시 v7 신규 시트 (2026.04) ──
    # PAPER ②: ADDIE 개발 사례 논문 — Design 단계 의사결정 증거
    #   최샘이 수기로 Google Sheets에 직접 입력 (행 append)
    #   또는 admin 페이지 내부 수기 입력 UI (다음 세션)
    "design_decisions": ["timestamp","addie_phase","topic","context",
                         "options","chosen","rationale","evidence",
                         "research_phase"],
    # PAPER ⑤: 세션 이벤트 로그 — 페이지 진입·이탈 흐름 분석
    "session_events":   ["timestamp","user_id","arena","event",
                         "duration_sec","extra_info","research_phase"],
    "attendance":    ["date","month","nickname","ts"],
    # ── 옵션 A: 데일리 게이트 (매일 5문항 = 매일 사전검사) ──────
    # PAPER ⑤⑦⑩⑪: 일일 반응시간·정답률 미세 궤적
    "gate_daily_logs":    ["timestamp","user_id","personal_day",
                           "q_id","is_correct","response_time_ms",
                           "q_type","difficulty","research_phase"],
    # ── 옵션 A: 관문검사 (Day 1, 11, 21... 30문항) ───────────
    # PAPER ①⑤⑩: 10일 단위 심화 측정, 임계값 돌파 확증
    "gate_milestone_logs":["timestamp","user_id","personal_day","milestone_round",
                           "q_id","is_correct","response_time_ms",
                           "q_type","difficulty","research_phase"],
    # ── 옵션 A: 관문검사 세션 요약 (1 row = 1 session) ──────
    "gate_milestone_summary":["timestamp","user_id","personal_day","milestone_round",
                              "total_questions","correct_count","accuracy_pct",
                              "avg_response_time_ms","duration_sec","research_phase"],
}


def save_to_sheets(log_key: str, entry: dict) -> bool:
    """
    PURPOSE: 로그 1개를 Google Sheets에 저장
    INPUT:   log_key (시트명), entry (dict)
    OUTPUT:  bool (성공 여부)
    PAPER:   모든 논문 데이터 영구 보존 (Cloud 재시작해도 유지)
    COMPAT:  gspread >= 6.0.0 (service_account_from_dict 방식)
    """
    try:
        import gspread
        gc = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        sh = gc.open_by_key(st.secrets["SPREADSHEET_ID"])
        headers = _SHEETS_HEADERS.get(log_key, list(entry.keys()))
        try:
            ws = sh.worksheet(log_key)
        except Exception:
            ws = sh.add_worksheet(title=log_key, rows=5000, cols=len(headers))
            ws.append_row(headers)
        if not ws.row_values(1):
            ws.append_row(headers)
        row = [str(entry.get(h, "")) if entry.get(h) is not None else "" for h in headers]
        ws.append_row(row)
        return True
    except Exception:
        return False


