import streamlit as st

st.session_state["BASE_URL"] = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Comptalpes",
    page_icon="⛷️",
)

pages = {
    "Comptalpes": [st.Page("pages/summary.py", title="Summary")],
    "Admin": [
        st.Page("pages/trips.py", title="Trips"),
        st.Page("pages/users.py", title="Users"),
    ],
}
pg = st.navigation(pages)
pg.run()
