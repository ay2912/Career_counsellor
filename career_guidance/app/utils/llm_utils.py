# Functions for LLM interactions
from langchain.chains import LLMChain, ConversationChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.utils.file_utils import save_uploaded_file
import json

# Initialize LLM and embeddings
llm = Ollama(model="llama3.1")
embeddings = OllamaEmbeddings(model="llama3.1")

def process_resume(resume):
    """Process the uploaded resume (PDF or TXT) and create a vector store."""
    if resume.type == "application/pdf":
        # Save the uploaded file temporarily
        file_path = save_uploaded_file(resume)
        # Use PyPDFLoader for PDF resumes
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        text = " ".join([page.page_content for page in pages])
    elif resume.type == "text/plain":
        # Read text directly from TXT files
        text = resume.read().decode("utf-8")
    else:
        raise ValueError("Unsupported file type. Please upload a PDF or TXT file.")
    
    # Split text into chunks for vector storage
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    
    # Create a vector store from the resume chunks
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    return vector_store

def generate_initial_questions(user_input, vector_store, example_questions):
    """Generate initial interview questions based on user input, resume context, and example questions."""
    relevant_chunks = vector_store.similarity_search(user_input, k=3)
    resume_context = " ".join([chunk.page_content for chunk in relevant_chunks])
    
    prompt = PromptTemplate(
        input_variables=["user_input", "resume_context", "example_questions"],
        template="""
        You are a career counsellor. Based on the following user input, resume context, and example questions, generate 10 questions for an interview with the counselling candidate:
        
        User Input: {user_input}
        Resume Context: {resume_context}
        Example Questions: {example_questions}
        """
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(user_input=user_input, resume_context=resume_context, example_questions=example_questions)

def suggest_career_pathways(chat_history, vector_store):
    relevant_chunks = vector_store.similarity_search(chat_history, k=3)
    resume_context = " ".join([chunk.page_content for chunk in relevant_chunks])
    
    prompt = PromptTemplate(
        input_variables=["chat_history", "resume_context"],
        template="""
        As a career counselor, analyze the following conversation and resume context.
        Provide 3 distinct career suggestions with these details for each:
        1. Occupation title
        2. Key skills needed (5-7 skills)
        3. Brief reasoning (50 words)
        4. Growth potential (High/Medium/Low)
        5. Typical salary range
        
        Format as JSON-friendly list of dictionaries.
        
        Chat History: {chat_history}
        Resume Context: {resume_context}
        """
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.run(chat_history=chat_history, resume_context=resume_context)
    
    try:
        suggestions = json.loads(result)
        if not isinstance(suggestions, list):
            suggestions = [suggestions]
        return suggestions
    except json.JSONDecodeError:
        # Fallback if LLM doesn't return proper JSON
        return [
            {
                "occupation": "Software Developer",
                "skills": "Python, Problem Solving, Algorithms\nTeamwork\nDebugging",
                "reasoning": "Your technical skills align well with software development roles.",
                "growth_potential": "High",
                "salary_range": "$80,000 - $120,000"
            }
        ]