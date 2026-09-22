"""
app.py
------
This is the Streamlit web app. It shows the form for pasting/uploading a
resume and job description, and displays the AI agent's feedback report.

Run locally with:
    streamlit run app.py
"""

import streamlit as st
from pypdf import PdfReader

from crew_agent import run_resume_review

# The exact Groq production model to use.
# "openai/gpt-oss-120b" is a current Groq production model (Sept 2026).
MODEL_NAME = "groq/openai/gpt-oss-120b"

st.set_page_config(page_title="AI Resume Review Agent", page_icon="📄", layout="wide")


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Tries to pull plain text out of an uploaded PDF.
    Returns an empty string if the PDF can't be read (e.g. it's a scanned
    image with no selectable text, or the file is corrupted).
    """
    try:
        reader = PdfReader(uploaded_file)
        pages_text = []
        for page in reader.pages:
            # extract_text() can return None for image-only pages
            pages_text.append(page.extract_text() or "")
        return "\n".join(pages_text).strip()
    except Exception:
        # Any parsing error (corrupted file, encrypted PDF, etc.) lands here
        return ""


def get_groq_api_key():
    """
    Reads the Groq API key from Streamlit secrets.
    Returns None if it hasn't been configured yet, instead of crashing.
    """
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return None


def main():
    st.title("📄 AI Resume Review Agent")
    st.caption(
        "Paste or upload a resume and a target job description. A single AI "
        "agent (built with CrewAI + Groq) scores the match and gives honest, "
        "specific improvement tips — without inventing skills you don't have."
    )

    # ---- Check the API key first, before showing the rest of the app ----
    api_key = get_groq_api_key()
    if not api_key:
        st.error(
            "⚠️ No Groq API key found.\n\n"
            "Add a key named **GROQ_API_KEY** to your Streamlit secrets:\n"
            "- On Streamlit Community Cloud: App settings → Secrets\n"
            "- Locally: create a file at `.streamlit/secrets.toml` with:\n"
            '  `GROQ_API_KEY = "your-key-here"`'
        )
        st.stop()

    # ---- Input section ----
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Your Resume")
        input_mode = st.radio(
            "How would you like to provide your resume?",
            ["Paste text", "Upload PDF"],
            horizontal=True,
        )

        resume_text = ""
        if input_mode == "Paste text":
            resume_text = st.text_area(
                "Paste your resume text here",
                height=300,
                placeholder="Paste your full resume text...",
            )
        else:
            uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])
            if uploaded_file is not None:
                with st.spinner("Reading PDF..."):
                    resume_text = extract_text_from_pdf(uploaded_file)

                if not resume_text:
                    st.warning(
                        "Couldn't extract any text from this PDF. It might be "
                        "a scanned image, password-protected, or corrupted. "
                        "Try 'Paste text' instead, or upload a different file."
                    )
                else:
                    with st.expander("Preview extracted text"):
                        st.text(resume_text[:3000])

    with col2:
        st.subheader("2. Target Job Description")
        job_description = st.text_area(
            "Paste the job description here",
            height=300,
            placeholder="Paste the full job description...",
        )

    st.divider()
    analyze_clicked = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)

    # ---- Run the agent ----
    if analyze_clicked:
        # Guard against missing inputs
        if not resume_text or not resume_text.strip():
            st.error("Please provide your resume text (paste it, or upload a readable PDF) before analyzing.")
            return
        if not job_description or not job_description.strip():
            st.error("Please paste the target job description before analyzing.")
            return

        with st.spinner("The AI agent is reviewing your resume... this can take 20-60 seconds."):
            try:
                report = run_resume_review(
                    api_key=api_key,
                    resume_text=resume_text,
                    job_description=job_description,
                    model_name=MODEL_NAME,
                )
            except Exception as e:
                error_text = str(e).lower()

                if "rate limit" in error_text or "429" in error_text:
                    st.error(
                        "🚦 Groq's API rate limit was reached. Please wait a "
                        "minute and try again. If this keeps happening, check "
                        "the usage limits on your Groq account."
                    )
                elif "api key" in error_text or "auth" in error_text or "401" in error_text:
                    st.error(
                        "🔑 The Groq API key was rejected. Double-check that "
                        "GROQ_API_KEY in your Streamlit secrets is correct and "
                        "still active."
                    )
                elif "timeout" in error_text or "timed out" in error_text:
                    st.error("⏱️ The request to Groq timed out. Please try again.")
                elif "context" in error_text and "length" in error_text:
                    st.error(
                        "📏 The resume and job description together are too "
                        "long for the model. Try shortening the job "
                        "description or resume and try again."
                    )
                else:
                    st.error(f"Something went wrong while contacting the AI model: {e}")
                return

        st.success("✅ Analysis complete!")
        st.markdown(report)

        st.download_button(
            "⬇️ Download Report as Markdown",
            data=report,
            file_name="resume_review_report.md",
            mime="text/markdown",
        )


if __name__ == "__main__":
    main()
