import streamlit as st
import uuid
from app.utils.llm_utils import generate_initial_questions, llm
from app.utils.text_utils import extract_questions
from app.utils.speech_utils import text_to_speech, continuous_listen
from langchain.chains import LLMChain, ConversationChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from app.database.crud import save_conversation
from app.database.session import get_db
from app.config import EXAMPLE_QUESTIONS_PATH

def page():
    # Initialize session state variables
    if 'listening' not in st.session_state:
        st.session_state.listening = False
    if 'accumulated_text' not in st.session_state:
        st.session_state.accumulated_text = ""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4()) 
    
    # Authentication check
    if not st.session_state.get("authenticated"):
        st.warning("Please login first")
        return
    
    # Data validation check
    if not st.session_state.get("user_input") or not st.session_state.user_input.get("vector_store"):
        st.error("Missing required data. Please complete the questionnaire first.")
        st.session_state.current_page = "page1"
        st.rerun()
    
    st.title("Career Guidance Interview")
    
    # Initialize questions if not already done
    if "questions" not in st.session_state:
        initialize_questions()
    
    # Display current question
    if st.session_state.current_question_index < len(st.session_state.questions):
        # Create a container for the question section
        question_container = st.container()
        with question_container:
            display_current_question()
        
        # Answer section with clear separation
        st.markdown("---")
        st.subheader("Your Response")
        
        # Continuous listening toggle
        if not st.session_state.listening:
            if st.button("🎙️ Start Recording", type="primary", use_container_width=True):
                st.session_state.listening = True
                st.session_state.accumulated_text = ""
                st.rerun()
        else:
            if st.button("⏹️ Stop Recording", type="secondary", use_container_width=True):
                st.session_state.listening = False
                st.rerun()
            
            # Show listening status and accumulated text
            with st.status("🔴 Recording... Speak now", expanded=True):
                if st.session_state.accumulated_text:
                    st.write(st.session_state.accumulated_text)
                
                # Continuous listening
                new_text = continuous_listen()
                if new_text:
                    if "stop" in new_text.lower():
                        st.session_state.listening = False
                    else:
                        st.session_state.accumulated_text += " " + new_text
                    st.rerun()
        
        # Process answer when recording stops
        if not st.session_state.listening and st.session_state.accumulated_text:
            process_answer(st.session_state.accumulated_text.strip(), 
                         st.session_state.current_question)
        
        # Manual input fallback
        with st.expander("✏️ Type answer instead"):
            manual_answer = st.text_area("Type your response:", height=150)
            if st.button("Submit Text Answer", use_container_width=True):
                if manual_answer.strip():
                    process_answer(manual_answer.strip(), 
                                 st.session_state.current_question)
    else:
        st.success("🎉 Interview completed!")
        st.session_state.current_page = "page3"
        st.rerun()

def initialize_questions():
    """Initialize interview questions"""
    db = next(get_db())
    with open(EXAMPLE_QUESTIONS_PATH, "r") as f:
        example_questions = f.read()
    
    questions_text = generate_initial_questions(
        st.session_state.user_input["work_experience"],
        st.session_state.user_input["vector_store"],
        example_questions
    )
    
    st.session_state.questions = extract_questions(questions_text)
    st.session_state.current_question_index = 0
    st.session_state.memory = ConversationBufferMemory()
    st.session_state.cross_question_count = 0
    st.session_state.conversation_history = []
    st.session_state.waiting_for_followup = False
    st.session_state.followup_questions = []

def display_current_question():
    """Display the current question with guaranteed visibility"""
    # Determine current question and its type
    if st.session_state.waiting_for_followup:
        current_question = st.session_state.followup_questions[-1]
        question_type = "Follow-up Question"
        question_number = st.session_state.cross_question_count
        border_color = "#6c757d"  # Gray for follow-ups
        bg_color = "#f8f9fa"      # Light gray background
    else:
        current_question = st.session_state.questions[st.session_state.current_question_index]
        question_type = "Question"
        question_number = st.session_state.current_question_index + 1
        border_color = "#4e8cff"  # Blue for main questions
        bg_color = "#ffffff"      # White background

    # Store current question in session state
    st.session_state.current_question = current_question

    # Display conversation history with improved visibility
    if st.session_state.conversation_history:
        with st.expander("🗒️ Conversation History", expanded=False):
            for entry in st.session_state.conversation_history:
                role_color = "#4e8cff" if entry['role'] == "You" else "#495057"
                st.markdown(f"""
                <div style='
                    background: {"#f8f9fa" if entry['role'] == "Interviewer" else "#ffffff"};
                    padding: 1rem;
                    margin: 0.5rem 0;
                    border-radius: 8px;
                    border-left: 4px solid {role_color};
                '>
                    <div style='font-weight: bold; color: {role_color};'>
                        {entry['role']}
                    </div>
                    <div style='color: #6c757d; font-size: 0.9rem;'>
                        {entry.get('time', '')}
                    </div>
                    <div style='margin-top: 0.5rem; color: #212529;'>
                        {entry['text']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Display current question with high visibility styling
    st.markdown(f"""
    <div style='
        background: {bg_color};
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: 8px;
        border-left: 4px solid {border_color};
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    '>
        <div style='
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        '>
            <h3 style='margin: 0; color: #212529;'>
                {question_type} {question_number}
            </h3>
            <div style='
                background: {border_color};
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 12px;
                font-size: 0.9rem;
            '>
                {question_type.split()[0]}
            </div>
        </div>
        <p style='
            margin: 0;
            font-size: 1.2rem;
            line-height: 1.6;
            color: #212529;
            font-weight: 500;
        '>
            {current_question}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Auto-speak the question with visual feedback
    if st.session_state.get('last_spoken') != current_question:
        text_to_speech(current_question, autoplay=True, show_player=False)
        st.session_state.last_spoken = current_question
def process_answer(answer_text, question_text):
    """Process user answer and generate follow-up or move to next question"""
    db = next(get_db())
    
    # Save to memory and database
    st.session_state.memory.save_context({"input": question_text}, {"output": answer_text})
    save_conversation(
        db,
        st.session_state["user_id"],
        st.session_state["session_id"],
        "user",
        answer_text
    )
    
    # Add to conversation history
    st.session_state.conversation_history.append({"role": "You", "text": answer_text})
    
    # Handle follow-up questions or move to next question
    if st.session_state.cross_question_count < 3:
        generate_followup_question(answer_text)
    else:
        move_to_next_question()

def generate_followup_question(answer_text):
    """Generate follow-up question based on answer"""
    cross_question_prompt = PromptTemplate(
        input_variables=["user_answer"],
        template="Ask one relevant follow-up question about: {user_answer}"
    )
    cross_question_chain = LLMChain(llm=llm, prompt=cross_question_prompt)
    cross_question = cross_question_chain.run(user_answer=answer_text)
    
    st.session_state.followup_questions.append(cross_question)
    st.session_state.conversation_history.append({"role": "Interviewer", "text": cross_question})
    st.session_state.waiting_for_followup = True
    st.session_state.cross_question_count += 1
    st.session_state.listening = False
    st.session_state.accumulated_text = ""
    st.rerun()

def move_to_next_question():
    """Move to next question or end interview"""
    st.session_state.cross_question_count = 0
    st.session_state.waiting_for_followup = False
    st.session_state.followup_questions = []
    st.session_state.conversation_history = []
    st.session_state.current_question_index += 1
    st.session_state.listening = False
    st.session_state.accumulated_text = ""
    st.rerun()