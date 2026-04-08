import streamlit as st
import gspread

st.title("Sheets 연결 테스트 v3")

if st.button("gspread 테스트"):
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        st.write("secrets 읽기 성공!")
        gc = gspread.service_account_from_dict(creds_dict)
        st.write("gspread 연결 성공!")
        sh = gc.open_by_key(st.secrets["SPREADSHEET_ID"])
        st.write("Sheets 열기 성공!")
        try:
            ws = sh.worksheet("test")
        except:
            ws = sh.add_worksheet(title="test", rows=100, cols=5)
            ws.append_row(["timestamp", "message"])
        ws.append_row(["2026-04-08", "성공!"])
        st.success("완전 성공!")
    except Exception as e:
        st.error(f"에러: {type(e).__name__}: {e}")

st.write("secrets keys:", list(st.secrets.keys()) if hasattr(st, "secrets") else "없음")
