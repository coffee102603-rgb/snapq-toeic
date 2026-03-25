"""
SnapQ TOEIC V2 - Main Hub (새 디자인)
C안: 상단배너 + P5/P7 나란히 + 역전장 전체 + 하단 서브메뉴
"""

import streamlit as st
import os
import json
import time
from datetime import datetime, date
from pathlib import Path

from app.core.access_guard import require_access
from app.core.pretest_gate import require_pretest_gate
from app.core.attendance_engine import mark_attendance_once, has_attended_today
from app.core.battle_state import load_profile

st.set_page_config(
    page_title='SnapQ TOEIC',
    page_icon='⚡',
    layout='wide',
    initial_sidebar_state='collapsed'
)

# =========================================================
# 데이터 헬퍼
# =========================================================
BASE = Path(__file__).resolve().parent

def _get_month_key():
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

def _get_motivation(rate, logs, activity_type):
    """정답률/연속상승/오늘여부 기반 자극 멘트"""
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

def _calc_stats(nickname: str):
    """P5 정답률, P7 정답률, 역전장 P5/보카 정복률, 접속시간 계산"""
    logs = _load_research_logs(nickname)

    # P5 정답률
    p5_logs = [l for l in logs if l.get("activity_type") == "p5_answer"]
    p5_correct = sum(1 for l in p5_logs if l.get("is_correct"))
    p5_rate = round(p5_correct / len(p5_logs) * 100) if p5_logs else None

    # P7 정답률
    p7_logs = [l for l in logs if l.get("activity_type") == "p7_answer"]
    p7_correct = sum(1 for l in p7_logs if l.get("is_correct"))
    p7_rate = round(p7_correct / len(p7_logs) * 100) if p7_logs else None

    # 역전장 P5 정복률
    armory_p5 = [l for l in logs if l.get("activity_type") == "armory_p5"]
    armory_p5_rate = round(sum(1 for l in armory_p5 if l.get("is_correct")) / len(armory_p5) * 100) if armory_p5 else None

    # 역전장 보카 정복률
    armory_voca = [l for l in logs if l.get("activity_type") == "armory_voca"]
    armory_voca_rate = round(sum(1 for l in armory_voca if l.get("is_correct")) / len(armory_voca) * 100) if armory_voca else None

    # 역전장 전체 정복률
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

def _arrow(rate):
    if rate is None:
        return ""
    if rate >= 70:
        return "↑"
    elif rate >= 50:
        return "→"
    return "↓"

def _arrow_color(rate):
    if rate is None:
        return "#888"
    if rate >= 70:
        return "#00E5A0"
    elif rate >= 50:
        return "#FFD600"
    return "#FF4560"

def _mini_bar(rate):
    """간단한 바 그래프 HTML"""
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
def load_css():
    # 모바일 뷰포트 메타태그 - 휴대폰에서 올바른 크기로 표시
    st.markdown('<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">', unsafe_allow_html=True)
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Noto+Sans+KR:wght@400;700;900&display=swap');

    .stApp { background: #0A0C15 !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 0 8px 40px 8px !important; max-width: 860px !important; margin: 0 auto !important; }
    div[data-testid="stVerticalBlock"] > div { gap: 0 !important; margin: 0 !important; padding: 0 !important; }
    iframe { display: block !important; margin: 0 !important; padding: 0 !important; }

    /* 상단 배너 - 형광 반짝 테두리 */
    .top-banner {
        background: linear-gradient(135deg, rgba(124,92,255,0.2), rgba(0,229,160,0.15));
        border: 2px solid rgba(0,229,255,0.6);
        border-radius: 16px;
        padding: 14px 18px;
        margin: 12px 0 20px 0;
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
        padding: 14px 0 20px 0;
    }
    .hub-teacher-photo {
        width: 80px;
        height: 80px;
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
        font-size: 46px;
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
        margin-top: 4px;
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
        .hub-brand { gap: 10px; padding: 10px 0 14px 0; }
        .hub-teacher-photo { width: 60px; height: 60px; }
        .hub-title-text { font-size: 34px; letter-spacing: 2px; }
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
        .hub-brand { gap: 8px; padding: 8px 0 10px 0; }
        .hub-teacher-photo { width: 48px; height: 48px; border-width: 2px; }
        .hub-title-text { font-size: 26px; letter-spacing: 1px; }
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

# 로그인 + 검사 체크
nickname = require_access()
require_pretest_gate()

# 출석 자동 기록
mark_attendance_once(nickname)

# ══════════════════════════════════════════════════════════
# ★ viewport_width 자동 수집 (논문 07 KCI 핵심 — 선행연구 0건)
# window.innerWidth → URL query param → storage_data.json devices
# ══════════════════════════════════════════════════════════
import streamlit.components.v1 as _vp_cmp
_vp_cmp.html("""
<script>
(function(){
    try {
        var vw = window.innerWidth;
        var url = new URL(window.parent.location.href);
        if(!url.searchParams.get('vw') || url.searchParams.get('vw') !== String(vw)){
            url.searchParams.set('vw', vw);
            window.parent.history.replaceState({}, '', url.toString());
        }
    } catch(e){}
})();
</script>
""", height=0)

# viewport_width를 devices storage에 저장
try:
    _vw_raw = st.query_params.get("vw", None)
    if _vw_raw and not st.session_state.get("_vw_saved_" + nickname):
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
student_name = nickname.split('_')[0] if '_' in nickname else nickname

# =========================================================
# 상단 배너
# =========================================================
st.markdown(f"""
<div class="top-banner">
    <span class="banner-name">⚡ {student_name}</span>
    <span class="banner-divider">|</span>
    <span class="banner-item">📅 출석 {att_days}일</span>
    <span class="banner-divider">|</span>
    <span class="banner-item">⏱ {total_time}</span>
    <span class="banner-divider">|</span>
    <span class="banner-rank">🔥 전투참여도 {ranking}</span>
</div>
""", unsafe_allow_html=True)

# =========================================================
# 타이틀 + 브랜딩
# =========================================================
TEACHER_B64 = "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"

st.markdown(f"""
<div class="hub-brand">
    <img class="hub-teacher-photo" 
         src="data:image/jpeg;base64,{TEACHER_B64}"
         alt="최샘"/>
    <div class="hub-brand-text">
        <div class="hub-title-text">⚡ SnapQ TOEIC</div>
        <div class="hub-subtitle">by Crazy 최샘 · HACKERS</div>
        <div class="hub-platform">BATTLE LOBBY · 전장을 선택하세요</div>
    </div>
</div>
""", unsafe_allow_html=True)

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
if _is_first_check:
    _hc.html(f"""
<style>
*{{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,sans-serif;}}
@keyframes wi{{0%{{opacity:0;transform:translateY(8px);}}100%{{opacity:1;transform:translateY(0);}}}}
.wel{{background:linear-gradient(135deg,rgba(0,200,100,0.15),rgba(0,100,255,0.15));
      border:1.5px solid rgba(0,220,120,0.35);border-radius:12px;
      padding:7px 14px;animation:wi 0.4s ease forwards;display:flex;align-items:center;gap:8px;}}
.wt{{font-size:0.88rem;font-weight:900;color:#fff;white-space:nowrap;}}
.ws{{font-size:0.78rem;color:rgba(255,255,255,0.55);}}
</style>
<div class="wel">
  <div class="wt">👋 반가워요, {student_name}님!</div>
  <div class="ws">🔥 첫판 · 지금 바로 시작!</div>
</div>""", height=36)
else:
    _total = p5_count + p7_count
    _hc.html(f"""
<style>
*{{box-sizing:border-box;margin:0;padding:0;font-family:-apple-system,sans-serif;}}
@keyframes wi{{0%{{opacity:0;transform:translateY(8px);}}100%{{opacity:1;transform:translateY(0);}}}}
.wel{{background:linear-gradient(135deg,rgba(255,100,0,0.12),rgba(200,0,255,0.12));
      border:1.5px solid rgba(255,150,0,0.3);border-radius:12px;
      padding:7px 14px;animation:wi 0.4s ease forwards;display:flex;align-items:center;gap:8px;}}
.wt{{font-size:0.88rem;font-weight:900;color:#fff;white-space:nowrap;}}
.ws{{font-size:0.78rem;color:rgba(255,255,255,0.55);}}
</style>
<div class="wel">
  <div class="wt">🔥 다시 왔군요, {student_name}님!</div>
  <div class="ws">💥 {_total}문제 완료 · 오늘도 한 판 더!</div>
</div>""", height=36)

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
# 역전장 로테이션 멘트
_ARM_ROT = [
    ("반복 P5문제 · 33초 · 5문제", "반복 P7어휘 · 44초 · 10문제", "🗡️ 오답 설욕전! 토익 역전! 인생 역전!"),
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
def _trend(logs, activity_type):
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
    _p5_s1_big  = f"⚡ P5전장"
    _p5_s1_lbl  = "문법·어휘 속도전!"
    _p7_s1_big  = f"📖 P7전장"
    _p7_s1_lbl  = "독해 · 읽는 뇌를 깨워라!"
    _arm_s1_big = f"🔥 오답전장"
    _arm_s1_lbl = "틀린 문제가 무기가 된다"
    _p5_s2_big  = "3개↑ 생존"
    _p5_s2_lbl  = "30초 · 5문제 · 미만 전멸"
    _p7_s2_big  = "1오답 즉사"
    _p7_s2_lbl  = "60초 · 3문제 · 시간초과 즉사"
    _arm_s2_big = "저장→반복"
    _arm_s2_lbl = "틀린 문제가 무기가 된다"
    _p5_s3  = "⚡ 5문제 중 3개↑ 맞춰야 생존!"
    _p7_s3  = "📖 오답 1개 즉사 · 시간초과 즉사"
    _arm_s3 = "🔥 저장 → 반복 → 완전 정복!"
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
.p5c{background:linear-gradient(145deg,#001f55,#0055bb,#0099ee);}
.p7c{background:linear-gradient(145deg,#220044,#6600bb,#aa44ff);}
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

def _mk_card(cls, title, s1b, s1l, s1svg, s2b, s2l, s2svg, s3mot, page=""):
    _js = f"window.parent.postMessage({{action:'goto',page:'{page}'}},'*')" if page else ""
    return f"""<div class="card {cls}"
  onclick="{_js}"
  ontouchend="{_js};event.preventDefault();"
  ontouchstart=""
  style="cursor:pointer;touch-action:manipulation;-webkit-tap-highlight-color:transparent;">
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

# ── P5 ──
_hc.html(_CSS + _GO_STYLE + "<style>.p5c .go-btn{--go-bg:linear-gradient(270deg,#1565c0,#4fc3f7,#0d47a1,#29b6f6);--go-border:rgba(79,195,247,0.9);}</style>" + _mk_card("p5c","⚡ P5 전장",
    _p5_s1_big,_p5_s1_lbl,_p5_rate_svg,
    _p5_s2_big,_p5_s2_lbl,_p5_cnt_svg,_p5_s3, page="p5") + """
<button class="go-btn" style="background:linear-gradient(270deg,#1565c0,#4fc3f7,#0d47a1,#29b6f6);border-color:rgba(79,195,247,0.9);" onclick="window.parent.postMessage({action:'goto',page:'p5'},'*')" ontouchend="window.parent.postMessage({action:'goto',page:'p5'},'*');event.preventDefault();" ontouchstart="">⚡</button>
<script>
(function(){
  var h=window.innerWidth<=480?70:window.innerWidth<=768?100:140;
  document.querySelector('.card').style.height=h+'px';
})();
</script>""", height=70)
_p5_go = st.button("P5_GO", key="p5_btn")
if _p5_go:
    st.session_state.phase = "lobby"
    st.session_state._p5_active = False
    st.switch_page("pages/02_P5_Arena.py")

# ★ postMessage 리스너 — iOS Safari 포함 모든 기기에서 카드 클릭 수신
import streamlit.components.v1 as _msg_cmp
_msg_cmp.html("""<script>
(function(){
  window.addEventListener('message', function(e){
    try {
      var d = e.data;
      if(!d || d.action !== 'goto') return;
      var target = {p5:'P5_GO', p7:'P7_GO', arm:'ARM_GO'}[d.page];
      if(!target) return;
      var btns = window.parent.document.querySelectorAll('button');
      for(var i=0;i<btns.length;i++){
        if((btns[i].innerText||btns[i].textContent||'').trim()===target){
          btns[i].click(); break;
        }
      }
    } catch(err){}
  });
})();
</script>""", height=0)


# ── P7 ──
_hc.html(_CSS + _GO_STYLE + "<style>.p7c .go-btn{--go-bg:linear-gradient(270deg,#6a1b9a,#ce93d8,#4a148c,#ab47bc);--go-border:rgba(155,127,212,0.9);}</style>" + _mk_card("p7c","📖 P7 전장",
    _p7_s1_big,_p7_s1_lbl,_p7_rate_svg,
    _p7_s2_big,_p7_s2_lbl,_p7_cnt_svg,_p7_s3, page="p7") + """
<button class="go-btn" style="background:linear-gradient(270deg,#6a1b9a,#ce93d8,#4a148c,#ab47bc);border-color:rgba(155,127,212,0.9);" onclick="window.parent.postMessage({action:'goto',page:'p7'},'*')" ontouchend="window.parent.postMessage({action:'goto',page:'p7'},'*');event.preventDefault();" ontouchstart="">📖</button>
<script>
(function(){
  var h=window.innerWidth<=480?70:window.innerWidth<=768?100:140;
  document.querySelector('.card').style.height=h+'px';
})();
</script>""", height=70)
_p7_go = st.button("P7_GO", key="p7_btn")
if _p7_go:
    if "p7_phase" in st.session_state:
        st.session_state.p7_phase = "lobby"
    st.switch_page("pages/04_P7_Reading.py")


# ── 역전장 ──
_hc.html(_CSS + _GO_STYLE + "<style>.arc .go-btn{--go-bg:linear-gradient(270deg,#e65100,#ffd54f,#bf360c,#ffca28);--go-border:rgba(255,215,0,0.95);}</style>" + _mk_card("arc","🔥 오답전장",
    _arm_s1_big,_arm_s1_lbl,_arm_p5_svg,
    _arm_s2_big,_arm_s2_lbl,_arm_vc_svg,_arm_s3, page="arm") + """
<button class="go-btn" style="background:linear-gradient(270deg,#e65100,#ffd54f,#bf360c,#ffca28);border-color:rgba(255,215,0,0.95);" onclick="window.parent.postMessage({action:'goto',page:'arm'},'*')" ontouchend="window.parent.postMessage({action:'goto',page:'arm'},'*');event.preventDefault();" ontouchstart="">🗡️</button>
<script>
(function(){
  var h=window.innerWidth<=480?70:window.innerWidth<=768?100:140;
  document.querySelector('.card').style.height=h+'px';
})();
</script>""", height=70)
_arm_go = st.button("ARM_GO", key="armory_btn")
if _arm_go:
    st.switch_page("pages/03_오답전장.py")


# ── 하단 박스 2개 ──
_adm_go = st.button("ADMIN_GO", key="admin_go_btn")
if _adm_go:
    st.switch_page("pages/01_Admin.py")

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
  <div class="box box-adm" onclick="goAdmin()">
    <div class="ico">🔒</div>
    <div class="lbl lbl-adm">관리자 전용</div>
  </div>
</div>
<script>
function goAdmin(){
  window.parent.document.querySelectorAll('button').forEach(b=>{
    if((b.innerText||'').trim()==='ADMIN_GO') b.click();
  });
}
function hideBtn(){
  window.parent.document.querySelectorAll('button').forEach(b=>{
    const t=(b.innerText||'').trim();
    if(t==='ADMIN_GO'||t==='P5_GO'||t==='P7_GO'||t==='ARM_GO'){
      const w=b.closest('[data-testid="stButton"]');
      if(w) w.style.cssText='position:absolute;opacity:0;pointer-events:none;height:0;overflow:hidden;';
    }
  });
}
setTimeout(hideBtn,100);setTimeout(hideBtn,600);
new MutationObserver(hideBtn).observe(window.parent.document.body,{childList:true,subtree:true});
</script>
""", height=50)
