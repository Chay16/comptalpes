import requests
import streamlit as st

import webapp.webapp_utils as utils

if "BASE_URL" not in st.session_state:
    st.error(
        "Accesing Trips page without coming from home page. \
        Must be accessed through homepage !"
    )

else:
    BASE_URL = st.session_state["BASE_URL"]
    trips = utils.get_trips(BASE_URL)

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
                f"{BASE_URL}/trip/",
                json={
                    "name": trip_name,
                    "start_date": trip_start.isoformat(),
                    "end_date": trip_end.isoformat(),
                    "currency": trip_currency,
                },
                timeout=2,
            )
            if response.status_code == 200:
                d = dict(response.json())
                st.success("Trip added successfully!")
                st.session_state["trip_id"] = d.get("id")
                st.rerun()
            else:
                st.error(f"Error: {response.json().get('detail')}")
