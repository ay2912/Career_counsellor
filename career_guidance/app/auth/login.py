import streamlit as st
from datetime import datetime
from app.auth.auth_utils import register_user, verify_user

def login_page():
    """Modified to redirect to profile after login"""
    st.title("Career Guidance App - Login")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                success, user_id = verify_user(username, password)
                if success:
                    st.session_state.update({
                        "authenticated": True,
                        "username": username,
                        "user_id": user_id,
                        "session_id": str(hash(f"{username}{datetime.now()}")),
                        "current_page": "profile"  # Redirect to profile
                    })
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    with tab2:
        with st.form("register_form", clear_on_submit=True):
            st.subheader("Personal Information")
            name = st.text_input("Full Name*")
            email = st.text_input("Email*")
            phone = st.text_input("Mobile Number* (10 digits)")
            
            st.subheader("Account Details")
            username = st.text_input("Username*")
            password = st.text_input("Password* (min 8 characters)", type="password")
            confirm_password = st.text_input("Confirm Password*", type="password")
            
            submitted = st.form_submit_button("Create Account")
            
            if submitted:
                user_data = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "username": username,
                    "password": password,
                    "confirm_password": confirm_password
                }
                
                success, message = register_user(user_data)
                if success:
                    st.success(message)
                else:
                    st.error(message)

def logout():
    keys = list(st.session_state.keys())
    for key in keys:
        if key != "rerun":
            del st.session_state[key]
    st.rerun()