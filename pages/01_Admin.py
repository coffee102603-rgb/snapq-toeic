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
</style>""", unsafe_allow_html=True)

col_title, col_back = st.columns([5, 1])
with col_title:
    st.title("📊 SnapQ 관리자 대시보드")
    st.caption("논문 연구용 데이터 분석 시스템 — 학생에게 비공개")
with col_back:
    st.markdown("<div style='padding-top:1.2rem;'>", unsafe_allow_html=True)
    if st.button("🏠 메인으로", use_container_width=True):
        st.switch_page("main_hub.py")
    st.markdown("</div>", unsafe_allow_html=True)
DATA_DIR = "data/research_logs"

def load_all_logs():
    logs = []
    if not os.path.exists(DATA_DIR): return pd.DataFrame()
    for fname in os.listdir(DATA_DIR):
        if fname.endswith(".jsonl"):
            with open(os.path.join(DATA_DIR, fname), "r", encoding="utf-8") as f:
                for line in f:
                    try: logs.append(json.loads(line.strip()))
                    except: pass
    return pd.DataFrame(logs) if logs else pd.DataFrame()

df_all = load_all_logs()
if df_all.empty:
    st.warning("아직 수집된 데이터가 없습니다.")
    st.stop()

df = df_all[~df_all.get("type", pd.Series([""]*len(df_all))).isin(["session","session_v2"])].copy() if "type" in df_all.columns else df_all.copy()
tab1, tab2, tab3, tab4, tab5 = st.tabs(["👥 학생 현황","📈 학습 분석","🎮 게이미피케이션","📋 설문 데이터","💾 내보내기"])

with tab1:
    st.subheader("👥 전체 학생 현황")
    if "user_id" in df.columns:
        users = df["user_id"].unique()
        total_users = len(users); total_q = len(df)
        correct_sum = df["correct"].sum() if "correct" in df.columns else 0
        acc = round(correct_sum/total_q*100,1) if total_q>0 else 0
        avg_q = round(total_q/total_users,1) if total_users>0 else 0
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card"><div class="metric-val">{total_users}</div><div class="metric-label">전체 학생 수</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><div class="metric-val">{total_q}</div><div class="metric-label">총 풀이 문제 수</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><div class="metric-val">{acc}%</div><div class="metric-label">전체 평균 정답률</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card"><div class="metric-val">{avg_q}</div><div class="metric-label">학생당 평균 풀이수</div></div>', unsafe_allow_html=True)
        st.divider()
        rows = []
        for uid in sorted(users):
            udf = df[df["user_id"]==uid]; total = len(udf)
            correct = udf["correct"].sum() if "correct" in udf.columns else 0
            acc_u = round(correct/total*100,1) if total>0 else 0
            avg_t = round(udf["time_taken"].mean(),1) if "time_taken" in udf.columns else "-"
            modules = [m for m in (list(udf["module"].unique()) if "module" in udf.columns else []) if str(m) != "nan"]
            last = udf["timestamp"].max()[:10] if "timestamp" in udf.columns else "-"
            rows.append({"학생":uid,"총문제":total,"정답수":int(correct),"정답률(%)":acc_u,"평균응답(초)":avg_t,"사용모듈":", ".join(modules),"최근접속":last})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("📈 학습 분석")
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("#### 모듈별 사용 빈도")
        if "module" in df.columns:
            mc = df["module"].value_counts().reset_index(); mc.columns=["모듈","문제수"]; st.bar_chart(mc.set_index("모듈"))
    with col2:
        st.markdown("#### 카테고리별 정답률")
        if "category" in df.columns and "correct" in df.columns:
            cat_df = df.groupby("category").agg(총문제=("correct","count"),정답수=("correct","sum")).reset_index()
            cat_df["정답률(%)"] = (cat_df["정답수"]/cat_df["총문제"]*100).round(1)
            st.dataframe(cat_df.sort_values("정답률(%)"), use_container_width=True, hide_index=True)
    st.divider()
    st.markdown("#### 주차별 정답률 변화")
    if "week" in df.columns and "correct" in df.columns:
        wdf = df.groupby("week").agg(총문제=("correct","count"),정답수=("correct","sum")).reset_index()
        wdf["정답률(%)"] = (wdf["정답수"]/wdf["총문제"]*100).round(1)
        st.line_chart(wdf.set_index("week")["정답률(%)"])
    st.markdown("#### 시간대별 접속 패턴")
    if "hour" in df.columns:
        hc = df["hour"].value_counts().sort_index().reset_index(); hc.columns=["시간대","문제수"]; st.bar_chart(hc.set_index("시간대"))

with tab3:
    st.subheader("🎮 게이미피케이션 지표")
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("#### 타이머 선택 패턴 (P5)")
        if "timer_selected" in df.columns:
            tdf = df[df["timer_selected"].notna()]
            if not tdf.empty:
                tc = tdf["timer_selected"].value_counts().reset_index(); tc.columns=["타이머(초)","선택횟수"]; st.bar_chart(tc.set_index("타이머(초)"))
    with col2:
        st.markdown("#### 재도전 vs 첫도전")
        if "is_retry" in df.columns:
            rc = df["is_retry"].value_counts()
            rdf = pd.DataFrame({"구분":["재도전" if k else "첫도전" for k in rc.index],"횟수":rc.values})
            st.dataframe(rdf, use_container_width=True, hide_index=True)
    st.divider()
    st.markdown("#### 요일별 학습 패턴")
    if "day_of_week" in df.columns:
        dow = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dc = df["day_of_week"].value_counts().reindex(dow, fill_value=0).reset_index(); dc.columns=["요일","문제수"]; st.bar_chart(dc.set_index("요일"))
    st.markdown("#### 학생별 평균 응답시간 변화 (순발력)")
    if "user_id" in df.columns and "time_taken" in df.columns and "week" in df.columns:
        sel = st.selectbox("학생 선택", sorted(df["user_id"].unique()), key="spd")
        udf = df[df["user_id"]==sel]
        spd = udf.groupby("week")["time_taken"].mean().round(2).reset_index(); spd.columns=["주차","평균응답(초)"]; st.line_chart(spd.set_index("주차"))


with tab4:
    st.subheader("📋 사전/사후 설문 데이터")
    SURVEY_DIR = "data/cohorts"
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
                            pre = p.get("surveys",{}).get("pre",{}).get("items",{})
                            post = p.get("surveys",{}).get("post",{}).get("items",{})
                            if pre or post:
                                row = {"학생":fname.replace(".json",""),"코호트":cohort}
                                for k,v in pre.items(): row[f"사전_{k}"] = v
                                for k,v in post.items(): row[f"사후_{k}"] = v
                                survey_data.append(row)
                        except: pass
    if survey_data:
        sdf = pd.DataFrame(survey_data)
        st.dataframe(sdf, use_container_width=True, hide_index=True)
        pre_cols = [c for c in sdf.columns if c.startswith("사전_Q")]
        post_cols = [c for c in sdf.columns if c.startswith("사후_Q")]
        if pre_cols and post_cols:
            st.markdown("#### 사전 vs 사후 평균 비교")
            crows = []
            for pc in pre_cols:
                qn = pc.replace("사전_",""); psc = f"사후_{qn}"
                if psc in sdf.columns:
                    crows.append({"문항":qn,"사전평균":round(sdf[pc].mean(),2),"사후평균":round(sdf[psc].mean(),2),"변화":round(sdf[psc].mean()-sdf[pc].mean(),2)})
            if crows: st.dataframe(pd.DataFrame(crows), use_container_width=True, hide_index=True)
    else:
        st.info("아직 수집된 설문 데이터가 없습니다.")

with tab5:
    st.subheader("💾 데이터 내보내기")
    st.markdown("#### 전체 데이터 CSV")
    csv = df_all.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="📥 전체 데이터 다운로드",
        data=csv.encode("utf-8-sig"),
        file_name=f"snapq_all_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv", use_container_width=True
    )
    st.divider()
    st.markdown("#### 학생별 개별 CSV")
    if "user_id" in df_all.columns:
        su = st.selectbox("학생 선택", sorted(df_all["user_id"].unique()), key="exp")
        udf = df_all[df_all["user_id"]==su]
        csv_u = udf.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label=f"📥 {su} 데이터 다운로드",
            data=csv_u.encode("utf-8-sig"),
            file_name=f"snapq_{su}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv", use_container_width=True
        )
    st.divider()
    st.markdown("#### 현황 요약")
    def _get_date_range(d):
        for col in ["date", "timestamp", "ts", "created_at"]:
            if col in d.columns:
                vals = d[col].dropna().astype(str).str[:10]
                vals = vals[vals.str.match(r'\d{4}-\d{2}-\d{2}')]
                if not vals.empty:
                    return vals.min(), vals.max()
        return "미상", "미상"
    _start, _end = _get_date_range(df_all)
    _modules = [m for m in (list(df_all["module"].unique()) if "module" in df_all.columns else []) if str(m) != "nan"]
    _summary = pd.DataFrame([
        {"항목": "총 로그 수", "값": str(len(df_all))},
        {"항목": "학생 수", "값": str(int(df_all["user_id"].nunique()) if "user_id" in df_all.columns else 0)},
        {"항목": "수집 시작일", "값": _start},
        {"항목": "최근 수집일", "값": _end},
        {"항목": "사용 모듈", "값": ", ".join(_modules) if _modules else "없음"},
    ])
    st.dataframe(_summary, use_container_width=True, hide_index=True)
