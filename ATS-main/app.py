from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
from PIL import Image 
import pdf2image
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the API key for Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get the response from the Generative AI model
def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, pdf_content[0], prompt])
    return response.text

# Function to handle PDF upload and conversion to image
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# ---------- Enhanced UI Starts Here ----------

# Page Configuration
st.set_page_config(
    page_title="ATS Resume Expert",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 40px;
        color: #1f77b4;
        font-weight: bold;
    }
    .subtitle {
        font-size: 20px;
        color: #444;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        padding: 0.5em 1em;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2721/2721291.png", width=80)
st.sidebar.title("ATS System Menu")
st.sidebar.markdown("- 📤 Upload Resume\n- 🧾 Job Description\n- ✅ AI Matching")

# Main Title
st.markdown('<div class="main-title">ATS Resume Expert</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Match your resume with job descriptions using Google Gemini AI</div>', unsafe_allow_html=True)

# Tabs for organization
tab1, tab2 = st.tabs(["📄 Resume Analysis", "📊 Match Percentage"])

with tab1:
    st.subheader("Step 1: Paste Job Description")
    input_text = st.text_area("Job Description", key="input")

    st.subheader("Step 2: Upload Resume (PDF)")
    uploaded_file = st.file_uploader("Upload your resume...", type=["pdf"])

    if uploaded_file:
        st.success("✅ Resume uploaded successfully!")

    if st.button("🔍 Tell Me About the Resume"):
        if uploaded_file:
            pdf_content = input_pdf_setup(uploaded_file)
            response = get_gemini_response(input_text, pdf_content, """
            You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description. 
            Please share your professional evaluation on whether the candidate's profile aligns with the role. 
            Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
            """)
            st.subheader("🧠 AI Evaluation")
            st.write(response)
        else:
            st.warning("⚠️ Please upload a resume.")

with tab2:
    st.subheader("Check Resume-Job Description Match %")
    if uploaded_file:
        if st.button("📈 Show Match Percentage"):
            pdf_content = input_pdf_setup(uploaded_file)
            response = get_gemini_response(input_text, pdf_content, """
            You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
            Your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
            the job description. First, the output should come as a percentage, followed by keywords missing, and finally, your overall thoughts.
            """)
            st.subheader("📊 Match Result")
            st.write(response)
    else:
        st.info("💡 Please upload a resume in the first tab.")