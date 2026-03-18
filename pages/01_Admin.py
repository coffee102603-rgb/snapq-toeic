import streamlit as st
import json, os, pandas as pd
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
.paper-title{font-size:1rem;font-weight:800;color:#12274D;}
.paper-sub{font-size:0.85rem;color:#555;margin-top:4px;}
.alert-box{background:#fff0f0;border-left:5px solid #cc0000;border-radius:8px;
  padding:0.8rem 1.2rem;margin-bottom:0.5rem;}
.stDataFrame {color:#111111 !important;}
.stTabs [data-baseweb="tab"] {color:#111111 !important; font-weight:700;}
</style>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
col_title, col_back = st.columns([5, 1])
with col_title:
    st.markdown("<h2 style='margin-bottom:0;'>📊 SnapQ 관리자 대시보드</h2>", unsafe_allow_html=True)
    st.caption("논문 연구용 데이터 분석 시스템 — 학생에게 비공개")
with col_back:
    st.markdown("<div style='padding-top:0.8rem;'>", unsafe_allow_html=True)
    if st.button("🏠 메인으로", use_container_width=True):
        st.switch_page("main_hub.py")
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# DATA LOADING — storage_data.json + 기존 JSONL 병합
# ─────────────────────────────────────────────────────────────
STORAGE_FILE = "storage_data.json"
DATA_DIR = "data/research_logs"
SURVEY_DIR = "data/cohorts"


def load_storage():
    """storage_data.json에서 논문용 데이터 로드"""
    if not os.path.exists(STORAGE_FILE):
        return {}
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_storage(data: dict):
    """storage_data.json에 저장"""
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_all_logs():
    """기존 JSONL 로그 로드"""
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


def get_device_df(storage: dict) -> pd.DataFrame:
    """A. 디바이스 정보"""
    rows = storage.get("devices", [])
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def get_survey_df(storage: dict) -> pd.DataFrame:
    """B. 첫 접속 설문"""
    rows = storage.get("surveys", [])
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def get_diagnosis_df(storage: dict) -> pd.DataFrame:
    """C. Day1·Day10·Day20 진단"""
    rows = storage.get("diagnosis", [])
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def get_p5_df(storage: dict) -> pd.DataFrame:
    """D. P5 전장 로그"""
    rows = storage.get("p5_logs", [])
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def get_p7_df(storage: dict) -> pd.DataFrame:
    """E. P7 전장 로그"""
    rows = storage.get("p7_logs", [])
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def get_retry_df(storage: dict) -> pd.DataFrame:
    """F. 역전장 로그"""
    rows = storage.get("retry_logs", [])
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def get_session_df(storage: dict) -> pd.DataFrame:
    """G. 출석·세션"""
    rows = storage.get("sessions", [])
    return pd.DataFrame(rows) if rows else pd.DataFrame()


# ── 로드 실행 ──────────────────────────────────────────────────
storage = load_storage()
df_all  = load_all_logs()

df_device   = get_device_df(storage)
df_survey   = get_survey_df(storage)
df_diag     = get_diagnosis_df(storage)
df_p5       = get_p5_df(storage)
df_p7       = get_p7_df(storage)
df_retry    = get_retry_df(storage)
df_session  = get_session_df(storage)

# 기존 JSONL에서 문제풀이 df
df_qa = pd.DataFrame()
if not df_all.empty:
    df_qa = df_all[
        ~df_all.get("type", pd.Series([""] * len(df_all))).isin(["session", "session_v2"])
    ].copy() if "type" in df_all.columns else df_all.copy()

# 전체 user_id 목록 (모든 소스 통합)
all_users = set()
for _df in [df_qa, df_device, df_survey, df_diag, df_p5, df_p7, df_retry, df_session]:
    if not _df.empty and "user_id" in _df.columns:
        all_users.update(_df["user_id"].dropna().unique())
all_users = sorted(all_users)

# ─────────────────────────────────────────────────────────────
# TABS (기존 5개 + 신규 4개)
# ─────────────────────────────────────────────────────────────
(tab1, tab2, tab3, tab4, tab5,
 tab6, tab7, tab8, tab9) = st.tabs([
    "👥 학생 현황",
    "📈 학습 분석",
    "🎮 게이미피케이션",
    "📋 설문 데이터",
    "💾 내보내기",
    "📱 디바이스 분석",      # 논문 1편 핵심
    "📖 진단 Day1·10·20",   # 논문 측정
    "🔬 논문 데이터 요약",   # 논문 3편 통합
    "⚠️ 미완료 알림",        # 관리용
])


# ═══════════════════════════════════════════════════════════════
# TAB 1 — 기존 학생 현황 (유지 + 강화)
# ═══════════════════════════════════════════════════════════════
with tab1:
    st.subheader("👥 전체 학생 현황")

    total_users = len(all_users)
    total_q = len(df_qa) if not df_qa.empty else 0
    correct_sum = df_qa["correct"].sum() if (not df_qa.empty and "correct" in df_qa.columns) else 0
    acc = round(correct_sum / total_q * 100, 1) if total_q > 0 else 0
    avg_q = round(total_q / total_users, 1) if total_users > 0 else 0
    diag_done = df_diag["user_id"].nunique() if not df_diag.empty else 0
    returning = df_session["user_id"][df_session["is_returning_student"] == True].nunique() \
        if (not df_session.empty and "is_returning_student" in df_session.columns) else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    for col, val, label in zip(
        [c1, c2, c3, c4, c5, c6],
        [total_users, total_q, f"{acc}%", avg_q, diag_done, returning],
        ["전체 학생", "총 풀이수", "평균 정답률", "학생당 풀이", "진단 완료", "재수강생"]
    ):
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-val">{val}</div>'
                f'<div class="metric-label">{label}</div>'
                f'</div>', unsafe_allow_html=True
            )

    st.divider()

    # 학생별 요약 테이블
    rows = []
    for uid in all_users:
        # 문제풀이
        uqa = df_qa[df_qa["user_id"] == uid] if (not df_qa.empty and "user_id" in df_qa.columns) else pd.DataFrame()
        total = len(uqa)
        correct = uqa["correct"].sum() if (not uqa.empty and "correct" in uqa.columns) else 0
        acc_u = round(correct / total * 100, 1) if total > 0 else "-"
        # 디바이스
        udev = df_device[df_device["user_id"] == uid] if (not df_device.empty and "user_id" in df_device.columns) else pd.DataFrame()
        dev_type = udev["device_type"].iloc[0] if (not udev.empty and "device_type" in udev.columns) else "-"
        screen_w = udev["screen_width"].iloc[0] if (not udev.empty and "screen_width" in udev.columns) else "-"
        # 진단
        udiag = df_diag[df_diag["user_id"] == uid] if (not df_diag.empty and "user_id" in df_diag.columns) else pd.DataFrame()
        days_done = sorted(udiag["diagnosis_day"].tolist()) if (not udiag.empty and "diagnosis_day" in udiag.columns) else []
        diag_str = ", ".join([f"Day{d}" for d in days_done]) if days_done else "미진단"
        # 최근 접속
        last = "-"
        for _d, _c in [(df_qa, "timestamp"), (df_session, "session_start")]:
            if not _d.empty and "user_id" in _d.columns and _c in _d.columns:
                u_ = _d[_d["user_id"] == uid][_c].dropna()
                if not u_.empty:
                    last = str(u_.max())[:10]
                    break
        # 재수강
        is_ret = "-"
        if not df_session.empty and "user_id" in df_session.columns and "is_returning_student" in df_session.columns:
            u_s = df_session[df_session["user_id"] == uid]
            if not u_s.empty:
                is_ret = "재수강" if u_s["is_returning_student"].iloc[0] else "신규"

        rows.append({
            "학생": uid, "총문제": total, "정답수": int(correct),
            "정답률(%)": acc_u, "기기": dev_type,
            "화면너비(px)": screen_w, "진단완료": diag_str,
            "구분": is_ret, "최근접속": last
        })

    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("아직 학생 데이터가 없습니다.")


# ═══════════════════════════════════════════════════════════════
# TAB 2 — 기존 학습 분석 (유지)
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
            cat_df = df_qa.groupby("category").agg(
                총문제=("correct", "count"), 정답수=("correct", "sum")
            ).reset_index()
            cat_df["정답률(%)"] = (cat_df["정답수"] / cat_df["총문제"] * 100).round(1)
            st.dataframe(cat_df.sort_values("정답률(%)"), use_container_width=True, hide_index=True)
    st.divider()
    st.markdown("#### 주차별 정답률 변화")
    if not df_qa.empty and "week" in df_qa.columns and "correct" in df_qa.columns:
        wdf = df_qa.groupby("week").agg(
            총문제=("correct", "count"), 정답수=("correct", "sum")
        ).reset_index()
        wdf["정답률(%)"] = (wdf["정답수"] / wdf["총문제"] * 100).round(1)
        st.line_chart(wdf.set_index("week")["정답률(%)"])
    st.markdown("#### 시간대별 접속 패턴")
    if not df_qa.empty and "hour" in df_qa.columns:
        hc = df_qa["hour"].value_counts().sort_index().reset_index()
        hc.columns = ["시간대", "문제수"]
        st.bar_chart(hc.set_index("시간대"))


# ═══════════════════════════════════════════════════════════════
# TAB 3 — 기존 게이미피케이션 (유지)
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.subheader("🎮 게이미피케이션 지표")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 타이머 선택 패턴 (P5)")
        # storage p5_logs 우선, 없으면 기존 df
        src = df_p5 if (not df_p5.empty and "timer_selected" in df_p5.columns) else df_qa
        if not src.empty and "timer_selected" in src.columns:
            tdf = src[src["timer_selected"].notna()]
            if not tdf.empty:
                tc = tdf["timer_selected"].value_counts().reset_index()
                tc.columns = ["타이머(초)", "선택횟수"]
                st.bar_chart(tc.set_index("타이머(초)"))
    with col2:
        st.markdown("#### 재도전 vs 첫도전")
        src2 = df_retry if not df_retry.empty else df_qa
        if not src2.empty and "is_retry" in src2.columns:
            rc = src2["is_retry"].value_counts()
            rdf = pd.DataFrame({"구분": ["재도전" if k else "첫도전" for k in rc.index], "횟수": rc.values})
            st.dataframe(rdf, use_container_width=True, hide_index=True)
    st.divider()
    st.markdown("#### 요일별 학습 패턴")
    if not df_qa.empty and "day_of_week" in df_qa.columns:
        dow = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dc = df_qa["day_of_week"].value_counts().reindex(dow, fill_value=0).reset_index()
        dc.columns = ["요일", "문제수"]
        st.bar_chart(dc.set_index("요일"))
    st.markdown("#### 학생별 평균 응답시간 변화 (순발력)")
    if all_users and not df_qa.empty and "time_taken" in df_qa.columns and "week" in df_qa.columns:
        sel = st.selectbox("학생 선택", all_users, key="spd")
        udf = df_qa[df_qa["user_id"] == sel] if "user_id" in df_qa.columns else pd.DataFrame()
        if not udf.empty:
            spd = udf.groupby("week")["time_taken"].mean().round(2).reset_index()
            spd.columns = ["주차", "평균응답(초)"]
            st.line_chart(spd.set_index("주차"))

    # P5 VICTORY/GAME OVER 비율
    st.divider()
    st.markdown("#### P5 전장 승패 비율")
    if not df_p5.empty and "result" in df_p5.columns:
        res = df_p5["result"].value_counts().reset_index()
        res.columns = ["결과", "횟수"]
        st.bar_chart(res.set_index("결과"))

    # P7 단계 도달률
    st.markdown("#### P7 전장 단계별 도달률")
    if not df_p7.empty and "step_reached" in df_p7.columns:
        sr = df_p7["step_reached"].value_counts().reset_index()
        sr.columns = ["도달단계", "횟수"]
        st.bar_chart(sr.set_index("도달단계"))


# ═══════════════════════════════════════════════════════════════
# TAB 4 — 기존 설문 + 신규 첫접속 설문 (B항목)
# ═══════════════════════════════════════════════════════════════
with tab4:
    st.subheader("📋 설문 데이터")

    # ── B. 첫 접속 설문 (storage) ──────────────────────────────
    st.markdown("#### B. 첫 접속 설문 4문항 (논문 1편)")
    if not df_survey.empty:
        st.dataframe(df_survey, use_container_width=True, hide_index=True)
        col1, col2 = st.columns(2)
        with col1:
            if "survey_device" in df_survey.columns:
                st.markdown("**기기 종류 분포**")
                dvc = df_survey["survey_device"].value_counts().reset_index()
                dvc.columns = ["기기", "명수"]
                st.bar_chart(dvc.set_index("기기"))
        with col2:
            if "survey_posture" in df_survey.columns:
                st.markdown("**학습 자세 분포**")
                pos = df_survey["survey_posture"].value_counts().reset_index()
                pos.columns = ["자세", "명수"]
                st.bar_chart(pos.set_index("자세"))
        if "survey_distance" in df_survey.columns:
            st.markdown("**눈-화면 거리 분포**")
            dist = df_survey["survey_distance"].value_counts().reset_index()
            dist.columns = ["거리", "명수"]
            st.bar_chart(dist.set_index("거리"))
    else:
        st.info("첫 접속 설문 데이터가 아직 없습니다.")

    st.divider()

    # ── 기존 사전/사후 설문 (cohorts) ──────────────────────────
    st.markdown("#### 기존 사전/사후 설문 데이터")
    survey_data = []
    if os.path.exists(SURVEY_DIR):
        for cohort in os.listdir(SURVEY_DIR):
            pdir = os.path.join(SURVEY_DIR, cohort, "profiles")
            if os.path.isdir(pdir):
                for fname in os.listdir(pdir):
                    if fname.endswith(".json"):
                        try:
                            with open(os.path.join(pdir, fname), encoding="utf-8") as f:
                                p = json.load(f)
                            pre = p.get("surveys", {}).get("pre", {}).get("items", {})
                            post = p.get("surveys", {}).get("post", {}).get("items", {})
                            if pre or post:
                                row = {"학생": fname.replace(".json", ""), "코호트": cohort}
                                for k, v in pre.items():
                                    row[f"사전_{k}"] = v
                                for k, v in post.items():
                                    row[f"사후_{k}"] = v
                                survey_data.append(row)
                        except:
                            pass
    if survey_data:
        sdf = pd.DataFrame(survey_data)
        st.dataframe(sdf, use_container_width=True, hide_index=True)
        pre_cols = [c for c in sdf.columns if c.startswith("사전_Q")]
        post_cols = [c for c in sdf.columns if c.startswith("사후_Q")]
        if pre_cols and post_cols:
            st.markdown("##### 사전 vs 사후 평균 비교")
            crows = []
            for pc in pre_cols:
                qn = pc.replace("사전_", "")
                psc = f"사후_{qn}"
                if psc in sdf.columns:
                    crows.append({
                        "문항": qn,
                        "사전평균": round(sdf[pc].mean(), 2),
                        "사후평균": round(sdf[psc].mean(), 2),
                        "변화": round(sdf[psc].mean() - sdf[pc].mean(), 2)
                    })
            if crows:
                st.dataframe(pd.DataFrame(crows), use_container_width=True, hide_index=True)
    else:
        st.info("사전/사후 설문 데이터가 없습니다.")


# ═══════════════════════════════════════════════════════════════
# TAB 5 — 기존 내보내기 (유지 + 논문별 export 추가)
# ═══════════════════════════════════════════════════════════════
with tab5:
    st.subheader("💾 데이터 내보내기")

    # 전체 JSONL 데이터
    if not df_all.empty:
        st.markdown("#### 전체 기존 로그 CSV")
        csv = df_all.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥 전체 데이터 다운로드",
            data=csv.encode("utf-8-sig"),
            file_name=f"snapq_all_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv", use_container_width=True
        )
        st.divider()
        if "user_id" in df_all.columns:
            su = st.selectbox("학생별 다운로드", sorted(df_all["user_id"].unique()), key="exp")
            udf = df_all[df_all["user_id"] == su]
            csv_u = udf.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label=f"📥 {su} 데이터 다운로드",
                data=csv_u.encode("utf-8-sig"),
                file_name=f"snapq_{su}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True
            )

    st.divider()

    # 논문별 export
    st.markdown("#### 논문별 데이터 export")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**논문 1편** — 화면 너비 × 성취도")
        if not df_device.empty and not df_diag.empty:
            paper1 = pd.merge(df_device, df_diag, on="user_id", how="inner")
            st.download_button(
                "📥 논문1편 데이터",
                data=paper1.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
                file_name=f"paper1_screen_width_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True
            )
        else:
            st.info("디바이스 또는 진단 데이터 부족")

    with col2:
        st.markdown("**논문 2편** — Scaffolded Reading")
        if not df_p7.empty and not df_diag.empty:
            paper2 = pd.merge(df_p7, df_diag, on="user_id", how="inner")
            st.download_button(
                "📥 논문2편 데이터",
                data=paper2.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
                file_name=f"paper2_scaffolded_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True
            )
        else:
            st.info("P7 또는 진단 데이터 부족")

    with col3:
        st.markdown("**논문 3편** — Time Pressure 종단")
        if not df_p5.empty and not df_diag.empty and not df_session.empty:
            paper3 = pd.merge(df_p5, df_diag, on="user_id", how="inner")
            paper3 = pd.merge(paper3, df_session[["user_id","cohort_month","is_returning_student"]], on="user_id", how="left")
            st.download_button(
                "📥 논문3편 데이터",
                data=paper3.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
                file_name=f"paper3_time_pressure_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv", use_container_width=True
            )
        else:
            st.info("P5·진단·세션 데이터 부족")

    st.divider()
    st.markdown("#### 현황 요약")

    def _get_date_range(d):
        for col in ["date", "timestamp", "ts", "created_at", "session_start"]:
            if col in d.columns:
                vals = d[col].dropna().astype(str).str[:10]
                vals = vals[vals.str.match(r'\d{4}-\d{2}-\d{2}')]
                if not vals.empty:
                    return vals.min(), vals.max()
        return "미상", "미상"

    _start, _end = _get_date_range(df_all) if not df_all.empty else ("미상","미상")
    _summary = pd.DataFrame([
        {"항목": "총 로그 수 (기존)",       "값": str(len(df_all))},
        {"항목": "학생 수 (전체)",           "값": str(len(all_users))},
        {"항목": "디바이스 수집 수",          "값": str(len(df_device))},
        {"항목": "설문 완료 수",             "값": str(len(df_survey))},
        {"항목": "진단 기록 수",             "값": str(len(df_diag))},
        {"항목": "P5 전장 세션 수",          "값": str(len(df_p5))},
        {"항목": "P7 전장 세션 수",          "값": str(len(df_p7))},
        {"항목": "역전장 재도전 수",          "값": str(len(df_retry))},
        {"항목": "수집 시작일",              "값": _start},
        {"항목": "최근 수집일",              "값": _end},
    ])
    st.dataframe(_summary, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════
# TAB 6 — 📱 디바이스 분석 (논문 1편 핵심) ★NEW★
# ═══════════════════════════════════════════════════════════════
with tab6:
    st.subheader("📱 디바이스 분석 — 논문 1편 핵심 데이터")
    st.caption("screen_width × Day1→Day20 향상도 비교 (세계 최초 가설 실증)")

    if df_device.empty:
        st.warning("아직 디바이스 데이터가 없습니다. 플랫폼에서 수집을 시작하세요.")
    else:
        # 기기 종류 분포
        c1, c2, c3 = st.columns(3)
        with c1:
            if "device_type" in df_device.columns:
                mobile_n = (df_device["device_type"] == "mobile").sum()
                st.markdown(f'<div class="metric-card"><div class="metric-val">{mobile_n}</div><div class="metric-label">모바일</div></div>', unsafe_allow_html=True)
        with c2:
            if "device_type" in df_device.columns:
                desktop_n = (df_device["device_type"] == "desktop").sum()
                st.markdown(f'<div class="metric-card"><div class="metric-val">{desktop_n}</div><div class="metric-label">노트북/PC</div></div>', unsafe_allow_html=True)
        with c3:
            if "screen_width" in df_device.columns:
                avg_sw = round(df_device["screen_width"].mean(), 1)
                st.markdown(f'<div class="metric-card"><div class="metric-val">{avg_sw}px</div><div class="metric-label">평균 화면너비</div></div>', unsafe_allow_html=True)

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 기기 종류 분포")
            if "device_type" in df_device.columns:
                dc = df_device["device_type"].value_counts().reset_index()
                dc.columns = ["기기", "명수"]
                st.bar_chart(dc.set_index("기기"))
        with col2:
            st.markdown("#### OS 분포")
            if "os_type" in df_device.columns:
                oc = df_device["os_type"].value_counts().reset_index()
                oc.columns = ["OS", "명수"]
                st.bar_chart(oc.set_index("OS"))

        st.divider()
        st.markdown("#### 📊 screen_width 구간별 진단 향상도 (논문 1편 핵심 분석)")
        st.caption("화면너비 1cm 증가 시 향상도 변화량 → 회귀분석 원데이터")

        if not df_diag.empty and "screen_width" in df_device.columns:
            # Day1, Day20 정답률 계산
            diag_wide = df_diag.pivot_table(
                index="user_id", columns="diagnosis_day", values="total_score", aggfunc="mean"
            ).reset_index()
            diag_wide.columns = ["user_id"] + [f"day{c}" for c in diag_wide.columns[1:]]

            merged = pd.merge(df_device[["user_id","screen_width","device_type"]],
                              diag_wide, on="user_id", how="inner")

            if "day1" in merged.columns and "day20" in merged.columns:
                merged["향상도"] = merged["day20"] - merged["day1"]
                # 구간 분류
                def sw_group(w):
                    if w < 400:   return "모바일(~400px)"
                    elif w < 800: return "태블릿(400~800px)"
                    else:         return "노트북/PC(800px~)"
                merged["화면구간"] = merged["screen_width"].apply(sw_group)
                grp = merged.groupby("화면구간")["향상도"].mean().round(2).reset_index()
                grp.columns = ["화면구간", "평균 향상도(문제수)"]
                st.dataframe(grp, use_container_width=True, hide_index=True)
                st.bar_chart(grp.set_index("화면구간"))

                st.markdown("#### 전체 원데이터 (회귀분석용)")
                st.dataframe(merged[["user_id","screen_width","device_type","day1","day20","향상도"]],
                             use_container_width=True, hide_index=True)
        else:
            st.info("디바이스 + 진단 데이터가 모두 있어야 분석 가능합니다.")

        st.divider()
        st.markdown("#### 전체 디바이스 원데이터")
        st.dataframe(df_device, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════
# TAB 7 — 📖 Day1·Day10·Day20 진단 (논문 측정) ★NEW★
# ═══════════════════════════════════════════════════════════════
with tab7:
    st.subheader("📖 Day1·Day10·Day20 진단 추적")
    st.caption("논문 3편 공통 종속변수 — 대응표본 t-test 원데이터")

    if df_diag.empty:
        st.warning("진단 데이터가 아직 없습니다.")
    else:
        # 요약 지표
        day_counts = df_diag["diagnosis_day"].value_counts() if "diagnosis_day" in df_diag.columns else {}
        c1, c2, c3, c4 = st.columns(4)
        for col, day, label in zip([c1,c2,c3,c4],
                                   [1,10,20,"all"],
                                   ["Day1 완료","Day10 완료","Day20 완료","전체 기록"]):
            with col:
                n = day_counts.get(day, 0) if day != "all" else len(df_diag)
                st.markdown(f'<div class="metric-card"><div class="metric-val">{n}</div><div class="metric-label">{label}</div></div>',
                            unsafe_allow_html=True)

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
                    ud_chart = udiag.set_index("diagnosis_day")["total_score"]
                    st.line_chart(ud_chart)
            else:
                st.info(f"{sel_u}의 진단 기록이 없습니다.")

        st.divider()
        st.markdown("#### 전체 진단 원데이터")
        st.dataframe(df_diag, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════
# TAB 8 — 🔬 논문 데이터 요약 ★NEW★
# ═══════════════════════════════════════════════════════════════
with tab8:
    st.subheader("🔬 논문 3편 데이터 수집 현황")

    # 논문 1편
    st.markdown('<div class="paper-card"><div class="paper-title">📄 논문 1편 — 모바일 화면 너비 × 인지 집중력 × 토익 성취도</div><div class="paper-sub">세계 최초 가설 실증 · KCI 등재지 목표 · 핵심 데이터: A(디바이스) + C(진단)</div></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        n_dev = len(df_device)
        color = "metric-val" if n_dev >= 30 else "metric-val" if n_dev > 0 else "metric-val"
        st.markdown(f'<div class="metric-card"><div class="{color}">{n_dev}</div><div class="metric-label">디바이스 수집 (목표: 100+)</div></div>', unsafe_allow_html=True)
    with c2:
        n_diag1 = (df_diag["diagnosis_day"] == 1).sum() if (not df_diag.empty and "diagnosis_day" in df_diag.columns) else 0
        st.markdown(f'<div class="metric-card"><div class="metric-val">{n_diag1}</div><div class="metric-label">Day1 진단 완료</div></div>', unsafe_allow_html=True)
    with c3:
        n_diag20 = (df_diag["diagnosis_day"] == 20).sum() if (not df_diag.empty and "diagnosis_day" in df_diag.columns) else 0
        st.markdown(f'<div class="metric-card"><div class="metric-val">{n_diag20}</div><div class="metric-label">Day20 진단 완료 (유효 표본)</div></div>', unsafe_allow_html=True)

    st.divider()

    # 논문 2편
    st.markdown('<div class="paper-card"><div class="paper-title">📄 논문 2편 — Scaffolded Reading × ZPD × 토익 독해 성취도</div><div class="paper-sub">AI 플랫폼 기반 ZPD 실증 · KCI 등재지 목표 · 핵심 데이터: E(P7) + C(진단)</div></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        n_p7 = len(df_p7)
        st.markdown(f'<div class="metric-card"><div class="metric-val">{n_p7}</div><div class="metric-label">P7 세션 수</div></div>', unsafe_allow_html=True)
    with c2:
        step3 = (df_p7["step_reached"] == "8문장").sum() if (not df_p7.empty and "step_reached" in df_p7.columns) else 0
        st.markdown(f'<div class="metric-card"><div class="metric-val">{step3}</div><div class="metric-label">8문장(최종단계) 도달</div></div>', unsafe_allow_html=True)
    with c3:
        clear = (df_p7["final_result"] == "CLEAR").sum() if (not df_p7.empty and "final_result" in df_p7.columns) else 0
        st.markdown(f'<div class="metric-card"><div class="metric-val">{clear}</div><div class="metric-label">CLEAR 달성</div></div>', unsafe_allow_html=True)

    if not df_p7.empty and "step_reached" in df_p7.columns:
        st.markdown("##### P7 단계별 도달 현황")
        step_df = df_p7["step_reached"].value_counts().reset_index()
        step_df.columns = ["단계", "횟수"]
        st.bar_chart(step_df.set_index("단계"))

    st.divider()

    # 논문 3편
    st.markdown('<div class="paper-card"><div class="paper-title">📄 논문 3편 — Time Pressure × 자동화 × 토익 종단 연구 (학위논문)</div><div class="paper-sub">SSCI 목표 · 핵심 데이터: D(P5) + C(진단) + G(세션)</div></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        n_p5 = len(df_p5)
        st.markdown(f'<div class="metric-card"><div class="metric-val">{n_p5}</div><div class="metric-label">P5 세션 수</div></div>', unsafe_allow_html=True)
    with c2:
        ret_n = (df_session["is_returning_student"] == True).sum() if (not df_session.empty and "is_returning_student" in df_session.columns) else 0
        st.markdown(f'<div class="metric-card"><div class="metric-val">{ret_n}</div><div class="metric-label">재수강생 (종단 코호트)</div></div>', unsafe_allow_html=True)
    with c3:
        cohorts = df_session["cohort_month"].nunique() if (not df_session.empty and "cohort_month" in df_session.columns) else 0
        st.markdown(f'<div class="metric-card"><div class="metric-val">{cohorts}</div><div class="metric-label">코호트 수 (월별)</div></div>', unsafe_allow_html=True)

    if not df_p5.empty and "timer_selected" in df_p5.columns:
        st.markdown("##### 타이머 선택 패턴 (Time Pressure 자율성)")
        tc = df_p5["timer_selected"].value_counts().reset_index()
        tc.columns = ["타이머(초)", "선택횟수"]
        st.bar_chart(tc.set_index("타이머(초)"))

    st.divider()

    # storage 원본 보기
    st.markdown("#### storage_data.json 전체 키 현황")
    key_summary = {k: len(v) if isinstance(v, list) else "object" for k, v in storage.items()}
    st.json(key_summary)


# ═══════════════════════════════════════════════════════════════
# TAB 9 — ⚠️ 미완료 알림 ★NEW★
# ═══════════════════════════════════════════════════════════════
with tab9:
    st.subheader("⚠️ 미완료 학생 알림")
    st.caption("논문 데이터 완성을 위해 follow-up이 필요한 학생 목록")

    if not all_users:
        st.info("학생 데이터가 없습니다.")
    else:
        # Day별 완료 여부 체크
        diag_done_map = {}
        if not df_diag.empty and "user_id" in df_diag.columns and "diagnosis_day" in df_diag.columns:
            for uid in all_users:
                udiag = df_diag[df_diag["user_id"] == uid]
                diag_done_map[uid] = set(udiag["diagnosis_day"].tolist())

        # 설문 완료 여부
        survey_done = set()
        if not df_survey.empty and "user_id" in df_survey.columns:
            survey_done = set(df_survey["user_id"].unique())

        # 디바이스 수집 여부
        device_done = set()
        if not df_device.empty and "user_id" in df_device.columns:
            device_done = set(df_device["user_id"].unique())

        rows = []
        for uid in all_users:
            days = diag_done_map.get(uid, set())
            rows.append({
                "학생": uid,
                "디바이스 수집": "✅" if uid in device_done else "❌",
                "설문 완료": "✅" if uid in survey_done else "❌",
                "Day1": "✅" if 1 in days else "❌",
                "Day10": "✅" if 10 in days else "❌",
                "Day20": "✅" if 20 in days else "❌",
                "완료 여부": "✅ 완료" if (uid in device_done and uid in survey_done and {1,10,20}.issubset(days)) else "⚠️ 미완료"
            })

        alert_df = pd.DataFrame(rows)
        incomplete = alert_df[alert_df["완료 여부"] == "⚠️ 미완료"]
        complete = alert_df[alert_df["완료 여부"] == "✅ 완료"]

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#cc0000">{len(incomplete)}</div><div class="metric-label">미완료 학생</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="metric-val" style="color:#009944">{len(complete)}</div><div class="metric-label">완전 완료 학생</div></div>', unsafe_allow_html=True)

        st.divider()
        if not incomplete.empty:
            st.markdown("#### ❌ 미완료 학생 목록 (follow-up 필요)")
            st.dataframe(incomplete, use_container_width=True, hide_index=True)

        if not complete.empty:
            st.markdown("#### ✅ 완료 학생 목록")
            st.dataframe(complete, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("#### 전체 완료 현황")
        st.dataframe(alert_df, use_container_width=True, hide_index=True)

        # CSV 다운로드
        st.download_button(
            "📥 완료 현황 CSV 다운로드",
            data=alert_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
            file_name=f"snapq_completion_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv", use_container_width=True
        )
