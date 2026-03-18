import streamlit as st
import importlib

st.set_page_config(page_title="SnapQ MASTER", layout="wide")

# main_hub 로드
hub = importlib.import_module("main_hub")

# 가드 무시하고 메인 허브 함수 실행
if hasattr(hub, "render_main_hub"):
    hub.render_main_hub()
elif hasattr(hub, "main"):
    hub.main()
else:
    st.error("❌ Main Hub 진입 함수(render_main_hub / main)를 찾을 수 없습니다.")
