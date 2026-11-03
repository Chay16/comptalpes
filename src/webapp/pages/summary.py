import streamlit as st

if "BASE_URL" not in st.session_state:
    st.error(
        "Accesing Summary page without coming from home page. \
        Must be accessed through homepage !"
    )
else:
    st.markdown(
        "<h1 style='text-align: center;'>⛷️<br>Comptalpes</h1>",
        unsafe_allow_html=True,
    )
