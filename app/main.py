import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
import os
import re
from chains import Chain
from portfolio import Portfolio
from utils import clean_text


# 🔥 Streamlit Page Configuration
st.set_page_config(
    layout="centered",
    page_title="Cold Mail Generator",
    page_icon="📧",
)

# 🎨 Modern Dark UI Styling
st.markdown(
    """
    <style>
    body {
        background-color: #121212;
    }
    .main-container {
        background-color: #1e1e1e;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(255,255,255,0.1);
        max-width: 800px;
        margin: auto;
        color: #f5f5f5;
    }
    h1, h4 {
        color: #4CAF50;
    }
    p, pre {
        color: #c7c7c7;
    }
    hr {
        border: 0.5px solid #333;
    }
    .stTextInput>div>div>input {
        padding: 15px;
        border: 1px solid #444;
        border-radius: 8px;
        font-size: 16px;
        background-color: #1f1f1f;
        color: #f5f5f5;
    }
    .stButton>button {
        background: linear-gradient(to right, #4CAF50, #45a049);
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        border: none;
        font-size: 16px;
        cursor: pointer;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(to right, #45a049, #4CAF50);
        transform: scale(1.05);
    }
    .process-container {
        background-color: #1f1f1f;
        padding: 20px;
        border-left: 5px solid #ff9800;
        border-radius: 8px;
        margin-top: 20px;
        font-size: 14px;
        line-height: 1.6;
        color: #f5f5f5;
    }
    .email-container {
        background-color: #1f2a3c;
        border-left: 5px solid #4CAF50;
        padding: 20px;
        border-radius: 8px;
        margin-top: 20px;
        font-size: 14px;
        line-height: 1.6;
        color: #d1e8ff;
    }
    .footer {
        text-align: center;
        padding-top: 20px;
        font-size: 14px;
        color: #888;
    }
    a {
        color: #4CAF50;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 🚀 Main Page Container
st.markdown(
    """
    <div class="main-container">
    <h1 style="text-align:center;">📧 Cold Mail Generator</h1>
    <p style="text-align:center; font-size:16px;">
        Generate high-conversion cold emails for job opportunities with ease.
    </p>
    <hr>
    """,
    unsafe_allow_html=True,
)

# ✅ URL Input Section
st.markdown("### 🔗 Enter the Job URL Below")
url_input = st.text_input(
    "",
    placeholder="Paste the URL here (e.g., https://jobs.nike.com/job/R-33460)",
)

# 🎯 Submit Button with Hover Effect
submit_button = st.button("🚀 Generate Cold Email")

# 📝 Instantiate Required Classes
chain = Chain()
portfolio = Portfolio()


def extract_company_name_from_content(data):
    # Use regex to search for common patterns
    patterns = [
        r"(?:Company Name|About|Organization|Employer):?\s*([A-Za-z0-9 .,&'-]+)",  # Pattern for common name markers
        r"<title>(.*?)</title>",  # Extract from title tag
    ]

    for pattern in patterns:
        match = re.search(pattern, data, re.IGNORECASE)
        if match:
            company_name = match.group(1).strip()
            if company_name and len(company_name) > 2:  # Valid name check
                return company_name

    return None


# # 🕵️‍♂️ Extract Company Name from URL
# def extract_company_name(url):
#     parts = url.split("/")
#     for part in parts:
#         if "." in part:
#             sub_parts = part.split(".")
#             if len(sub_parts) > 1:
#                 return sub_parts[1].capitalize()
#     return "[Company Name]"


# 📧 Process URL & Generate Email
if submit_button and url_input:
    try:
        with st.spinner("🔎 Analyzing the URL and generating your email..."):
            # Load and clean data from URL
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)

            # Load Portfolio into ChromaDB (If Required)
            portfolio.load_portfolio()

            # Extract job details and required skills
            jobs = chain.extract_jobs(data)

            if not jobs:
                st.warning(
                    "⚠️ No valid job details found. Please check the URL and try again."
                )
            else:
                company_name = extract_company_name_from_content(data)

                for job in jobs:
                    # Query relevant portfolio links
                    links = portfolio.query_links(job.get("skills", ""))

                    # 🎯 Display Process/Thinking Section
                    st.markdown(
                        f"""
                        <div class="process-container">
                        <h4>🕵️‍♂️ Process Overview for Role: <strong>{job.get('role', 'N/A')}</strong></h4>
                        <p><strong>Role:</strong> {job.get('role', 'N/A')}</p>
                        <p><strong>Required Skills:</strong> {', '.join(job.get('skills', ['N/A']))}</p>
                        <p><strong>Job Description Analysis:</strong> {job.get('description', 'No description available.')}</p>
                        <hr>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # 📧 Generate the Final Email
                    email = chain.write_mail(job, links)

                    # 🎉 Display Final Email Section
                    st.markdown(
                        f"""
                        <div class="email-container">
                        <h4>📧 Cold Email for Role: <strong>{job.get('role', 'N/A')}</strong></h4>
                        <pre style="white-space: pre-wrap;">{email.replace('AtliQ', company_name)}</pre>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    except Exception as e:
        st.error(f"❌ An Error Occurred: {str(e)}")

# 📚 Footer Section
st.markdown(
    """
    <div class="footer">
        🌟 Need help or have questions? <a href="mailto:support@[company name].com">Contact Us</a> | Powered by <strong>[company name]</strong>
    </div>
    """,
    unsafe_allow_html=True,
)
