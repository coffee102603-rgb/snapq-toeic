import streamlit as st

st.set_page_config(page_title="ARCHIVE - SNAPQ_TOEIC", layout="wide")

st.error("🧊 이 폴더는 ARCHIVE 입니다. 실행하면 안 됩니다.")
st.markdown("### ✅ MASTER 실행 폴더")
st.code(r"C:\Users\최정은\Desktop\snapq_toeic")

st.markdown("### 실행 명령(복사해서 실행)")
st.code(r'cd "C:\Users\최정은\Desktop\snapq_toeic"\npython -m streamlit run main_hub.py --server.port 8502')

st.info("이 창은 실수 방지용입니다. (B 폴더에서 실행되지 않도록 막았습니다.)")
