import streamlit as st
from app.database.crud import save_career_suggestions, get_user_conversations
from app.database.session import get_db
from app.utils.llm_utils import suggest_career_pathways
import time

def page():
    if not st.session_state.get("authenticated"):
        st.warning("Please login first")
        return
    
    db = next(get_db())
    
    st.title("🎉 Interview Completed!")
    
    # Generate career suggestions if not already done
    if "career_suggestions_generated" not in st.session_state:
        with st.spinner("Analyzing your interview responses..."):
            try:
                # Get conversation history for this session
                conversations = get_user_conversations(
                    db,
                    st.session_state["user_id"],
                    st.session_state["session_id"]
                )
                
                if not conversations:
                    st.error("No conversation history found for this session")
                    st.session_state.current_page = "profile"
                    st.rerun()
                    return
                
                # Format chat history for LLM
                chat_history = "\n".join(
                    f"{conv.role}: {conv.content}" 
                    for conv in conversations
                )
                
                # Validate we have the vector store
                if "user_input" not in st.session_state or "vector_store" not in st.session_state.user_input:
                    st.error("Missing resume data. Please upload your resume again.")
                    st.session_state.current_page = "page1"
                    st.rerun()
                    return
                
                # Generate career suggestions with retry
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        suggestions = suggest_career_pathways(
                            chat_history,
                            st.session_state.user_input["vector_store"]
                        )
                        break
                    except Exception as e:
                        if attempt == max_retries - 1:
                            raise
                        time.sleep(2)
                
                # Save suggestions to database
                if suggestions:
                    save_career_suggestions(
                        db,
                        st.session_state["user_id"],
                        st.session_state["session_id"],
                        suggestions
                    )
                    st.session_state.career_suggestions_generated = True
                else:
                    st.error("Failed to generate career suggestions. Please try again.")
                    st.session_state.current_page = "page2"
                    st.rerun()
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.session_state.current_page = "profile"
                st.rerun()
    
    st.markdown("""
    <style>
    .big-font {
        font-size:24px !important;
        text-align: center;
    }
    .center-button {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="big-font">Congratulations on completing your career guidance interview!</p>', 
               unsafe_allow_html=True)
    st.markdown('<p class="big-font">Your personalized career suggestions are ready.</p>', 
               unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown('<div class="center-button">', unsafe_allow_html=True)
    if st.button("View Your Results", type="primary", use_container_width=True):
        st.session_state.current_page = "results"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)