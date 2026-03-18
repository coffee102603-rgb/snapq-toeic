"""
SnapQ TOEIC V2 - Main Hub (새 디자인)
C안: 상단배너 + P5/P7 나란히 + 역전장 전체 + 하단 서브메뉴
"""

import streamlit as st

# iOS Safari 호환
_IOS_CSS = True
# iOS Safari Chrome 유도
import streamlit.components.v1 as _components
_components.html("""
<script>
var ua = navigator.userAgent;
var isIOS = /iPad|iPhone|iPod/.test(ua);
var isSafari = /Safari/.test(ua) && !/Chrome/.test(ua) && !/CriOS/.test(ua);
if (isIOS && isSafari) {
    document.body.style.overflow = 'hidden';
    var div = document.createElement('div');
    div.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.95);z-index:99999;display:flex;align-items:center;justify-content:center;';
    div.innerHTML = '<div style="background:#1a1a2e;border:2px solid #ff8800;border-radius:20px;padding:30px 20px;text-align:center;max-width:300px;">'
        + '<div style="font-size:2rem;margin-bottom:8px;">⚠️</div>'
        + '<div style="color:#ff8800;font-size:1.1rem;font-weight:900;margin-bottom:8px;">Safari는 지원 안 됩니다!</div>'
        + '<div style="color:#fff;font-size:0.9rem;margin-bottom:16px;line-height:1.6;">아이폰에서는<br><b style=\"color:#ff8800\">Chrome 브라우저</b>로<br>접속해주세요! 🙏</div>'
        + '<a href=\"googlechrome://snapq-toeic.onrender.com\" style=\"display:block;background:#ff8800;color:#fff;padding:12px;border-radius:12px;font-weight:900;font-size:0.95rem;text-decoration:none;margin-bottom:8px;\">📱 Chrome으로 열기</a>'
        + '<div style=\"color:#aaa;font-size:0.75rem;\">Chrome 없으면 App Store에서 설치!</div>'
        + '</div>';
    document.body.appendChild(div);
}
</script>
""", height=0)

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
    layout='centered',
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
    

# =========================================================
# 메인
# =========================================================
load_css()

# 로그인 + 검사 체크
nickname = require_access()
require_pretest_gate()

# 출석 자동 기록
mark_attendance_once(nickname)

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
    <img class="hub-teacher-photo" style="width:72px;height:72px;border-radius:50%;"
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
    ("아직도 느리냐?", "전쟁터엔 핑계 없다!", "⚡ 30초 · 5문제 · 지금 바로!"),
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
    _p5_s1_big  = f"{_sn}! 문법 속도전"
    _p5_s1_lbl  = "30초 · 5문제 · 지금 바로!"
    _p7_s1_big  = f"{_sn}! 독해 집중전"
    _p7_s1_lbl  = "60초 · 1지문 · 3문제!"
    _arm_s1_big = f"{_sn}! 설욕할 시간"
    _arm_s1_lbl = "오답 · 지금 없애라!"
    _p5_s2_big  = "아직도 망설여?"
    _p5_s2_lbl  = "전쟁터엔 핑계 없다!"
    _p7_s2_big  = "읽지도 않고 찍어?"
    _p7_s2_lbl  = "지문을 읽어라!"
    _arm_s2_big = "틀린 문제가 웃는다"
    _arm_s2_lbl = "네가 도망치는 중!"
    _p5_s3  = "⚡ 30초 · 5문제 · 지금 바로!"
    _p7_s3  = "📖 60초 · 1지문 · 지금 증명해!"
    _arm_s3 = "🗡️ 오답 설욕 · 토익 역전!"
else:
    _sn = student_name
    _p5_s1_big  = f"{p5_rate}%{_p5_trend}" if p5_rate is not None else f"{_sn}! 첫 도전"
    _p5_s1_lbl  = "7일 정답률"
    _p5_s2_big  = f"{p5_count}문제"
    _p5_s2_lbl  = "이번달 풀이"
    _p7_s1_big  = f"{p7_rate}%{_p7_trend}" if p7_rate is not None else f"{_sn}! 첫 도전"
    _p7_s1_lbl  = "7일 정답률"
    _p7_s2_big  = f"{p7_count}문제"
    _p7_s2_lbl  = "이번달 풀이"
    _arm_s1_big = f"{arm_pending}개" if arm_pending > 0 else "완벽!"
    _arm_s1_lbl = "🔥 오답 아직 남았다!" if arm_pending > 0 else "✅ 오답 제로!"
    _arm_s2_big = f"{arm_p5}%" if arm_p5 is not None else "—"
    _arm_s2_lbl = "정복률"
    _p5_s3  = _p5_rot[2]
    _p7_s3  = _p7_rot[2]
    _arm_s3 = f"🔥 {arm_pending}개 남았다! 지금 없애라!" if arm_pending > 0 else "✅ 다 잡았다! 완벽!" 

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

def _mk_card(cls, title, s1b, s1l, s1svg, s2b, s2l, s2svg, s3mot):
    return f"""<div class="card {cls}">
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
    _p5_s2_big,_p5_s2_lbl,_p5_cnt_svg,_p5_s3) + """
<button class="go-btn" style="background:linear-gradient(270deg,#1565c0,#4fc3f7,#0d47a1,#29b6f6);border-color:rgba(79,195,247,0.9);" onclick="window.parent.document.querySelectorAll('button').forEach(b=>{if((b.innerText||'').trim()==='P5_GO')b.click()})">⚡</button>
""", height=70)
_p5_go = st.button("P5_GO", key="p5_btn")
if _p5_go:
    st.session_state.phase = "lobby"
    st.session_state._p5_active = False
    st.switch_page("pages/02_P5_Arena.py")


# ── P7 ──
_hc.html(_CSS + _GO_STYLE + "<style>.p7c .go-btn{--go-bg:linear-gradient(270deg,#6a1b9a,#ce93d8,#4a148c,#ab47bc);--go-border:rgba(155,127,212,0.9);}</style>" + _mk_card("p7c","📖 P7 전장",
    _p7_s1_big,_p7_s1_lbl,_p7_rate_svg,
    _p7_s2_big,_p7_s2_lbl,_p7_cnt_svg,_p7_s3) + """
<button class="go-btn" style="background:linear-gradient(270deg,#6a1b9a,#ce93d8,#4a148c,#ab47bc);border-color:rgba(155,127,212,0.9);" onclick="window.parent.document.querySelectorAll('button').forEach(b=>{if((b.innerText||'').trim()==='P7_GO')b.click()})">📖</button>
""", height=70)
_p7_go = st.button("P7_GO", key="p7_btn")
if _p7_go:
    if "p7_phase" in st.session_state:
        st.session_state.p7_phase = "lobby"
    st.switch_page("pages/04_P7_Reading.py")


# ── 역전장 ──
_hc.html(_CSS + _GO_STYLE + "<style>.arc .go-btn{--go-bg:linear-gradient(270deg,#e65100,#ffd54f,#bf360c,#ffca28);--go-border:rgba(255,215,0,0.95);}</style>" + _mk_card("arc","🗡️ 역전장",
    _arm_s1_big,_arm_s1_lbl,_arm_p5_svg,
    _arm_s2_big,_arm_s2_lbl,_arm_vc_svg,_arm_s3) + """
<button class="go-btn" style="background:linear-gradient(270deg,#e65100,#ffd54f,#bf360c,#ffca28);border-color:rgba(255,215,0,0.95);" onclick="window.parent.document.querySelectorAll('button').forEach(b=>{if((b.innerText||'').trim()==='ARM_GO')b.click()})">🗡️</button>
""", height=70)
_arm_go = st.button("ARM_GO", key="armory_btn")
if _arm_go:
    st.switch_page("pages/03_역전장.py")


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
