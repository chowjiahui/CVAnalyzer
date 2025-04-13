import streamlit as st
import google.generativeai as genai
import PyPDF2
import docx
import io
import time # To simulate processing if needed, or handle rate limits

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

