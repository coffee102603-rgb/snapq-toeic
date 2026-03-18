# app/core/access_guard.py
from __future__ import annotations
import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Optional
import streamlit as st

_ROOT = Path(__file__).resolve().parents[2]
COHORTS_DIR = _ROOT / "data" / "cohorts"
ACCESS_CODE_FILE = _ROOT / "data" / "access_code.json"
DEFAULT_ACCESS_CODE = "1111"

def load_access_code() -> str:
    try:
        if ACCESS_CODE_FILE.exists():
            data = json.loads(ACCESS_CODE_FILE.read_text(encoding="utf-8"))
            return str(data.get("code", DEFAULT_ACCESS_CODE))
    except Exception:
        pass
    return DEFAULT_ACCESS_CODE

def save_access_code(code: str, cohort_month: str) -> None:
    ACCESS_CODE_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {"code": code, "cohort_month": cohort_month, "updated_at": datetime.now().isoformat(timespec="seconds")}
    ACCESS_CODE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def get_cohort_month() -> str:
    mk = st.session_state.get("cohort_month")
    if mk:
        return str(mk)
    try:
        if ACCESS_CODE_FILE.exists():
            data = json.loads(ACCESS_CODE_FILE.read_text(encoding="utf-8"))
            cm = data.get("cohort_month")
            if cm:
                return str(cm)
    except Exception:
        pass
    return date.today().strftime("%Y-%m")

def _profile_path(student_id: str, cohort_month: str) -> Path:
    return COHORTS_DIR / cohort_month / "students" / f"{student_id}.json"

def _load_profile(student_id: str, cohort_month: str) -> dict:
    path = _profile_path(student_id, cohort_month)
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

def _save_profile(student_id: str, cohort_month: str, profile: dict) -> None:
    path = _profile_path(student_id, cohort_month)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

def is_returning_student(student_id: str, cohort_month: str) -> bool:
    try:
        if COHORTS_DIR.exists():
            for cohort_dir in COHORTS_DIR.iterdir():
                if not cohort_dir.is_dir():
                    continue
                if cohort_dir.name == cohort_month:
                    continue
                if (cohort_dir / "students" / f"{student_id}.json").exists():
                    return True
    except Exception:
        pass
    return False

def _apply_css() -> None:
    st.markdown("""
<style>
.stApp{background:linear-gradient(160deg,#07090f 0%,#050810 60%,#000000 100%);}
.block-container{padding-top:2rem;max-width:420px;}
.auth-title{font-size:2rem;font-weight:900;color:#ffffff;text-align:center;letter-spacing:2px;margin-bottom:0.2rem;}
.auth-sub{font-size:0.95rem;color:rgba(255,255,255,0.5);text-align:center;margin-bottom:1.8rem;letter-spacing:1px;}
.auth-label{font-size:0.85rem;font-weight:700;color:rgba(255,200,0,0.9);letter-spacing:1px;margin-bottom:0.3rem;}
.auth-hint{font-size:0.78rem;color:rgba(255,255,255,0.4);margin-top:0.3rem;margin-bottom:1rem;}
div[data-testid="stTextInput"] input{background:rgba(255,255,255,0.07)!important;border:1.5px solid rgba(255,255,255,0.15)!important;border-radius:12px!important;color:#ffffff!important;font-size:1.5rem!important;font-weight:900!important;text-align:center!important;letter-spacing:6px!important;padding:12px!important;}
div[data-testid="stButton"] button{background:linear-gradient(135deg,#ffaa00,#ff6600)!important;color:#000!important;font-weight:900!important;font-size:1rem!important;border-radius:14px!important;border:none!important;padding:0.7rem!important;width:100%!important;}
</style>
""", unsafe_allow_html=True)

def _render_auth_ui() -> None:
    _apply_css()
    st.markdown('<div class="auth-title">⚡ SNAPQ TOEIC</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">BATTLE LOBBY · 전장 입장</div>', unsafe_allow_html=True)
    valid_code = load_access_code()
    cohort_month = get_cohort_month()

    if not st.session_state.get("_code_verified"):
        st.markdown('<div class="auth-label">🔐 이번 달 접속코드 (숫자 4자리)</div>', unsafe_allow_html=True)
        code_input = st.text_input(label="접속코드", max_chars=4, placeholder="0000", key="code_input", label_visibility="collapsed")
        st.markdown('<div class="auth-hint">선생님이 알려준 4자리 숫자를 입력하세요</div>', unsafe_allow_html=True)
        if st.button("확인 →", key="code_btn"):
            if code_input.strip() == valid_code:
                st.session_state["_code_verified"] = True
                st.session_state["cohort_month"] = cohort_month
                st.rerun()
            else:
                st.error("❌ 접속코드가 틀렸습니다. 선생님께 확인하세요.")
        st.stop()

    if not st.session_state.get("_id_verified"):
        st.markdown('<div class="auth-label">📱 내 번호 뒤 4자리 (익명ID)</div>', unsafe_allow_html=True)
        id_input = st.text_input(label="익명ID", max_chars=4, placeholder="0000", key="id_input", label_visibility="collapsed")
        st.markdown('<div class="auth-hint">전화번호 뒤 4자리 · 매번 동일하게 입력</div>', unsafe_allow_html=True)
        if st.button("입장 →", key="id_btn"):
            sid = id_input.strip()
            if len(sid) == 4 and sid.isdigit():
                returning = is_returning_student(sid, cohort_month)
                profile = _load_profile(sid, cohort_month)
                if not profile:
                    profile = {"student_id": sid, "cohort_month": cohort_month, "is_returning": returning, "first_access": datetime.now().isoformat(timespec="seconds"), "diagnosis": {}}
                    _save_profile(sid, cohort_month, profile)
                st.session_state["battle_nickname"] = sid
                st.session_state["student_id"] = sid
                st.session_state["access_granted"] = True
                st.session_state["is_returning"] = returning
                st.session_state["student_profile"] = profile
                st.session_state["_id_verified"] = True
                st.rerun()
            else:
                st.error("❌ 숫자 4자리를 정확히 입력하세요.")
        st.stop()

def require_access(context_tag: str = "ACCESS", roster_path: str = "") -> str:
    if (st.session_state.get("access_granted") and st.session_state.get("battle_nickname") and st.session_state.get("_id_verified")):
        return st.session_state["battle_nickname"]
    _render_auth_ui()
    st.stop()
