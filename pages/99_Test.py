import streamlit as st
import gspread

st.title("Sheets 연결 테스트 v2")

if st.button("gspread 6.x 방식으로 테스트"):
    try:
        gc = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        sh = gc.open_by_key(st.secrets["SPREADSHEET_ID"])
        try:
            ws = sh.worksheet("test")
        except:
            ws = sh.add_worksheet(title="test", rows=100, cols=5)
            ws.append_row(["timestamp", "message"])
        ws.append_row(["2026-04-08", "gspread 6.x 연결 성공!"])
        st.success("Sheets 저장 성공!")
    except Exception as e:
        st.error(f"에러: {e}")
