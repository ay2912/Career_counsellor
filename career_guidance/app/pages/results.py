import streamlit as st
from app.database.session import get_db
from app.database.crud import get_suggestions_by_session
from app.apis.coursera_api import display_courses_for_skill

def format_skills(skills_str):
    """Format skills string into a list of skills"""
    if not skills_str:
        return []
    # Handle both newline and comma separated skills
    skills = []
    for skill in skills_str.split('\n'):
        skill = skill.strip()
        if skill:
            if ',' in skill:
                skills.extend([s.strip() for s in skill.split(',') if s.strip()])
            else:
                skills.append(skill)
    return skills

def display_suggestion(suggestion, index):
    """Display a single career suggestion with all details"""
    with st.expander(f"Option {index}: {suggestion.occupation}", expanded=index==1):
        tab1, tab2 = st.tabs(["Career Details", "Skills Development"])
        
        with tab1:
            st.subheader("Why this career fits you:")
            st.write(suggestion.reasoning or "No reasoning provided.")
            
            st.subheader("Market Outlook:")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Growth Potential", 
                         suggestion.growth_potential or "Not specified",
                         help="Industry growth potential (High/Medium/Low)")
            with col2:
                st.metric("Salary Range", 
                         suggestion.salary_range or "Not specified",
                         help="Typical salary range for this role")
            
            st.subheader("Additional Insights:")
            st.write("Our analysis suggests this career aligns well with your skills and experience. Market demand for this role is currently strong.")
        
        with tab2:
            st.subheader("Key Skills Required:")
            skills = format_skills(suggestion.skills)
            
            if skills:
                st.info("Click on each skill to see recommended courses:")
                for skill in skills:
                    with st.expander(f"📚 {skill}"):
                        display_courses_for_skill(skill)
            else:
                st.warning("No skills information available for this occupation.")

def page():
    if not st.session_state.get("authenticated"):
        st.warning("Please login first")
        return
    
    db = next(get_db())
    
    # Try to get suggestions for current session first
    session_id = st.session_state.get("session_id")
    if not session_id:
        st.error("No active session found")
        st.session_state.current_page = "profile"
        st.rerun()
        return
    
    suggestions = get_suggestions_by_session(db, session_id)
    
    st.title("Your Career Suggestions")
    st.markdown("""
    Below are the career paths we've identified as potential good matches for you. 
    Explore each option to understand why it might be a good fit and what skills you 
    would need to develop.
    """)
    
    if not suggestions:
        st.error("No career suggestions found for this session. Please complete the interview process.")
        if st.button("Back to Profile", type="primary"):
            st.session_state.current_page = "profile"
            st.rerun()
        return
    
    for idx, suggestion in enumerate(suggestions, 1):
        display_suggestion(suggestion, idx)
    
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back to Profile", type="secondary"):
            st.session_state.current_page = "profile"
            st.rerun()
    with col2:
        if st.button("Start New Session", type="primary"):
            # Clear session-specific data
            for key in ['session_id', 'career_suggestions_generated', 'questions', 
                       'current_question_index', 'memory', 'conversation_history']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.current_page = "page1"
            st.rerun()