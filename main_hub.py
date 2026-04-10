"""
SnapQ TOEIC - Main Hub (개인화 피드백 시스템 탑재)
- Day 1: 전장 소개 투어
- Day 2~: 데이터 기반 개인화 피드백 (정답률, 약점, 강점, 파이팅)
- 월별 순위 표시
"""

import streamlit as st
import os, sys, json, random, re
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(
    page_title="SnapQ TOEIC",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── 공통 모듈 ──
try:
    import _storage
    from app.core.access_guard import require_access
    from app.core.pretest_gate import require_pretest_gate
    from app.core.attendance_engine import mark_attendance_once, has_attended_today
except Exception:
    st.error("모듈 로드 실패 — pages/ 폴더 확인 필요")
    st.stop()

# ══════════════════════════════════════════
# ★ 개인화 피드백 함수
# ══════════════════════════════════════════

CAT_KR = {
    "수동태/수일치": "수동태·수일치",
    "시제": "시제",
    "가정법": "가정법",
    "분사/동명사": "분사·동명사",
    "접속사/전치사": "접속사·전치사",
    "관사/명사": "관사·명사",
    "어휘": "어휘",
    "VOCAB": "어휘",
    "GRM": "문법",
    "FORM": "어형",
    "LINK": "연결어",
}

def _kr_cat(c):
    return CAT_KR.get(c, c)

def get_user_stats(nickname):
    """rt_logs + zpd_logs + word_prison 기반 개인 통계 추출"""
    try:
        data = _storage.load()
    except Exception:
        return None

    uid = nickname.strip()

    # ── rt_logs 분석 ──
    all_rt = data.get("rt_logs", [])
    user_rt = [r for r in all_rt if r.get("user_id", "").strip() == uid]
    if not user_rt:
        return None

    total   = len(user_rt)
    correct = sum(1 for r in user_rt if r.get("is_correct"))
    accuracy = round(correct / total * 100, 1) if total > 0 else 0

    # 카테고리별 정답률
    cat_stats = {}
    for r in user_rt:
        cat = r.get("cat", "기타")
        if not cat: cat = "기타"
        if cat not in cat_stats:
            cat_stats[cat] = {"total": 0, "correct": 0}
        cat_stats[cat]["total"] += 1
        if r.get("is_correct"):
            cat_stats[cat]["correct"] += 1

    cat_acc = {
        c: round(v["correct"] / v["total"] * 100, 1)
        for c, v in cat_stats.items() if v["total"] >= 3
    }
    weak   = min(cat_acc, key=cat_acc.get) if cat_acc else None
    strong = max(cat_acc, key=cat_acc.get) if cat_acc else None

    # 오답 타이밍 분포
    timing_counts = {"fast_wrong": 0, "mid_wrong": 0, "slow_wrong": 0}
    for r in user_rt:
        t = r.get("error_timing_type")
        if t in timing_counts:
            timing_counts[t] += 1

    # 첫 접속일 계산
    start_key = f"{uid}_start_date"
    today_str = datetime.now().strftime("%Y-%m-%d")
    first_date = data.get(start_key, today_str)
    try:
        day_count = (
            datetime.strptime(today_str, "%Y-%m-%d") -
            datetime.strptime(first_date,  "%Y-%m-%d")
        ).days + 1
    except Exception:
        day_count = 1

    # 포로 수
    word_prison = len(data.get("word_prison", []))
    saved_q     = len(data.get("saved_questions", []))

    # zpd_logs — 화력전 세션 수
    zpd = data.get("zpd_logs", [])
    user_zpd = [z for z in zpd if z.get("user_id", "").strip() == uid]
    sessions = len(user_zpd)

    # 이번 달 활동 (랭킹용)
    this_month = datetime.now().strftime("%Y-%m")
    month_rt = [r for r in all_rt if r.get("timestamp", "").startswith(this_month)]

    # 월별 순위 계산
    month_uid_correct = {}
    month_uid_total   = {}
    for r in month_rt:
        u = r.get("user_id", "").strip()
        if not u: continue
        month_uid_total[u]   = month_uid_total.get(u, 0) + 1
        if r.get("is_correct"):
            month_uid_correct[u] = month_uid_correct.get(u, 0) + 1

    month_acc = {
        u: round(month_uid_correct.get(u, 0) / t * 100, 1)
        for u, t in month_uid_total.items() if t >= 5
    }
    sorted_users = sorted(month_acc.items(), key=lambda x: -x[1])
    rank = next((i+1 for i, (u, _) in enumerate(sorted_users) if u == uid), None)
    total_users = len(sorted_users)

    return {
        "accuracy":      accuracy,
        "total":         total,
        "correct":       correct,
        "weak":          weak,
        "weak_acc":      cat_acc.get(weak, 0) if weak else 0,
        "strong":        strong,
        "strong_acc":    cat_acc.get(strong, 0) if strong else 0,
        "timing":        timing_counts,
        "day_count":     day_count,
        "word_prison":   word_prison,
        "saved_q":       saved_q,
        "sessions":      sessions,
        "rank":          rank,
        "total_users":   total_users,
        "month_acc":     month_acc.get(uid, 0),
    }


def make_npc_message(nickname, stats, is_tori):
    """데이터 기반 개인화 NPC 메시지 생성"""
    if stats is None:
        # 첫 접속 — 플랫폼 소개
        if is_tori:
            msgs = [
                f"{nickname}! 화력전 FIREPOWER에 온 걸 환영해!",
                f"5문제로 문법·어휘를 박살내는 전장이야!",
                f"3개 이상 맞히면 브리핑도 열려! 도전해봐!",
            ]
        else:
            msgs = [
                f"{nickname}! 암호해독 DECRYPT OP야!",
                f"비즈니스 독해 지문 3문제로 실력 측정!",
                f"한 번 틀리면 즉시 철수야. 집중해!",
            ]
        return random.choice(msgs), "🎖️"

    day  = stats["day_count"]
    acc  = stats["accuracy"]
    weak = stats["weak"]
    strong = stats["strong"]
    rank = stats["rank"]
    total_users = stats["total_users"]
    slow_wrong  = stats["timing"]["slow_wrong"]
    fast_wrong  = stats["timing"]["fast_wrong"]

    icon = "🔥" if is_tori else "📡"

    # Day 1~2: 격려 위주
    if day <= 2:
        candidates = [
            (f"{nickname}! 시작이 반이야. 계속 나와!", "💪"),
            (f"{nickname}! 첫 {day}일 — 잘 하고 있어!", "⚡"),
            (f"첫날부터 오다니 {nickname} 의지 불태우는데?!", "🔥"),
        ]
        return random.choice(candidates)

    # Day 3~: 데이터 기반 메시지
    candidates = []

    # 정답률 기반
    if acc >= 80:
        candidates.append((f"{nickname}! 정답률 {acc}%야. 완전 강해지고 있어!", "🏆"))
        candidates.append((f"정답률 {acc}%! 이 기세면 토익 900+ 간다!", "💎"))
    elif acc >= 60:
        candidates.append((f"{nickname}! 정답률 {acc}%. 딱 중간이야. 더 올려!", "📈"))
        candidates.append((f"{acc}%면 아직 아깝다. 80% 넘겨야 진짜야!", "⚔️"))
    else:
        candidates.append((f"정답률 {acc}%... {nickname}야, 지금 집중 안 되는 거야?", "😤"))
        candidates.append((f"{acc}%? 틀린 문제 포로사령부에서 다시 박살내!", "💀"))

    # 약점 기반
    if weak:
        w_kr = _kr_cat(weak)
        candidates.append((f"{nickname}! {w_kr} 계속 막히고 있어. 오늘 집중 공략 각!", "🎯"))
        candidates.append((f"{w_kr} 정답률 {stats['weak_acc']}%야. 약점이 보여, {nickname}!", "⚠️"))

    # 강점 기반
    if strong and stats["strong_acc"] >= 75:
        s_kr = _kr_cat(strong)
        candidates.append((f"{s_kr}은 {stats['strong_acc']}%! {nickname} 여기서만큼은 강자야!", "✨"))

    # 충동형 오답 기반
    if fast_wrong > slow_wrong and fast_wrong >= 5:
        candidates.append((f"{nickname}! 빨리 찍다가 틀리는 게 많아. 한 번 더 읽고!", "⏱️"))

    # 인지과부하형 오답 기반
    if slow_wrong >= 5:
        candidates.append((f"오래 고민해도 틀리는 문제들 있지? 포로사령부에 잡혀있어!", "🔒"))

    # 순위 기반
    if rank and total_users >= 3:
        if rank == 1:
            candidates.append((f"🥇 이번 달 {nickname} 1등! 이 기세 유지해!", "👑"))
        elif rank <= 3:
            candidates.append((f"이번 달 TOP {rank}! {nickname} 완전 날아가고 있잖아!", "🚀"))
        elif rank <= total_users // 2:
            candidates.append((f"이번 달 {rank}위/{total_users}명! 상위권 노려봐!", "📊"))

    if not candidates:
        candidates = [(f"{nickname}! 오늘도 출격 준비됐어?", "⚡")]

    return random.choice(candidates)


# ══════════════════════════════════════════
# ★ 메인 허브 렌더링
# ══════════════════════════════════════════

# 로그인 체크
nickname = require_access()
require_pretest_gate()
st.session_state["nickname"]        = nickname
st.session_state["battle_nickname"] = nickname

# 출석
attended_today = has_attended_today(nickname)
if not attended_today:
    mark_attendance_once(nickname)
    attended_today = True

# 통계 로드
stats = get_user_stats(nickname)

# ── CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
.stApp{background:#07080f!important;}
#MainMenu,header[data-testid="stHeader"],footer{visibility:hidden!important;height:0!important;}
.block-container{padding:8px 12px 20px!important;margin:0!important;max-width:100%!important;}
div[data-testid="stVerticalBlock"]{gap:6px!important;}
.element-container{margin:0!important;padding:0!important;}

/* HUD 헤더 */
.hud-bar{
  background:linear-gradient(135deg,#0d0d1a,#141428);
  border:1px solid rgba(0,200,255,0.2);
  border-radius:14px;padding:10px 14px;
  display:flex;align-items:center;justify-content:space-between;
  flex-wrap:wrap;gap:6px;margin-bottom:6px;
}
.hud-name{font-family:Orbitron,sans-serif;font-size:0.85rem;font-weight:900;
  color:#00ccee;letter-spacing:2px;}
.hud-item{font-size:0.7rem;color:#8899aa;font-weight:700;}
.hud-val{color:#ffdd44;font-weight:900;}

/* NPC 피드백 카드 */
.npc-card{
  background:linear-gradient(135deg,#0a0f1e,#101828);
  border:1.5px solid rgba(0,200,255,0.3);
  border-left:4px solid #00ccee;
  border-radius:14px;padding:12px 14px;margin-bottom:6px;
}
.npc-icon{font-size:1.8rem;margin-bottom:4px;display:block;text-align:center;}
.npc-msg{font-size:0.88rem;font-weight:800;color:#ddeeff;text-align:center;line-height:1.5;}

/* 통계 카드 */
.stat-row{display:flex;gap:8px;margin:6px 0;}
.stat-card{
  flex:1;background:#0d0d1a;border:1px solid rgba(255,255,255,0.08);
  border-radius:12px;padding:10px 8px;text-align:center;
}
.stat-val{font-size:1.4rem;font-weight:900;margin-bottom:2px;}
.stat-label{font-size:0.65rem;color:#8899aa;font-weight:700;}

/* 순위 배너 */
.rank-banner{
  background:linear-gradient(135deg,#1a0a00,#2a1400);
  border:1.5px solid #ff8833;border-radius:12px;
  padding:8px 14px;text-align:center;margin:4px 0 8px;
}
.rank-txt{font-size:0.85rem;font-weight:900;color:#ffaa44;}

/* 단어수용소 배너 */
.prison-banner{
  background:linear-gradient(135deg,#0a0018,#140828);
  border:1.5px solid #8833ff;border-left:4px solid #8833ff;
  border-radius:14px;padding:10px 14px;
  display:flex;align-items:center;justify-content:space-between;
}
.prison-left{font-size:0.82rem;color:#cc99ff;font-weight:800;line-height:1.6;}
.prison-count{font-size:1.6rem;font-weight:900;color:#aa55ff;text-align:right;}
.prison-sub{font-size:0.62rem;color:#664488;}

/* 전장 카드 */
.arena-fp{
  background:linear-gradient(135deg,#1a0800,#2a1200,#1a0800);
  border:1.5px solid rgba(255,100,0,0.4);
  border-radius:18px;padding:16px 14px 12px;margin:4px 0;
}
.arena-dc{
  background:linear-gradient(135deg,#001520,#002030,#001520);
  border:1.5px solid rgba(0,200,255,0.3);
  border-radius:18px;padding:16px 14px 12px;margin:4px 0;
}
.arena-pow{
  background:linear-gradient(135deg,#0e0020,#1a0030,#0e0020);
  border:2px solid rgba(136,51,255,0.4);
  border-radius:18px;padding:14px;margin:4px 0;
}
.arena-tag{font-size:0.6rem;font-weight:900;letter-spacing:2px;margin-bottom:6px;
  padding:2px 8px;border-radius:20px;display:inline-block;}
.fp-tag{background:rgba(255,100,0,0.15);color:#ff8833;}
.dc-tag{background:rgba(0,200,255,0.1);color:#00ccee;}
.pow-tag{background:rgba(136,51,255,0.15);color:#aa66ff;}
.arena-title{font-size:1.6rem;font-weight:900;margin-bottom:2px;}
.fp-title{color:#ffaa44;}
.dc-title{color:#00ddff;}
.pow-title{color:#bb88ff;}
.arena-en{font-size:0.65rem;letter-spacing:3px;font-weight:700;margin-bottom:8px;}
.fp-en{color:#885500;}
.dc-en{color:#006688;}
.pow-en{color:#552288;}
.arena-badges{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px;}
.arena-badge{font-size:0.65rem;font-weight:900;padding:2px 8px;border-radius:20px;}
.fp-badge{background:rgba(255,100,0,0.12);color:#ff8833;border:1px solid rgba(255,100,0,0.2);}
.dc-badge{background:rgba(0,200,255,0.08);color:#00aacc;border:1px solid rgba(0,200,255,0.15);}
.pow-badge{background:rgba(136,51,255,0.1);color:#8844bb;border:1px solid rgba(136,51,255,0.15);}
.arena-desc{font-size:0.72rem;color:#888;margin-bottom:10px;}
.arena-count{font-size:0.68rem;font-weight:900;margin-bottom:4px;}
.fp-cnt{color:#ff6622;}
.dc-cnt{color:#00aacc;}
.pow-cnt{color:#7733bb;}

div[data-testid="stButton"] button{
  touch-action:manipulation!important;
  -webkit-tap-highlight-color:transparent!important;
  user-select:none!important;
}
</style>
""", unsafe_allow_html=True)

# ── 통계 계산 ──
day_count    = stats["day_count"] if stats else 1
accuracy     = stats["accuracy"]  if stats else None
word_prison  = stats["word_prison"]  if stats else 0
saved_q      = stats["saved_q"]      if stats else 0
rank         = stats["rank"]         if stats else None
total_users  = stats["total_users"]  if stats else 0
sessions     = stats["sessions"]     if stats else 0
total_minutes = max(1, sessions * 8)  # 세션당 평균 8분

# storage에서 포로 카운트
try:
    _d = _storage.load()
    wp_count = len(_d.get("word_prison", []))
    sq_count = len(_d.get("saved_questions", []))
    sx_count = len(_d.get("saved_expressions", []))
    fp_count = sum(1 for w in _d.get("word_prison",[]) if w.get("source","").startswith("P5"))
    dc_count = sum(1 for w in _d.get("word_prison",[]) if w.get("source","").startswith("P7") or w.get("source")=="P7")
except Exception:
    wp_count = sq_count = sx_count = fp_count = dc_count = 0

# ── HUD 헤더 ──
st.markdown(f"""
<div class="hud-bar">
  <span class="hud-name">⚡ SNAPQ</span>
  <span class="hud-item">👤 <span class="hud-val">{nickname}</span></span>
  <span class="hud-item">📅 <span class="hud-val">{day_count}일</span></span>
  <span class="hud-item">⏱ <span class="hud-val">{total_minutes}분</span></span>
  <span class="hud-item">🔥 {'집계중' if sessions == 0 else f'{sessions}세션'}</span>
</div>
""", unsafe_allow_html=True)

# ── NPC 개인화 메시지 ──
tori_msg, tori_icon = make_npc_message(nickname, stats, is_tori=True)
st.markdown(f"""
<div class="npc-card">
  <span class="npc-icon">{tori_icon} TORI</span>
  <div class="npc-msg">{tori_msg}</div>
</div>
""", unsafe_allow_html=True)

# ── 통계 카드 (Day 2~) ──
if stats and day_count >= 2:
    weak_kr   = _kr_cat(stats["weak"])   if stats["weak"]   else "–"
    strong_kr = _kr_cat(stats["strong"]) if stats["strong"] else "–"
    acc_col   = "#44ff88" if accuracy >= 70 else "#ffdd44" if accuracy >= 50 else "#ff5555"
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-card">
        <div class="stat-val" style="color:{acc_col};">{accuracy}%</div>
        <div class="stat-label">📈 정답률</div>
      </div>
      <div class="stat-card">
        <div class="stat-val" style="color:#ff7755;">{weak_kr}</div>
        <div class="stat-label">⚠️ 약점</div>
      </div>
      <div class="stat-card">
        <div class="stat-val" style="color:#55ddff;">{strong_kr}</div>
        <div class="stat-label">✨ 강점</div>
      </div>
      <div class="stat-card">
        <div class="stat-val" style="color:#aa88ff;">{wp_count}</div>
        <div class="stat-label">⛓ 단어포로</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── 월별 순위 ──
if rank and total_users >= 3:
    rank_emoji = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🎖️"
    rank_txt   = f"이번 달 {rank_emoji} {rank}위 / {total_users}명 — 파이팅 {nickname}!"
    st.markdown(f'<div class="rank-banner"><div class="rank-txt">{rank_txt}</div></div>', unsafe_allow_html=True)

# ── 단어 포로수용소 배너 ──
new_label = f'<span style="background:#ff3366;border-radius:4px;padding:1px 5px;font-size:0.6rem;font-weight:900;color:#fff;margin-right:4px;">NEW {wp_count}명</span>' if wp_count > 0 else ""
st.markdown(f"""
<div class="prison-banner">
  <div class="prison-left">
    💀 단어 포로수용소<br>
    {new_label}틀린 단어를 가두고 · 외울 때까지 석방 금지!<br>
    <span style="font-size:0.65rem;color:#664488;">
      ⚡ 화력전 {fp_count}명 &nbsp;·&nbsp; 📡 암호해독 {dc_count}명
    </span>
  </div>
  <div>
    <div class="prison-count">{wp_count}</div>
    <div class="prison-sub">수감중</div>
  </div>
</div>
""", unsafe_allow_html=True)

if st.button("심문 →", key="wp_enter", use_container_width=False):
    st.session_state.sg_phase = "word_prison"
    st.session_state._wp_guard = True
    st.session_state._wp_prev_phase = "hub"
    st.switch_page("pages/03_POW_HQ.py")

# ── 화력전 카드 ──
fp_played = stats["sessions"] if stats else 0
fp_display = f"✅ {fp_played}세션 완료" if fp_played > 0 else "🔥 첫 도전!"
st.markdown(f"""
<div class="arena-fp">
  <div><span class="arena-tag fp-tag">문법·어휘 실전훈련</span></div>
  <div class="arena-title fp-title">⚡ 화력전</div>
  <div class="arena-en fp-en">FIREPOWER BATTLE</div>
  <div class="arena-badges">
    <span class="arena-badge fp-badge">문법</span>
    <span class="arena-badge fp-badge">어휘</span>
    <span class="arena-badge fp-badge">5문제</span>
  </div>
  <div class="arena-desc">💀 5문제 중 3개↑ 맞아야 생존</div>
  <div class="arena-count fp-cnt">{fp_display}</div>
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns([3, 1])
with c2:
    if st.button("출격 ▶", key="fp_go", use_container_width=True):
        if "phase" in st.session_state: del st.session_state["phase"]
        st.switch_page("pages/02_Firepower.py")

# ── 암호해독 카드 ──
dc_played  = stats["total"] // 3 if stats else 0
dc_display = f"📡 {dc_played}회 출격" if dc_played > 0 else "🔍 첫 도전!"
st.markdown(f"""
<div class="arena-dc">
  <div><span class="arena-tag dc-tag">TOEIC 독해 훈련</span></div>
  <div class="arena-title dc-title">📡 암호해독</div>
  <div class="arena-en dc-en">DECRYPT OP</div>
  <div class="arena-badges">
    <span class="arena-badge dc-badge">해독</span>
    <span class="arena-badge dc-badge">3문제</span>
    <span class="arena-badge dc-badge">즉사</span>
  </div>
  <div class="arena-desc">☠️ 한 번 틀리면 즉시 철수</div>
  <div class="arena-count dc-cnt">{dc_display}</div>
</div>
""", unsafe_allow_html=True)

c3, c4 = st.columns([3, 1])
with c4:
    if st.button("출격 ▶", key="dc_go", use_container_width=True):
        if "p7_phase" in st.session_state: del st.session_state["p7_phase"]
        st.switch_page("pages/04_Decrypt_Op.py")

# ── 포로사령부 ──
total_prisoners = sq_count + sx_count
st.markdown(f"""
<div class="arena-pow">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
    <div>
      <div><span class="arena-tag pow-tag">BOSS STAGE</span></div>
      <div class="arena-title pow-title" style="font-size:1.4rem;">💀 포로사령부</div>
      <div class="arena-en pow-en">POW HEADQUARTERS</div>
      <div style="font-size:0.7rem;color:#664488;margin-bottom:6px;">
        💀 틀린 문제가 무기가 된다
      </div>
      <div style="display:flex;gap:4px;flex-wrap:wrap;">
        <span class="arena-badge pow-badge">틀린 문제 복습</span>
        <span class="arena-badge pow-badge">단어 퀴즈</span>
        <span class="arena-badge pow-badge">완전 정복</span>
      </div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:2rem;font-weight:900;color:#9955ff;">{total_prisoners}</div>
      <div style="font-size:0.62rem;color:#552288;">포로 수감중</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

if st.button("입장 ▶", key="pow_go", use_container_width=True):
    st.session_state.sg_phase = "lobby"
    st.switch_page("pages/03_POW_HQ.py")

# ── 서브 메뉴 ──
sc1, sc2 = st.columns(2)
with sc1:
    st.markdown('<div style="background:#0a0a14;border:1px solid #1a1a2a;border-radius:12px;padding:12px;text-align:center;"><div style="font-size:1.2rem;">🎵</div><div style="font-size:0.72rem;color:#444;font-weight:700;">P4 Coming Soon</div></div>', unsafe_allow_html=True)
with sc2:
    if st.button("🔒 관리자 전용", key="admin_go", use_container_width=True):
        st.switch_page("pages/01_Admin.py")
