"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     01_Admin.py
ROLE:     관리자 대시보드 — Google Sheets 실시간 데이터
VERSION:  SnapQ TOEIC V3 — 2026.04.23 재작성
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA SOURCE:
    Google Sheets (SPREADSHEET_ID in secrets)
    읽는 시트: rt_logs, p5_logs, zpd_logs, activity, attendance,
              forget_logs, cross_logs, session_events
PAPERS:
    ⑤ 탐색적 로그 분석 — 핵심 시각화 도구
    ② ADDIE 개발 사례 — Implementation 증거
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AI-AGENT NOTES:
    [이전 문제]
    기존 01_Admin.py는 data/research_logs/*.jsonl 에서 읽었으나
    실제 데이터는 Google Sheets에 저장됨 → 항상 빈 대시보드.
    [수정 내용]
    gspread로 Sheets에서 직접 읽도록 전면 재작성.
    st.cache_data(ttl=300)로 5분 캐싱 → API 호출 최소화.
    [안전 장치]
    Sheets 연결 실패 시 로컬 storage_data.json fallback.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import streamlit as st
import json, os, pandas as pd
from datetime import datetime

st.set_page_config(page_title="SnapQ Admin", page_icon="📊", layout="wide")
st.markdown("""<style>
.main, .block-container {background:#ffffff !important; color:#111111 !important;}
h1,h2,h3,h4,h5,h6,p,span,div,label {color:#111111 !important;}
.metric-card{background:#f0f4ff;border:1px solid #ccddff;border-radius:16px;padding:1.2rem;text-align:center;}
.metric-val{font-size:2.5rem;font-weight:900;color:#0044cc;}
.metric-label{font-size:0.9rem;color:#333333;margin-top:4px;font-weight:600;}
.stDataFrame {color:#111111 !important;}
.stTabs [data-baseweb="tab"] {color:#111111 !important; font-weight:700;}
.sheet-badge{display:inline-block;background:#e8f5e9;color:#2e7d32;padding:2px 10px;
             border-radius:8px;font-size:0.75rem;font-weight:700;margin-left:8px;}
.sheet-badge-warn{background:#fff3e0;color:#e65100;}
</style>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 헤더
# ═══════════════════════════════════════════════════════════════
col_title, col_back = st.columns([5, 1])
with col_title:
    st.title("📊 SnapQ 관리자 대시보드")
    st.caption("논문 연구용 데이터 분석 시스템 — 학생에게 비공개")
with col_back:
    st.markdown("<div style='padding-top:1.2rem;'>", unsafe_allow_html=True)
    if st.button("🏠 메인으로", use_container_width=True):
        st.switch_page("main_hub.py")
    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# Google Sheets에서 데이터 로드 (5분 캐싱)
# ─────────────────────────────────────────────────────────────
# AI-AGENT NOTE:
#   ttl=300 → 5분마다 Sheets 재요청. API 할당량 절약.
#   실패 시 빈 DataFrame 반환 (게임 페이지와 동일 원칙).
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner="📡 Google Sheets에서 데이터 로딩 중...")
def load_sheet(sheet_name: str) -> pd.DataFrame:
    """Google Sheets의 특정 시트를 DataFrame으로 로드."""
    try:
        import gspread
        gc = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        sh = gc.open_by_key(st.secrets["SPREADSHEET_ID"])
        ws = sh.worksheet(sheet_name)
        rows = ws.get_all_records()
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows)
    except Exception as e:
        # 시트가 없거나 연결 실패 → 빈 DataFrame
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def load_all_sheets() -> dict:
    """모든 논문 관련 시트를 한 번에 로드."""
    sheets = {}
    for name in ["rt_logs", "p5_logs", "zpd_logs", "activity", "attendance",
                  "forget_logs", "cross_logs", "session_events"]:
        sheets[name] = load_sheet(name)
    return sheets


# ─────────────────────────────────────────────────────────────
# 로컬 fallback (Sheets 완전 실패 시)
# ─────────────────────────────────────────────────────────────
def load_local_fallback() -> dict:
    """storage_data.json에서 로컬 데이터 로드 (fallback)."""
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "storage_data.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            result = {}
            for key in ["rt_logs", "p5_logs", "zpd_logs", "forget_logs", "cross_logs"]:
                items = data.get(key, [])
                if isinstance(items, list) and items:
                    result[key] = pd.DataFrame(items)
                else:
                    result[key] = pd.DataFrame()
            return result
        except Exception:
            pass
    return {}


# ═══════════════════════════════════════════════════════════════
# 데이터 로드 실행
# ═══════════════════════════════════════════════════════════════
sheets = load_all_sheets()

# Sheets에서 데이터가 하나도 없으면 로컬 fallback 시도
_total_rows = sum(len(df) for df in sheets.values())
data_source = "sheets"
if _total_rows == 0:
    local = load_local_fallback()
    if local:
        sheets.update(local)
        _total_rows = sum(len(df) for df in sheets.values())
        data_source = "local"

if _total_rows == 0:
    st.warning("아직 수집된 데이터가 없습니다. (Sheets 연결 확인 또는 데이터 수집 시작 필요)")
    st.stop()

# 데이터 소스 표시
if data_source == "sheets":
    st.markdown('<span class="sheet-badge">📡 Google Sheets 실시간</span>', unsafe_allow_html=True)
else:
    st.markdown('<span class="sheet-badge sheet-badge-warn">💾 로컬 백업 데이터</span>', unsafe_allow_html=True)

# 편의 변수
rt = sheets.get("rt_logs", pd.DataFrame())
p5 = sheets.get("p5_logs", pd.DataFrame())
zpd = sheets.get("zpd_logs", pd.DataFrame())
act = sheets.get("activity", pd.DataFrame())
att = sheets.get("attendance", pd.DataFrame())
forget = sheets.get("forget_logs", pd.DataFrame())
cross = sheets.get("cross_logs", pd.DataFrame())
events = sheets.get("session_events", pd.DataFrame())


# ═══════════════════════════════════════════════════════════════
# 탭 구성
# ═══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👥 학생 현황", "📈 학습 분석", "🎮 게이미피케이션",
    "📋 논문별 로그", "🔍 세션 이벤트", "💾 내보내기"
])


# ═══ 탭1: 학생 현황 ═══════════════════════════════════════════
with tab1:
    st.subheader("👥 전체 학생 현황")

    # rt_logs 기반 (핵심 데이터)
    if not rt.empty and "user_id" in rt.columns:
        # is_correct 필드 정리 (Sheets에서 문자열로 올 수 있음)
        if "is_correct" in rt.columns:
            rt["_correct"] = rt["is_correct"].apply(
                lambda x: True if str(x).lower() in ("true", "1", "yes") else False
            )
        else:
            rt["_correct"] = False

        users = rt["user_id"].unique()
        total_users = len(users)
        total_q = len(rt)
        correct_sum = rt["_correct"].sum()
        acc = round(correct_sum / total_q * 100, 1) if total_q > 0 else 0
        avg_q = round(total_q / total_users, 1) if total_users > 0 else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-val">{total_users}</div>'
                        f'<div class="metric-label">전체 학생 수</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="metric-val">{total_q}</div>'
                        f'<div class="metric-label">총 풀이 문제 수 (P5)</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><div class="metric-val">{acc}%</div>'
                        f'<div class="metric-label">전체 평균 정답률</div></div>', unsafe_allow_html=True)
        with c4:
            # 출석일수 (attendance 시트)
            att_count = len(att) if not att.empty else 0
            st.markdown(f'<div class="metric-card"><div class="metric-val">{att_count}</div>'
                        f'<div class="metric-label">총 출석 기록</div></div>', unsafe_allow_html=True)

        st.divider()

        # 학생별 요약
        rows = []
        for uid in sorted(users):
            udf = rt[rt["user_id"] == uid]
            total = len(udf)
            correct = udf["_correct"].sum()
            acc_u = round(correct / total * 100, 1) if total > 0 else 0
            avg_rt = round(udf["rt_proxy"].astype(float).mean(), 1) if "rt_proxy" in udf.columns else "-"
            cats = list(udf["grammar_type"].unique()) if "grammar_type" in udf.columns else []
            last = str(udf["timestamp"].max())[:10] if "timestamp" in udf.columns else "-"
            rows.append({
                "학생": uid, "총문제": total, "정답수": int(correct),
                "정답률(%)": acc_u, "평균RT(초)": avg_rt,
                "문법유형": ", ".join(str(c) for c in cats if str(c) != "nan"),
                "최근접속": last
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("rt_logs 데이터가 없습니다.")


# ═══ 탭2: 학습 분석 ═══════════════════════════════════════════
with tab2:
    st.subheader("📈 학습 분석")

    if not rt.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 문법유형별 문제수")
            if "grammar_type" in rt.columns:
                gc_df = rt["grammar_type"].value_counts().reset_index()
                gc_df.columns = ["문법유형", "문제수"]
                st.bar_chart(gc_df.set_index("문법유형"))

        with col2:
            st.markdown("#### 카테고리별 정답률")
            if "grammar_type" in rt.columns and "_correct" in rt.columns:
                cat_df = rt.groupby("grammar_type").agg(
                    총문제=("_correct", "count"),
                    정답수=("_correct", "sum")
                ).reset_index()
                cat_df["정답률(%)"] = (cat_df["정답수"] / cat_df["총문제"] * 100).round(1)
                st.dataframe(cat_df.sort_values("정답률(%)"), use_container_width=True, hide_index=True)

        st.divider()

        st.markdown("#### 주차별 정답률 변화")
        if "week" in rt.columns and "_correct" in rt.columns:
            wdf = rt.copy()
            wdf["week"] = pd.to_numeric(wdf["week"], errors="coerce")
            wdf = wdf.dropna(subset=["week"])
            if not wdf.empty:
                wg = wdf.groupby("week").agg(
                    총문제=("_correct", "count"),
                    정답수=("_correct", "sum")
                ).reset_index()
                wg["정답률(%)"] = (wg["정답수"] / wg["총문제"] * 100).round(1)
                st.line_chart(wg.set_index("week")["정답률(%)"])

        st.markdown("#### 타이머별 정답률 비교")
        if "timer_setting" in rt.columns and "_correct" in rt.columns:
            tg = rt.groupby("timer_setting").agg(
                총문제=("_correct", "count"),
                정답수=("_correct", "sum")
            ).reset_index()
            tg["정답률(%)"] = (tg["정답수"] / tg["총문제"] * 100).round(1)
            st.dataframe(tg, use_container_width=True, hide_index=True)
    else:
        st.info("rt_logs 데이터가 없습니다.")


# ═══ 탭3: 게이미피케이션 ═══════════════════════════════════════
with tab3:
    st.subheader("🎮 게이미피케이션 지표")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 타이머 선택 패턴 (P5)")
        if not p5.empty and "timer_selected" in p5.columns:
            tc = p5["timer_selected"].value_counts().reset_index()
            tc.columns = ["타이머(초)", "선택횟수"]
            st.bar_chart(tc.set_index("타이머(초)"))
        else:
            st.info("p5_logs 데이터 없음")

    with col2:
        st.markdown("#### 게임 결과 (VICTORY vs GAME_OVER)")
        if not p5.empty and "result" in p5.columns:
            rc = p5["result"].value_counts().reset_index()
            rc.columns = ["결과", "횟수"]
            st.dataframe(rc, use_container_width=True, hide_index=True)

    st.divider()

    st.markdown("#### 전장별 활동 기록")
    if not act.empty and "arena" in act.columns:
        ac = act["arena"].value_counts().reset_index()
        ac.columns = ["전장", "플레이수"]
        st.bar_chart(ac.set_index("전장"))

    st.markdown("#### 전장별 완주율")
    if not act.empty and "arena" in act.columns and "completed" in act.columns:
        act["_completed"] = act["completed"].apply(
            lambda x: True if str(x).lower() in ("true", "1", "yes") else False
        )
        comp = act.groupby("arena").agg(
            총플레이=("_completed", "count"),
            완주수=("_completed", "sum")
        ).reset_index()
        comp["완주율(%)"] = (comp["완주수"] / comp["총플레이"] * 100).round(1)
        st.dataframe(comp, use_container_width=True, hide_index=True)


# ═══ 탭4: 논문별 로그 ═══════════════════════════════════════════
with tab4:
    st.subheader("📋 논문별 로그 현황")

    # 시트별 행 수 요약
    summary_rows = []
    sheet_info = {
        "rt_logs":        ("④⑤ AI 분류 + 탐색적 분석", rt),
        "p5_logs":        ("⑤ P5 세션 요약", p5),
        "zpd_logs":       ("⑦ ZPD 스캐폴딩", zpd),
        "activity":       ("⑤ 활동 기록", act),
        "attendance":     ("⑤ 출석", att),
        "forget_logs":    ("⑤ 망각곡선", forget),
        "cross_logs":     ("⑥ 크로스스킬 전이", cross),
        "session_events": ("⑤ 세션 이벤트", events),
    }
    for name, (paper, df) in sheet_info.items():
        count = len(df) if not df.empty else 0
        status = "✅" if count > 0 else "⚠️"
        summary_rows.append({"시트": name, "논문": paper, "행 수": count, "상태": status})
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

    st.divider()

    # 개별 시트 미리보기
    selected_sheet = st.selectbox("시트 미리보기", list(sheet_info.keys()))
    _, sel_df = sheet_info[selected_sheet]
    if not sel_df.empty:
        st.dataframe(sel_df.tail(20), use_container_width=True, hide_index=True)
        st.caption(f"최근 20행 표시 (전체 {len(sel_df)}행)")
    else:
        st.info(f"{selected_sheet} 시트에 데이터가 없습니다.")


# ═══ 탭5: 세션 이벤트 ═══════════════════════════════════════════
with tab5:
    st.subheader("🔍 세션 이벤트 흐름")

    if not events.empty:
        st.markdown("#### 페이지별 진입 빈도")
        if "arena" in events.columns:
            ev_count = events["arena"].value_counts().reset_index()
            ev_count.columns = ["페이지", "진입 횟수"]
            st.bar_chart(ev_count.set_index("페이지"))

        st.markdown("#### 이벤트 유형별 빈도")
        if "event" in events.columns:
            et_count = events["event"].value_counts().reset_index()
            et_count.columns = ["이벤트", "횟수"]
            st.dataframe(et_count, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("#### 최근 이벤트 로그")
        st.dataframe(events.tail(30), use_container_width=True, hide_index=True)
    else:
        st.info("session_events 데이터가 없습니다.")


# ═══ 탭6: 내보내기 ═══════════════════════════════════════════
with tab6:
    st.subheader("💾 데이터 내보내기")

    for name, (paper, df) in sheet_info.items():
        if not df.empty:
            csv = df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label=f"📥 {name} 다운로드 ({len(df)}행)",
                data=csv.encode("utf-8-sig"),
                file_name=f"snapq_{name}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
                key=f"dl_{name}",
            )

    st.divider()
    st.markdown("#### 현황 요약")
    _summary = pd.DataFrame([
        {"항목": "데이터 소스", "값": "Google Sheets" if data_source == "sheets" else "로컬 백업"},
        {"항목": "총 로그 수", "값": str(_total_rows)},
        {"항목": "학생 수", "값": str(len(rt["user_id"].unique())) if not rt.empty and "user_id" in rt.columns else "0"},
        {"항목": "출석 기록", "값": str(len(att))},
        {"항목": "마지막 갱신", "값": datetime.now().strftime("%Y-%m-%d %H:%M")},
    ])
    st.dataframe(_summary, use_container_width=True, hide_index=True)

    if st.button("🔄 데이터 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
