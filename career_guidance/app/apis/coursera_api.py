# app/apis/coursera_api.py
import requests
import streamlit as st
from requests.auth import HTTPBasicAuth
from app.config import COURSERA_API_KEY, COURSERA_API_SECRET

def get_coursera_courses(skill: str, limit: int = 5) -> list:
    """Fetch relevant courses from Coursera API"""
    url = "https://api.coursera.org/api/courses.v1"
    auth = HTTPBasicAuth(COURSERA_API_KEY, COURSERA_API_SECRET)
    params = {
        "q": "search",
        "query": skill,
        "fields": "name,description,slug",
        "limit": limit
    }
    
    try:
        response = requests.get(url, auth=auth, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("elements", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch courses: {str(e)}")
        return []

def display_courses_for_skill(skill: str):
    """Display Coursera courses in a Streamlit-friendly format"""
    courses = get_coursera_courses(skill)
    
    if not courses:
        st.warning(f"No courses found for: {skill}")
        return
    
    for course in courses:
        name = course.get("name", "Untitled Course")
        description = course.get("description", "No description available")
        url = f"https://www.coursera.org/learn/{course.get('slug', '')}"
        
        with st.expander(name):
            st.write(description)
            st.markdown(f"[🔗 Enroll on Coursera]({url})", unsafe_allow_html=True)