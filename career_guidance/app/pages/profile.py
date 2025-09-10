import streamlit as st
from app.database.crud import (
    get_user_by_username,
    get_user_conversations,
    get_user_career_suggestions,
    get_questionnaire_data,
    delete_conversation_history,
    get_suggestions_by_session
)
from app.database.session import get_db
from app.utils.comparison_utils import display_comparison
from streamlit.components.v1 import html

def handle_new_session(db):
    """FIXED: Properly handle starting a new session"""
    # Clear previous session data
    for key in ['questions', 'current_question_index', 'memory', 
               'conversation_history', 'followup_questions',
               'waiting_for_followup', 'cross_question_count',
               'user_input', 'current_page']:
        if key in st.session_state:
            del st.session_state[key]
    
    # Check if questionnaire exists
    has_questionnaire = get_questionnaire_data(db, st.session_state["user_id"]) is not None
    
    if has_questionnaire and st.session_state.get("skip_questionnaire", False):
        st.session_state.current_page = "page2"  # Skip to interview
    else:
        st.session_state.current_page = "page1"  # Start with questionnaire
    
    st.rerun()

def page():
    if not st.session_state.get("authenticated"):
        st.warning("Please login first")
        return
    
    db = next(get_db())
    user = get_user_by_username(db, st.session_state["username"])
    
    if not user:
        st.error("User not found")
        return
    
    # Header with session management
    st.header("Your Profile")
    
    # Start New Session button - FIXED VERSION
    if st.button("🎯 Start New Session", 
               help="Begin a new career guidance session",
               use_container_width=True,
               key="new_session_button"):
        handle_new_session(db)
    
    
    # Reset confirmation dialog
    if st.session_state.get("show_reset_confirm", False):
        st.warning("This will permanently delete all your conversation history. Continue?")
        confirm_col1, confirm_col2 = st.columns([1, 2])
        with confirm_col1:
            if st.button("✅ Confirm", type="primary"):
                deleted_count = delete_conversation_history(db, user.id)
                st.success(f"Deleted {deleted_count} conversation records")
                st.session_state.show_reset_confirm = False
                st.rerun()
        with confirm_col2:
            if st.button("❌ Cancel"):
                st.session_state.show_reset_confirm = False
                st.rerun()
    
    st.markdown("---")
    
    # Tab system
    tab1, tab2, tab3 = st.tabs(["📜 Conversation History", "📊 Interview Results", "📈 Compare Careers"])
    
    with tab1:
        show_conversation_history(db, user)
    
    with tab2:
        show_interview_results(db, user)
    
    with tab3:
        show_comparison_tool(db, user)


def show_conversation_history(db, user):
    """Display conversation history with working reset functionality"""
    # Initialize reset confirmation state
    if 'confirm_reset' not in st.session_state:
        st.session_state.confirm_reset = False
    
    # Create columns for title and menu button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.subheader("Your Conversations")
    with col2:
        if st.button("⋮", key="menu_button"):
            st.session_state.show_menu = not st.session_state.get("show_menu", False)
    
    # Reset menu
    if st.session_state.get("show_menu"):
        if st.button("🗑️ Reset All History"):
            st.session_state.confirm_reset = True
    
    # Confirmation dialog
    if st.session_state.get("confirm_reset"):
        st.warning("Are you sure you want to delete ALL conversation history? This cannot be undone.")
        confirm_col1, confirm_col2 = st.columns(2)
        with confirm_col1:
            if st.button("✅ Confirm Delete", type="primary"):
                try:
                    deleted_count = delete_conversation_history(db, user.id)
                    st.success(f"Deleted {deleted_count} conversation records")
                    st.session_state.show_menu = False
                    st.session_state.confirm_reset = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting history: {str(e)}")
        with confirm_col2:
            if st.button("❌ Cancel"):
                st.session_state.confirm_reset = False
    
    # Display conversations
    conversations = get_user_conversations(db, user.id)
    
    if not conversations:
        st.info("No conversation history yet.")
        if st.button("Start Your First Session", use_container_width=True):
            st.session_state.current_page = "page1"
            st.rerun()
        return
    
    # Group conversations by session
    sessions = {}
    for conv in conversations:
        if conv.session_id not in sessions:
            sessions[conv.session_id] = []
        sessions[conv.session_id].append(conv)
    
    # Display each session
    for session_id, session_convs in sessions.items():
        session_date = session_convs[0].created_at.strftime('%Y-%m-%d %H:%M')
        
        with st.expander(f"🗓️ Interview Session - {session_date}"):
            for conv in session_convs:
                st.markdown(f"""
                <div style="margin-bottom: 1rem;">
                    <div style="font-weight: bold;">{conv.role}</div>
                    <div style="color: #666; font-size: 0.9rem;">{conv.created_at.strftime('%H:%M')}</div>
                    <div style="margin-top: 0.5rem;">{conv.content}</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("---")

def show_interview_results(db, user):
    """Display interview results"""
    suggestions = get_user_career_suggestions(db, user.id)
    
    if not suggestions:
        st.info("No interview results yet. Complete a session to see suggestions.")
        if st.button("Start a Session", 
                    key="results_start_session",
                    use_container_width=True):
            st.session_state.current_page = "page1"
            st.rerun()
        return
    
    st.subheader("Your Career Suggestions")
    
    # Group by session
    sessions = {}
    for suggestion in suggestions:
        if suggestion.session_id not in sessions:
            sessions[suggestion.session_id] = []
        sessions[suggestion.session_id].append(suggestion)
    
    for session_id, session_suggestions in sessions.items():
        st.markdown(f"**Session from {session_suggestions[0].created_at.strftime('%Y-%m-%d')}**")
        for suggestion in session_suggestions:
            with st.expander(f"{suggestion.occupation}"):
                st.metric("Growth Potential", suggestion.growth_potential)
                st.write(f"**Skills:** {suggestion.skills}")
                st.write(f"**Reasoning:** {suggestion.reasoning}")
        st.markdown("---")

def show_comparison_tool(db, user):
    """Display career comparison tool"""
    suggestions = get_user_career_suggestions(db, user.id)
    
    if len(suggestions) < 2:
        st.info("You need at least 2 career suggestions to compare.")
        if st.button("Complete More Sessions", 
                    key="compare_start_session",
                    use_container_width=True):
            st.session_state.current_page = "page1"
            st.rerun()
        return
    
    st.subheader("Compare Career Paths")
    display_comparison(suggestions)