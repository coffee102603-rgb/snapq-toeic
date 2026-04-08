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
    st.caption("논문 연구용 데이터 분석 시스템")
with col_back:
    st.markdown("<div style='padding-top:1.2rem;'>", unsafe_allow_html=True)
    if st.button("🏠 메인으로", use_container_width=True):
        st.switch_page("main_hub.py")
    st.markdown("</div>", unsafe_allow_html=True)

STATS_DIR = "data/stats"

def load_all_logs():
    logs = []
    if not os.path.exists(STATS_DIR):
        return pd.DataFrame()
    for fname in os.listdir(STATS_DIR):
        if fname.endswith(".jsonl"):
            src = fname.replace(".jsonl","")
            with open(os.path.join(STATS_DIR, fname), "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        row = json.loads(line.strip())
                        if "ts" in row and "timestamp" not in row:
                            row["timestamp"] = row["ts"]
                        if "mode" in row and "module" not in row:
                            row["module"] = row.get("arena","P5") + "_" + row.get("mode","")
                        if "accuracy" in row and "correct" not in row:
                            row["correct"] = 1 if row.get("accuracy",0) >= 60 else 0
                        if "category" in row:
                            row["cat"] = row["category"]
                        row["source_file"] = src
                        logs.append(row)
                    except:
                        pass
    if not logs:
        return pd.DataFrame()
    df = pd.DataFrame(logs)
    if "timestamp" in df.columns:
        try:
            df["hour"] = pd.to_datetime(df["timestamp"], errors="coerce").dt.hour
            df["day_of_week"] = pd.to_datetime(df["timestamp"], errors="coerce").dt.day_name()
            df["date"] = df["timestamp"].astype(str).str[:10]
        except:
            pass
    return df

df_all = load_all_logs()
if df_all.empty:
    st.warning("아직 수집된 데이터가 없습니다.")
    st.info(f"경로: {os.path.abspath(STATS_DIR)}")
    st.stop()

df = df_all.copy()
tab1, tab2, tab3, tab4, tab5 = st.tabs(["👥 학생 현황","📈 학습 분석","🎮 게이미피케이션","📋 설문 데이터","💾 내보내기"])

with tab1:
    st.subheader("👥 전체 학생 현황")
    st.dataframe(df_all.head(50), use_container_width=True)
    st.metric("총 로그 수", len(df_all))
    st.metric("데이터 파일", ", ".join(df_all["source_file"].unique().tolist()) if "source_file" in df_all.columns else "-")

with tab2:
    st.subheader("📈 학습 분석")
    if "module" in df.columns:
        st.bar_chart(df["module"].value_counts())
    if "category" in df.columns and "correct" in df.columns:
        cat_df = df.groupby("category").agg(총문제=("correct","count"),정답수=("correct","sum")).reset_index()
        cat_df["정답률(%)"] = (cat_df["정답수"]/cat_df["총문제"]*100).round(1)
        st.dataframe(cat_df.sort_values("정답률(%)"), use_container_width=True, hide_index=True)

with tab3:
    st.subheader("🎮 게이미피케이션")
    if "status" in df.columns:
        st.bar_chart(df["status"].value_counts())
    if "time_limit" in df.columns:
        st.bar_chart(df["time_limit"].value_counts())

with tab4:
    st.subheader("📋 설문 데이터")
    st.info("설문 데이터 준비 중")

with tab5:
    st.subheader("💾 내보내기")
    csv = df_all.to_csv(index=False, encoding="utf-8-sig")
    st.download_button("📥 전체 데이터 CSV", data=csv.encode("utf-8-sig"),
        file_name=f"snapq_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)
