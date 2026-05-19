"""
AutoDS-LLM Frontend - Main Streamlit App
Professional dashboard for ML pipeline recommendations
"""

import streamlit as st
import os
import sys
from pathlib import Path

# Page config
st.set_page_config(
    page_title="AutoDS-LLM - ML Pipeline Recommender",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS for professional styling
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    /* Main theme colors */
    :root {
        --abb-red: #EF3B39;
        --abb-dark: #1B1B1B;
        --abb-light: #F5F5F5;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #1B1B1B 0%, #2D2D2D 100%);
        padding: 2rem 0;
        margin: -2rem -2rem 2rem -2rem;
        border-bottom: 3px solid #EF3B39;
    }
    
    .header-title {
        color: white;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        color: #CCCCCC;
        font-size: 1.1em;
        font-weight: 300;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #EF3B39;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background: #EF3B39;
        color: white;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: #D63030;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(239, 59, 57, 0.3);
    }
    
    /* Sidebar styling */
    .sidebar-title {
        color: #EF3B39;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Success/Info/Warning colors */
    .success-box {
        background: #E8F5E9;
        padding: 1rem;
        border-radius: 4px;
        border-left: 4px solid #4CAF50;
    }
    
    .info-box {
        background: #E3F2FD;
        padding: 1rem;
        border-radius: 4px;
        border-left: 4px solid #2196F3;
    }
    
    .warning-box {
        background: #FFF3E0;
        padding: 1rem;
        border-radius: 4px;
        border-left: 4px solid #FF9800;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-container">
    <div class="header-title">🤖 AutoDS-LLM</div>
    <div class="header-subtitle">Intelligent ML Pipeline Recommendations for Automated Data Science</div>
</div>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    # Show logo if available, otherwise display text
    logo_path = Path(__file__).parent.parent / "assets" / "logo.png"
    if logo_path.exists():
        st.image(str(logo_path), caption="AutoDS-LLM", width=200)
    else:
        st.markdown("<h3 style='color: var(--abb-red); margin-bottom: 0.5rem;'>AutoDS-LLM</h3>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-title'>Navigation</div>", unsafe_allow_html=True)
    
    page = st.radio(
        "Select Page",
        ["🏠 Home", "📊 Data Upload & Analysis", "🎯 Task Prediction", "🔧 Pipeline Recommendation", "📈 Examples"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("<div class='sidebar-title'>About AutoDS-LLM</div>", unsafe_allow_html=True)
    st.info(
        """
        **Version:** 1.0.0  
        **Purpose:** Automated Data Science with LLM-based Pipeline Recommendations
        
        **Features:**
        - 📤 Upload & analyze datasets
        - 🎯 Automatic task type prediction
        - 🔧 ML pipeline recommendations
        - 📊 Comprehensive metrics suggestions
        """
    )

# Page routing
if page == "🏠 Home":
    from pages.home import show_home
    show_home()

elif page == "📊 Data Upload & Analysis":
    from pages.data_upload import show_data_upload
    show_data_upload()

elif page == "🎯 Task Prediction":
    from pages.task_prediction import show_task_prediction
    show_task_prediction()

elif page == "🔧 Pipeline Recommendation":
    from pages.pipeline_recommendation import show_pipeline_recommendation
    show_pipeline_recommendation()

elif page == "📈 Examples":
    from pages.examples import show_examples
    show_examples()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #999; margin-top: 2rem;'>
        <p>AutoDS-LLM © 2024 | ABB Internship Innovation Challenge</p>
        <p style='font-size: 0.9em;'>Powered by FastAPI, Streamlit, and ML Engineering</p>
    </div>
    """,
    unsafe_allow_html=True
)
