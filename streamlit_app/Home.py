import streamlit as st
import sys
import os

# fixing root issues
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.services.user_service import login_user, register_user
from app.data.db import connect_database

#import username & password validators from auth.py
from auth import validate_username, validate_password


# page info
st.set_page_config(
    page_title="Intelligence Platform",
    layout="wide"
)

st.title("🌐Intelligence Platform - Home")

# checking if user logged in or not
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# checking for user role 
def get_user_role(username):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "user"

# checking if user is already logged in to show then dashboard depending on role
if st.session_state.logged_in:
    st.success(f"Logged in as {st.session_state.username} ({st.session_state.role})")
    st.info("Open a dashboard from the Pages menu (top-left).")

    st.divider()
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

    st.stop()

# register and login tab
tab_login, tab_register = st.tabs(["Login", "Register"])

# login tab
with tab_login:
    st.subheader("Login to your account")

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Log in", key="login_button"):
        ok, result = login_user(username, password)

        if ok:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = get_user_role(username)
            st.success(result)
            st.rerun()
        else:
            st.error(result)

# register tab and confirming password 
with tab_register:
    st.subheader("Create a new account")

    reg_user = st.text_input("New Username", key="reg_user")
    reg_pass = st.text_input("Password", type="password", key="reg_pass")
    reg_pass2 = st.text_input("Confirm Password", type="password", key="reg_pass2")
    role = st.selectbox("Role", ["cyber", "data", "IT", "admin"], key="reg_role")

    if st.button("Register", key="register_button"):
        
        # empty field check
        if not reg_user or not reg_pass:
            st.warning("Please fill in all fields.")
            st.stop()

        # username validation using auth.py rules
        valid_user, msg_user = validate_username(reg_user)
        if not valid_user:
            st.error(f"Username error: {msg_user}")
            st.stop()

        # password validation using auth.py rules
        valid_pass, msg_pass = validate_password(reg_pass)
        if not valid_pass:
            st.error(f"Password error: {msg_pass}")
            st.stop()

        # confirm password
        if reg_pass != reg_pass2:
            st.error("Passwords do not match.")
            st.stop()

        # now try registering
        try:
            success, message = register_user(reg_user, reg_pass, role)
            if success:
                st.success("Account created! Switch to Login tab.")
            else:
                st.error(message)
        except Exception as e:
            st.error(f"Error: {e}")

# footer part of page
st.divider()
st.info("After logging in, access your dashboards from the Pages menu.")