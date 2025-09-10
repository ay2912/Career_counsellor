import streamlit as st
from typing import List
from app.database.models import CareerSuggestion

def display_comparison(suggestions: List[CareerSuggestion]):
    if len(suggestions) < 2:
        st.warning("Need at least 2 suggestions to compare")
        return
    
    st.subheader("Career Path Comparison")
    
    comparison_data = []
    for suggestion in suggestions:
        comparison_data.append({
            "Occupation": suggestion.occupation,
            "Key Skills": suggestion.skills.replace('\n', ', '),
            "Growth Potential": suggestion.growth_potential,
            "Salary Range": suggestion.salary_range,
            "Reasoning": suggestion.reasoning
        })
    
    for idx, suggestion in enumerate(comparison_data, 1):
        with st.expander(f"Option {idx}: {suggestion['Occupation']}"):
            cols = st.columns([1,2])
            with cols[0]:
                st.metric("Growth", suggestion['Growth Potential'])
                st.metric("Salary", suggestion['Salary Range'])
            with cols[1]:
                st.write("**Key Skills:**")
                st.write(suggestion['Key Skills'])
                st.write("**Reasoning:**")
                st.write(suggestion['Reasoning'])
    
    st.subheader("Visual Comparison")
    chart_data = {
        "Occupation": [s['Occupation'] for s in comparison_data],
        "Growth Score": [3 if "High" in s['Growth Potential'] else 
                        2 if "Medium" in s['Growth Potential'] else 1 
                        for s in comparison_data]
    }
    st.bar_chart(chart_data, x="Occupation", y="Growth Score")