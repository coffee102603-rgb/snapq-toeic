import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.title("Sheets 연결 테스트")

if st.button("Sheets에 쓰기 테스트"):
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]), scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(st.secrets["SPREADSHEET_ID"])
        try:
            ws = sh.worksheet("test")
        except:
            ws = sh.add_worksheet(title="test", rows=100, cols=5)
        ws.append_row(["성공!", "테스트", "2026-04-08"])
        st.success("Sheets 저장 성공!")
    except Exception as e:
        st.error(f"에러: {e}")
