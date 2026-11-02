import requests
import streamlit as st
from webapp_utils import get_trips

BASE_URL = "http://127.0.0.1:8000"
st.session_state["BASE_URL"] = BASE_URL

st.set_page_config(
    page_title="Comptalpes",
    page_icon="⛷️",
)
st.title("⛷️", text_alignment="center")
st.title("Comptalpes", text_alignment="center")

trips = get_trips(BASE_URL)

if not trips:
    st.info("No trips found.")
else:
    trips_data = {
        "Name": [trip.name for trip in trips],
        "Start": [trip.start_date.isoformat() for trip in trips],
        "End": [trip.end_date.isoformat() for trip in trips],
        "Members": [len(trip.members) for trip in trips],
        "Expenses": [len(trip.expenses) for trip in trips],
    }
    st.table(trips_data, border="horizontal")

    trip_name_selected = st.selectbox(
        "Trip",
        [trip.name for trip in trips],
        key="trip_selector",
    )
    trip_selected = next(trip for trip in trips if trip.name == trip_name_selected)
    st.session_state["TRIP_ID"] = trip_selected.id

with st.expander("Add Trip"):
    trip_name = st.text_input("Name", key="add_trip_name")
    trip_start = st.date_input("Start date", key="add_trip_start")
    trip_end = st.date_input("End date", key="add_trip_end")
    trip_currency = st.selectbox(
        "Currency",
        ["EUR", "CHF", "GBP", "USD"],
        key="add_trip_currency",
    )
    if st.button("Add Trip") and trip_name:
        response = requests.post(
            f"{BASE_URL}/trips/",
            json={
                "name": trip_name,
                "start_date": trip_start.isoformat(),
                "end_date": trip_end.isoformat(),
                "currency": trip_currency,
            },
            timeout=5,
        )
        if response.status_code == 200:
            st.success("Trip added successfully!")
            st.session_state["trip_selector"] = trip_name
            st.rerun()
        else:
            st.error(f"Error: {response.json().get('detail')}")

st.sidebar.success("Sections")
