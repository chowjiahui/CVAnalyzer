import streamlit as st
import google.generativeai as genai
import PyPDF2
import docx
import io
import os
import time # To simulate processing if needed, or handle rate limits

# --- Configuration ---
st.set_page_config(
    page_title="Resume Gap Analyzer",
    page_icon="📄",
    layout="wide"
)

# Load API key from Streamlit secrets
try:
    # This is the standard way for deployed apps
    api_key = st.secrets["GEMINI_API_KEY"]
except FileNotFoundError:
    # Fallback for local development if secrets.toml doesn't exist
    # You might use an environment variable locally instead
    st.warning("Secrets file not found. For local development, set GEMINI_API_KEY environment variable or create .streamlit/secrets.toml")
    # api_key = os.environ.get("GEMINI_API_KEY") # Example using environment variable
    api_key = None # Or handle this case as needed for local runs
    if not api_key:
        st.error("API Key not configured. Ensure secrets.toml or environment variable is set.")
except KeyError:
    st.error("GEMINI_API_KEY not found in secrets.toml. Please add it.")
    api_key = None

# --- Helper Functions ---

def extract_text_from_pdf(file_bytes):
    """Extracts text from a PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return None

def extract_text_from_docx(file_bytes):
    """Extracts text from a DOCX file."""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        st.error(f"Error reading DOCX file: {e}")
        return None

def get_gemini_response(prompt, api_key, retries=3, delay=5):
    """Interacts with the Gemini API with error handling and retries."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash') # Or use 'gemini-pro'
        for attempt in range(retries):
            try:
                response = model.generate_content(prompt)
                # Check for safety ratings or blocks if necessary (more robust error handling)
                if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                    st.error(f"Content blocked due to: {response.prompt_feedback.block_reason}")
                    return f"Error: Content generation blocked ({response.prompt_feedback.block_reason}). Please try rephrasing or check API safety settings."

                # Accessing the text part safely
                if response.parts:
                    return response.text
                elif response.candidates and response.candidates[0].content.parts:
                     return response.candidates[0].content.parts[0].text
                else:
                    # Handle cases where the expected structure isn't found
                    st.warning("Gemini response structure unexpected. Trying to access text differently.")
                    # Fallback or alternative access method if needed - adjust based on API response structure
                    try:
                       return response.text # Attempt direct access again
                    except AttributeError:
                       st.error("Could not extract text from Gemini response.")
                       return "Error: Could not parse Gemini response."

            except Exception as e: # Catch broader API errors or unexpected issues
                st.warning(f"Gemini API call failed (Attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(delay) # Wait before retrying
                else:
                    st.error("Gemini API call failed after multiple retries.")
                    return f"Error: API call failed after retries ({e})"
        return "Error: Max retries reached." # Should ideally be caught by the loop's else clause fail

    except Exception as e:
        st.error(f"An error occurred during Gemini API interaction: {e}")
        return f"Error: Configuration or critical API error ({e})"


# --- Streamlit App UI ---

st.title("📄 Resume Gap Analyzer & Action Planner")
st.markdown("""
Welcome! This app helps you identify gaps between your resume and a specific job description
using the power of Google's Gemini AI. Upload your resume, paste the job description,
and get an analysis and action plan to improve your chances.
""")
st.divider()

# --- Sidebar for API Key Input ---
# st.sidebar.header("Configuration")
# api_key = st.sidebar.text_input("Enter your Google Gemini API Key:", type="password")
#
# st.sidebar.markdown("---")
# st.sidebar.markdown("### Instructions:")
# st.sidebar.markdown("""
# 1.  Get your Gemini API Key from [Google AI Studio](https://aistudio.google.com/app/apikey).
# 2.  Paste the API Key above.
# 3.  Upload your resume (PDF or DOCX).
# 4.  Paste the full job description text.
# 5.  Click 'Analyze Gaps'.
# """)
# st.sidebar.markdown("---")
# st.sidebar.warning("🔒 Your API key is used only for this session and is not stored.")
# st.sidebar.info("ℹ️ Analysis uses the Gemini API. Ensure you understand Google's data usage policies and potential costs associated with your API key.")


# --- Main Area for Inputs and Outputs ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Your Resume")
    uploaded_file = st.file_uploader("Choose a file (PDF or DOCX)", type=["pdf", "docx"], label_visibility="collapsed")

with col2:
    st.subheader("2. Paste Job Description")
    job_description = st.text_area("Paste the full job description text here", height=300, label_visibility="collapsed")

st.divider()

analyze_button = st.button("✨ Analyze Gaps", type="primary", use_container_width=True)

st.divider()

# --- Analysis and Output Section ---
if analyze_button:
    # --- Input Validation ---
    if uploaded_file is None:
        st.error("⚠️ Please upload your resume file.")
    elif not job_description.strip():
        st.error("⚠️ Please paste the job description.")
    else:
        # --- Processing ---
        st.info("Processing... Reading resume file.")
        file_bytes = uploaded_file.getvalue()
        resume_text = None
        file_type = uploaded_file.type

        if file_type == "application/pdf":
            resume_text = extract_text_from_pdf(file_bytes)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            resume_text = extract_text_from_docx(file_bytes)
        else:
            st.error("Unsupported file type. Please upload PDF or DOCX.")

        if resume_text:
            st.success("✅ Resume text extracted successfully.")

            # --- Disclaimer ---
            st.warning("""
            **Privacy & Cost Notice:**
            Your resume text and the job description will be sent to the Google Gemini API for analysis.
            By proceeding, you acknowledge this and accept responsibility for any API usage costs
            associated with your key. Review Google's AI terms and privacy policy.
            """)

            # --- Define Prompts ---
            gap_analysis_prompt = f"""
            **Task:** Analyze the provided Resume against the Job Description (JD) and identify key gaps.

            **Context:** You are an expert career coach specializing in resume optimization. The goal is to find areas where the resume falls short of the JD's requirements.

            **Instructions:**
            1.  Carefully read both the Resume Text and the Job Description Text provided below.
            2.  Compare the candidate's qualifications (skills, experience, responsibilities, education) outlined in the resume against the requirements specified in the job description.
            3.  Identify specific, significant gaps. Categorize these gaps clearly (e.g., Missing Hard Skill, Underrepresented Soft Skill, Responsibility Mismatch, Experience Level Gap, Missing Keywords, Education/Certification Gap).
            4.  For each identified gap, provide a brief, clear explanation of the discrepancy (e.g., "JD requires 5+ years of Python, resume shows 2 years," or "JD emphasizes 'cross-functional team leadership', resume lacks specific examples of this.").
            5.  Focus on actionable insights. Avoid generic statements.
            6.  Format your output using Markdown for readability (e.g., use headings for categories, bullet points for gaps).

            **Resume Text:**
            ```
            {resume_text[:8000]}
            ```
            *(Note: Resume text might be truncated for brevity if very long)*

            **Job Description Text:**
            ```
            {job_description[:8000]}
            ```
            *(Note: Job Description text might be truncated for brevity if very long)*

            **Output:** Start your response directly with the gap analysis using Markdown formatting.
            """

            action_plan_prompt_template = """
            **Task:** Generate a personalized action plan based on identified resume gaps.

            **Context:** You are an expert career coach. Based *only* on the Gap Analysis provided below, create a concrete, actionable plan for the candidate to improve their resume and profile for the target job.

            **Instructions:**
            1.  Review the Gap Analysis provided.
            2.  For each major gap category identified, suggest 1-3 specific, practical actions the candidate can take.
            3.  Action items should focus on:
                *   **Resume Updates:** Suggest specific wording changes, how to rephrase bullet points, or sections to add/enhance (emphasize truthful representation).
                *   **Skill Development:** Recommend *types* of resources (e.g., specific online courses, certifications, project ideas, books, communities) relevant to the missing skills. Be specific if possible (e.g., "Consider a project demonstrating X skill" instead of just "learn X").
                *   **Experience Acquisition:** Suggest ways to gain relevant experience if possible (e.g., volunteering, freelance work, internal projects, seeking specific responsibilities in current role).
                *   **Keyword Integration:** Advise on naturally incorporating missing keywords where appropriate and accurate.
            4.  Keep the tone constructive and encouraging.
            5.  Format the action plan as a numbered list using Markdown.

            **Identified Gap Analysis:**
            ```markdown
            {gap_analysis_result}
            ```

            **Output:** Start your response directly with the Action Plan using Markdown numbered list format.
            """

            # --- Call Gemini API ---
            with st.spinner("🧠 Contacting Gemini for Gap Analysis... (This may take a moment)"):
                gap_analysis_result = get_gemini_response(gap_analysis_prompt, api_key)

            if gap_analysis_result and not gap_analysis_result.startswith("Error:"):
                st.subheader("📊 Identified Gaps")
                st.markdown(gap_analysis_result)
                st.divider()

                with st.spinner("💡 Generating Action Plan with Gemini..."):
                     # Create the specific prompt for the action plan
                     action_plan_prompt = action_plan_prompt_template.format(gap_analysis_result=gap_analysis_result)
                     action_plan_result = get_gemini_response(action_plan_prompt, api_key)

                if action_plan_result and not action_plan_result.startswith("Error:"):
                     st.subheader("🚀 Your Action Plan")
                     st.markdown(action_plan_result)
                else:
                     st.error(f"Failed to generate Action Plan. {action_plan_result}")

            elif gap_analysis_result: # Handle error messages from get_gemini_response
                 st.error(f"Failed to perform Gap Analysis. {gap_analysis_result}")
            else:
                 st.error("Failed to get a response from the Gemini API for Gap Analysis.")

        # else: Error message already displayed by extraction function