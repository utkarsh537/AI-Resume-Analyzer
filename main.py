import streamlit as st 
from openai import OpenAI
import os 
import re
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt             


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
st.set_page_config(page_title="AI Resume Analyzer", page_icon="🚀", layout="wide")
st.title('AI Resume Analyzer')
st.markdown("Upload your resume & get a **Summary, Key, Skills, Score And improvement Suggestion**")
uploaded_file = st.file_uploader("Upload Your Resume", type = ["PDF"])

if uploaded_file:
    pdf = PdfReader(uploaded_file)
    text = ""
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
            
    text_clean = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Resume Preview")
        st.text_area("Resume Text", value=text_clean, height=400)
        
    with col2:
        st.subheader("AI Analysis")
        if st.button("Analyze Resume"):
            with st.spinner("Analyzing resume..."):
                prompt = f"""
                You are a resume expert.
                Analyze the following resume provide:
                1. Summary
                2. List of key skills
                3. Suggestions for improvement
                4. A score out of 100 based on
                - skills match (30 points)
                - Experience & achievement (30 points)
                - Clarity & formatting (20 points)
                - Overall impression (20 points)
                Also provide the individual category score in JSON
                Resume:
                {text_clean}
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=700
                )
                result = response.choices[0].message.content
                
                parts = result.split("Score JSON:")
                analysis_text = parts[0]
                st.write(analysis_text)
                
                if len(parts) > 1:
                    try:
                        import json
                        score_data = json.loads(parts[1].strip())
                        st.subheader("Score Breakdown")
                        df = pd.DataFrame({
                            "Category": list(score_data.keys()),
                            "Score": list(score_data.values())
                        })
                        st.bar_chart(df.set_index("Category"))
                        st.subheader("Overall Score")
                        total_score = sum(score_data.values())
                        st.progress(min(total_score / 100, 1.0))
                    except:
                        st.warning("Could not parse score JSON")