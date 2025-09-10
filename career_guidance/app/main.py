import streamlit as st
from app.auth.login import login_page
from app.pages import profile, page1, page2, page3
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

# Hide the sidebar
st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    # Initialize all required session state variables
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.current_page = "login"
        st.session_state.skip_questionnaire = False
        st.session_state.user_input = {}  # Initialize empty user_input
        st.session_state.show_questionnaire_prompt = False
    
    # Navigation logic
    if not st.session_state.authenticated:
        login_page()
    else:
        # Profile icon in top right
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("👤", help="Go to Profile", key="profile_nav_button"):
                st.session_state.current_page = "profile"
                st.rerun()
        
        # Page content with proper state checks
        if st.session_state.current_page == "profile":
            profile.page()
        elif st.session_state.current_page == "page1":
            page1.page()
        elif st.session_state.current_page == "page2":
            # Verify we have the required data before showing page2
            if not st.session_state.get("user_input", {}).get("vector_store"):
                st.warning("Please complete the questionnaire first")
                st.session_state.current_page = "page1"
                st.rerun()
            page2.page()
        elif st.session_state.current_page == "page3":
            page3.page()
        elif st.session_state.current_page == "results":
            from app.pages import results
            results.page()

if __name__=="__main__":
    main()
