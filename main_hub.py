"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     main_hub.py
ROLE:     작전사령부 — 메인 허브 (로그인·스탯·NPC 피드백·전장 선택)
VERSION:  SnapQ TOEIC V3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASES:   LOGIN → LOBBY (NPC 피드백 + 단어수용소 카드 + 전장 3종 선택)
DATA IN:  storage_data.json (word_prison, rt_logs, saved_expressions)
          data/cohorts/YYYY-MM/ (attendance, activity)
DATA OUT: attendance.jsonl, session_time.json
LINKS:    main_hub.py → 02_Firepower.py | 03_POW_HQ.py | 04_Decrypt_Op.py | 01_Admin.py
PAPERS:   논문D (rt_logs 기반 NPC 개인화 피드백)
          논문A (adp_logs) 연결 허브
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AI-AGENT NOTES:
  [핵심 로직]
  - require_access(): 로그인 게이트 (이름+전화뒷4+월별코드)
  - _calc_stats(): rt_logs 분석 → p5_rate, p7_rate, arm_pending 계산
  - NPC 오버레이 메시지: _npc_p5_tx / _npc_p7_tx / _npc_pow_tx
    → 정답률 기반 개인화 (80%↑ / 60~79% / 60%↓ / 첫접속 분기)
  - 카드 호버 시 NPC 오버레이 표시 (ov-p5-a, ov-p7-a, ov-pow-a)
  - TEACHER_B64: 고양이 이미지 base64 내장 (외부 파일 의존 없음)

  [수정 주의사항]
  - st.switch_page() 경로: pages/02_Firepower.py 형식 유지
  - NPC 메시지 변수(_npc_p5_tx 등)는 _calc_stats() 이후에 정의됨
  - HTML 문자열 연결(+) 방식 유지 — f-string 멀티라인 금지
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import streamlit as st
import os
import json
import time
from datetime import datetime, date
from pathlib import Path

from app.core.access_guard import require_access
from app.core.pretest_gate import require_pretest_gate
# ★ v3 신규 (2026.04.27) — 박사 ⑩⑪ TOEIC 시계열 데이터 수집 게이트
from app.core.toeic_baseline_gate import require_toeic_baseline_gate
from app.core.attendance_engine import mark_attendance_once, has_attended_today, record_session_event
from app.core.battle_state import load_profile

st.set_page_config(
    page_title='SnapQ TOEIC',
    page_icon='⚡',
    layout='wide',
    initial_sidebar_state='collapsed'
)

# ★ BUG FIX 2026.04: WebSocket 끊김 등으로 session_state가 증발해도
# URL 쿼리(?nick=...&ag=1)로부터 닉네임 자동 복구.
# 02/03 페이지와 동일한 패턴. clear 하지 않음으로써 재복구 가능.
_qs_nick = st.query_params.get("nick", "")
_qs_ag   = st.query_params.get("ag", "")
if _qs_nick and _qs_ag == "1":
    if not st.session_state.get("nickname") or not st.session_state.get("battle_nickname"):
        st.session_state["battle_nickname"] = _qs_nick
        st.session_state["nickname"]        = _qs_nick
        st.session_state["access_granted"]  = True
        st.session_state["_code_verified"]  = True
        st.session_state["_id_verified"]    = True
        # PATCH v3.5: pilot/privacy 상태도 함께 복구 (페이지 전환 시 안내 재표시 방지)
        st.session_state["privacy_agreed"]            = True
        st.session_state["pilot_notice_acknowledged"] = True
        st.session_state["consent_research_given"]    = False

# =========================================================
# 데이터 헬퍼
# =========================================================
BASE = Path(__file__).resolve().parent

def _get_month_key() -> str:
    """현재 월 키 반환 (예: "2026-04")."""
    return date.today().strftime("%Y-%m")

def _load_research_logs(nickname: str) -> list:
    """data/research_logs 에서 이번달 로그 로드"""
    today = date.today().strftime("%Y%m%d")
    month = date.today().strftime("%Y%m")
    logs = []
    log_dir = BASE / "data" / "research_logs"
    if not log_dir.exists():
        return logs
    for f in log_dir.glob(f"{nickname.split('_')[0]}*.jsonl"):
        try:
            for line in f.read_text(encoding="utf-8").strip().split("\n"):
                if line:
                    logs.append(json.loads(line))
        except:
            pass
    return logs

def _daily_rates(logs: list, activity_type: str, days: int = 7) -> list:
    """최근 N일간 일별 정답률 리스트 반환 (데이터 없는 날은 None)"""
    from collections import defaultdict
    import datetime as _dt2
    daily = defaultdict(lambda: [0, 0])  # {date_str: [correct, total]}
    for l in logs:
        if l.get("activity_type") != activity_type:
            continue
        ts = l.get("timestamp") or l.get("ts") or l.get("created_at") or l.get("date") or ""
        try:
            if len(str(ts)) >= 10:
                d = str(ts)[:10].replace("/","-")
                daily[d][1] += 1
                if l.get("is_correct"):
                    daily[d][0] += 1
        except:
            pass
    result = []
    today = _dt2.date.today()
    for i in range(days - 1, -1, -1):
        d = (today - _dt2.timedelta(days=i)).strftime("%Y-%m-%d")
        if daily[d][1] > 0:
            result.append(round(daily[d][0] / daily[d][1] * 100))
        else:
            result.append(None)
    return result

def _svg_line(pts: list, color: str, w: int = 200, h: int = 45) -> str:
    """네온 글로우 + 면적채우기 SVG"""
    valid = [p for p in pts if p is not None]
    if len(valid) < 2:
        sample = [30, 35, 28, 42, 50, 45, 60]
        return _svg_line(sample, color, w, h)
    last_two = valid[-2:]
    if last_two[1] > last_two[0]: lc = color
    elif last_two[1] < last_two[0]: lc = "#ff4466"
    else: lc = color
    n = len(pts); pad = 4
    uw = (w - pad*2) / (n - 1)
    coords = []
    for i, v in enumerate(pts):
        if v is None: coords.append(None)
        else:
            x = pad + i * uw
            y = h - pad - (v / 100) * (h - pad*2)
            coords.append((x, y))
    path_d = ""
    for i, c in enumerate(coords):
        if c is None: continue
        if path_d == "" or coords[i-1] is None: path_d += f"M{c[0]:.1f},{c[1]:.1f} "
        else: path_d += f"L{c[0]:.1f},{c[1]:.1f} "
    vc = [c for c in coords if c is not None]
    area_d = f"M{vc[0][0]:.1f},{h} L{vc[0][0]:.1f},{vc[0][1]:.1f} "
    area_d += " ".join(f"L{c[0]:.1f},{c[1]:.1f}" for c in vc[1:])
    area_d += f" L{vc[-1][0]:.1f},{h} Z"
    uid = abs(hash(str(pts)+color)) % 99999
    dots = "".join(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="2.8" fill="{lc}" filter="url(#ng{uid})"/>' for c in vc)
    svg = (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg"><defs><filter id="ng{uid}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter><linearGradient id="ag{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="{lc}" stop-opacity="0.45"/><stop offset="100%" stop-color="{lc}" stop-opacity="0.02"/></linearGradient></defs><path d="{area_d}" fill="url(#ag{uid})" stroke="none"/><path d="{path_d.strip()}" stroke="{lc}" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round" filter="url(#ng{uid})"/><path d="{path_d.strip()}" stroke="{lc}" stroke-width="1.2" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>{dots}</svg>')
    return svg

def _daily_counts(logs: list, activity_type: str, days: int = 7) -> list:
    """최근 N일간 일별 풀이수 리스트"""
    from collections import defaultdict
    import datetime as _dt3
    daily = defaultdict(int)
    for l in logs:
        if l.get("activity_type") != activity_type:
            continue
        ts = l.get("timestamp") or l.get("ts") or l.get("created_at") or l.get("date") or ""
        try:
            if len(str(ts)) >= 10:
                d = str(ts)[:10].replace("/","-")
                daily[d] += 1
        except:
            pass
    result = []
    today = _dt3.date.today()
    for i in range(days - 1, -1, -1):
        d = (today - _dt3.timedelta(days=i)).strftime("%Y-%m-%d")
        result.append(daily[d] if daily[d] > 0 else None)
    return result

def _get_motivation(rate: float | None, logs: list, activity_type: str) -> str:
    """정답률/연속상승/오늘여부 기반 NPC 자극 멘트 생성."""
    import datetime as _dt4
    from collections import defaultdict
    today_str = _dt4.date.today().strftime("%Y-%m-%d")
    # 오늘 풀었는지
    today_count = sum(1 for l in logs
        if l.get("activity_type") == activity_type
        and str(l.get("timestamp","") or l.get("ts","") or l.get("created_at","") or l.get("date",""))[:10].replace("/","-") == today_str)
    # 최근 3일 추이
    pts = _daily_rates(logs, activity_type, 7)
    valid = [p for p in pts if p is not None]
    rising = len(valid) >= 3 and valid[-1] > valid[-2] > valid[-3]
    falling = len(valid) >= 3 and valid[-1] < valid[-2] < valid[-3]

    if today_count == 0:
        return "😴  오늘 아직 0문제!"
    if rate is None:
        return "🔥  첫 도전을 시작하자!"
    if rate >= 90:
        return "🏆  상위 5%! 완벽에 가깝다"
    if rate >= 80:
        return "🔥  상위 10% 수준!"
    if rate >= 70:
        if rising:
            return "📈  3일 연속 상승 중!"
        return "💪  조금만 더! 목표 80%"
    if falling:
        return "⚠️  3일 연속 하락! 지금 당장"
    return "⚠️  복습이 필요하다!"

def _get_visit_count(nickname: str) -> int:
    """이번달 접속 횟수 (출석일수 기반)"""
    att_file = BASE / "data" / "cohorts" / _get_month_key() / "attendance.json"
    try:
        import json as _j
        data = _j.loads(att_file.read_text(encoding="utf-8"))
        return len(data.get(nickname, {}).get("days", []))
    except:
        return 0

def _calc_stats(nickname: str) -> None:
    """P5 정답률, P7 정답률, 포로사령부 P5/보카 정복률, 접속시간 계산."""
    logs = _load_research_logs(nickname)

    # P5 정답률
    p5_logs = [l for l in logs if l.get("activity_type") == "p5_answer"]
    p5_correct = sum(1 for l in p5_logs if l.get("is_correct"))
    p5_rate = round(p5_correct / len(p5_logs) * 100) if p5_logs else None

    # P7 정답률
    p7_logs = [l for l in logs if l.get("activity_type") == "p7_answer"]
    p7_correct = sum(1 for l in p7_logs if l.get("is_correct"))
    p7_rate = round(p7_correct / len(p7_logs) * 100) if p7_logs else None

    # 포로사령부 P5 정복률
    armory_p5 = [l for l in logs if l.get("activity_type") == "armory_p5"]
    armory_p5_rate = round(sum(1 for l in armory_p5 if l.get("is_correct")) / len(armory_p5) * 100) if armory_p5 else None

    # 포로사령부 보카 정복률
    armory_voca = [l for l in logs if l.get("activity_type") == "armory_voca"]
    armory_voca_rate = round(sum(1 for l in armory_voca if l.get("is_correct")) / len(armory_voca) * 100) if armory_voca else None

    # 포로사령부 전체 정복률
    armory_all = armory_p5 + armory_voca
    armory_total_rate = round(sum(1 for l in armory_all if l.get("is_correct")) / len(armory_all) * 100) if armory_all else None

    # 재도전 대기 수 (틀린 문제)
    armory_pending = sum(1 for l in logs if l.get("activity_type") in ["p5_answer", "p7_answer"] and not l.get("is_correct"))

    # P5 문제 수
    p5_count = len(p5_logs)
    p7_count = len(p7_logs)

    return {
        "p5_rate": p5_rate,
        "p7_rate": p7_rate,
        "p5_count": p5_count,
        "p7_count": p7_count,
        "armory_p5_rate": armory_p5_rate,
        "armory_voca_rate": armory_voca_rate,
        "armory_total_rate": armory_total_rate,
        "armory_pending": armory_pending,
        "_logs": logs,
    }

def _get_attendance_days(nickname: str) -> int:
    """이번달 출석일수"""
    att_file = BASE / "data" / "cohorts" / _get_month_key() / "attendance.json"
    if not att_file.exists():
        return 0
    try:
        data = json.loads(att_file.read_text(encoding="utf-8"))
        user_data = data.get(nickname, {})
        return len(user_data.get("days", []))
    except:
        return 0

def _get_session_minutes() -> int:
    """현재 세션 접속 시간(분)"""
    if "session_start" not in st.session_state:
        st.session_state.session_start = time.time()
    elapsed = time.time() - st.session_state.session_start
    return int(elapsed / 60)

def _get_total_time_str(nickname: str) -> str:
    """누적 접속 시간 (시간:분)"""
    time_file = BASE / "data" / "cohorts" / _get_month_key() / "session_time.json"
    total_min = 0
    if time_file.exists():
        try:
            data = json.loads(time_file.read_text(encoding="utf-8"))
            total_min = data.get(nickname, 0)
        except:
            pass
    total_min += _get_session_minutes()
    h = total_min // 60
    m = total_min % 60
    if h > 0:
        return f"{h}시간 {m}분"
    return f"{m}분"

def _get_ranking(nickname: str) -> str:
    """전투 참여도 랭킹 (접속시간 기준)"""
    time_file = BASE / "data" / "cohorts" / _get_month_key() / "session_time.json"
    if not time_file.exists():
        return "집계중"
    try:
        data = json.loads(time_file.read_text(encoding="utf-8"))
        my_time = data.get(nickname, 0) + _get_session_minutes()
        rank = sum(1 for v in data.values() if v > my_time) + 1
        return f"{rank}위"
    except:
        return "집계중"

def _arrow(rate: float | None) -> str:
    """정답률 기반 방향 화살표 반환."""
    if rate is None:
        return ""
    if rate >= 70:
        return "↑"
    elif rate >= 50:
        return "→"
    return "↓"

def _arrow_color(rate: float | None) -> str:
    """정답률 기반 색상코드 반환."""
    if rate is None:
        return "#888"
    if rate >= 70:
        return "#00E5A0"
    elif rate >= 50:
        return "#FFD600"
    return "#FF4560"

def _mini_bar(rate: float | None) -> str:
    """정답률 기반 미니 바 그래프 HTML 생성."""
    if rate is None:
        return '<span style="color:#666;font-size:14px;">데이터 없음</span>'
    filled = int(rate / 10)
    bar = ""
    for i in range(10):
        h = 6 + (i * 2)
        if i < filled:
            color = "#00E5A0" if rate >= 70 else ("#FFD600" if rate >= 50 else "#FF4560")
            bar += f'<span style="display:inline-block;width:8px;height:{h}px;background:{color};border-radius:2px;margin-right:2px;vertical-align:bottom;"></span>'
        else:
            bar += f'<span style="display:inline-block;width:8px;height:{h}px;background:rgba(255,255,255,0.1);border-radius:2px;margin-right:2px;vertical-align:bottom;"></span>'
    return bar

# =========================================================
# CSS
# =========================================================
def load_css() -> None:
    """전역 CSS + 뷰포트 메타태그 주입."""
    # 모바일 뷰포트 메타태그 - 휴대폰에서 올바른 크기로 표시
    st.markdown('<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">', unsafe_allow_html=True)
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Noto+Sans+KR:wght@400;700;900&display=swap');

    .stApp { background: #0A0C15 !important; overflow-x: hidden; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }
    header { display: none !important; height: 0 !important; }
    /* transform으로 레이아웃 무시하고 위로 이동 */
    .block-container {
        transform: translateY(-9rem) !important;
        padding-left: 8px !important;
        padding-right: 8px !important;
        max-width: 860px !important;
    }
    div[data-testid="stVerticalBlock"] > div { gap: 0 !important; margin: 0 !important; padding: 0 !important; }
    div[data-testid="stVerticalBlock"] > div > div { margin: 0 !important; padding: 0 !important; }
    div[data-testid="element-container"] { margin: 0 !important; padding: 0 !important; }
    div[data-testid="stMarkdownContainer"] { margin: 0 !important; padding: 0 !important; }
    div.stMarkdown { margin: 0 !important; padding: 0 !important; }
    iframe { display: block !important; margin: 0 !important; padding: 0 !important; border: none !important; }
    .stApp > div > div > div > div { gap: 0 !important; }
    iframe { display: block !important; margin: 0 !important; padding: 0 !important; border: none !important; }
    .stApp > div > div > div > div { gap: 0 !important; }

    /* 상단 배너 - 형광 반짝 테두리 */
    .top-banner {
        background: linear-gradient(135deg, rgba(124,92,255,0.2), rgba(0,229,160,0.15));
        border: 2px solid rgba(0,229,255,0.6);
        border-radius: 16px;
        padding: 7px 12px;
        margin: 6px 0 6px 0;
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        align-items: center;
        box-shadow: 0 0 16px rgba(0,229,255,0.35), 0 0 32px rgba(0,229,255,0.15), inset 0 0 20px rgba(0,229,255,0.05);
        animation: bannerGlow 2s ease-in-out infinite alternate;
    }
    @keyframes bannerGlow {
        from { box-shadow: 0 0 12px rgba(0,229,255,0.3), 0 0 24px rgba(0,229,255,0.1); border-color: rgba(0,229,255,0.5); }
        to   { box-shadow: 0 0 24px rgba(0,229,255,0.7), 0 0 48px rgba(0,229,255,0.3); border-color: rgba(0,229,255,1.0); }
    }
    .banner-name {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 26px;
        font-weight: 900;
        color: #fff;
        text-shadow: 0 0 10px rgba(0,229,255,0.5);
    }
    .banner-item {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 18px;
        font-weight: 900;
        color: rgba(255,255,255,0.95);
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .banner-divider {
        color: rgba(0,229,255,0.5);
        font-size: 20px;
    }
    .banner-rank {
        background: linear-gradient(135deg, #FFD600, #FF6B35);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 900;
        font-size: 20px;
    }

    /* 타이틀 + 브랜딩 */
    .hub-brand {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 16px;
        padding: 4px 0 6px 0;
    }
    .hub-teacher-photo {
        width: 52px;
        height: 52px;
        border-radius: 50%;
        object-fit: cover;
        object-position: center top;
        border: 3px solid #00E5FF;
        box-shadow: 0 0 16px rgba(0,229,255,0.5), 0 0 32px rgba(0,229,255,0.2);
        flex-shrink: 0;
    }
    .hub-brand-text {
        text-align: left;
    }
    .hub-title-text {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 30px;
        letter-spacing: 4px;
        background: linear-gradient(135deg, #FF2D55, #7C5CFF, #00E5FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
        margin: 0;
    }
    .hub-subtitle {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 14px;
        font-weight: 900;
        color: #FFD600;
        letter-spacing: 1px;
        margin-top: 1px;
    }
    .hub-platform {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 11px;
        color: rgba(255,255,255,0.35);
        letter-spacing: 2px;
        margin-top: 2px;
    }

    /* 전장 버튼 공통 */
    .arena-btn {
        border-radius: 20px;
        padding: 16px 20px;
        margin-bottom: 4px;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        border: none;
        width: 100%;
        box-sizing: border-box;
        min-height: 130px;
    }

    /* P5 - 강렬한 파랑+시안 */
    .arena-p5 {
        background: linear-gradient(135deg, #050a0f, #0a1a2a);
        box-shadow: 0 0 24px rgba(0,229,255,0.5); border: 1.5px solid #00e5ff;
    }
    /* P7 - 보라+핑크 */
    .arena-p7 {
        background: linear-gradient(135deg, #0f0e05, #1f1a05);
        box-shadow: 0 0 24px rgba(255,215,0,0.5); border: 1.5px solid #ffd700;
    }
    /* 역전장 - 금+주황 */
    .arena-armory {
        background: linear-gradient(135deg, #0f0508, #1f0510);
        box-shadow: 0 0 24px rgba(255,45,85,0.5); border: 1.5px solid #ff2d55;
    }

    .arena-inner {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
    }
    .arena-enter-btn {
        background: rgba(0,0,0,0.3);
        border: 3px solid rgba(255,255,255,0.7);
        border-radius: 16px;
        color: #fff;
        font-family: "Noto Sans KR", sans-serif;
        font-size: 26px;
        font-weight: 900;
        padding: 24px 22px;
        min-width: 80px;
        text-align: center;
        letter-spacing: 2px;
        flex-shrink: 0;
        text-shadow: 0 2px 6px rgba(0,0,0,0.5);
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }
    .arena-left {}
    .arena-icon-title {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 28px;
        font-weight: 900;
        color: #fff;
        text-shadow: 0 2px 8px rgba(0,0,0,0.4);
        margin-bottom: 6px;
    }
    .arena-count {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 17px;
        color: rgba(255,255,255,0.9);
        font-weight: 900;
        margin-top: 8px;
    }
    /* 네온 그래프 + 멘트 전환 */
    @keyframes hubFadeGraph {
        0%,38%  {opacity:1;}
        45%,100%{opacity:0;}
    }
    @keyframes hubFadeMsg {
        0%,38%  {opacity:0;}
        45%,100%{opacity:1;}
    }
    .hub-layer {
        position:absolute; left:0; right:0; top:0; bottom:0;
        padding:10px 16px 12px;
        display:flex; flex-direction:column; justify-content:center;
    }
    .hub-graph-layer { animation:hubFadeGraph 7s ease-in-out infinite; }
    .hub-msg-layer   { animation:hubFadeMsg   7s ease-in-out infinite; }
    .neon-bar-row { display:flex; align-items:center; gap:8px; margin-bottom:8px; }
    .neon-label { font-size:0.9rem; font-weight:800; color:rgba(255,255,255,0.85); width:42px; flex-shrink:0; }
    .neon-track { flex:1; height:11px; background:rgba(0,0,0,0.25); border-radius:6px; overflow:hidden; }
    .neon-fill  { height:100%; border-radius:6px; }
    .neon-cyan   { background:linear-gradient(90deg,#00ccff,#00ffee); box-shadow:0 0 8px #00ccff; }
    .neon-purple { background:linear-gradient(90deg,#aa44ff,#dd88ff); box-shadow:0 0 8px #aa44ff; }
    .neon-green  { background:linear-gradient(90deg,#00ff88,#aaff44); box-shadow:0 0 8px #00ff88; }
    .neon-pct { font-size:0.95rem; font-weight:900; color:#fff; width:36px; text-align:right; flex-shrink:0; }
    .hub-msg-title { font-size:1.25rem; font-weight:900; color:#fff; margin-bottom:4px; }
    .hub-msg-sub   { font-size:1rem; font-weight:700; color:rgba(255,255,255,0.8); margin-bottom:3px; }
    .hub-msg-count { font-size:0.85rem; color:rgba(255,255,255,0.55); }

    .arena-right {
        text-align: right;
    }
    .arena-rate {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 48px;
        color: #fff;
        line-height: 1;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    .arena-arrow {
        font-size: 26px;
        font-weight: 900;
        margin-left: 4px;
    }
    .arena-first {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 17px;
        font-weight: 900;
        background: rgba(255,255,255,0.25);
        color: #fff;
        padding: 8px 14px;
        border-radius: 999px;
        display: inline-block;
    }

    /* 역전장 분리 표시 */
    .armory-sub {
        display: flex;
        gap: 16px;
        margin-top: 8px;
    }
    .armory-sub-item {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 18px;
        font-weight: 900;
        color: rgba(0,0,0,0.85);
    }
    .armory-pending {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 17px;
        color: rgba(0,0,0,0.75);
        font-weight: 900;
        margin-top: 6px;
    }

    /* 하단 서브 버튼 */
    .sub-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-top: 8px;
    }
    .sub-btn {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        cursor: pointer;
    }
    .sub-btn-disabled {
        opacity: 0.4;
        cursor: not-allowed;
    }
    .sub-btn-icon { font-size: 28px; margin-bottom: 6px; }
    .sub-btn-label {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 13px;
        font-weight: 700;
        color: rgba(255,255,255,0.7);
    }

    /* 출격 버튼 - 작은 컬럼 버튼 */
    div[data-testid="stButton"] { margin: 0 !important; }
    div.stButton > button {
        background: rgba(0,0,0,0.3) !important;
        border: 2px solid rgba(255,255,255,0.7) !important;
        border-radius: 10px !important;
        color: #fff !important;
        font-size: 14px !important;
        font-weight: 900 !important;
        height: 140px !important;
        cursor: pointer !important;
        letter-spacing: 1px !important;
        text-shadow: 0 2px 6px rgba(0,0,0,0.5) !important;
        padding: 0 !important;
    }
    div.stButton > button:hover {
        background: rgba(0,0,0,0.5) !important;
        transform: scale(1.05);
    }
    div.stButton > button p {
        font-size: 26px !important;
        font-weight: 900 !important;
        color: #fff !important;
    }

    /* ══════════════════════════════════
       반응형 — 태블릿 (768px 이하)
    ══════════════════════════════════ */
    @media (max-width: 768px) {
        .block-container { padding: 0 6px 30px 6px !important; }
        .top-banner { padding: 10px 12px; gap: 6px; }
        .banner-name { font-size: 20px; }
        .banner-item { font-size: 14px; }
        .banner-rank { font-size: 16px; }
        .hub-brand { gap: 6px; padding: 2px 0 4px 0; }
        .hub-teacher-photo { width: 44px; height: 44px; }
        .hub-title-text { font-size: 24px; letter-spacing: 1px; }
        .hub-subtitle { font-size: 12px; }
        .hub-platform { font-size: 10px; }
        .arena-icon-title { font-size: 22px; }
        .arena-count { font-size: 14px; }
        .arena-rate { font-size: 38px; }
        .arena-enter-btn { font-size: 20px; padding: 18px 14px; min-width: 64px; }
        .arena-btn { min-height: 100px; padding: 12px 14px; }
        .neon-label { font-size: 0.78rem; width: 36px; }
        .neon-pct { font-size: 0.82rem; }
        .hub-msg-title { font-size: 1.05rem; }
        .hub-msg-sub { font-size: 0.88rem; }
        div.stButton > button { font-size: 20px !important; height: 72px !important; }
        div.stButton > button p { font-size: 20px !important; }
    }

    /* ══════════════════════════════════
       반응형 — 모바일 (480px 이하)
    ══════════════════════════════════ */
    @media (max-width: 480px) {
        .block-container { padding: 0 4px 20px 4px !important; }
        .top-banner { padding: 8px 10px; gap: 4px; flex-wrap: wrap; }
        .banner-name { font-size: 16px; }
        .banner-item { font-size: 12px; }
        .banner-rank { font-size: 13px; }
        .banner-divider { font-size: 14px; }
        .hub-brand { gap: 6px; padding: 2px 0 4px 0; }
        .hub-teacher-photo { width: 40px; height: 40px; border-width: 2px; }
        .hub-title-text { font-size: 22px; letter-spacing: 1px; }
        .hub-subtitle { font-size: 11px; }
        .hub-platform { font-size: 9px; letter-spacing: 1px; }
        .arena-icon-title { font-size: 18px; margin-bottom: 4px; }
        .arena-count { font-size: 12px; margin-top: 4px; }
        .arena-rate { font-size: 30px; }
        .arena-enter-btn { font-size: 16px; padding: 14px 10px; min-width: 52px; border-width: 2px; }
        .arena-btn { min-height: 86px; padding: 10px; border-radius: 14px; }
        .arena-first { font-size: 13px; padding: 6px 10px; }
        .neon-label { font-size: 0.72rem; width: 30px; }
        .neon-track { height: 9px; }
        .neon-pct { font-size: 0.75rem; width: 28px; }
        .neon-bar-row { gap: 5px; margin-bottom: 5px; }
        .hub-msg-title { font-size: 0.92rem; }
        .hub-msg-sub { font-size: 0.78rem; }
        .hub-msg-count { font-size: 0.72rem; }
        .sub-btn-icon { font-size: 22px; }
        .sub-btn-label { font-size: 11px; }
        .sub-row { gap: 8px; }
        .armory-sub-item { font-size: 14px; }
        .armory-pending { font-size: 13px; }
        .armory-sub { gap: 10px; }
        div.stButton > button { font-size: 16px !important; height: 60px !important; border-width: 2px !important; border-radius: 12px !important; letter-spacing: 1px !important; }
        div.stButton > button p { font-size: 16px !important; }
    }

    /* ══════════════════════════════════
       반응형 — 초소형 (360px 이하)
    ══════════════════════════════════ */
    @media (max-width: 360px) {
        .hub-title-text { font-size: 22px; }
        .hub-teacher-photo { width: 40px; height: 40px; }
        .arena-icon-title { font-size: 15px; }
        .arena-enter-btn { font-size: 13px; padding: 12px 8px; min-width: 44px; }
        div.stButton > button { font-size: 11px !important; height: 70px !important; border-width: 1.5px !important; border-radius: 8px !important; letter-spacing: 0px !important; padding: 0 !important; }
        div.stButton > button p { font-size: 11px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# 메인
# =========================================================
load_css()

# ── Streamlit 상단 여백 완전 제거 (MutationObserver로 지속 감시) ──
import streamlit.components.v1 as _hc
_hc.html("""

""", height=0)

# 로그인 + 검사 체크
nickname = require_access()
# ★ v3 (2026.04.27): 매월 첫 접속 시 TOEIC 점수 입력 게이트
#   PAPER ⑩⑪ — Growth Curve Model의 시계열 종속변수 확보
require_toeic_baseline_gate(nickname)
require_pretest_gate()

# ★ BUG FIX 2026.04: URL 쿼리에 nickname 자동 저장 → 세션 증발 시 자동 복구
# 로그인 성공 직후 URL을 '?nick=사용자명&ag=1' 로 유지.
# WebSocket 끊김·탭 전환·페이지 이동 후에도 쿼리가 있으면 다른 페이지 상단
# 가드가 session_state를 자동 복구 (guest 낙인 방지).
if nickname:
    _cur_nick = st.query_params.get("nick", "")
    _cur_ag = st.query_params.get("ag", "")
    if _cur_nick != nickname or _cur_ag != "1":
        st.query_params["nick"] = nickname
        st.query_params["ag"] = "1"

# 출석 자동 기록
mark_attendance_once(nickname)

# ── 페이지 진입 이벤트 기록 (대서사시 L1: 세션 흐름 추적) ──────
# PAPER: ⑤ 탐색적 로그 분석 (허브 방문 빈도·체류 시간 분석)
# ──────────────────────────────────────────────────────────────
if nickname and not st.session_state.get("_arena_entered_MAIN_HUB"):
    try:
        record_session_event(nickname=nickname, arena="MAIN_HUB", event="enter")
        st.session_state["_arena_entered_MAIN_HUB"] = True
    except Exception:
        pass

# ★★★ iOS Safari 세션 영속화 — localStorage에 닉네임 저장 + WebSocket 킵얼라이브 ★★★
import streamlit.components.v1 as _ios_persist_cmp
_ios_nick_js = str(nickname).replace("'", "\\'") if nickname else ""
_ios_persist_cmp.html(f"""

""", height=0)

# ══════════════════════════════════════════════════════════
# ★ viewport_width 자동 수집 (논문 07 KCI 핵심 — 선행연구 0건)
# window.innerWidth → URL query param → storage_data.json devices
# ══════════════════════════════════════════════════════════
import streamlit.components.v1 as _vp_cmp
_vp_cmp.html("""

""", height=0)

# viewport_width를 devices storage에 저장
try:
    _vw_raw = st.query_params.get("vw", None)
    _vh_raw = st.query_params.get("vh", None)
    # ★ 2026.04: session_state에도 저장 → _storage.save_rt_log()에서 자동 추출
    # PAPER ⑤: rt_logs에 device_type·viewport 필드 연동
    if _vw_raw:
        try:
            _vw_int_live = int(_vw_raw)
            st.session_state["_dev_vw"] = _vw_int_live
            st.session_state["_dev_device_type"] = "mobile" if _vw_int_live < 768 else "desktop"
        except Exception:
            pass
    if _vh_raw:
        try:
            st.session_state["_dev_vh"] = int(_vh_raw)
        except Exception:
            pass

    if _vw_raw and nickname and not st.session_state.get("_vw_saved_" + nickname):
        _vw_int = int(_vw_raw)
        _STORAGE_FILE_HUB = os.path.join(os.path.dirname(__file__), "storage_data.json")
        if os.path.exists(_STORAGE_FILE_HUB):
            with open(_STORAGE_FILE_HUB, "r", encoding="utf-8") as _f_vw:
                _st_vw = json.load(_f_vw)
        else:
            _st_vw = {}
        # devices 리스트에서 이 학생 기록 찾아서 viewport_width 추가/업데이트
        _devs = _st_vw.get("devices", [])
        _updated = False
        for _dev in _devs:
            if isinstance(_dev, dict) and _dev.get("user_id") == nickname:
                _dev["viewport_width"] = _vw_int
                _updated = True
                break
        if not _updated:
            # 없으면 새 레코드 추가
            import platform as _plat
            _devs.append({
                "user_id":        nickname,
                "viewport_width": _vw_int,
                "screen_width":   _vw_int,   # 대리값 (JS에서 더 정확히 얻으려면 추가)
                "device_type":    "mobile" if _vw_int < 768 else "desktop",
                "timestamp":      datetime.now().isoformat(),
            })
        _st_vw["devices"] = _devs
        with open(_STORAGE_FILE_HUB, "w", encoding="utf-8") as _f_vw2:
            json.dump(_st_vw, _f_vw2, ensure_ascii=False, indent=2)
        st.session_state["_vw_saved_" + nickname] = True
except:
    pass

# 데이터 로드
stats = _calc_stats(nickname)
att_days = _get_attendance_days(nickname)
import datetime as _dt
_today_day = _dt.date.today().day
att_rate = round(att_days / _today_day * 100) if _today_day > 0 else 0
total_time = _get_total_time_str(nickname)
ranking = _get_ranking(nickname)
student_name = st.session_state.get("student_nickname") or (nickname.split('_')[0] if '_' in nickname else nickname)

# =========================================================
# 브랜딩 사진 (topbar에서 사용)
# =========================================================
# Base64를 파일에서 로드 (assets/teacher_cat.jpg)
import base64 as _b64
_teacher_path = Path(__file__).parent / "assets" / "teacher_cat.jpg"
if _teacher_path.exists():
    TEACHER_B64 = _b64.b64encode(_teacher_path.read_bytes()).decode("ascii")
else:
    TEACHER_B64 = ""

# hub-brand 제거 → 아래 compact topbar로 통합

# =========================================================
# 3개 전장 카드 (SVG 라인차트 + 키워드 페이드)
# =========================================================
import streamlit.components.v1 as _hc

p5_rate  = stats["p5_rate"]
p5_count = stats["p5_count"]
p7_rate  = stats["p7_rate"]
p7_count = stats["p7_count"]
arm_total = stats["armory_total_rate"]
arm_p5   = stats["armory_p5_rate"]
arm_voca = stats["armory_voca_rate"]
arm_pending = stats["armory_pending"]
_logs    = stats["_logs"]

# ── SVG 그래프 (크게) ──
_p5_rate_svg = _svg_line(_daily_rates(_logs, "p5_answer"),  "#00eeff", 200, 38)
_p5_cnt_svg  = _svg_line(_daily_counts(_logs, "p5_answer"), "#44ffaa", 200, 38)
_p7_rate_svg = _svg_line(_daily_rates(_logs, "p7_answer"),  "#dd88ff", 200, 38)
_p7_cnt_svg  = _svg_line(_daily_counts(_logs, "p7_answer"), "#ffcc44", 200, 38)
_arm_p5_svg  = _svg_line(_daily_rates(_logs, "armory_p5"),  "#ffee44", 200, 38)
_arm_vc_svg  = _svg_line(_daily_rates(_logs, "armory_voca"),"#ff9944", 200, 38)

# =========================================================
# 환영/복귀 메시지
# =========================================================
_is_first_check = (p5_count == 0 and p7_count == 0)
_total_solved = p5_count + p7_count
_welcome_short = "🔥 첫판 · 바로 시작!" if _is_first_check else f"💥 {_total_solved}문제 완료!"

# ── 접속 횟수 기반 로테이션 멘트 ──
_visit = _get_visit_count(nickname)
_is_first = (p5_count == 0 and p7_count == 0)

# P5 로테이션 멘트 (슬1/슬2/슬3)
_P5_ROT = [
    ("시험장은 전쟁터다!", "편하게 있지 마라!", "⚡ 30초 · 5문제 · 문법 속도전!"),
    ("아직도 느리냐?", "전쟁터엔 핑계 없다!", "⚡ 문법·어휘 속도전!"),
    ("문장 1개도 못 읽으면서", "시험장 갈 건가?", "⚡ 30초 · 5문제 · 틀리면 탈락!"),
    ("실력은 연습이 만든다!", "오늘도 도망치면 내일도 같다!", "⚡ 30초 · 5문제 · 도망치지 마라!"),
    ("빠르게, 정확하게!", "그게 전부다!", "⚡ 30초 · 5문제 · 완벽하게!"),
]
# P7 로테이션 멘트
_P7_ROT = [
    ("고득점, 원하니?", "그럼 지금 증명해!", "📖 60초 · 1지문 · 3문제 · 독해 집중전!"),
    ("내용 이해 못 하면", "다 틀린다. 지문을 읽어라!", "📖 60초 · 1지문 · 3문제 · 오늘 끝내!"),
    ("고득점?", "말만 하지 말고 증명해!", "📖 60초 · 1지문 · 3문제 · 읽고 끝내라!"),
    ("지문을 읽지 않으면", "찍는 것과 다름없다!", "📖 60초 · 1지문 · 3문제 · 집중하라!"),
    ("독해는 속도가 아니다!", "이해가 전부다!", "📖 60초 · 1지문 · 3문제 · 완벽 이해!"),
]
# 포로사령부 로테이션 멘트
_ARM_ROT = [
    ("P5 포로 · 33초 · 5문제", "P7 포로 · 44초 · 10문제", "💀 포로 심문! 오답 정복! 역전 인생!"),
    ("또 틀렸나?", "반복만이 살길이다!", "🗡️ 설욕 못 하면 역전도 없다!"),
    ("틀린 문제가", "너를 기다린다!", "🗡️ 이번엔 반드시 정복하라!"),
    ("오답은 기회다!", "다시 보면 반드시 안다!", "🗡️ 역전의 시작은 지금이다!"),
    ("포기하면 편하다!", "하지만 점수는 안 오른다!", "🗡️ 끝까지 싸워라!"),
]

_ri = _visit % len(_P5_ROT)
_p5_rot  = _P5_ROT[_ri]
_p7_rot  = _P7_ROT[_ri % len(_P7_ROT)]
_arm_rot = _ARM_ROT[_ri % len(_ARM_ROT)]

# 슬라이드1: 정답률 (재접속) or 소개멘트 (첫접속)
def _trend(logs: list, activity_type: str) -> str:
    """최근 7일 정답률 추세 문자열 반환."""
    pts = [p for p in _daily_rates(logs, activity_type, 7) if p is not None]
    if len(pts) < 2: return ""
    diff = pts[-1] - pts[-2]
    if diff > 0: return f" ▲{diff}%"
    if diff < 0: return f" ▼{abs(diff)}%"
    return " ―"
_p5_trend = _trend(_logs, "p5_answer")
_p7_trend = _trend(_logs, "p7_answer")
if _is_first:
    _sn = student_name
    _p5_s1_big  = f"⚡ 화력전"
    _p5_s1_lbl  = "문법·어휘 속도전!"
    _p7_s1_big  = f"📡 암호해독 작전"
    _p7_s1_lbl  = "해독 작전 · 암호를 풀어라!"
    _arm_s1_big = f"💀 포로사령부"
    _arm_s1_lbl = "틀린 문제가 무기가 된다"
    _p5_s2_big  = "3개↑ 생존"
    _p5_s2_lbl  = "30초 · 5문제 · 미만 전멸"
    _p7_s2_big  = "1오답 즉사"
    _p7_s2_lbl  = "60초 · 3문제 · 시간초과 즉사"
    _arm_s2_big = "저장→반복"
    _arm_s2_lbl = "틀린 문제가 무기가 된다"
    _p5_s3  = "⚡ 5문제 서바이벌 · 즉사룰"
    _p7_s3  = "📡 독해 지문 정보전 · 1오답 즉사"
    _arm_s3 = "💀 저장 → 반복 → 완전정복!"
else:
    _sn = student_name
    _p5_s1_big  = f"{p5_rate}%{_p5_trend}" if p5_rate is not None else f"{_sn}! 첫 도전"
    _p5_s1_lbl  = "7일 정답률"
    _p5_s2_big  = f"{p5_count}문제"
    _p5_s2_lbl  = f"이번달 · {_p5_trend} 변화" if _p5_trend.strip() not in ["", "―", " ―"] else "이번달 풀이"
    _p7_s1_big  = f"{p7_rate}%{_p7_trend}" if p7_rate is not None else f"{_sn}! 첫 도전"
    _p7_s1_lbl  = "7일 정답률"
    _p7_s2_big  = f"{p7_count}문제"
    _p7_s2_lbl  = f"이번달 · {_p7_trend} 변화" if _p7_trend.strip() not in ["", "―", " ―"] else "이번달 풀이"
    _arm_s1_big = f"{arm_pending}개" if arm_pending > 0 else "완벽!"
    _arm_s1_lbl = "🔥 오답 아직 남았다!" if arm_pending > 0 else "✅ 오답 제로!"
    _arm_s2_big = f"{arm_p5}%" if arm_p5 is not None else "—"
    _arm_s2_lbl = "정복률"
    if p5_rate is None:
        _p5_s3 = f"⚡ {_sn}! 첫 도전 기다리는 중!"
    elif p5_rate >= 80:
        _p5_s3 = f"🏆 {p5_rate}% · 상위 10%! 이 기세 유지해!"
    elif p5_rate >= 60:
        _p5_s3 = f"⚡ {p5_rate}% → 목표 80% · 지금 도전!"
    else:
        _p5_s3 = f"💀 {p5_rate}%?! 이게 실력이야? 당장 들어와!"
    if p7_rate is None:
        _p7_s3 = f"📖 {_sn}! 첫 독해 전투 시작해라!"
    elif p7_rate >= 80:
        _p7_s3 = f"🏆 {p7_rate}% · 독해 마스터! 계속 달려!"
    elif p7_rate >= 60:
        _p7_s3 = f"📖 {p7_rate}% → 지문 더 꼼꼼히 읽어라!"
    else:
        _p7_s3 = f"💀 {p7_rate}%?! 지문 읽긴 한 거야?!"
    if arm_pending == 0:
        _arm_s3 = "✅ 오답 제로! 완벽 정복! 진짜 전사!"
    elif arm_pending <= 5:
        _arm_s3 = f"🔥 {arm_pending}개 남았다! 거의 다 왔어!"
    else:
        _arm_s3 = f"💀 {arm_pending}개 쌓이는 중! 또 도망쳐?"

# ── 공통 CSS ──
_CSS = """<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,sans-serif;}
@keyframes s1{0%,30%{opacity:1;}36%,100%{opacity:0;}}
@keyframes s2{0%,30%{opacity:0;}36%,63%{opacity:1;}69%,100%{opacity:0;}}
@keyframes s3{0%,63%{opacity:0;}69%,96%{opacity:1;}100%{opacity:0;}}
.card{border-radius:18px 0 0 18px;padding:14px 18px 12px;position:relative;height:178px;overflow:hidden;}
.p5c{background:linear-gradient(145deg,#1a0500,#aa3300,#ff6600);}
.p7c{background:linear-gradient(145deg,#002233,#005577,#00aacc);}
.arc{background:linear-gradient(145deg,#551100,#bb5500,#ffaa00);}
.ttl{font-size:0;height:0;margin:0;overflow:hidden;}
.sl{position:absolute;left:18px;right:18px;top:10px;}
.sl1{animation:s1 9s ease-in-out infinite;}
.sl2{animation:s2 9s ease-in-out infinite;}
.sl3{animation:s3 9s ease-in-out infinite;}
.row{display:flex;align-items:center;gap:14px;}
.numbox{min-width:80px;flex-shrink:0;}
.big{font-size:1.62rem;font-weight:900;color:#fff;line-height:1.25;}
.lbl{font-size:0.95rem;font-weight:700;color:rgba(255,255,255,0.85);margin-top:4px;}
.chart{flex:1;min-width:0;}
.mot{font-size:1.68rem;font-weight:900;color:#fff;line-height:1.35;padding-top:6px;}
svg{display:block;overflow:visible;width:100%;}
@media(max-width:768px){
  .card{height:150px;padding:10px 14px 8px;border-radius:14px 0 0 14px;}
  .ttl{font-size:0;height:0;}
  .big{font-size:1.3rem;}
  .mot{font-size:1.3rem;}
  .sl{top:8px;}
  .numbox{min-width:64px;}
}
@media(max-width:480px){
  .card{height:124px;padding:8px 10px 6px;border-radius:12px 0 0 12px;}
  .ttl{font-size:0;height:0;}
  .big{font-size:1.1rem;}
  .lbl{font-size:0.82rem;}
  .mot{font-size:1.05rem;line-height:1.3;}
  .sl{top:6px;left:10px;right:10px;}
  .numbox{min-width:52px;}
  .row{gap:8px;}
}
</style>"""

def _mk_card(cls, title, s1b, s1l, s1svg, s2b, s2l, s2svg, s3mot, go=""):
    _href = f"?nav={go}" if go else ""
    return f"""<a class="card {cls}" href="{_href}" target="_parent"
  style="cursor:pointer;touch-action:manipulation;-webkit-tap-highlight-color:transparent;text-decoration:none;display:block;">
  <div class="ttl">{title}</div>
  <div class="sl sl1"><div class="row">
    <div class="numbox"><div class="big">{s1b}</div><div class="lbl">{s1l}</div></div>
    <div class="chart">{s1svg}</div>
  </div></div>
  <div class="sl sl2"><div class="row">
    <div class="numbox"><div class="big">{s2b}</div><div class="lbl">{s2l}</div></div>
    <div class="chart">{s2svg}</div>
  </div></div>
  <div class="sl sl3"><div class="mot">{s3mot}</div></div>
</div>"""

# ── 공통 go-btn 스타일 ──
_GO_STYLE = """
<style>
.card{position:relative;overflow:hidden;}
@keyframes goPulse{
  0%,100%{box-shadow:0 0 10px #ff8800,0 0 20px #ff4400,0 0 40px rgba(255,100,0,0.4);border-color:rgba(255,200,0,0.9);}
  50%{box-shadow:0 0 20px #ffcc00,0 0 40px #ff8800,0 0 80px rgba(255,150,0,0.7);border-color:#fff;}
}
@keyframes goShine{
  0%{background-position:200% center;}
  100%{background-position:-200% center;}
}
.go-btn{
  position:absolute;right:8px;top:50%;transform:translateY(-50%);
  background:var(--go-bg,linear-gradient(270deg,#ff6600,#ffcc00,#ff3300,#ffaa00));
  background-size:300% 300%;
  animation:goPulse 1.2s ease-in-out infinite, goShine 2s linear infinite;
  border:2.5px solid var(--go-border,rgba(255,220,100,0.95));
  border-radius:14px;color:#fff;font-size:24px;
  width:56px;height:75%;min-height:52px;max-height:84px;
  cursor:pointer;display:flex;align-items:center;justify-content:center;
  text-shadow:0 0 10px rgba(255,255,100,1),0 0 20px rgba(255,150,0,0.8);
  filter:drop-shadow(0 0 6px rgba(255,150,0,0.8));
}
.go-btn:active{transform:translateY(-50%) scale(0.9);filter:brightness(1.3);}
</style>
"""

# ═══════════════════════════════════════════
# 💀 C안 그리드 카드 — 포로수용소 + 화력전 + 암호해독 + 포로사령부
# 한 iframe에 전부 → 스크롤 없이 한 화면에!
# ═══════════════════════════════════════════

# ── 숨김 버튼 CSS (JS 실행 전 즉시 숨기기) ──
st.markdown("""
<style>
/* 네비게이션 숨김 버튼 — 화면에 절대 보이지 않게 */
div[data-testid="stButton"]:has(button[kind="secondary"]) {
    position: fixed !important;
    top: -9999px !important;
    left: -9999px !important;
    width: 1px !important;
    height: 1px !important;
    opacity: 0 !important;
}
</style>
""", unsafe_allow_html=True)
# postMessage 리스너 (iOS 호환)
import streamlit.components.v1 as _msg_cmp
_msg_cmp.html("""
<script>
window.addEventListener('message', function(e) {
  var msg = e.data;
  if (typeof msg !== 'string' || !msg.startsWith('snapq:')) return;
  var target = msg.replace('snapq:', '');
  var btns = window.parent.document.querySelectorAll('button');
  for (var i = 0; i < btns.length; i++) {
    if ((btns[i].innerText || '').trim() === target) {
      btns[i].click();
      break;
    }
  }
});
</script>
""", height=0)
# iOS URL 파라미터 감지
# ★ BUG FIX 2026.04: clear() 전면 삭제 대신 nav만 제거 → nick, ag 유지로 세션 복구 가능
_nav = st.query_params.get("nav", "")
if _nav == "PRISON_GO":
    if "nav" in st.query_params: del st.query_params["nav"]
    st.session_state.sg_phase = "word_prison"
    st.switch_page("pages/03_POW_HQ.py")
elif _nav == "P5_GO":
    if "nav" in st.query_params: del st.query_params["nav"]
    st.session_state.phase = "lobby"
    st.session_state._p5_active = False
    st.switch_page("pages/02_Firepower.py")
elif _nav == "P7_GO":
    if "nav" in st.query_params: del st.query_params["nav"]
    if "p7_phase" in st.session_state:
        st.session_state.p7_phase = "lobby"
    st.switch_page("pages/04_Decrypt_Op.py")
elif _nav == "ARM_GO":
    if "nav" in st.query_params: del st.query_params["nav"]
    st.session_state.sg_phase = "lobby"
    st.session_state["_wp_guard"] = False
    st.switch_page("pages/03_POW_HQ.py")
elif _nav == "ADMIN_GO":
    if "nav" in st.query_params: del st.query_params["nav"]
    st.switch_page("pages/01_Admin.py")

_prison_go = st.button("PRISON_GO", key="prison_btn")
if _prison_go:
    st.session_state.sg_phase = "word_prison"
    st.switch_page("pages/03_POW_HQ.py")

_p5_go = st.button("P5_GO", key="p5_btn")
if _p5_go:
    st.session_state.phase = "lobby"
    st.session_state._p5_active = False
    st.switch_page("pages/02_Firepower.py")

_p7_go = st.button("P7_GO", key="p7_btn")
if _p7_go:
    if "p7_phase" in st.session_state:
        st.session_state.p7_phase = "lobby"
    st.switch_page("pages/04_Decrypt_Op.py")

_arm_go = st.button("ARM_GO", key="armory_btn")
if _arm_go:
    st.session_state.sg_phase = "lobby"
    st.session_state["_wp_guard"] = False

    st.switch_page("pages/03_POW_HQ.py")
_adm_go = st.button("ADMIN_GO", key="admin_go_btn")
if _adm_go:
    st.switch_page("pages/01_Admin.py")

# ── 포로수용소 데이터 로드 ──
try:
    _pr_sf = os.path.join(os.path.dirname(__file__), "storage_data.json")
    _pr_raw = {}
    if os.path.exists(_pr_sf):
        with open(_pr_sf, "r", encoding="utf-8") as _pf:
            _pr_raw = json.load(_pf)
    _pr_data  = _pr_raw.get("word_prison", [])
    _pr_total = len(_pr_data)
    import datetime as _pr_dt
    _pr_today_str = _pr_dt.datetime.now().strftime("%Y-%m-%d")
    _pr_danger = sum(1 for p in _pr_data if p.get("captured_date","") and
                     (_pr_dt.datetime.now() - _pr_dt.datetime.strptime(
                         p.get("captured_date",_pr_today_str),"%Y-%m-%d")).days >= 7)
    _pr_warn  = sum(1 for p in _pr_data if p.get("captured_date","") and
                    3 <= (_pr_dt.datetime.now() - _pr_dt.datetime.strptime(
                        p.get("captured_date",_pr_today_str),"%Y-%m-%d")).days < 7)
    _pr_new   = max(0, _pr_total - _pr_danger - _pr_warn)
    _pr_p5 = sum(1 for p in _pr_data if p.get("source","") == "P5")
    _pr_p7 = sum(1 for p in _pr_data if p.get("source","") == "P7")
except Exception:
    _pr_total = 0; _pr_danger = 0; _pr_warn = 0; _pr_new = 0
    _pr_p5 = 0; _pr_p7 = 0

_pr_badge_txt = (f"🚨 탈출 직전 {_pr_danger}명" if _pr_danger > 0
                 else (f"⚠️ 위험 {_pr_warn}명" if _pr_warn > 0
                       else ("" if _pr_total == 0
                             else f"🆕 신입 {_pr_new}명")))
_pr_color = ("#ff4040" if _pr_danger > 0
             else ("#ff9040" if _pr_warn > 0
                   else ("#44cc88" if _pr_total == 0 else "#c0a030")))
_pr_border = ("rgba(255,64,64,0.7)" if _pr_danger > 0
              else ("rgba(255,144,64,0.6)" if _pr_warn > 0
                    else ("rgba(68,200,136,0.4)" if _pr_total == 0
                          else "rgba(192,160,48,0.5)")))

# ── P5 카드 슬라이드3 멘트 (한 줄 압축) ──
_p5_mot  = _p5_s3[:28] + "..." if len(_p5_s3) > 28 else _p5_s3
_p7_mot  = _p7_s3[:28] + "..." if len(_p7_s3) > 28 else _p7_s3
_arm_mot = _arm_s3[:28] + "..." if len(_arm_s3) > 28 else _arm_s3

# ── 통계 표시값 ──
_p5_disp  = f"{p5_rate}%" if p5_rate is not None else "첫 도전!"
_p7_disp  = f"{p7_rate}%" if p7_rate is not None else "첫 도전!"
_arm_disp = f"포로 {_pr_total}명" if _pr_total > 0 else "포로 없음"

def _goto(key):
    return f"window.parent.document.querySelectorAll('button').forEach(function(b){{if((b.innerText||'').trim()==='{key}')b.click()}})"


if p5_rate is not None:
    _npc_p5_stat = f"P5 정답률 {p5_rate}% · 누적 {p5_count}문제"
else:
    _npc_p5_stat = "아직 첫 도전 전 · P5 문법어휘 속도전!"
if p7_rate is not None:
    _npc_p7_stat = f"P7 정답률 {p7_rate}% · 누적 {p7_count}문제"
else:
    _npc_p7_stat = "아직 첫 도전 전 · P7 독해 지문 해독전!"
if arm_p5 is not None:
    _npc_pow_stat = f"오답 {arm_pending}개 수감 · 정복률 {arm_p5}%"
else:
    _npc_pow_stat = f"오답 {arm_pending}개 수감중"
if _pr_total > 0:
    _npc_pb_stat = f"총 {_pr_total}개 · P5:{_pr_p5} P7:{_pr_p7}"
else:
    _npc_pb_stat = "포로 없음! 완벽 정복 중"
_npc_att_stat = f"출석 {att_days}일 · 참여도 {att_rate}%"

# ── rt_logs 기반 개인화 NPC 메시지 ──
if _is_first:
    _npc_p5_tx  = "화력전은 불이야.<br>5문제, 3개 생존.<br>첫 전투 — 지금 시작해!"
    _npc_p7_tx  = "지문 해독 임무.<br>단 1번 오판 = 즉시 철수.<br>첫 도전 — 집중해."
    _npc_pow_tx = "네가 틀린 문제들이<br>여기 갇혔어.<br>완전히 외울 때까지 석방 없음."
else:
    # 화력전 메시지
    if p5_rate is None:
        _npc_p5_tx = "화력전은 불이야.<br>빠르고 정확하게.<br>화력이 약하면 전멸이다!"
    elif p5_rate >= 80:
        _npc_p5_tx = f"정답률 {p5_rate}% — 최정예다.<br>이 속도 절대 늦추지 마.<br>상위 전사만이 살아남는다!"
    elif p5_rate >= 60:
        _npc_p5_tx = f"정답률 {p5_rate}% — 아직 부족해.<br>80% 넘어야 진짜 전사다.<br>지금 바로 다시 들어와!"
    else:
        _npc_p5_tx = f"정답률 {p5_rate}%?!<br>이게 실력이야? 당장 각성해.<br>느리면 죽는다!"
    # 암호해독 메시지
    if p7_rate is None:
        _npc_p7_tx = "지문 해독 임무.<br>1번 오판 = 즉시 철수.<br>집중 = 승리."
    elif p7_rate >= 80:
        _npc_p7_tx = f"독해 {p7_rate}% — 독해 마스터.<br>지문을 꿰뚫는 눈.<br>이 집중력 계속 유지해!"
    elif p7_rate >= 60:
        _npc_p7_tx = f"독해 {p7_rate}% — 지문 더 꼼꼼히.<br>1번 오판 = 즉시 철수.<br>읽고 또 읽어라!"
    else:
        _npc_p7_tx = f"독해 {p7_rate}%?!<br>지문 읽긴 한 거야?<br>적군 문서 — 다시 해독해!"
    # 포로사령부 메시지
    if arm_pending == 0:
        _npc_pow_tx = "오답 제로 — 완벽 정복.<br>네가 틀린 문제 하나도 없어.<br>진짜 전사다!"
    elif arm_pending <= 5:
        _npc_pow_tx = f"오답 {arm_pending}개 — 거의 다 왔어.<br>이번엔 반드시 정복하라.<br>역전의 시작은 지금이다!"
    else:
        _npc_pow_tx = f"오답 {arm_pending}개 — 아직 갇혔어.<br>화력전·암호해독 약점.<br>다 여기 있어. 끝내라!"
_IOS_FIX = """
<script>
(function(){
  document.addEventListener('touchstart', function(){}, {passive:true});
  var style = document.createElement('style');
  style.innerHTML = '* { -webkit-tap-highlight-color: transparent; touch-action: manipulation; } .card, .pb { cursor: pointer; }';
  document.head.appendChild(style);
})();
</script>
"""
_GRID_HTML = f"""
<style>
*{{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,'Noto Sans KR',sans-serif;}}

/* ── 폰게임 HUD 상단바 ── */
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap');
.topbar{{
  display:flex;align-items:center;gap:6px;flex-wrap:wrap;
  padding:4px 10px;margin-bottom:14px;
  background:linear-gradient(135deg,rgba(124,92,255,0.18),rgba(0,229,160,0.12));
  border:1.5px solid rgba(0,229,255,0.55);
  border-radius:10px;
  animation:tbGlow 2s ease-in-out infinite alternate;
}}
@keyframes tbGlow{{
  from{{box-shadow:0 0 10px rgba(0,229,255,0.2);border-color:rgba(0,229,255,0.4);}}
  to{{box-shadow:0 0 22px rgba(0,229,255,0.65);border-color:rgba(0,229,255,0.95);}}
}}
.tb-photo{{width:26px;height:26px;border-radius:50%;object-fit:cover;object-position:center top;
  border:2px solid #00E5FF;flex-shrink:0;}}
.tb-brand{{font-family:'Bebas Neue',sans-serif;font-size:14px;letter-spacing:2px;
  background:linear-gradient(135deg,#FF2D55,#7C5CFF,#00E5FF);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  font-weight:900;white-space:nowrap;}}
.tb-sep{{color:rgba(0,229,255,0.35);font-size:11px;}}
.tb-name{{font-size:12px;font-weight:900;color:#fff;white-space:nowrap;}}
.tb-item{{font-size:11px;font-weight:700;color:rgba(255,255,255,0.82);white-space:nowrap;}}
.tb-rank{{font-size:11px;font-weight:900;
  background:linear-gradient(135deg,#FFD600,#FF6B35);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  white-space:nowrap;}}
.tb-msg{{font-size:10px;font-weight:700;color:rgba(255,255,255,0.45);white-space:nowrap;}}

/* ── 포로수용소 바 ── */
.pb{{
  background:linear-gradient(90deg,#110820,#2a0e55);
  border:1.5px solid {_pr_border};
  border-radius:14px;
  padding:12px 14px;
  display:flex;align-items:center;justify-content:space-between;
  margin-bottom:8px;
  min-height:52px;
  cursor:pointer;
  touch-action:manipulation;
  -webkit-tap-highlight-color:transparent;
  user-select:none;
}}
.pb:active{{opacity:0.8;transform:scale(0.98);}}
.pb-left{{display:flex;align-items:center;gap:8px;}}
.pb-icon{{font-size:20px;flex-shrink:0;}}
.pb-name{{font-size:13px;font-weight:900;color:#e8d0ff;}}
.pb-sub{{font-size:10px;color:{_pr_color};margin-top:1px;}}
.pb-btn{{
  background:{_pr_color};
  border-radius:8px;padding:6px 12px;
  font-size:11px;color:#fff;font-weight:700;
  white-space:nowrap;flex-shrink:0;
}}

/* ── 전장 그리드 ── */
.grid{{
  display:grid;
  grid-template-columns:1fr 1fr;
  grid-template-rows:auto auto;
  gap:8px;
}}

/* ── 공통 카드 ── */
.card{{
  border-radius:18px;
  display:flex;flex-direction:column;
  overflow:hidden;
  cursor:pointer;
  touch-action:manipulation;
  -webkit-tap-highlight-color:transparent;
  user-select:none;
  position:relative;
}}
.card:active{{opacity:0.85;transform:scale(0.97);transition:transform 0.1s;}}

.card-p5{{background:linear-gradient(160deg,#1a0800,#cc4400,#ff6600);}}
.card-p7{{background:linear-gradient(160deg,#001a2a,#005577,#00aacc);}}
.card-pow{{
  grid-column:1/-1;
  background:linear-gradient(135deg,#1a0035,#440088);
  flex-direction:row;align-items:center;
}}

/* ── 카드 내부 ── */
.card-body{{
  flex:1;
  padding:14px 12px 8px;
  display:flex;flex-direction:column;
}}
.badge{{
  background:rgba(255,255,255,0.18);
  border-radius:5px;padding:3px 7px;
  font-size:9px;color:rgba(255,255,255,0.9);font-weight:700;
  letter-spacing:1px;width:fit-content;margin-bottom:6px;
}}
.card-icon{{font-size:32px;margin-bottom:4px;}}
.card-name{{font-size:18px;font-weight:900;color:#fff;line-height:1.1;}}
.card-en{{font-size:8px;color:rgba(255,255,255,0.35);letter-spacing:1.5px;margin:3px 0 8px;}}
.card-tags{{display:flex;gap:4px;flex-wrap:wrap;margin-bottom:6px;}}
.tag{{
  background:rgba(0,0,0,0.25);
  border-radius:4px;padding:3px 6px;
  font-size:9px;color:rgba(255,255,255,0.8);font-weight:600;
}}
.card-rule{{font-size:9px;color:rgba(255,255,255,0.5);margin-top:auto;}}
/* NPC 투어·인바디 오버레이 */
.pb{{position:relative;overflow:hidden;}}
.npc-ov{{
  position:absolute;top:0;left:0;right:0;bottom:0;
  border-radius:18px;
  background:rgba(0,0,0,0.87);
  display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  opacity:0;pointer-events:none;
  transition:opacity 0.32s ease;
  z-index:10;padding:14px 12px;text-align:center;
}}
.npc-ov.tour-active{{opacity:1;pointer-events:none;}}
/* npc-inbody-on disabled */
.npc-sk{{font-size:26px;margin-bottom:6px;animation:skPulse 0.85s ease-in-out infinite;}}
@keyframes skPulse{{0%,100%{{transform:scale(1);}}50%{{transform:scale(1.2);}}}}
.npc-tx{{font-size:12px;font-weight:900;color:#fff;line-height:1.6;text-shadow:0 0 10px rgba(255,255,255,0.5);}}
.npc-stat{{font-size:11px;font-weight:700;color:rgba(255,220,80,1);margin-top:5px;line-height:1.5;}}
/* NPC 카드 오버레이 */
.npc-ov{{
  position:absolute;top:0;left:0;right:0;bottom:0;
  border-radius:18px;
  background:rgba(0,0,0,0.82);
  display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  opacity:0;pointer-events:none;
  transition:opacity 0.28s;
  z-index:10;padding:20px;text-align:center;
}}
.card.npc-on .npc-ov{{opacity:1;pointer-events:none;}}
.pb.npc-on .npc-ov{{opacity:1;pointer-events:none;}}
.npc-sk{{font-size:34px;margin-bottom:10px;animation:skPulse 0.9s ease-in-out infinite;}}
@keyframes skPulse{{0%,100%{{transform:scale(1);}}50%{{transform:scale(1.3);}}}}
.npc-tx{{
  font-size:13px;font-weight:900;color:#fff;
  line-height:1.6;letter-spacing:0.3px;
  text-shadow:0 0 14px rgba(255,255,255,0.7);
}}

/* ── 출격 버튼 바 ── */
.go-bar{{
  background:rgba(0,0,0,0.3);
  padding:10px 12px;
  display:flex;align-items:center;justify-content:space-between;
}}
.go-stat{{font-size:11px;color:rgba(255,255,255,0.6);font-weight:700;}}
.go-btn{{
  background:rgba(255,255,255,0.92);
  border-radius:10px;
  padding:8px 14px;
  font-size:12px;font-weight:900;color:#111;
  white-space:nowrap;
}}

/* ── 포로사령부 가로형 ── */
.pow-left{{flex:1;padding:14px 12px;}}
.pow-right{{
  padding:12px 14px 12px 0;
  display:flex;flex-direction:column;
  align-items:flex-end;justify-content:center;gap:6px;
}}
.pow-n{{font-size:28px;font-weight:900;color:#fff;line-height:1;text-align:right;}}
.pow-l{{font-size:8px;color:rgba(255,255,255,0.4);text-align:right;}}
.pow-go{{
  background:rgba(255,255,255,0.92);
  border-radius:10px;padding:8px 14px;
  font-size:12px;font-weight:900;color:#111;
}}

@keyframes pulse{{
  0%,100%{{opacity:1;}} 50%{{opacity:0.7;}}
}}
.pb-btn{{animation:pulse 2s ease-in-out infinite;}}
</style>

<!-- ★ HUD 상단바 -->
<div class="topbar">
  <img class="tb-photo" src="data:image/jpeg;base64,{TEACHER_B64}" alt="최샘">
  <span class="tb-brand">⚡ SNAPQ</span>
  <span class="tb-sep">|</span>
  <span class="tb-name">👤 {student_name}</span>
  <span class="tb-sep">|</span>
  <span class="tb-item">📅 {att_days}일</span>
  <span class="tb-sep">|</span>
  <span class="tb-item">⏱ {total_time}</span>
  <span class="tb-sep">|</span>
  <span class="tb-rank">🔥 {ranking}</span>
  <span class="tb-sep">|</span>
  <span class="tb-msg">{_welcome_short}</span>
</div>

<!-- 포로수용소 바 -->
<div class="pb"
  onclick="{_goto('PRISON_GO')}">
<div class="npc-ov" style="border-radius:14px;"><div class="npc-sk">💀</div><div class="npc-tx">틀린 단어들이 여기 갇혔어.<br>3번 연속 맞혀야 석방.<br>모르면 평생 여기야.</div></div>
<div class="npc-ov" id="ov-pb-a" style="border-radius:14px;"><div class="npc-sk">💀</div><div class="npc-tx">화력전·암호해독에서 틀린 단어들.<br>여기 다 갇혔어.<br>3번 연속 맞혀야 석방!</div><div class="npc-stat">{_npc_pb_stat}</div></div><div class="npc-ov" id="ov-pb-b" style="border-radius:14px;"><div class="npc-sk">💀</div><div class="npc-tx">화력전·암호해독에서 네가 모른 단어들.<br>여기 다 있어.<br>외울 때까지 절대 못 나가.</div><div class="npc-stat">{_npc_pb_stat}</div></div>
  <div class="pb-left">
    <div class="pb-icon">💀</div>
    <div>
      <div class="pb-name">단어 포로수용소</div>
      <div style="font-size:9px;color:#aa88dd;margin-top:1px;font-weight:600;">틀린 단어를 가두고 · 외울 때까지 석방 금지!</div>
      <div class="pb-sub">{_pr_badge_txt}</div>
      <div style="font-size:10px;margin-top:3px;">
        <span style="color:#ff8833;font-weight:700;">⚡ 화력전 {_pr_p5}명</span>
        <span style="color:#445566;margin:0 4px;">·</span>
        <span style="color:#00ccee;font-weight:700;">📡 암호해독 {_pr_p7}명</span>
      </div>
    </div>
  </div>
  <div class="pb-btn">심문 →</div>
</div>

<!-- 전장 그리드 -->
<div class="grid">

  <!-- ⚡ 화력전 -->
  <div class="card card-p5"
    onclick="{_goto('P5_GO')}">
<div class="npc-ov"><div class="npc-sk">⚡</div><div class="npc-tx">속도가 전부야.<br>5문제, 3개 생존.<br>불처럼 밀어붙여!</div></div>
<div class="npc-ov" id="ov-p5-a"><div class="npc-sk">⚡</div><div class="npc-tx">{_npc_p5_tx}</div><div class="npc-stat">{_npc_p5_stat}</div></div><div class="npc-ov" id="ov-p5-b"><div class="npc-sk">⚡</div><div class="npc-tx">문법·어휘 전장.<br>불처럼 밀어붙여.<br>5문제 3개 생존.<br>느리면 죽는다!</div><div class="npc-stat">{_npc_p5_stat}</div></div>
    <div class="card-body">
      <div class="badge">문법·어휘 실전훈련</div>
      <img src="data:image/png;base64,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" style="width:50px;height:50px;border-radius:50%;margin:4px 0;">
      <div class="card-name">화력전</div>
      <div class="card-en">FIREPOWER</div>
      <div class="card-tags">
        <span class="tag">문법</span>
        <span class="tag">어휘</span>
        <span class="tag">5문제</span>
      </div>
      <div class="card-rule">💀 5문제 중 3개↑ 맞아야 생존</div>
    </div>
    <div class="go-bar">
      <div class="go-stat">{_p5_disp}</div>
      <div class="go-btn">출격 ▶</div>
    </div>
  </div>

  <!-- 📡 암호해독 -->
  <div class="card card-p7"
    onclick="{_goto('P7_GO')}">
<div class="npc-ov"><div class="npc-sk">📡</div><div class="npc-tx">지문 해독 임무.<br>단 1번 오판 = 즉시 철수.<br>집중해.</div></div>
<div class="npc-ov" id="ov-p7-a"><div class="npc-sk">📡</div><div class="npc-tx">{_npc_p7_tx}</div><div class="npc-stat">{_npc_p7_stat}</div></div><div class="npc-ov" id="ov-p7-b"><div class="npc-sk">📡</div><div class="npc-tx">적군 문서 해독.<br>지문 속 단서가 답이야.<br>읽어야 산다.</div><div class="npc-stat">{_npc_p7_stat}</div></div>
    <div class="card-body">
      <div class="badge">TOEIC 독해 훈련</div>
      <img src="data:image/png;base64,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" style="width:50px;height:50px;border-radius:50%;margin:4px 0;">
      <div class="card-name">암호해독</div>
      <div class="card-en">DECRYPT OP</div>
      <div class="card-tags">
        <span class="tag">해독</span>
        <span class="tag">3문제</span>
        <span class="tag">즉사</span>
      </div>
      <div class="card-rule">☠ 한 번 틀리면 즉시 철수</div>
    </div>
    <div class="go-bar">
      <div class="go-stat">{_p7_disp}</div>
      <div class="go-btn">출격 ▶</div>
    </div>
  </div>

  <!-- 💀 포로사령부 (BOSS) -->
  <div class="card card-pow"
    onclick="{_goto('ARM_GO')}">
<div class="npc-ov"><div class="npc-sk">💀</div><div class="npc-tx">네가 틀린 문제들이<br>여기 갇혔어.<br>완전히 외울 때까지 석방 없음.</div></div>
<div class="npc-ov" id="ov-pow-a"><div class="npc-sk">💀</div><div class="npc-tx">{_npc_pow_tx}</div><div class="npc-stat">{_npc_pow_stat}</div></div><div class="npc-ov" id="ov-pow-b"><div class="npc-sk">💀</div><div class="npc-tx">화력전서 놓친 문법.<br>암호해독서 못 읽은 문장.<br>다 여기 있어. 이번엔 정복해.</div><div class="npc-stat">{_npc_pow_stat}</div></div>
    <div class="pow-left">
      <div class="badge" style="background:rgba(255,255,255,0.15);">BOSS STAGE</div>
      <div style="font-size:22px;margin:4px 0 2px;">💀</div>
      <div class="card-name">포로사령부</div>
      <div class="card-en">POW HEADQUARTERS</div>
      <div style="font-size:9px;color:rgba(255,255,255,0.5);margin:2px 0 4px;font-weight:600;">💀 틀린 문제가 무기가 된다</div>
      <div class="card-tags">
        <span class="tag">틀린 문제 복습</span>
        <span class="tag">단어 퀴즈</span>
        <span class="tag">완전 정복</span>
      </div>
    </div>
    <div class="pow-right">
      <div>
        <div class="pow-n">{_pr_total}</div>
        <div class="pow-l">포로 수감중</div>
      </div>
      <div class="pow-go">입장 ▶</div>
    </div>
  </div>

</div>



<script>
(function(){{
  var allOvs=document.querySelectorAll('.npc-ov');
  allOvs.forEach(function(el){{
    var t=el.querySelector('.npc-tx');if(t)t.style.display='none';
    var s=el.querySelector('.npc-stat');if(s)s.style.display='block';
  }});
  document.querySelectorAll('.card,.pb').forEach(function(el){{
    /* hover overlay disabled */
  }});
}})();
</script>

<script>
(function(){{
  var allOvs=document.querySelectorAll('.npc-ov');
  allOvs.forEach(function(el){{
    var t=el.querySelector('.npc-tx');if(t)t.style.display='none';
    var s=el.querySelector('.npc-stat');if(s)s.style.display='block';
  }});
  document.querySelectorAll('.card,.pb').forEach(function(el){{
    /* hover overlay disabled */
  }});
}})();
</script>
"""

_hc.html(_IOS_FIX + _GRID_HTML, height=580)


_hc.html("""
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,sans-serif;}
.row{display:flex;gap:8px;padding:2px 0 6px;}
.box{flex:1;border-radius:10px;padding:6px 0;display:flex;flex-direction:column;
     align-items:center;justify-content:center;gap:3px;}
.box-p4{background:rgba(255,255,255,0.05);border:1.5px solid rgba(255,255,255,0.1);cursor:default;}
.box-adm{background:rgba(255,255,255,0.07);border:1.5px solid rgba(255,255,255,0.18);
         cursor:pointer;transition:background 0.2s;}
.box-adm:hover{background:rgba(255,255,255,0.15);}
.box-adm:active{background:rgba(255,255,255,0.22);}
.ico{font-size:0.9rem;}
.lbl{font-size:0.6rem;font-weight:700;color:rgba(255,255,255,0.45);}
.lbl-adm{color:rgba(255,255,255,0.65);}
</style>
<div class="row">
  <div class="box box-p4">
    <div class="ico">🎵</div>
    <div class="lbl">P4 Coming Soon</div>
  </div>
  <div class="box box-adm" id="admBox" onclick="goAdmin()" style="display:none;">
    <div class="ico">🔒</div>
    <div class="lbl lbl-adm">관리자 전용</div>
  </div>
</div>
<script>
// v13: 선생님(admin_CJE)일 때만 관리자 박스 표시
(function checkAdminVisibility(){
    try {
        var nicknameEl = document.querySelector('[data-testid="stMarkdownContainer"]');
        var bodyText = document.body.innerText || '';
        // nickname이 admin_CJE로 시작하면 관리자 박스 표시
        if (bodyText.indexOf('admin_CJE') !== -1 || bodyText.indexOf('최정은_ADMIN') !== -1) {
            var admBox = document.getElementById('admBox');
            if (admBox) { admBox.style.display = ''; }
        }
    } catch(e) { console.log('admin check error:', e); }
})();
// 500ms 후에 다시 한 번 체크 (Streamlit 렌더링 지연 대응)
setTimeout(function(){
    try {
        var bodyText = document.body.innerText || '';
        if (bodyText.indexOf('admin_CJE') !== -1 || bodyText.indexOf('최정은_ADMIN') !== -1) {
            var admBox = document.getElementById('admBox');
            if (admBox) { admBox.style.display = ''; }
        }
    } catch(e) {}
}, 500);

function goAdmin(){
  window.parent.document.querySelectorAll('button').forEach(b=>{
    if((b.innerText||'').trim()==='ADMIN_GO') b.click();
  });
}
function hideBtn(){
  try {
    window.parent.document.querySelectorAll('button').forEach(b=>{
      const t=(b.innerText||'').trim();
      if(t==='ADMIN_GO'||t==='P5_GO'||t==='P7_GO'||t==='ARM_GO'||t==='PRISON_GO'){
        const w=b.closest('[data-testid="stButton"]');
        if(w) w.style.cssText='position:absolute;opacity:0;pointer-events:none;height:0;overflow:hidden;';
      }
    });
    // iOS용 — 이전 리스너 제거 후 매번 새로 등록 (홈 재진입 시에도 정상 동작)
    if(window.parent._snapq_ios_handler){
      window.parent.removeEventListener('message', window.parent._snapq_ios_handler);
    }
    window.parent._snapq_ios_handler = function(e){
      try {
        var d = (typeof e.data==='string') ? JSON.parse(e.data) : e.data;
        if(!d || d.action!=='goto') return;
        var map = {p5:'P5_GO', p7:'P7_GO', arm:'ARM_GO'};
        var target = map[d.page];
        if(!target) return;
        window.parent.document.querySelectorAll('button').forEach(function(b){
          var t=(b.innerText||b.textContent||'').trim();
          if(t===target){ b.style.pointerEvents='auto'; b.click(); }
        });
      } catch(err){}
    };
    window.parent.addEventListener('message', window.parent._snapq_ios_handler);
  } catch(ex){}
}
setTimeout(hideBtn,100);setTimeout(hideBtn,600);
new MutationObserver(hideBtn).observe(window.parent.document.body,{childList:true,subtree:true});
</script>
""", height=50)
