"""
FILE: _storage.py
ROLE: 공통 저장소 모듈 (사용자별 데이터 격리 v2)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
변경 이력 (2026.05.09):
  - 사용자별 데이터 격리 추가 (word_prison, saved_questions, saved_expressions)
  - 기존 통합 데이터는 자동 마이그레이션 → "_legacy" 사용자로 보존
  - load_storage()/save_storage() 호출자 입장에서는 변경 없음 (투명)
  - 각 페이지에서 호출하는 load()/save()가 자동으로 현재 사용자만 반환
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
사용자별 격리 키:
  - word_prison         → word_prison_by_user[uid]
  - saved_questions     → saved_questions_by_user[uid]
  - saved_expressions   → saved_expressions_by_user[uid]
공유 키 (변경 없음):
  - rt_logs, p5_logs, zpd_logs, cross_logs, recon_xyz_logs, forget_logs 등
  - {uid}_start_date (기존부터 사용자별 분리되어 있던 항목)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import os, json, threading
from datetime import datetime
import streamlit as st

STORAGE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage_data.json")
RESEARCH_PHASE = "pre_irb"

# ═══════════════════════════════════════════════════════════════
# 사용자별 격리가 필요한 키 (위에 명시)
# ═══════════════════════════════════════════════════════════════
_PER_USER_KEYS = ("word_prison", "saved_questions", "saved_expressions")


def get_uid():
    """현재 사용자 ID 반환. 없으면 'guest'."""
    for k in ["nickname", "battle_nickname", "p7_player_id"]:
        v = st.session_state.get(k, "")
        if v and str(v).strip():
            return str(v).strip()
    return "guest"


# ═══════════════════════════════════════════════════════════════
# RAW 입출력 (디스크 직접 접근) — 외부 호출 금지
# ═══════════════════════════════════════════════════════════════
def _read_raw():
    """디스크에서 storage_data.json 전체를 읽음. 마이그레이션 후 반환."""
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if not content:
                return _empty_raw()
            d = json.loads(content)
            # 옛날 list 형태 → dict 형태로 (saved_questions만 있던 시절)
            if isinstance(d, list):
                d = {"saved_questions": d, "saved_expressions": []}
            return _migrate(d)
        except Exception:
            return _empty_raw()
    return _empty_raw()


def _write_raw(data):
    """디스크에 storage_data.json 전체를 씀."""
    try:
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def _empty_raw():
    """완전히 비어있는 storage_data.json 기본 구조."""
    return {
        # 사용자별 격리 키 (dict[uid] = list)
        "word_prison_by_user":       {},
        "saved_questions_by_user":   {},
        "saved_expressions_by_user": {},
        # 전역 공유 로그 (사용자별 row 단위로 user_id 들어감)
        "rt_logs":        [],
        "p5_logs":        [],
        "zpd_logs":       [],
        "cross_logs":     [],
        "recon_xyz_logs": [],
        "recon_logs":     [],
        "forget_logs":    [],
    }


def _migrate(d):
    """
    기존 통합 리스트 → 사용자별 격리 dict 자동 마이그레이션.

    [핵심 안전 장치]
    - 기존 데이터를 절대 삭제하지 않음
    - "_legacy" 사용자에게 보존 → 박사논문 데이터로 활용 가능
    - 마이그레이션은 1회만 수행 (이미 *_by_user가 있으면 건드리지 않음)
    """
    # 사용자별 격리 키들이 없으면 생성
    if "word_prison_by_user" not in d:
        d["word_prison_by_user"] = {}
    if "saved_questions_by_user" not in d:
        d["saved_questions_by_user"] = {}
    if "saved_expressions_by_user" not in d:
        d["saved_expressions_by_user"] = {}

    # 기존 통합 리스트 → _legacy 사용자에게 한 번만 이전
    # (이미 _legacy로 옮겼으면 두 번 합치지 않음)
    if "word_prison" in d and isinstance(d["word_prison"], list) and d["word_prison"]:
        if "_legacy" not in d["word_prison_by_user"]:
            d["word_prison_by_user"]["_legacy"] = d["word_prison"]
        # 원본은 빈 리스트로 (다음 마이그레이션 방지, 데이터는 _legacy에 보존)
        d["word_prison"] = []

    if "saved_questions" in d and isinstance(d["saved_questions"], list) and d["saved_questions"]:
        if "_legacy" not in d["saved_questions_by_user"]:
            d["saved_questions_by_user"]["_legacy"] = d["saved_questions"]
        d["saved_questions"] = []

    if "saved_expressions" in d and isinstance(d["saved_expressions"], list) and d["saved_expressions"]:
        if "_legacy" not in d["saved_expressions_by_user"]:
            d["saved_expressions_by_user"]["_legacy"] = d["saved_expressions"]
        d["saved_expressions"] = []

    # 빈 list 키 보장
    for k in ("rt_logs", "p5_logs", "zpd_logs", "cross_logs",
              "recon_xyz_logs", "recon_logs", "forget_logs"):
        if k not in d:
            d[k] = []

    return d


# ═══════════════════════════════════════════════════════════════
# PUBLIC API: load() / save() — 호출자 관점에서는 변경 없음
#   load()는 "현재 사용자의 데이터만 합성한 dict" 반환
#   save(d)는 "현재 사용자 데이터만 추출해서 디스크에 반영"
# ═══════════════════════════════════════════════════════════════
def load():
    """
    현재 사용자의 데이터를 합성한 dict 반환.
    호출자는 마치 자기만 쓰는 storage처럼 사용 가능.

    반환 dict 구조 (호출자 관점 — 기존과 동일):
      {
        "word_prison":        [현재 사용자의 단어수용소 리스트],
        "saved_questions":    [현재 사용자의 저장 문제 리스트],
        "saved_expressions":  [현재 사용자의 저장 표현 리스트],
        "rt_logs":            [전역 로그 — 변경 없음],
        ...
        "{uid}_start_date":   기존 키 보존
      }
    """
    raw = _read_raw()
    uid = get_uid()

    # 호출자에게 보여줄 dict 구성
    view = {}
    # 사용자별 격리 키: 현재 사용자의 데이터만 꺼내서 평면 키로 노출
    view["word_prison"]       = list(raw.get("word_prison_by_user", {}).get(uid, []))
    view["saved_questions"]   = list(raw.get("saved_questions_by_user", {}).get(uid, []))
    view["saved_expressions"] = list(raw.get("saved_expressions_by_user", {}).get(uid, []))

    # 전역 공유 키: 그대로 노출
    for k in ("rt_logs", "p5_logs", "zpd_logs", "cross_logs",
              "recon_xyz_logs", "recon_logs", "forget_logs"):
        view[k] = raw.get(k, [])

    # {uid}_start_date 등 기타 키 (사용자별 시작일) 보존
    for k, v in raw.items():
        if k in view:
            continue
        if k.endswith("_by_user"):
            continue  # 내부 구조는 노출하지 않음
        if k in ("word_prison", "saved_questions", "saved_expressions"):
            continue  # 빈 셸은 노출 안 함 (격리된 키로 대체됨)
        view[k] = v

    return view


def save(data):
    """
    호출자가 수정한 dict를 디스크에 반영.
    사용자별 격리 키는 자동으로 현재 사용자 슬롯에만 저장.
    전역 키는 그대로 덮어씀.
    """
    if not isinstance(data, dict):
        return False

    raw = _read_raw()
    uid = get_uid()

    # 사용자별 격리 키: 호출자가 넘긴 리스트를 현재 사용자 슬롯에만 저장
    if "word_prison" in data:
        raw.setdefault("word_prison_by_user", {})[uid] = list(data.get("word_prison") or [])
    if "saved_questions" in data:
        raw.setdefault("saved_questions_by_user", {})[uid] = list(data.get("saved_questions") or [])
    if "saved_expressions" in data:
        raw.setdefault("saved_expressions_by_user", {})[uid] = list(data.get("saved_expressions") or [])

    # 전역 공유 키: 호출자가 넘긴 값으로 덮어씀
    for k in ("rt_logs", "p5_logs", "zpd_logs", "cross_logs",
              "recon_xyz_logs", "recon_logs", "forget_logs"):
        if k in data:
            raw[k] = data[k]

    # 기타 키 (예: {uid}_start_date): 호출자 값으로 덮어씀
    for k, v in data.items():
        if k in raw and isinstance(raw.get(k), dict) and k.endswith("_by_user"):
            continue
        if k in ("word_prison", "saved_questions", "saved_expressions"):
            continue
        if k in ("rt_logs", "p5_logs", "zpd_logs", "cross_logs",
                 "recon_xyz_logs", "recon_logs", "forget_logs"):
            continue
        raw[k] = v

    # 호환성을 위해 빈 셸 키도 유지 (다른 코드가 raw를 들여다볼 경우 대비)
    raw.setdefault("word_prison", [])
    raw.setdefault("saved_questions", [])
    raw.setdefault("saved_expressions", [])

    return _write_raw(raw)


# ═══════════════════════════════════════════════════════════════
# 진단 & 관리 헬퍼 (관리자 페이지에서 활용 가능)
# ═══════════════════════════════════════════════════════════════
def list_all_users():
    """현재 storage_data.json에 데이터가 있는 모든 사용자 ID 반환."""
    raw = _read_raw()
    users = set()
    for key in ("word_prison_by_user", "saved_questions_by_user", "saved_expressions_by_user"):
        users.update(raw.get(key, {}).keys())
    return sorted(users)


def get_user_stats(uid):
    """특정 사용자의 데이터 개수 통계 반환."""
    raw = _read_raw()
    return {
        "word_prison":       len(raw.get("word_prison_by_user", {}).get(uid, [])),
        "saved_questions":   len(raw.get("saved_questions_by_user", {}).get(uid, [])),
        "saved_expressions": len(raw.get("saved_expressions_by_user", {}).get(uid, [])),
    }


# ═══════════════════════════════════════════════════════════════
# 로그 append (변경 없음 — 기존 동작 유지)
# ═══════════════════════════════════════════════════════════════
def append_log(key, entry):
    """전역 로그 시트에 1행 append. (rt_logs, p5_logs 등)"""
    threading.Thread(target=save_to_sheets, args=(key, entry), daemon=True).start()
    try:
        raw = _read_raw()
        if key not in raw:
            raw[key] = []
        raw[key].append(entry)
        return _write_raw(raw)
    except Exception:
        return False


def get_week(uid):
    """사용자별 학습 시작일 기준 주차 계산. (기존 그대로)"""
    try:
        raw = _read_raw()
        key = f"{uid}_start_date"
        today = datetime.now().strftime("%Y-%m-%d")
        if key not in raw:
            raw[key] = today
            _write_raw(raw)
        delta = (datetime.strptime(today, "%Y-%m-%d") - datetime.strptime(raw[key], "%Y-%m-%d")).days
        return delta // 7 + 1
    except Exception:
        return 1


def save_rt_log(q, is_correct, seconds_remaining, timer_setting, session_no, adp_level,
                error_timing_type=None,
                answer_changes=0,
                hesitation_ms=0):
    """
    문항 응답 기록 — rt_logs 시트.
    (기존과 완전히 동일 — 변경 없음)
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
        "answer_changes":  int(answer_changes) if answer_changes else 0,
        "hesitation_ms":   int(hesitation_ms) if hesitation_ms else 0,
        "device_type":     st.session_state.get("_dev_device_type", ""),
        "viewport_w":      st.session_state.get("_dev_vw", ""),
        "viewport_h":      st.session_state.get("_dev_vh", ""),
    })


# ═══ 옵션 A: 게이트 로그 저장 함수 (기존 그대로) ════════════════
def save_gate_daily_log(user_id, personal_day, q_id, is_correct,
                        response_time_ms, q_type="grammar", difficulty=""):
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


# ─── 하위 호환을 위한 alias ───────────────────────────────────
# 기존 코드에서 _empty/_ensure를 직접 호출하는 곳이 있을 경우 대비
def _empty():
    return _empty_raw()

def _ensure(d):
    return _migrate(d)


# ═══ Google Sheets 저장 (변경 없음) ════════════════════════════
_SHEETS_HEADERS = {
    "rt_logs":       ["timestamp","user_id","question_id","is_correct",
                      "seconds_remaining","timer_setting","rt_proxy",
                      "grammar_type","cat","diff","adp_level","session_no",
                      "week","error_timing_type","research_phase",
                      "answer_changes",
                      "hesitation_ms",
                      "device_type","viewport_w","viewport_h"],
    "p5_logs":       ["timestamp","user_id","session_no","result",
                      "correct_count","wrong_count","timer_selected","mode",
                      "week","research_phase"],
    "zpd_logs":      ["timestamp","user_id","session_no","arena",
                      "timer_setting","result","game_over_q_no",
                      "max_q_reached","week","research_phase",
                      "threshold_event",
                      "current_level",
                      "rt_recent_mean",
                      "rt_target",
                      "consecutive_correct",
                      "is_correct_at_speed"],
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
    "design_decisions": ["timestamp","addie_phase","topic","context",
                         "options","chosen","rationale","evidence",
                         "research_phase"],
    "session_events":   ["timestamp","user_id","arena","event",
                         "duration_sec","extra_info","research_phase"],
    "attendance":    ["date","month","nickname","ts"],
    "gate_daily_logs":    ["timestamp","user_id","personal_day",
                           "q_id","is_correct","response_time_ms",
                           "q_type","difficulty","research_phase"],
    "gate_milestone_logs":["timestamp","user_id","personal_day","milestone_round",
                           "q_id","is_correct","response_time_ms",
                           "q_type","difficulty","research_phase"],
    "gate_milestone_summary":["timestamp","user_id","personal_day","milestone_round",
                              "total_questions","correct_count","accuracy_pct",
                              "avg_response_time_ms","duration_sec","research_phase"],
}


def save_to_sheets(log_key: str, entry: dict) -> bool:
    """
    PURPOSE: 로그 1개를 Google Sheets에 저장
    INPUT:   log_key (시트명), entry (dict)
    OUTPUT:  bool (성공 여부)
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
