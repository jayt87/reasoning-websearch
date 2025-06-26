import streamlit as st
import hmac

def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["username"], st.secrets["credentials"]["username"]) and \
           hmac.compare_digest(st.session_state["password"], st.secrets["credentials"]["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password
            del st.session_state["username"]  # Don't store the username
        else:
            st.session_state["password_correct"] = False

    # Initialize session state
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    # Show login form if not authenticated
    if not st.session_state["password_correct"]:
        st.title("Login")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        return False
    
    return True
