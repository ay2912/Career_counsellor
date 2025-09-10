import streamlit as st
from app.database.session import get_db
from app.database.crud import (
    get_questionnaire_data,
    save_questionnaire
)
from app.utils.llm_utils import process_resume

def page():
    if not st.session_state.get("authenticated"):
        st.warning("Please login first")
        return
    
    if "user_input" not in st.session_state:
        st.session_state.user_input = {}

    db = next(get_db())
    
    if st.session_state.get("skip_questionnaire", False):
        st.session_state.current_page = "page2"
        st.rerun()
    
    st.title("Career Guidance Questionnaire")
    
    prev_data = get_questionnaire_data(db, st.session_state["user_id"])
    
    with st.form("questionnaire_form"):
        name = st.text_input("What is your name?", 
                           value=prev_data.get("name") if prev_data else "")
        age = st.number_input("How old are you?", 
                            min_value=0, max_value=100,
                            value=prev_data.get("age") if prev_data else 0)
        personality = st.text_area("Describe your personality in a few words:",
                                 value=prev_data.get("personality") if prev_data else "")
        work_experience = st.text_area("Briefly describe your work experience:",
                                     value=prev_data.get("work_experience") if prev_data else "")
        resume = st.file_uploader("Upload your resume (PDF or TXT)", 
                                 type=["pdf", "txt"])
        
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            # Process resume and get vector_store
            vector_store = process_resume(resume) if resume else None
            
            questionnaire_data = {
                "name": name,
                "age": age,
                "personality": personality,
                "work_experience": work_experience,
                "resume_data": str(vector_store) if vector_store else None
            }
            
            save_questionnaire(db, st.session_state["user_id"], questionnaire_data)
            
            # Store both the questionnaire data AND the vector_store
            st.session_state.user_input = {
                **questionnaire_data,
                "vector_store": vector_store  # This is the key addition
            }
            
            st.session_state.current_page = "page2"
            st.rerun()