import json
from pathlib import Path

import streamlit as st

BASE_URL = "http://127.0.0.1:8000"
st.session_state["BASE_URL"] = BASE_URL
DB = Path(__file__).parent.parent.parent / "db/local-db.json"
if not DB.is_file():
    DB.parent.mkdir(exist_ok=True)
    with open(DB, "w") as f:
        json.dump({}, f)
st.session_state["DB"] = DB

st.set_page_config(
    page_title="Comptalpes",
    page_icon="⛷️",
)
st.title("⛷️", text_alignment="center")
st.title("Comptalpes", text_alignment="center")
st.sidebar.success("Sections")
