import streamlit as st
import os
import sys

# fix root path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from services.database_manager import DatabaseManager
from services.auth_manager import AuthManager

# page config
st.set_page_config(page_title="Intelligence Platform", layout="wide")
st.title("🌐 Intelligence Platform")

#checking if user is logged in before showing dashboards
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# managers (for Week 11)
db = DatabaseManager("database/platform.db")
auth = AuthManager(db)

# already logged in
if st.session_state.logged_in:
    user = st.session_state.current_user
    st.success(f"Logged in as {user.get_username()} ({user.get_role()})")
    st.info("Open a dashboard from the Pages menu.")

    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    st.stop()

tab_login, tab_register = st.tabs(["Login", "Register"])

# login
with tab_login:
    st.subheader("Login")

    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Log in"):
        user = auth.login_user(username, password)

        if user is None:
            st.error("Invalid username or password")
        else:
            st.session_state.logged_in = True
            st.session_state.current_user = user
            st.success("Login successful")
            st.rerun()

# register
with tab_register:
    st.subheader("Register")

    new_user = st.text_input("New Username", key="reg_user")
    new_pass = st.text_input("Password", type="password", key="reg_pass")
    role = st.selectbox("Role", ["cyber", "data", "IT", "admin"], key="reg_role")

    if st.button("Register"):
        if not new_user or not new_pass:
            st.error("All fields required")
        else:
            try:
                auth.register_user(new_user, new_pass, role)
                st.success("Account created. Please login.")
            except Exception as e:
                st.error(f"Registration failed: {e}")