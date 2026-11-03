import requests
import streamlit as st

import webapp.webapp_utils as utils

if "BASE_URL" not in st.session_state:
    st.error(
        "Accesing Users page without coming from home page. \
        Must be accessed through homepage !"
    )

else:
    BASE_URL = st.session_state["BASE_URL"]
    try:
        users = utils.get_users(BASE_URL)
    except requests.RequestException:
        users = None
        st.error("API not reachable.")

    if users == []:
        st.info("No users found.")
    elif users:
        users_data = {
            "Name": [user.name for user in users],
        }
        st.table(users_data, border="horizontal")

        with st.expander("Update User"):
            user_selected = st.selectbox(
                "User to Update",
                [user.name for user in users],
                key="update_user_selector",
            )
            user_name = st.text_input("New name", key="update_user_name")
            if st.button("Update User") and user_name:
                user_id = next(user.id for user in users if user.name == user_selected)
                response = requests.patch(
                    f"{BASE_URL}/user/{user_id}",
                    json={"name": user_name},
                    timeout=2,
                )
                if response.status_code == 200:
                    st.success("User updated successfully!")
                    st.rerun()
                else:
                    st.error(f"Error: {response.json().get('detail')}")

    with st.expander("Add User"):
        user_name = st.text_input("Name", key="add_user_name")
        if st.button("Add User") and user_name:
            response = requests.post(
                f"{BASE_URL}/user/",
                json={"name": user_name},
                timeout=2,
            )
            if response.status_code == 200:
                st.success("User added successfully!")
                st.rerun()
            else:
                st.error(f"Error: {response.json().get('detail')}")

    with st.expander("Delete User"):
        user_to_delete = st.selectbox(
            "User to Delete",
            [user.name for user in users],
            key="delete_user_selector",
        )
        delete_confirmed = st.checkbox(
            f"Confirm deletion of {user_to_delete}",
            key="delete_user_confirm",
        )
        if st.button("Delete User") and delete_confirmed:
            user_id = next(user.id for user in users if user.name == user_to_delete)
            response = requests.delete(
                f"{BASE_URL}/user/{user_id}",
                timeout=2,
            )
            if response.status_code == 200:
                st.success(f"User {user_to_delete} deleted successfully!")
                st.rerun()
            else:
                st.error(f"Error: {response.json().get('detail')}")
