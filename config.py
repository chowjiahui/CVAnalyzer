import os
import streamlit as st

GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY") #st.secrets["GEMINI_API_KEY"]
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY") #st.secrets["TAVILY_API_KEY"]