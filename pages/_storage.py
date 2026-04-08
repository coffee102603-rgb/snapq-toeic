"""
FILE: _storage.py
ROLE: 공통 저장소 모듈
"""
import os, json
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
    try:
        save_to_sheets(key, entry)
    except: pass
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

def save_rt_log(q, is_correct, seconds_remaining, timer_setting, session_no, adp_level, error_timing_type=None):
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


# ═══ Google Sheets 저장 ═══
def _get_sheets_client():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(st.secrets["SPREADSHEET_ID"])
        return sh
    except Exception:
        return None

def save_to_sheets(log_key, entry):
    try:
        sh = _get_sheets_client()
        if not sh: return False
        headers_map = {
            "rt_logs":["timestamp","user_id","question_id","is_correct","seconds_remaining","timer_setting","rt_proxy","grammar_type","cat","diff","adp_level","session_no","week","error_timing_type","research_phase"],
            "p5_logs":["timestamp","user_id","session_no","result","correct_count","wrong_count","timer_selected","mode","week","research_phase"],
            "zpd_logs":["timestamp","user_id","session_no","arena","timer_setting","result","game_over_q_no","max_q_reached","week","research_phase"],
            "forget_logs":["timestamp","user_id","problem_id","grammar_type","source","first_wrong_date","revisit_date","interval_days","re_wrong","revisit_count","finally_correct","days_to_overcome","week","research_phase"],
            "cross_logs":["timestamp","user_id","p7_passage_id","p5_matched_ids","match_count","week","research_phase"],
            "recon_xyz_logs":["timestamp","user_id","passage_id","x_correct","y_correct","z_correct","x_sec","y_sec","z_sec","total_score","session_no","week","research_phase"],
        }
        headers = headers_map.get(log_key, list(entry.keys()))
        try:
            ws = sh.worksheet(log_key)
        except Exception:
            ws = sh.add_worksheet(title=log_key, rows=1000, cols=len(headers))
        if not ws.row_values(1):
            ws.append_row(headers)
        row = [str(entry.get(h,"")) if entry.get(h) is not None else "" for h in headers]
        ws.append_row(row)
        return True
    except Exception:
        return False


