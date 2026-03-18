# app/core/pretest_gate.py
# ============================================
# SnapQ TOEIC - PRETEST MISSION GATE (UI 강화)
# - 프리테스트(사전 설문) 완료 전에는 로비/전장 진입 차단
# - 완료 시 data/cohorts/<cohort>/pretest_done.json 에 기록
# - main_hub.py 에서 require_pretest_gate() 호출 형태 유지
#
# ✅ 패치(Option A):
# 1) PRETEST_URL이 비어있으면 게이트를 "자동 스킵" (바로 Main Hub)
# 2) Windows 파일 잠김(PermissionError) 대비: 저장 재시도 + 폴백
# 3) Gate 화면 가독성(폰트/대비) 상향
# ============================================

from __future__ import annotations

import base64
import json
import os
import time
from dataclasses import dataclass
from typing import Optional

import streamlit as st

# -----------------------------
# Settings
# -----------------------------
COHORTS_DIR = os.path.join("data", "cohorts")
DONE_FILENAME = "pretest_done.json"

PRETEST_URL = ""  # 예: "https://forms.gle/...."


# -----------------------------
# Utilities
# -----------------------------
def _safe_read_json(path: str, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default


def _safe_write_json(path: str, data) -> None:
    """Windows에서 streamlit 핫리로드/백신 등으로 파일이 잠길 때를 대비한 안전 저장.
    - 여러 번 재시도
    - 마지막에는 '직접 덮어쓰기' 폴백
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    tmp = f"{path}.tmp_{int(time.time()*1000)}_{os.getpid()}"
    payload = json.dumps(data, ensure_ascii=False, indent=2)

    # 1) tmp에 기록
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(payload)

    # 2) 원자적 교체(잠김이면 재시도)
    for _ in range(12):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            time.sleep(0.08)
        except Exception:
            time.sleep(0.05)

    # 3) 폴백: 직접 쓰기
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(payload)
    finally:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass


def _detect_latest_cohort() -> str:
    """
    data/cohorts 폴더 안에서 가장 최신(문자열 정렬 기준) 코호트 폴더를 잡는다.
    예: 2026-01, 2026-02 ...
    """
    if not os.path.isdir(COHORTS_DIR):
        return "default"

    names = []
    for name in os.listdir(COHORTS_DIR):
        p = os.path.join(COHORTS_DIR, name)
        if os.path.isdir(p):
            names.append(name)

    if not names:
        return "default"

    names.sort()
    return names[-1]


def _get_current_cohort() -> str:
    """
    access_guard 쪽에서 코호트를 session_state에 넣는 경우도 있어서 우선 사용하고,
    없으면 data/cohorts에서 자동 감지.
    """
    for k in ("cohort", "cohort_id", "current_cohort", "active_cohort"):
        v = st.session_state.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return _detect_latest_cohort()


def _get_nickname() -> str:
    for k in ("battle_nickname", "nickname", "codename", "call_sign"):
        v = st.session_state.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def _done_path(cohort: str) -> str:
    return os.path.join(COHORTS_DIR, cohort, DONE_FILENAME)


def _is_done(nickname: str, cohort: str) -> bool:
    data = _safe_read_json(_done_path(cohort), default={})
    if isinstance(data, dict):
        return bool(data.get(nickname))
    if isinstance(data, list):
        return nickname in data
    return False


def _mark_done(nickname: str, cohort: str) -> None:
    path = _done_path(cohort)
    data = _safe_read_json(path, default={})

    if isinstance(data, list):
        if nickname not in data:
            data.append(nickname)
    elif isinstance(data, dict):
        data[nickname] = True
    else:
        data = {nickname: True}

    _safe_write_json(path, data)


def _img_to_data_uri(path: str) -> Optional[str]:
    try:
        if not os.path.exists(path):
            return None
        ext = os.path.splitext(path)[1].lower().replace(".", "")
        mime = "png" if ext == "png" else "jpeg" if ext in ("jpg", "jpeg") else "png"
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/{mime};base64,{b64}"
    except Exception:
        return None


# -----------------------------
# UI (MISSION GATE)
# -----------------------------
def _apply_gate_css(bg_img_data_uri: Optional[str]) -> None:
    bg_img = (
        f"background-image: radial-gradient(1100px 650px at 20% 0%, rgba(255,170,0,0.10), transparent 55%),"
        f" radial-gradient(900px 520px at 95% 20%, rgba(255,60,80,0.12), transparent 60%),"
        f" linear-gradient(160deg, rgba(7,12,22,1) 0%, rgba(5,8,15,1) 60%, rgba(0,0,0,1) 100%);"
    )

    st.markdown(
        f"""
        <style>
        .block-container {{
          padding-top: 1.2rem;
          padding-bottom: 2.2rem;
          max-width: 1200px;
        }}

        .gate-wrap {{
          border-radius: 22px;
          padding: 26px 28px;
          background: rgba(20,24,34,0.62);
          border: 1px solid rgba(255,255,255,0.09);
          box-shadow: 0 12px 42px rgba(0,0,0,0.55);
          position: relative;
          overflow: hidden;
        }}

        .gate-topline {{
          height: 3px;
          border-radius: 99px;
          background: linear-gradient(90deg, rgba(255,170,0,0.95), rgba(255,60,80,0.90), rgba(255,170,0,0.95));
          box-shadow: 0 0 18px rgba(255,120,40,0.35);
          margin-bottom: 16px;
        }}

        .gate-title {{
          font-size: 46px;
          font-weight: 900;
          letter-spacing: 1px;
          margin: 0 0 8px 0;
          color: rgba(255,255,255,0.95);
          text-shadow: 0 6px 18px rgba(0,0,0,0.65);
        }}

        .gate-sub {{
          font-size: 18px;
          font-weight: 800;
          color: rgba(255,255,255,0.85);
          margin: 0 0 10px 0;
        }}

        .gate-desc {{
          font-size: 18px;
          color: rgba(255,255,255,0.82);
          margin-bottom: 16px;
          line-height: 1.45;
        }}

        .chiprow {{
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
          margin-top: 10px;
          margin-bottom: 6px;
        }}
        .chip {{
          display: inline-flex;
          align-items: center;
          gap: 8px;
          border-radius: 999px;
          padding: 7px 12px;
          background: rgba(0,0,0,0.35);
          border: 1px solid rgba(255,255,255,0.08);
          color: rgba(255,255,255,0.88);
          font-size: 13px;
          font-weight: 800;
        }}

        .gate-alert {{
          margin-top: 18px;
          padding: 14px 16px;
          border-radius: 16px;
          background: rgba(255,70,90,0.18);
          border: 1px solid rgba(255,70,90,0.30);
          color: rgba(255,255,255,0.92);
          font-weight: 900;
        }}

        .small-note {{
          font-size: 14px;
          color: rgba(255,255,255,0.70);
          line-height: 1.5;
          margin-top: 10px;
        }}

        .btn-hero > div > button {{
          border-radius: 16px !important;
          height: 64px !important;
          font-size: 19px !important;
          font-weight: 900 !important;
        }}

        .stApp {{
          {bg_img}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_gate(nickname: str, cohort: str) -> None:
    _apply_gate_css(bg_img_data_uri=None)

    st.markdown('<div class="gate-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="gate-topline"></div>', unsafe_allow_html=True)
    st.markdown('<div class="gate-title">🔒 MISSION GATE</div>', unsafe_allow_html=True)
    st.markdown('<div class="gate-sub">AUTHORIZED PERSONNEL ONLY.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="gate-desc">사전 설문(PRETEST)을 완료해야 전장 입장이 허가됩니다.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="chiprow">
          <div class="chip">🧑 CALL SIGN: {nickname or "UNKNOWN"}</div>
          <div class="chip">🗂️ ACTIVE COHORT: {cohort}</div>
          <div class="chip">📁 LOG: {COHORTS_DIR}\\{cohort}\\{DONE_FILENAME}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # 닉네임이 없으면 안내만
    if not nickname:
        st.markdown(
            """
            <div class="gate-alert">
              ⚠️ CALL SIGN 미확인. 먼저 닉네임 인증 게이트를 통과하십시오.
            </div>
            <div class="small-note">
              • 권장 흐름: <b>access_guard(닉네임 인증)</b> → <b>pretest_gate(사전 설문)</b><br/>
              • 닉네임이 세팅되면, 이 화면이 자동으로 정상 작동합니다.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # 설문 링크 안내 + 완료 체크
    colL, colR = st.columns([1.2, 1.0], gap="large")
    with colL:
        st.markdown('<div class="gate-alert">🚫 ACCESS DENIED — PRETEST 미완료.</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="small-note">
              1) 설문 이동 → 제출<br/>
              2) 돌아와서 아래의 <b>✅ 완료 체크(입장 허가)</b> 버튼 클릭
            </div>
            """,
            unsafe_allow_html=True,
        )

        if PRETEST_URL.strip():
            st.link_button("📝 PRETEST BRIEFING (설문 이동)", PRETEST_URL, use_container_width=True)
        else:
            st.warning("PRETEST_URL이 비어있습니다. (Option A에선 이 게이트는 자동 스킵이지만, 강제로 들어온 경우 표시됩니다)")

    with colR:
        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
        if st.button("✅ 완료 체크(입장 허가)", use_container_width=True, key="pretest_done_btn"):
            _mark_done(nickname, cohort)
            st.success("✅ 기록 완료! 이제 전장 입장 가능합니다. (자동으로 다음 화면으로 진행)")
            st.rerun()

        st.markdown(
            """
            <div class="small-note">
              ※ 제출했는데도 막히면: <b>완료 체크</b>를 다시 눌러 기록을 갱신하세요.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.stop()


def require_pretest_gate() -> None:
    """
    main_hub.py에서 호출:
    - PRETEST_URL 비어있으면(설문 미운영) => 자동 스킵(바로 Main Hub)
    - 프리테스트 완료 전이면 Gate UI 띄우고 st.stop()
    - 완료면 그대로 통과
    """
    cohort = _get_current_cohort()
    nickname = _get_nickname()

    if not nickname:
        _render_gate(nickname="", cohort=cohort)
        return

    # ✅ Option A 핵심: 설문 링크가 비어있으면 게이트를 띄우지 않는다.
    if not PRETEST_URL.strip():
        return

    if _is_done(nickname, cohort):
        return

    _render_gate(nickname=nickname, cohort=cohort)

# -----------------------------
# Backward-compat helper
# (main_hub.py 등에서 import 하던 이름 유지)
# -----------------------------
def mark_pretest_done(nickname: str, cohort: str) -> None:
    """"pretest 완료 기록을 강제로 찍어주는 호환 함수."""
    if not nickname:
        return
    _mark_done(nickname, cohort)

