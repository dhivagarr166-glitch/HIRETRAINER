import streamlit as st
import pdfplumber
from questions import TECHNICAL_QUESTIONS, NON_TECHNICAL_QUESTIONS

st.set_page_config(page_title="HIRE TRAINER", layout="wide")

# ------------------- LOGIN -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        st.session_state.logged_in = True
        st.session_state.batch_index = 0
        st.rerun()
    st.stop()

# ------------------- RESUME SCORER -------------------
def extract_resume_text(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.lower()

ROLE_KEYWORDS = {
    "Python Developer": ["python", "flask", "django", "oop", "api"],
    "Data Scientist": ["python", "pandas", "numpy", "ml", "statistics"],
    "Web Developer": ["html", "css", "javascript", "react"],
    "Machine Learning Engineer": ["ml", "regression", "classification", "neural network"],
    "AI Engineer": ["ai", "nlp", "deep learning", "computer vision"],
    "Cloud Engineer": ["aws", "cloud", "ec2", "s3", "vpc"],

    "HR Executive": ["recruitment", "communication", "onboarding"],
    "Business Analyst": ["brd", "frd", "stakeholder"],
    "Digital Marketing Executive": ["seo", "ads", "analytics"],
    "Content Writer": ["content", "seo", "copywriting"],
    "Customer Support Executive": ["crm", "communication", "ticketing"],
    "Operations Executive": ["operations", "planning", "coordination"]
}

# ------------------- SESSION STATE -------------------
if "batch_index" not in st.session_state:
    st.session_state.batch_index = 0
if "apt_answers" not in st.session_state:
    st.session_state.apt_answers = {}
if "resume_score" not in st.session_state:
    st.session_state.resume_score = 0
if "apt_score" not in st.session_state:
    st.session_state.apt_score = 0
if "interview_score" not in st.session_state:
    st.session_state.interview_score = 0

# ------------------- NAVIGATION -------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Resume Scorer", "Aptitude Test", "Mock Interview", "Dashboard"]
)

# ------------------- RESUME SCORER -------------------
if page == "Resume Scorer":
    st.header("Resume Scorer")

    role = st.selectbox("Select Role", list(ROLE_KEYWORDS.keys()))
    resume = st.file_uploader("Upload Resume (PDF)", type="pdf")

    if resume:
        text = extract_resume_text(resume)
        keywords = ROLE_KEYWORDS[role]

        matched = [k for k in keywords if k in text]
        missing = [k for k in keywords if k not in text]

        score = min(len(matched) * 20, 100)
        st.session_state.resume_score = score

        st.metric("Resume Score", f"{score}/100")

        st.subheader("Strengths")
        for m in matched:
            st.write(f"✔ {m}")

        st.subheader("Gaps")
        for g in missing:
            st.write(f"✘ {g}")

# ------------------- APTITUDE TEST -------------------
elif page == "Aptitude Test":
    st.header("Aptitude Test")

    category = st.radio("Category", ["Technical", "Non-Technical"])

    if category == "Technical":
        role = st.selectbox("Role", list(TECHNICAL_QUESTIONS.keys()))
        questions = TECHNICAL_QUESTIONS[role]
    else:
        role = st.selectbox("Role", list(NON_TECHNICAL_QUESTIONS.keys()))
        questions = NON_TECHNICAL_QUESTIONS[role]

    batch_size = 10
    start = st.session_state.batch_index * batch_size
    end = start + batch_size
    current_batch = questions[start:end]

    st.subheader(f"Questions {start + 1} to {min(end, len(questions))}")

    for idx, q in enumerate(current_batch):
        q_text, options, _ = q
        q_key = f"{role}_{start + idx}"

        if options:
            st.radio(q_text, options, key=q_key)
        else:
            st.text_area(q_text, key=q_key)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Next Batch"):
            if end < len(questions):
                st.session_state.batch_index += 1
                st.rerun()

    with col2:
        if st.button("Submit Aptitude"):
            st.session_state.apt_score = 70
            st.success("Aptitude Test Submitted")

# ------------------- MOCK INTERVIEW -------------------
elif page == "Mock Interview":
    st.header("Mock Interview")

    QUESTIONS = [
        "Tell me about yourself",
        "Why should we hire you?",
        "What are your strengths?",
        "What are your weaknesses?",
        "How do you handle pressure?",
        "Describe a challenge you faced",
        "Why do you want this job?",
        "Where do you see yourself in 5 years?",
        "How will you add value?",
        "What do you know about our company?"
    ]

    for i, q in enumerate(QUESTIONS, 1):
        st.text_area(f"{i}. {q}", key=f"interview_{i}")

    if st.button("Submit Interview"):
        st.session_state.interview_score = 80
        st.success("Mock Interview Submitted")

# ------------------- DASHBOARD -------------------
elif page == "Dashboard":
    st.header("Dashboard")

    st.metric("Resume Score", f"{st.session_state.resume_score}/100")
    st.metric("Aptitude Score", f"{st.session_state.apt_score}/100")
    st.metric("Mock Interview Score", f"{st.session_state.interview_score}/100")

    if st.button("Restart / Refresh"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
