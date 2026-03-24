import streamlit as st
import json, os, pandas as pd, numpy as np
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG & STYLE
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="SnapQ Admin", page_icon="📊", layout="wide")
st.markdown("""<style>
.main, .block-container {background:#ffffff !important; color:#111111 !important;}
h1,h2,h3,h4,h5,h6,p,span,div,label {color:#111111 !important;}
.metric-card{background:#f0f4ff;border:1px solid #ccddff;border-radius:16px;
  padding:1.2rem;text-align:center;margin-bottom:0.5rem;}
.metric-val{font-size:2.2rem;font-weight:900;color:#0044cc;}
.metric-label{font-size:0.85rem;color:#333333;margin-top:4px;font-weight:600;}
.paper-card{background:#fff8ec;border-left:5px solid #f4a200;border-radius:8px;
  padding:1rem 1.2rem;margin-bottom:0.8rem;}
.paper-card-ssci{background:#fff0f0;border-left:5px solid #cc0000;border-radius:8px;
  padding:1rem 1.2rem;margin-bottom:0.8rem;}
.paper-title{font-size:1rem;font-weight:800;color:#12274D;}
.paper-sub{font-size:0.85rem;color:#555;margin-top:4px;}
.alert-box{background:#fff0f0;border-left:5px solid #cc0000;border-radius:8px;
  padding:0.8rem 1.2rem;margin-bottom:0.5rem;}
.ok-box{background:#f0fff4;border-left:5px solid #009944;border-radius:8px;
  padding:0.8rem 1.2rem;margin-bottom:0.5rem;}
.info-box{background:#e8f4fd;border-left:5px solid #0066cc;border-radius:8px;
  padding:0.8rem 1.2rem;margin-bottom:0.5rem;}
.field-tag{display:inline-block;background:#e8f0fe;border:1px solid #4a86e8;
  border-radius:6px;padding:2px 8px;font-size:0.75rem;font-weight:700;
  color:#1a56cc;margin:2px;}
.missing-tag{display:inline-block;background:#fce8e8;border:1px solid #cc0000;
  border-radius:6px;padding:2px 8px;font-size:0.75rem;font-weight:700;
  color:#cc0000;margin:2px;}
.stDataFrame {color:#111111 !important;}
.stTabs [data-baseweb="tab"] {color:#111111 !important; font-weight:700;}
</style>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
col_title, col_back = st.columns([5, 1])
with col_title:
    st.markdown("<h2 style='margin-bottom:0;'>📊 SnapQ 관리자 대시보드 v2</h2>", unsafe_allow_html=True)
    st.caption("논문 10편 + 특허 3개 입증 데이터 분석 시스템 — 학생에게 비공개")
with col_back:
    st.markdown("<div style='padding-top:0.8rem;'>", unsafe_allow_html=True)
    if st.button("🏠 메인으로", use_container_width=True):
        st.switch_page("main_hub.py")
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────
STORAGE_FILE = "storage_data.json"
DATA_DIR     = "data/research_logs"

def load_storage():
    if not os.path.exists(STORAGE_FILE):
        return {}
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_storage(data: dict):
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_all_logs():
    logs = []
    if not os.path.exists(DATA_DIR):
        return pd.DataFrame()
    for fname in os.listdir(DATA_DIR):
        if fname.endswith(".jsonl"):
            with open(os.path.join(DATA_DIR, fname), "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        logs.append(json.loads(line.strip()))
                    except:
                        pass
    return pd.DataFrame(logs) if logs else pd.DataFrame()

def _df(storage, key):
    rows = storage.get(key, [])
    return pd.DataFrame(rows) if rows else pd.DataFrame()

# ── 로드 실행 ──────────────────────────────────────────────────
storage    = load_storage()
df_all     = load_all_logs()

# 기존 7개
df_device  = _df(storage, "devices")
df_survey  = _df(storage, "surveys")
df_diag    = _df(storage, "diagnosis")
df_p5      = _df(storage, "p5_logs")
df_p7      = _df(storage, "p7_logs")
df_retry   = _df(storage, "retry_logs")
df_session = _df(storage, "sessions")

# ★ 신규 7개 (논문·특허 보강)
df_rt      = _df(storage, "rt_logs")          # 반응속도 로그 (논문 01·03)
df_forget  = _df(storage, "forget_logs")      # 오답전장 재접속 (논문 02)
df_cross   = _df(storage, "cross_logs")       # P7→P5 크로스 변환 (논문 04)
df_timer   = _df(storage, "timer_history")    # 타이머 선택 변경 이력 (논문 05)
df_zpd     = _df(storage, "zpd_logs")         # ZPD 종료 지점 이력 (논문 06)
df_fb      = _df(storage, "feedback_logs")    # 인바디 피드백 (논문 10)
df_cluster = _df(storage, "grammar_cluster")  # 오답 문법 유형 (논문 09)

# 기존 JSONL 문제풀이
df_qa = pd.DataFrame()
if not df_all.empty:
    df_qa = df_all[
        ~df_all.get("type", pd.Series([""] * len(df_all))).isin(["session","session_v2"])
    ].copy() if "type" in df_all.columns else df_all.copy()

# 전체 user_id
all_users = set()
for _d in [df_qa, df_device, df_survey, df_diag, df_p5, df_p7,
           df_retry, df_session, df_rt, df_forget, df_cross, df_zpd]:
    if not _d.empty and "user_id" in _d.columns:
        all_users.update(_d["user_id"].dropna().unique())
all_users = sorted(all_users)

# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────
(tab1, tab2, tab3, tab4, tab5,
 tab6, tab7, tab8, tab9,
 tab10, tab11, tab12, tab13, tab14) = st.tabs([
    "👥 학생 현황",
    "📈 학습 분석",
    "🎮 게이미피케이션",
    "📋 설문 데이터",
    "💾 내보내기",
    "📱 디바이스 분석",
    "📖 Day1·10·20 진단",
    "🔬 논문 데이터 요약",
    "⚠️ 미완료 알림",
    # ── 신규 탭 (논문·특허 보강) ──
    "⚡ 반응속도 RT 분석",      # 논문 01·03 (SSCI)
    "🌀 망각곡선 분석",         # 논문 02 (SSCI)
    "🔀 크로스스킬 전이",       # 논문 04 (SSCI·특허)
    "🧩 ZPD 경계 추적",        # 논문 06 (KCI)
    "🗺️ 데이터 필드 현황",     # 누락 필드 알림
])


# ═══════════════════════════════════════════════════════════════
# TAB 1 — 학생 현황 (기존 유지)
# ═══════════════════════════════════════════════════════════════
with tab1:
    st.subheader("👥 전체 학생 현황")
    total_users = len(all_users)
    total_q  = len(df_qa) if not df_qa.empty else 0
    correct_sum = df_qa["correct"].sum() if (not df_qa.empty and "correct" in df_qa.columns) else 0
    acc  = round(correct_sum / total_q * 100, 1) if total_q > 0 else 0
    avg_q = round(total_q / total_users, 1) if total_users > 0 else 0
    diag_done = df_diag["user_id"].nunique() if not df_diag.empty else 0
    returning = df_session["user_id"][df_session["is_returning_student"] == True].nunique() \
        if (not df_session.empty and "is_returning_student" in df_session.columns) else 0
    # 신규: RT 수집 여부
    rt_users = df_rt["user_id"].nunique() if not df_rt.empty else 0

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    for col, val, label in zip(
        [c1, c2, c3, c4, c5, c6, c7],
        [total_users, total_q, f"{acc}%", avg_q, diag_done, returning, rt_users],
        ["전체 학생", "총 풀이수", "평균 정답률", "학생당 풀이",
         "진단 완료", "재수강생", "RT 수집(신규)"]
    ):
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-val">{val}</div>'
                f'<div class="metric-label">{label}</div></div>',
                unsafe_allow_html=True
            )

    st.divider()
    rows = []
    for uid in all_users:
        uqa = df_qa[df_qa["user_id"] == uid] if (not df_qa.empty and "user_id" in df_qa.columns) else pd.DataFrame()
        total  = len(uqa)
        correct = uqa["correct"].sum() if (not uqa.empty and "correct" in uqa.columns) else 0
        acc_u  = round(correct / total * 100, 1) if total > 0 else "-"
        udev   = df_device[df_device["user_id"] == uid] if (not df_device.empty and "user_id" in df_device.columns) else pd.DataFrame()
        dev_type = udev["device_type"].iloc[0] if (not udev.empty and "device_type" in udev.columns) else "-"
        screen_w = udev["screen_width"].iloc[0] if (not udev.empty and "screen_width" in udev.columns) else "-"
        viewport_w = udev["viewport_width"].iloc[0] if (not udev.empty and "viewport_width" in udev.columns) else "❌미수집"
        udiag  = df_diag[df_diag["user_id"] == uid] if (not df_diag.empty and "user_id" in df_diag.columns) else pd.DataFrame()
        days_done = sorted(udiag["diagnosis_day"].tolist()) if (not udiag.empty and "diagnosis_day" in udiag.columns) else []
        diag_str = ", ".join([f"Day{d}" for d in days_done]) if days_done else "미진단"
        last = "-"
        for _d, _c in [(df_qa, "timestamp"), (df_session, "session_start")]:
            if not _d.empty and "user_id" in _d.columns and _c in _d.columns:
                u_ = _d[_d["user_id"] == uid][_c].dropna()
                if not u_.empty:
                    last = str(u_.max())[:10]; break
        is_ret = "-"
        if not df_session.empty and "user_id" in df_session.columns and "is_returning_student" in df_session.columns:
            u_s = df_session[df_session["user_id"] == uid]
            if not u_s.empty:
                is_ret = "재수강" if u_s["is_returning_student"].iloc[0] else "신규"
        has_rt = "✅" if (not df_rt.empty and uid in df_rt.get("user_id", pd.Series([])).values) else "❌"
        rows.append({
            "학생": uid, "총문제": total, "정답률(%)": acc_u,
            "기기": dev_type, "화면너비(px)": screen_w,
            "뷰포트(px)": viewport_w,
            "진단완료": diag_str, "구분": is_ret,
            "RT수집": has_rt, "최근접속": last
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("아직 학생 데이터가 없습니다.")


# ═══════════════════════════════════════════════════════════════
# TAB 2 — 학습 분석 (기존 유지)
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.subheader("📈 학습 분석")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 모듈별 사용 빈도")
        if not df_qa.empty and "module" in df_qa.columns:
            mc = df_qa["module"].value_counts().reset_index()
            mc.columns = ["모듈", "문제수"]
            st.bar_chart(mc.set_index("모듈"))
    with col2:
        st.markdown("#### 카테고리별 정답률")
        if not df_qa.empty and "category" in df_qa.columns and "correct" in df_qa.columns:
            cat_df = df_qa.groupby("category").agg(총문제=("correct","count"),정답수=("correct","sum")).reset_index()
            cat_df["정답률(%)"] = (cat_df["정답수"] / cat_df["총문제"] * 100).round(1)
            st.dataframe(cat_df.sort_values("정답률(%)"), use_container_width=True, hide_index=True)
    st.divider()
    st.markdown("#### 주차별 정답률 변화")
    if not df_qa.empty and "week" in df_qa.columns and "correct" in df_qa.columns:
        wdf = df_qa.groupby("week").agg(총문제=("correct","count"),정답수=("correct","sum")).reset_index()
        wdf["정답률(%)"] = (wdf["정답수"] / wdf["총문제"] * 100).round(1)
        st.line_chart(wdf.set_index("week")["정답률(%)"])
    st.markdown("#### 시간대별 접속 패턴")
    if not df_qa.empty and "hour" in df_qa.columns:
        hc = df_qa["hour"].value_counts().sort_index().reset_index()
        hc.columns = ["시간대", "문제수"]
        st.bar_chart(hc.set_index("시간대"))


# ═══════════════════════════════════════════════════════════════
# TAB 3 — 게이미피케이션 (기존 유지)
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🎮 게이미피케이션 지표")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 타이머 선택 패턴 (P5)")
        src = df_p5 if (not df_p5.empty and "timer_selected" in df_p5.columns) else df_qa
        if not src.empty and "timer_selected" in src.columns:
            tc = src["timer_selected"].value_counts().reset_index()
            tc.columns = ["타이머(초)", "선택횟수"]
            st.bar_chart(tc.set_index("타이머(초)"))
    with col2:
        st.markdown("#### 재도전 vs 첫도전")
        src2 = df_retry if not df_retry.empty else df_qa
        if not src2.empty and "is_retry" in src2.columns:
            rc = src2["is_retry"].value_counts()
            rdf = pd.DataFrame({"구분":["재도전" if k else "첫도전" for k in rc.index],"횟수":rc.values})
            st.dataframe(rdf, use_container_width=True, hide_index=True)
    st.divider()
    st.markdown("#### P5 전장 승패 비율")
    if not df_p5.empty and "result" in df_p5.columns:
        res = df_p5["result"].value_counts().reset_index()
        res.columns = ["결과", "횟수"]
        st.bar_chart(res.set_index("결과"))
    st.markdown("#### P7 전장 단계별 도달률")
    if not df_p7.empty and "step_reached" in df_p7.columns:
        sr = df_p7["step_reached"].value_counts().reset_index()
        sr.columns = ["도달단계", "횟수"]
        st.bar_chart(sr.set_index("도달단계"))
    st.markdown("#### 요일별 학습 패턴")
    if not df_qa.empty and "day_of_week" in df_qa.columns:
        dow = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dc = df_qa["day_of_week"].value_counts().reindex(dow, fill_value=0).reset_index()
        dc.columns = ["요일", "문제수"]
        st.bar_chart(dc.set_index("요일"))
    st.markdown("#### 학생별 평균 응답시간 변화")
    if all_users and not df_qa.empty and "time_taken" in df_qa.columns and "week" in df_qa.columns:
        sel = st.selectbox("학생 선택", all_users, key="spd")
        udf = df_qa[df_qa["user_id"] == sel] if "user_id" in df_qa.columns else pd.DataFrame()
        if not udf.empty:
            spd = udf.groupby("week")["time_taken"].mean().round(2).reset_index()
            spd.columns = ["주차", "평균응답(초)"]
            st.line_chart(spd.set_index("주차"))


# ═══════════════════════════════════════════════════════════════
# TAB 4 — 설문 데이터 (기존 유지)
# ═══════════════════════════════════════════════════════════════
with tab4:
    st.subheader("📋 설문 데이터")
    st.markdown("#### B. 첫 접속 설문 (논문 1편)")
    if not df_survey.empty:
        st.dataframe(df_survey, use_container_width=True, hide_index=True)
        col1, col2 = st.columns(2)
        with col1:
            if "survey_device" in df_survey.columns:
                st.markdown("**기기 종류 분포**")
                dvc = df_survey["survey_device"].value_counts().reset_index()
                dvc.columns = ["기기", "명수"]; st.bar_chart(dvc.set_index("기기"))
        with col2:
            if "survey_posture" in df_survey.columns:
                st.markdown("**학습 자세 분포**")
                pos = df_survey["survey_posture"].value_counts().reset_index()
                pos.columns = ["자세", "명수"]; st.bar_chart(pos.set_index("자세"))
        if "survey_distance" in df_survey.columns:
            st.markdown("**눈-화면 거리 분포**")
            dist = df_survey["survey_distance"].value_counts().reset_index()
            dist.columns = ["거리", "명수"]; st.bar_chart(dist.set_index("거리"))
    else:
        st.info("첫 접속 설문 데이터가 아직 없습니다.")


# ═══════════════════════════════════════════════════════════════
# TAB 5 — 내보내기 (기존 유지 + 신규 논문용 추가)
# ═══════════════════════════════════════════════════════════════
with tab5:
    st.subheader("💾 데이터 내보내기")

    if not df_all.empty:
        st.download_button(
            "📥 전체 로그 CSV",
            data=df_all.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
            file_name=f"snapq_all_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv", use_container_width=True
        )

    st.divider()
    st.markdown("#### 논문별 데이터 export")

    papers = [
        ("논문 01 — RT × 자동화 (SSCI)", "paper01_RT_automaticity",
         [df_p5, df_rt, df_diag], ["user_id"]),
        ("논문 02 — 망각곡선 (SSCI)",    "paper02_forgetting_curve",
         [df_forget, df_diag], ["user_id"]),
        ("논문 03 — 오답타이밍 × 인지부하 (SSCI)", "paper03_error_timing",
         [df_rt, df_p5], ["user_id"]),
        ("논문 04 — 크로스스킬 전이 (SSCI)", "paper04_cross_skill",
         [df_cross, df_p7, df_diag], ["user_id"]),
        ("논문 05 — 자기선택 난이도", "paper05_self_difficulty",
         [df_timer, df_p5, df_diag], ["user_id"]),
        ("논문 06 — ZPD 경계 추적",  "paper06_zpd",
         [df_zpd, df_diag], ["user_id"]),
        ("논문 07 — 화면너비 자연실험", "paper07_screen_width",
         [df_device, df_diag], ["user_id"]),
        ("논문 08 — Day1 예측력",    "paper08_day1_prediction",
         [df_p5, df_session], ["user_id"]),
        ("논문 09 — 오답 클러스터링", "paper09_grammar_cluster",
         [df_cluster, df_retry, df_diag], ["user_id"]),
        ("논문 10 — 인바디 피드백",  "paper10_inbody_feedback",
         [df_fb, df_session], ["user_id"]),
    ]

    cols = st.columns(2)
    for i, (label, fname, dfs, merge_on) in enumerate(papers):
        with cols[i % 2]:
            st.markdown(f"**{label}**")
            valid = [d for d in dfs if not d.empty]
            if len(valid) >= 1:
                merged = valid[0]
                for d in valid[1:]:
                    merged = pd.merge(merged, d, on=merge_on, how="inner", suffixes=("","_r"))
                st.download_button(
                    f"📥 {fname[:20]}",
                    data=merged.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
                    file_name=f"{fname}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv", use_container_width=True, key=f"dl_{i}"
                )
            else:
                st.info("데이터 수집 중")

    st.divider()
    st.markdown("#### 현황 요약")
    _summary = pd.DataFrame([
        {"소스": "기존 JSONL",       "레코드 수": len(df_all)},
        {"소스": "devices",          "레코드 수": len(df_device)},
        {"소스": "surveys",          "레코드 수": len(df_survey)},
        {"소스": "diagnosis",        "레코드 수": len(df_diag)},
        {"소스": "p5_logs",          "레코드 수": len(df_p5)},
        {"소스": "p7_logs",          "레코드 수": len(df_p7)},
        {"소스": "retry_logs",       "레코드 수": len(df_retry)},
        {"소스": "sessions",         "레코드 수": len(df_session)},
        {"소스": "★ rt_logs",        "레코드 수": len(df_rt)},
        {"소스": "★ forget_logs",    "레코드 수": len(df_forget)},
        {"소스": "★ cross_logs",     "레코드 수": len(df_cross)},
        {"소스": "★ timer_history",  "레코드 수": len(df_timer)},
        {"소스": "★ zpd_logs",       "레코드 수": len(df_zpd)},
        {"소스": "★ feedback_logs",  "레코드 수": len(df_fb)},
        {"소스": "★ grammar_cluster","레코드 수": len(df_cluster)},
    ])
    st.dataframe(_summary, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════
# TAB 6 — 디바이스 분석 (기존 유지 + viewport 추가)
# ═══════════════════════════════════════════════════════════════
with tab6:
    st.subheader("📱 디바이스 분석 — 논문 07 핵심 데이터")
    st.caption("screen_width + viewport_width × Day1→Day20 향상도 회귀분석 원데이터")

    if df_device.empty:
        st.warning("아직 디바이스 데이터가 없습니다.")
    else:
        has_viewport = "viewport_width" in df_device.columns
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            mobile_n = (df_device["device_type"] == "mobile").sum() if "device_type" in df_device.columns else 0
            st.markdown(f'<div class="metric-card"><div class="metric-val">{mobile_n}</div><div class="metric-label">모바일</div></div>', unsafe_allow_html=True)
        with c2:
            desktop_n = (df_device["device_type"] == "desktop").sum() if "device_type" in df_device.columns else 0
            st.markdown(f'<div class="metric-card"><div class="metric-val">{desktop_n}</div><div class="metric-label">노트북/PC</div></div>', unsafe_allow_html=True)
        with c3:
            avg_sw = round(df_device["screen_width"].mean(), 1) if "screen_width" in df_device.columns else "-"
            st.markdown(f'<div class="metric-card"><div class="metric-val">{avg_sw}px</div><div class="metric-label">평균 화면너비</div></div>', unsafe_allow_html=True)
        with c4:
            avg_vp = round(df_device["viewport_width"].mean(), 1) if has_viewport else "❌ 미수집"
            color = "metric-val" if has_viewport else "metric-val" + ' style="color:#cc0000"'
            st.markdown(f'<div class="metric-card"><div class="{color}">{avg_vp}px</div><div class="metric-label">평균 뷰포트너비 ★필수</div></div>', unsafe_allow_html=True)

        if not has_viewport:
            st.markdown('<div class="alert-box">⚠️ <b>viewport_width 미수집</b> — 논문 07 핵심 변수. 게임 페이지에서 JS로 즉시 추가 필요 (window.innerWidth)</div>', unsafe_allow_html=True)

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 기기 종류 분포")
            if "device_type" in df_device.columns:
                dc = df_device["device_type"].value_counts().reset_index()
                dc.columns = ["기기", "명수"]; st.bar_chart(dc.set_index("기기"))
        with col2:
            st.markdown("#### OS 분포")
            if "os_type" in df_device.columns:
                oc = df_device["os_type"].value_counts().reset_index()
                oc.columns = ["OS", "명수"]; st.bar_chart(oc.set_index("OS"))

        st.divider()
        st.markdown("#### 📊 screen_width 구간별 진단 향상도 (논문 07 핵심 분석)")
        if not df_diag.empty:
            for width_col in (["viewport_width"] if has_viewport else []) + ["screen_width"]:
                if width_col not in df_device.columns:
                    continue
                diag_wide = df_diag.pivot_table(
                    index="user_id", columns="diagnosis_day", values="total_score", aggfunc="mean"
                ).reset_index() if "diagnosis_day" in df_diag.columns and "total_score" in df_diag.columns else pd.DataFrame()
                if diag_wide.empty:
                    continue
                diag_wide.columns = ["user_id"] + [f"day{c}" for c in diag_wide.columns[1:]]
                merged = pd.merge(df_device[["user_id", width_col, "device_type"]], diag_wide, on="user_id", how="inner")
                if "day1" in merged.columns and ("day20" in merged.columns or "day10" in merged.columns):
                    end_col = "day20" if "day20" in merged.columns else "day10"
                    merged["향상도"] = merged[end_col] - merged["day1"]
                    def sw_group(w):
                        if w < 400:   return "모바일(~400px)"
                        elif w < 800: return "태블릿(400~800px)"
                        else:         return "노트북/PC(800px~)"
                    merged["화면구간"] = merged[width_col].apply(sw_group)
                    grp = merged.groupby("화면구간")["향상도"].mean().round(2).reset_index()
                    grp.columns = ["화면구간", f"평균 향상도({width_col})"]
                    st.markdown(f"**{width_col} 기준 구간별 향상도**")
                    st.dataframe(grp, use_container_width=True, hide_index=True)
                    st.bar_chart(grp.set_index("화면구간"))
                    st.markdown("**회귀분석용 원데이터**")
                    st.dataframe(merged[["user_id", width_col, "device_type", "day1", end_col, "향상도"]],
                                 use_container_width=True, hide_index=True)
        st.divider()
        st.dataframe(df_device, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════
# TAB 7 — Day1·10·20 진단 (기존 유지)
# ═══════════════════════════════════════════════════════════════
with tab7:
    st.subheader("📖 Day1·Day10·Day20 진단 추적")
    st.caption("논문 10편 공통 종속변수 — 대응표본 t-test 원데이터")
    if df_diag.empty:
        st.warning("진단 데이터가 아직 없습니다.")
    else:
        day_counts = df_diag["diagnosis_day"].value_counts() if "diagnosis_day" in df_diag.columns else {}
        c1, c2, c3, c4 = st.columns(4)
        for col, day, label in zip([c1,c2,c3,c4],[1,10,20,"all"],["Day1 완료","Day10 완료","Day20 완료","전체 기록"]):
            with col:
                n = day_counts.get(day, 0) if day != "all" else len(df_diag)
                st.markdown(f'<div class="metric-card"><div class="metric-val">{n}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 진단일별 평균 정답률")
            if "diagnosis_day" in df_diag.columns and "total_score" in df_diag.columns:
                dag = df_diag.groupby("diagnosis_day")["total_score"].mean().round(2).reset_index()
                dag.columns = ["진단일", "평균정답수"]
                st.line_chart(dag.set_index("진단일"))
        with col2:
            st.markdown("#### P5 vs P7 향상도 비교")
            if all(c in df_diag.columns for c in ["diagnosis_day","p5_score","p7_score"]):
                pg = df_diag.groupby("diagnosis_day")[["p5_score","p7_score"]].mean().round(2)
                st.line_chart(pg)
        st.divider()
        st.markdown("#### 학생별 Day1→Day10→Day20 추적")
        if all_users and "user_id" in df_diag.columns:
            sel_u = st.selectbox("학생 선택", all_users, key="diag_sel")
            udiag = df_diag[df_diag["user_id"] == sel_u]
            if not udiag.empty:
                st.dataframe(udiag.sort_values("diagnosis_day") if "diagnosis_day" in udiag.columns else udiag,
                             use_container_width=True, hide_index=True)
                if "diagnosis_day" in udiag.columns and "total_score" in udiag.columns:
                    st.line_chart(udiag.set_index("diagnosis_day")["total_score"])
            else:
                st.info(f"{sel_u}의 진단 기록이 없습니다.")
        st.divider()
        st.dataframe(df_diag, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════
# TAB 8 — 논문 데이터 요약 (기존 + 신규 논문 추가)
# ═══════════════════════════════════════════════════════════════
with tab8:
    st.subheader("🔬 논문 10편 데이터 수집 현황")

    papers_info = [
        ("SSCI", "논문 01 — 타이머 잔여시간 = 문법처리 RT 종단 지표",
         "rt_logs: seconds_remaining + p5_logs + diagnosis",
         [df_rt, df_p5, df_diag], "★★★★★"),
        ("SSCI", "논문 02 — 오답전장 재접속 간격 × 재오답률 (망각곡선)",
         "forget_logs: entry_timestamp + interval_days + re_wrong",
         [df_forget, df_retry, df_diag], "★★★★★"),
        ("SSCI", "논문 03 — 빠른 오답 vs 느린 오답 × 인지부하 유형",
         "rt_logs: error_at_second + wrong_type + timer_setting",
         [df_rt, df_p5], "★★★★"),
        ("SSCI", "논문 04 — P7 사전 노출 × P5 파생문제 정답률 (크로스 스킬)",
         "cross_logs: p7_passage_id + derived_p5_id + p7_correct + p5_correct",
         [df_cross, df_p7, df_diag], "★★★★"),
        ("KCI", "논문 05 — 자기선택 타임어택 난이도 × 문법 습득",
         "timer_history: timer_changes + upgrade_day",
         [df_timer, df_p5, df_diag], "★★★★"),
        ("KCI", "논문 06 — 게임오버 발생 문제 번호 이동 = ZPD 발달 추적",
         "zpd_logs: session_date + game_over_q_no + timer_setting",
         [df_zpd, df_diag], "★★★★"),
        ("KCI", "논문 07 — 모바일 화면너비 × EFL 수행 자연실험",
         "devices: viewport_width + screen_width + device_type",
         [df_device, df_diag], "★★★★★"),
        ("KCI", "논문 08 — Day1 서바이벌 패턴 → 6개월 지속성 예측",
         "p5_logs: day1_result + gameover_count / sessions: return_interval",
         [df_p5, df_session], "★★★"),
        ("KCI", "논문 09 — 오답 문법 유형 클러스터링 × 학습자 프로파일",
         "grammar_cluster: grammar_type + wrong_count + user_level",
         [df_cluster, df_retry, df_diag], "★★★"),
        ("KCI", "논문 10 — 인바디 피드백 확인 후 다음 세션 전략 변화",
         "feedback_logs: viewed_ms + next_timer + next_arena",
         [df_fb, df_session], "★★"),
    ]

    for tier, title, data_src, dfs, stars in papers_info:
        color = "paper-card-ssci" if tier == "SSCI" else "paper-card"
        has_data = any(not d.empty for d in dfs)
        status = "✅ 데이터 있음" if has_data else "❌ 수집 필요"
        status_color = "#009944" if has_data else "#cc0000"
        st.markdown(
            f'<div class="{color}">'
            f'<div class="paper-title">[{tier}] {title} {stars}</div>'
            f'<div class="paper-sub">필요 데이터: {data_src}</div>'
            f'<div class="paper-sub" style="color:{status_color};font-weight:700;">{status}</div>'
            f'</div>', unsafe_allow_html=True
        )

    st.divider()
    st.markdown("#### storage_data.json 전체 키 현황")
    key_summary = {k: len(v) if isinstance(v, list) else "object" for k, v in storage.items()}
    st.json(key_summary)


# ═══════════════════════════════════════════════════════════════
# TAB 9 — 미완료 알림 (기존 유지 + 신규 필드 체크)
# ═══════════════════════════════════════════════════════════════
with tab9:
    st.subheader("⚠️ 미완료 학생 알림")
    st.caption("논문 데이터 완성을 위해 follow-up이 필요한 학생 목록")

    if not all_users:
        st.info("학생 데이터가 없습니다.")
    else:
        diag_done_map = {}
        if not df_diag.empty and "user_id" in df_diag.columns and "diagnosis_day" in df_diag.columns:
            for uid in all_users:
                udiag = df_diag[df_diag["user_id"] == uid]
                diag_done_map[uid] = set(udiag["diagnosis_day"].tolist())

        survey_done = set(df_survey["user_id"].unique()) if not df_survey.empty and "user_id" in df_survey.columns else set()
        device_done = set(df_device["user_id"].unique()) if not df_device.empty and "user_id" in df_device.columns else set()
        rt_done     = set(df_rt["user_id"].unique()) if not df_rt.empty and "user_id" in df_rt.columns else set()
        forget_done = set(df_forget["user_id"].unique()) if not df_forget.empty and "user_id" in df_forget.columns else set()

        rows = []
        for uid in all_users:
            days = diag_done_map.get(uid, set())
            rows.append({
                "학생": uid,
                "디바이스": "✅" if uid in device_done else "❌",
                "설문": "✅" if uid in survey_done else "❌",
                "Day1": "✅" if 1 in days else "❌",
                "Day10": "✅" if 10 in days else "❌",
                "Day20": "✅" if 20 in days else "❌",
                "★RT로그": "✅" if uid in rt_done else "❌",
                "★망각로그": "✅" if uid in forget_done else "❌",
                "완료": "✅" if (uid in device_done and uid in survey_done
                              and {1,10,20}.issubset(days)) else "⚠️"
            })

        alert_df = pd.DataFrame(rows)
        incomplete = alert_df[alert_df["완료"] == "⚠️"]
        complete   = alert_df[alert_df["완료"] == "✅"]

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#cc0000">{len(incomplete)}</div><div class="metric-label">미완료</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#009944">{len(complete)}</div><div class="metric-label">완전 완료</div></div>', unsafe_allow_html=True)

        st.divider()
        if not incomplete.empty:
            st.markdown("#### ❌ 미완료 학생 목록")
            st.dataframe(incomplete, use_container_width=True, hide_index=True)
        if not complete.empty:
            st.markdown("#### ✅ 완료 학생 목록")
            st.dataframe(complete, use_container_width=True, hide_index=True)

        st.download_button(
            "📥 완료 현황 CSV",
            data=alert_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
            file_name=f"snapq_completion_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv", use_container_width=True
        )


# ═══════════════════════════════════════════════════════════════
# TAB 10 — ⚡ 반응속도 RT 분석 (논문 01·03 SSCI)
# ═══════════════════════════════════════════════════════════════
with tab10:
    st.subheader("⚡ 반응속도(RT) 분석 — 논문 01·03 SSCI 핵심")
    st.markdown("""
    <div class="info-box">
    <b>핵심 원리:</b> SnapQ 타이머 잔여초 = 반응속도 대리변수 (RT Proxy)<br>
    타임설정 40초에서 35초 남기고 답함 = 5초 안에 처리 = RT 5초<br>
    Han & Suzuki 2023(SSCI): RT 감소 = 문법 처리 자동화 지표<br>
    <b>→ 실험실 없이 매 세션 자동 수집 가능. 세계 최초 게임 기반 RT 자동화 측정.</b>
    </div>
    """, unsafe_allow_html=True)

    # ── rt_logs 필드 체크 ─────────────────────────────────────
    required_rt_fields = ["user_id", "session_date", "timer_setting",
                          "seconds_remaining", "correct", "question_no",
                          "grammar_type", "error_at_second"]
    if df_rt.empty:
        st.markdown('<div class="alert-box">❌ <b>rt_logs 데이터 없음</b> — 게임 페이지(P5전장)에서 아래 필드 수집 코드 추가 필요</div>', unsafe_allow_html=True)
        st.markdown("#### rt_logs 필드 스펙 (게임 페이지에 추가할 것)")
        spec_df = pd.DataFrame([
            {"필드명": "user_id",           "타입": "str",   "설명": "학습자 ID"},
            {"필드명": "session_date",       "타입": "str",   "설명": "세션 날짜 YYYY-MM-DD"},
            {"필드명": "session_no",         "타입": "int",   "설명": "누적 세션 번호 (종단 순서)"},
            {"필드명": "timer_setting",      "타입": "int",   "설명": "선택한 타임어택 초 (30/40/50)"},
            {"필드명": "question_no",        "타입": "int",   "설명": "문제 번호 (1~5)"},
            {"필드명": "seconds_remaining",  "타입": "float", "설명": "★ 핵심 — 정답/오답 시 남은 초"},
            {"필드명": "rt_proxy",           "타입": "float", "설명": "timer_setting - seconds_remaining (실질 반응시간)"},
            {"필드명": "correct",            "타입": "bool",  "설명": "정오답 여부"},
            {"필드명": "grammar_type",       "타입": "str",   "설명": "문법 유형 (tense/prep/relation/vocab/etc)"},
            {"필드명": "error_timing_type",  "타입": "str",   "설명": "fast_wrong(<20% 남음)/slow_wrong(>80% 남음)/correct"},
            {"필드명": "week",               "타입": "int",   "설명": "수집 주차 (종단 분석용)"},
        ])
        st.dataframe(spec_df, use_container_width=True, hide_index=True)

        st.markdown("#### 게임 페이지에 추가할 Python 코드 (P5 전장)")
        st.code("""
# P5 전장 문제풀이 종료 시 rt_logs에 저장
import time

def save_rt_log(storage, user_id, timer_setting, seconds_remaining,
                question_no, correct, grammar_type, session_no, week):
    rt_proxy = timer_setting - seconds_remaining
    remaining_ratio = seconds_remaining / timer_setting

    if correct:
        error_timing_type = "correct"
    elif remaining_ratio > 0.8:
        error_timing_type = "fast_wrong"   # 빠른 오답 = 충동 반응
    elif remaining_ratio < 0.2:
        error_timing_type = "slow_wrong"   # 느린 오답 = 인지부하
    else:
        error_timing_type = "mid_wrong"

    log = {
        "user_id":          user_id,
        "session_date":     datetime.now().strftime("%Y-%m-%d"),
        "session_no":       session_no,
        "timer_setting":    timer_setting,
        "question_no":      question_no,
        "seconds_remaining": seconds_remaining,
        "rt_proxy":         round(rt_proxy, 2),
        "correct":          correct,
        "grammar_type":     grammar_type,
        "error_timing_type": error_timing_type,
        "week":             week,
        "timestamp":        datetime.now().isoformat(),
    }
    if "rt_logs" not in storage:
        storage["rt_logs"] = []
    storage["rt_logs"].append(log)
    return storage
        """, language="python")

    else:
        # ── 데이터 있을 때 분석 ──────────────────────────────
        st.success(f"✅ rt_logs 수집 중 — {len(df_rt)}개 레코드")

        # RT 분포
        if "rt_proxy" in df_rt.columns:
            st.markdown("#### 전체 RT(반응시간) 분포")
            rt_hist = df_rt.groupby("rt_proxy").size().reset_index(name="횟수")
            st.bar_chart(rt_hist.set_index("rt_proxy"))

        # 오답 타이밍 유형 분포
        if "error_timing_type" in df_rt.columns:
            st.markdown("#### 오답 타이밍 유형 분포 (논문 03)")
            etc = df_rt["error_timing_type"].value_counts().reset_index()
            etc.columns = ["유형", "횟수"]
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(etc, use_container_width=True, hide_index=True)
            with col2:
                st.bar_chart(etc.set_index("유형"))
            st.markdown("""
            | 유형 | 의미 | 학습 처방 |
            |------|------|----------|
            | fast_wrong | 충동적 반응, 자동화 실패 | 개념 재학습 필요 |
            | mid_wrong  | 일반 오류 | 반복 훈련 |
            | slow_wrong | 작업기억 초과, 인지부하 | 타임 늘리기 |
            """)

        # 주차별 RT 변화 (자동화 종단 지표)
        if "week" in df_rt.columns and "rt_proxy" in df_rt.columns:
            st.markdown("#### 주차별 평균 RT 변화 — 자동화 종단 지표 (논문 01)")
            rt_week = df_rt.groupby("week")["rt_proxy"].mean().round(2).reset_index()
            rt_week.columns = ["주차", "평균 RT(초)"]
            st.line_chart(rt_week.set_index("주차"))
            st.caption("RT가 감소할수록 문법 처리 자동화 진행 중 (Han & Suzuki 2023 이론)")

        # 문법 유형별 RT
        if "grammar_type" in df_rt.columns and "rt_proxy" in df_rt.columns:
            st.markdown("#### 문법 유형별 평균 RT (어느 유형이 가장 느린가)")
            gt_rt = df_rt.groupby("grammar_type")["rt_proxy"].mean().round(2).reset_index()
            gt_rt.columns = ["문법 유형", "평균 RT(초)"]
            st.bar_chart(gt_rt.set_index("문법 유형"))

        # 학생별 RT 종단 추적
        if all_users and "user_id" in df_rt.columns:
            st.markdown("#### 학생별 RT 종단 추적")
            sel_rt = st.selectbox("학생 선택", all_users, key="rt_sel")
            urt = df_rt[df_rt["user_id"] == sel_rt]
            if not urt.empty and "week" in urt.columns:
                rt_u = urt.groupby("week")["rt_proxy"].mean().round(2)
                st.line_chart(rt_u)
                st.caption(f"RT 변화 범위: {urt['rt_proxy'].min():.1f}초 ~ {urt['rt_proxy'].max():.1f}초")

        st.divider()
        st.markdown("#### 원데이터")
        st.dataframe(df_rt, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════
# TAB 11 — 🌀 망각곡선 분석 (논문 02 SSCI)
# ═══════════════════════════════════════════════════════════════
with tab11:
    st.subheader("🌀 망각곡선 분석 — 논문 02 SSCI")
    st.markdown("""
    <div class="info-box">
    <b>핵심 원리:</b> 오답전장 재접속 간격 × 재오답률 = 개인별 망각곡선 실증<br>
    Tabibian et al. 2019 (PNAS): Duolingo 어휘 데이터로 망각곡선 최적화<br>
    <b>→ SnapQ: 어휘가 아닌 문법·독해 오답의 망각곡선 = 세계 최초</b><br>
    같은 문제를 N일 후 다시 틀리는 비율 = 개인별 망각 속도 측정
    </div>
    """, unsafe_allow_html=True)

    required_forget_fields = ["user_id", "problem_id", "first_wrong_date",
                               "revisit_date", "interval_days", "re_wrong", "grammar_type"]
    if df_forget.empty:
        st.markdown('<div class="alert-box">❌ <b>forget_logs 데이터 없음</b> — 오답전장에서 재접속 로그 수집 필요</div>', unsafe_allow_html=True)
        st.markdown("#### forget_logs 필드 스펙")
        spec_df2 = pd.DataFrame([
            {"필드명": "user_id",          "타입": "str",   "설명": "학습자 ID"},
            {"필드명": "problem_id",        "타입": "str",   "설명": "오답 문제 고유 ID"},
            {"필드명": "grammar_type",      "타입": "str",   "설명": "문법 유형"},
            {"필드명": "source",            "타입": "str",   "설명": "P5/P7 구분"},
            {"필드명": "first_wrong_date",  "타입": "str",   "설명": "최초 오답 날짜"},
            {"필드명": "revisit_date",      "타입": "str",   "설명": "오답전장 재접속 날짜"},
            {"필드명": "interval_days",     "타입": "int",   "설명": "★ 핵심 — 재접속까지 경과 일수"},
            {"필드명": "re_wrong",          "타입": "bool",  "설명": "★ 핵심 — 재도전 시 또 틀렸는지"},
            {"필드명": "revisit_count",     "타입": "int",   "설명": "누적 재방문 횟수"},
            {"필드명": "finally_correct",   "타입": "bool",  "설명": "최종 극복 여부"},
            {"필드명": "days_to_overcome",  "타입": "int",   "설명": "극복까지 걸린 일수"},
        ])
        st.dataframe(spec_df2, use_container_width=True, hide_index=True)

        st.markdown("#### 오답전장 페이지에 추가할 Python 코드")
        st.code("""
def save_forget_log(storage, user_id, problem_id, grammar_type,
                    source, first_wrong_date, re_wrong, revisit_count):
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        interval = (datetime.strptime(today, "%Y-%m-%d") -
                    datetime.strptime(first_wrong_date, "%Y-%m-%d")).days
    except:
        interval = 0

    log = {
        "user_id":         user_id,
        "problem_id":      problem_id,
        "grammar_type":    grammar_type,
        "source":          source,
        "first_wrong_date": first_wrong_date,
        "revisit_date":    today,
        "interval_days":   interval,
        "re_wrong":        re_wrong,
        "revisit_count":   revisit_count,
        "timestamp":       datetime.now().isoformat(),
    }
    if "forget_logs" not in storage:
        storage["forget_logs"] = []
    storage["forget_logs"].append(log)
    return storage
        """, language="python")

    else:
        st.success(f"✅ forget_logs 수집 중 — {len(df_forget)}개 레코드")

        if "interval_days" in df_forget.columns and "re_wrong" in df_forget.columns:
            st.markdown("#### 재접속 간격 × 재오답률 (망각곡선 데이터)")
            fc = df_forget.groupby("interval_days")["re_wrong"].mean().round(3).reset_index()
            fc.columns = ["경과일수", "재오답률"]
            st.line_chart(fc.set_index("경과일수"))
            st.caption("Ebbinghaus 망각곡선: 경과일 증가 → 재오답률 증가 예측")

        if "grammar_type" in df_forget.columns and "interval_days" in df_forget.columns:
            st.markdown("#### 문법 유형별 평균 망각 속도")
            fg = df_forget.groupby("grammar_type")["interval_days"].mean().round(1).reset_index()
            fg.columns = ["문법 유형", "평균 망각간격(일)"]
            st.bar_chart(fg.set_index("문법 유형"))

        if "days_to_overcome" in df_forget.columns:
            st.markdown("#### 문제 극복까지 걸린 평균 일수")
            ov = df_forget.groupby("grammar_type")["days_to_overcome"].mean().round(1).reset_index()
            ov.columns = ["문법 유형", "극복 평균 일수"]
            st.bar_chart(ov.set_index("문법 유형"))

        st.divider()
        st.dataframe(df_forget, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════
# TAB 12 — 🔀 크로스스킬 전이 (논문 04 SSCI + 특허 핵심)
# ═══════════════════════════════════════════════════════════════
with tab12:
    st.subheader("🔀 P7→P5 크로스스킬 전이 분석 — 논문 04 SSCI + 특허 청구항 1번 입증")
    st.markdown("""
    <div class="info-box">
    <b>핵심 원리:</b> P7 지문을 먼저 풀었을 때 → 그 지문에서 변환된 P5 문제 정답률 비교<br>
    P7 사전 노출 있음 vs 없음 → 파생 P5 문제 정답률 차이 = 크로스 스킬 전이 효과<br>
    <b>→ 특허 청구항 1번의 학습 효과를 직접 증명하는 유일한 데이터</b>
    </div>
    """, unsafe_allow_html=True)

    if df_cross.empty:
        st.markdown('<div class="alert-box">❌ <b>cross_logs 데이터 없음</b> — P7 전장에서 지문 ID와 파생 P5 문제 ID 연결 수집 필요</div>', unsafe_allow_html=True)
        st.markdown("#### cross_logs 필드 스펙 (P7 전장 + 오답전장에서 수집)")
        spec_df3 = pd.DataFrame([
            {"필드명": "user_id",          "타입": "str",  "설명": "학습자 ID"},
            {"필드명": "p7_passage_id",    "타입": "str",  "설명": "★ P7 지문 고유 ID"},
            {"필드명": "p7_correct",       "타입": "bool", "설명": "P7 지문 정답 여부"},
            {"필드명": "p7_session_date",  "타입": "str",  "설명": "P7 풀이 날짜"},
            {"필드명": "derived_p5_id",    "타입": "str",  "설명": "★ P7에서 변환된 P5 문제 ID"},
            {"필드명": "p5_correct",       "타입": "bool", "설명": "파생 P5 문제 정답 여부"},
            {"필드명": "p5_session_date",  "타입": "str",  "설명": "P5 풀이 날짜"},
            {"필드명": "p7_first_exposed", "타입": "bool", "설명": "P7 사전 노출 여부 (실험 조건)"},
            {"필드명": "days_gap",         "타입": "int",  "설명": "P7 풀이 후 P5 풀이까지 경과 일수"},
            {"필드명": "grammar_type",     "타입": "str",  "설명": "문법 유형"},
        ])
        st.dataframe(spec_df3, use_container_width=True, hide_index=True)

        st.markdown("#### P7 전장 페이지에 추가할 Python 코드")
        st.code("""
def save_cross_log(storage, user_id, p7_passage_id, p7_correct,
                   derived_p5_ids, p7_session_date):
    \"\"\"P7 풀이 완료 시 → 파생될 P5 문제들 등록\"\"\"
    for p5_id in derived_p5_ids:
        log = {
            "user_id":         user_id,
            "p7_passage_id":   p7_passage_id,
            "p7_correct":      p7_correct,
            "p7_session_date": p7_session_date,
            "derived_p5_id":   p5_id,
            "p5_correct":      None,  # P5 풀이 시 업데이트
            "p5_session_date": None,
            "p7_first_exposed": True,
            "days_gap":        0,
            "timestamp":       datetime.now().isoformat(),
        }
        if "cross_logs" not in storage:
            storage["cross_logs"] = []
        storage["cross_logs"].append(log)
    return storage

def update_cross_log_p5(storage, user_id, derived_p5_id, p5_correct):
    \"\"\"P5 문제 풀이 완료 시 → cross_logs 업데이트\"\"\"
    today = datetime.now().strftime("%Y-%m-%d")
    for log in storage.get("cross_logs", []):
        if log["user_id"] == user_id and log["derived_p5_id"] == derived_p5_id and log["p5_correct"] is None:
            log["p5_correct"] = p5_correct
            log["p5_session_date"] = today
            try:
                gap = (datetime.strptime(today, "%Y-%m-%d") -
                       datetime.strptime(log["p7_session_date"], "%Y-%m-%d")).days
                log["days_gap"] = gap
            except:
                pass
            break
    return storage
        """, language="python")

    else:
        st.success(f"✅ cross_logs 수집 중 — {len(df_cross)}개 레코드")

        if "p7_first_exposed" in df_cross.columns and "p5_correct" in df_cross.columns:
            st.markdown("#### P7 사전 노출 여부 × P5 정답률 비교 (논문 04 핵심 분석)")
            comp = df_cross.groupby("p7_first_exposed")["p5_correct"].mean().round(3).reset_index()
            comp["p7_first_exposed"] = comp["p7_first_exposed"].map({True: "P7 사전 노출 있음", False: "없음"})
            comp.columns = ["조건", "P5 정답률"]
            st.dataframe(comp, use_container_width=True, hide_index=True)
            st.bar_chart(comp.set_index("조건"))
            st.caption("두 조건 간 유의한 차이 → 크로스 스킬 전이 효과 입증 → 특허 청구항 1번 학술 근거")

        if "days_gap" in df_cross.columns and "p5_correct" in df_cross.columns:
            st.markdown("#### P7 풀이 후 경과 일수 × P5 정답률 (전이 지속 기간)")
            gap_df = df_cross.groupby("days_gap")["p5_correct"].mean().round(3).reset_index()
            gap_df.columns = ["경과 일수", "P5 정답률"]
            st.line_chart(gap_df.set_index("경과 일수"))

        st.divider()
        st.dataframe(df_cross, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════
# TAB 13 — 🧩 ZPD 경계 추적 (논문 06 KCI)
# ═══════════════════════════════════════════════════════════════
with tab13:
    st.subheader("🧩 ZPD 경계 추적 — 논문 06 KCI")
    st.markdown("""
    <div class="info-box">
    <b>핵심 원리:</b> 게임오버 발생 문제 번호 이동 = ZPD 경계 발달 지표<br>
    Day1: 2번 문제에서 종료 → Day30: 5번에서 종료 = ZPD 확장됨<br>
    Vygotsky ZPD: 실제 발달 수준과 잠재 발달 수준의 경계를 매 세션 자동 탐지<br>
    <b>→ 기존 ZPD 연구는 설문·사전사후검사. SnapQ는 매 세션 자동 기록.</b>
    </div>
    """, unsafe_allow_html=True)

    if df_zpd.empty:
        st.markdown('<div class="alert-box">❌ <b>zpd_logs 데이터 없음</b> — P5·P7 전장에서 게임오버 지점 저장 필요</div>', unsafe_allow_html=True)
        st.markdown("#### zpd_logs 필드 스펙")
        spec_zpd = pd.DataFrame([
            {"필드명": "user_id",           "타입": "str",   "설명": "학습자 ID"},
            {"필드명": "session_date",       "타입": "str",   "설명": "세션 날짜"},
            {"필드명": "session_no",         "타입": "int",   "설명": "누적 세션 번호"},
            {"필드명": "arena",              "타입": "str",   "설명": "P5/P7"},
            {"필드명": "timer_setting",      "타입": "int",   "설명": "타임어택 설정"},
            {"필드명": "game_over_q_no",     "타입": "int",   "설명": "★ 핵심 — 게임오버 발생 문제 번호"},
            {"필드명": "result",             "타입": "str",   "설명": "VICTORY/GAME_OVER"},
            {"필드명": "max_q_reached",      "타입": "int",   "설명": "도달한 최대 문제 번호"},
            {"필드명": "week",               "타입": "int",   "설명": "수집 주차"},
        ])
        st.dataframe(spec_zpd, use_container_width=True, hide_index=True)

        st.markdown("#### P5 전장 페이지에 추가할 Python 코드")
        st.code("""
def save_zpd_log(storage, user_id, arena, timer_setting,
                 game_over_q_no, result, max_q_reached, session_no, week):
    log = {
        "user_id":        user_id,
        "session_date":   datetime.now().strftime("%Y-%m-%d"),
        "session_no":     session_no,
        "arena":          arena,
        "timer_setting":  timer_setting,
        "game_over_q_no": game_over_q_no,  # VICTORY면 None
        "result":         result,
        "max_q_reached":  max_q_reached,
        "week":           week,
        "timestamp":      datetime.now().isoformat(),
    }
    if "zpd_logs" not in storage:
        storage["zpd_logs"] = []
    storage["zpd_logs"].append(log)
    return storage
        """, language="python")

    else:
        st.success(f"✅ zpd_logs 수집 중 — {len(df_zpd)}개 레코드")

        if "week" in df_zpd.columns and "max_q_reached" in df_zpd.columns:
            st.markdown("#### 주차별 평균 도달 문제 번호 — ZPD 발달 곡선")
            zpd_week = df_zpd.groupby("week")["max_q_reached"].mean().round(2).reset_index()
            zpd_week.columns = ["주차", "평균 도달 문제번호"]
            st.line_chart(zpd_week.set_index("주차"))
            st.caption("도달 번호 증가 = ZPD 확장 = 발달 수준 향상")

        if "game_over_q_no" in df_zpd.columns:
            st.markdown("#### 게임오버 발생 문제 번호 분포 (ZPD 경계 분포)")
            go = df_zpd["game_over_q_no"].dropna()
            if not go.empty:
                go_dist = go.value_counts().sort_index().reset_index()
                go_dist.columns = ["문제 번호", "게임오버 횟수"]
                st.bar_chart(go_dist.set_index("문제 번호"))

        if all_users and "user_id" in df_zpd.columns:
            st.markdown("#### 학생별 ZPD 발달 궤적")
            sel_zpd = st.selectbox("학생 선택", all_users, key="zpd_sel")
            uzpd = df_zpd[df_zpd["user_id"] == sel_zpd]
            if not uzpd.empty and "session_no" in uzpd.columns and "max_q_reached" in uzpd.columns:
                st.line_chart(uzpd.set_index("session_no")["max_q_reached"])
                st.caption(f"세션 수: {len(uzpd)} / 최고 도달: {uzpd['max_q_reached'].max()}번 문제")

        st.divider()
        st.dataframe(df_zpd, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════
# TAB 14 — 🗺️ 데이터 필드 현황 (누락 알림 + 추가 가이드)
# ═══════════════════════════════════════════════════════════════
with tab14:
    st.subheader("🗺️ 논문·특허 입증용 데이터 필드 전체 현황")
    st.caption("수집 중인 필드 vs 누락 필드 완전 점검 — 지금 당장 추가해야 할 것")

    # ── 현황 체크 ─────────────────────────────────────────────
    checks = [
        # (논문번호, 필드명, 소스df, 컬럼명, 중요도, 설명)
        ("논문01/03", "seconds_remaining", df_rt,     "seconds_remaining",  "🔴 최우선", "RT 대리변수 — 타임어택 잔여초"),
        ("논문01/03", "rt_proxy",          df_rt,     "rt_proxy",           "🔴 최우선", "실질 반응시간 = timer - remaining"),
        ("논문01/03", "error_timing_type", df_rt,     "error_timing_type",  "🔴 최우선", "빠른오답/느린오답/정답 구분"),
        ("논문01/03", "grammar_type",      df_rt,     "grammar_type",       "🔴 최우선", "문법 유형 태그"),
        ("논문02",    "interval_days",     df_forget, "interval_days",      "🔴 최우선", "오답전장 재접속 경과 일수"),
        ("논문02",    "re_wrong",          df_forget, "re_wrong",           "🔴 최우선", "재접속 시 재오답 여부"),
        ("논문04",    "p7_passage_id",     df_cross,  "p7_passage_id",      "🔴 최우선", "P7 지문 고유 ID"),
        ("논문04",    "derived_p5_id",     df_cross,  "derived_p5_id",      "🔴 최우선", "P7 파생 P5 문제 ID"),
        ("논문06",    "game_over_q_no",    df_zpd,    "game_over_q_no",     "🔴 최우선", "게임오버 발생 문제 번호"),
        ("논문07",    "viewport_width",    df_device, "viewport_width",     "🔴 최우선", "브라우저 뷰포트 너비 (window.innerWidth)"),
        ("논문05",    "timer_changes",     df_timer,  "timer_changes",      "🟡 중요",   "타이머 변경 이력"),
        ("논문08",    "session_no",        df_session,"session_no",         "🟡 중요",   "누적 세션 번호 (종단 순서)"),
        ("논문09",    "grammar_cluster",   df_cluster,"grammar_type",       "🟡 중요",   "오답 문법 유형 클러스터"),
        ("논문10",    "feedback_viewed_ms",df_fb,     "viewed_ms",          "🟢 권장",   "인바디 피드백 확인 시간(ms)"),
        ("논문10",    "next_timer",        df_fb,     "next_timer",         "🟢 권장",   "피드백 후 다음 세션 타이머 선택"),
        # 기존 (이미 수집 중)
        ("논문07",    "screen_width",      df_device, "screen_width",       "✅ 수집중", "화면 너비"),
        ("논문07",    "device_type",       df_device, "device_type",        "✅ 수집중", "기기 유형"),
        ("공통",      "diagnosis_day",     df_diag,   "diagnosis_day",      "✅ 수집중", "Day1/10/20 진단일"),
        ("논문03",    "timer_selected",    df_p5,     "timer_selected",     "✅ 수집중", "타임어택 선택"),
        ("논문06",    "result",            df_p5,     "result",             "✅ 수집중", "VICTORY/GAME OVER"),
        ("논문02",    "is_retry",          df_retry,  "is_retry",           "✅ 수집중", "재도전 여부"),
    ]

    rows_check = []
    for paper, field, df_src, col, priority, desc in checks:
        collected = not df_src.empty and col in df_src.columns and df_src[col].notna().any()
        count = df_src[col].notna().sum() if collected else 0
        rows_check.append({
            "논문": paper,
            "필드명": field,
            "우선순위": priority,
            "수집 현황": "✅ 수집 중" if collected else "❌ 미수집",
            "레코드 수": count,
            "설명": desc,
        })

    check_df = pd.DataFrame(rows_check)
    missing = check_df[check_df["수집 현황"] == "❌ 미수집"]
    collected = check_df[check_df["수집 현황"] == "✅ 수집 중"]

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#cc0000">{len(missing)}</div><div class="metric-label">미수집 필드</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#009944">{len(collected)}</div><div class="metric-label">수집 중 필드</div></div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("#### 🔴 지금 당장 추가해야 할 필드")
    urgent = missing[missing["우선순위"].str.contains("최우선")]
    if not urgent.empty:
        st.dataframe(urgent[["논문","필드명","설명"]], use_container_width=True, hide_index=True)

    st.markdown("#### 🟡 중요 — 가능한 빠른 시일 내 추가")
    important = missing[missing["우선순위"].str.contains("중요")]
    if not important.empty:
        st.dataframe(important[["논문","필드명","설명"]], use_container_width=True, hide_index=True)

    st.markdown("#### ✅ 현재 수집 중인 필드")
    st.dataframe(collected[["논문","필드명","레코드 수","설명"]], use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("#### storage_data.json에 추가해야 할 최소 키 구조")
    st.code("""
# storage_data.json 완전 구조 (현재 + 신규)
{
  # ── 기존 (유지) ────────────────────────────
  "devices":        [...],   # screen_width, device_type, os_type
  "surveys":        [...],   # survey_device, posture, distance
  "diagnosis":      [...],   # diagnosis_day, p5_score, p7_score, total_score
  "p5_logs":        [...],   # timer_selected, result, correct_count
  "p7_logs":        [...],   # step_reached, final_result, passage_id ← 추가필요
  "retry_logs":     [...],   # is_retry, problem_id, grammar_type ← grammar_type 추가필요
  "sessions":       [...],   # session_start, is_returning_student, cohort_month

  # ── 신규 추가 (논문·특허 입증용) ────────────
  "rt_logs":        [...],   # ★★★ seconds_remaining, rt_proxy, error_timing_type
  "forget_logs":    [...],   # ★★★ interval_days, re_wrong, revisit_count
  "cross_logs":     [...],   # ★★★ p7_passage_id, derived_p5_id, p5_correct
  "zpd_logs":       [...],   # ★★ game_over_q_no, max_q_reached, session_no
  "timer_history":  [...],   # ★★ timer_changes, upgrade_date
  "feedback_logs":  [...],   # ★  viewed_ms, next_timer, next_arena
  "grammar_cluster":[...]    # ★  grammar_type, wrong_count, user_level
}
    """, language="json")

    st.markdown("#### devices에 추가해야 할 1줄 코드 (viewport_width)")
    st.code("""
# main_hub.py 또는 첫 접속 페이지 상단에 추가
import streamlit.components.v1 as components

# viewport_width 자동 수집
components.html(\"\"\"
<script>
const vw = window.innerWidth;
window.parent.postMessage({type: 'viewport', width: vw}, '*');
</script>
\"\"\", height=0)

# 또는 st.query_params / session_state를 통해 전달
# 대안: user-agent 파싱 대신 JS로 직접 수집이 정확
    """, language="python")
