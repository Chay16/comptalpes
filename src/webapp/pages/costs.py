import requests
import streamlit as st

BASE_URL = st.session_state.get("BASE_URL")
DB = st.session_state.get("DB")
st.set_page_config("Costs 💰")

st.header("List of Costs")
response = requests.get(f"{BASE_URL}/costs")
if response.status_code == 200:
    costs = response.json()
    costs_data = {
        "Category": [f":material/label: {cost['category']}" for cost in costs],
        "Amount": [cost["amount"] for cost in costs],
    }
    st.table(costs_data, border="horizontal")
    
else:
    st.write("No Costs found.")

with st.expander("Add Cost"):
    cost_category = st.text_input("Category", key="add_cost_category")
    cost_amount = st.text_input("Amount", key="add_cost_amount")
    if st.button("Add Cost"):
        response = requests.post(
            f"{BASE_URL}/costs/{cost_category}",
            params={"amount": cost_amount},
        )
        if response.status_code == 200:
            st.success("Cost added successfully!")
        else:
            st.error(f"Error: {response.json().get('detail')}")

with st.expander("Update Cost"):
    cost_category = st.selectbox(
        "Cost to Update",
        [c["category"] for c in costs],
    )
    cost_amount = st.text_input("Amount", key="update_cost_amount")
    if st.button("Update Cost"):
        response = requests.patch(
            f"{BASE_URL}/costs/{cost_category}",
            params={"amount": cost_amount},
        )
        if response.status_code == 200:
            st.success("Cost Updated successfully!")
        else:
            st.error(f"Error: {response.json().get('detail')}")
