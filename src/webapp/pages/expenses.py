import requests
import streamlit as st

BASE_URL = st.session_state.get("BASE_URL")
DB = st.session_state.get("DB")
st.set_page_config("Expenses 💰")

st.header("List of Expenses")
response = requests.get(f"{BASE_URL}/expenses")
if response.status_code == 200:
    expenses = response.json()
    expenses_data = {
        "Description": [expense["description"] for expense in expenses],
        "Amount": [expense["amount"] for expense in expenses],
        "Date": [expense["expense_date"] for expense in expenses],
        "Category": [
            f":material/label: {expense['category']['name']}" for expense in expenses
        ],
    }
    st.table(expenses_data, border="horizontal")

else:
    expenses = []
    st.write("No Expenses found.")

with st.expander("Add Expense"):
    expense_description = st.text_input("Description", key="add_expense_description")
    expense_amount = st.text_input("Amount", key="add_expense_amount")
    expense_category = st.text_input("Category", key="add_expense_category")
    if st.button("Add Expense"):
        response = requests.post(
            f"{BASE_URL}/expenses",
            json={
                "description": expense_description,
                "amount": expense_amount,
                "category": expense_category,
            },
        )
        if response.status_code == 200:
            st.success("Expense added successfully!")
        else:
            st.error(f"Error: {response.json().get('detail')}")

with st.expander("Update Expense"):
    expense_description = st.selectbox(
        "Expense to Update",
        [e["description"] for e in expenses],
    )
    expense_amount = st.text_input("Amount", key="update_expense_amount")
    if st.button("Update Expense"):
        response = requests.patch(
            f"{BASE_URL}/expenses",
            json={"description": expense_description, "amount": expense_amount},
        )
        if response.status_code == 200:
            st.success("Expense Updated successfully!")
        else:
            st.error(f"Error: {response.json().get('detail')}")
