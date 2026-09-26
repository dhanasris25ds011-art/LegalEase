"""
frontend/app.py

Streamlit UI for LegalEase. Collects document details, sends them to the
FastAPI backend, previews the AI-generated document, and offers
editable download in .txt / .docx / .pdf formats.

Run with:
    streamlit run frontend/app.py
(Run the FastAPI backend first: uvicorn legalEaseAPI.main:app --reload)
"""
import os
import sys

import requests
import streamlit as st

# Allow imports from the project root when run as `streamlit run frontend/app.py`
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BACKEND_URL, WEB_LOGO_PATH  # noqa: E402
from utils.formatters import (  # noqa: E402
    sanitize_text,
    format_docx,
    format_pdf,
    format_html_preview,
)

st.set_page_config(page_title="LegalEase", layout="centered")

# ---- Header / Logo ----
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists(WEB_LOGO_PATH):
        st.image(WEB_LOGO_PATH, use_column_width=True)

st.markdown(
    "<h2 style='text-align: center;'>AI Legal Document Generator</h2>",
    unsafe_allow_html=True,
)

# ---- Inputs ----
document_type = st.text_input("Document Type (Ex: Agreement, Contract, NDA)")
parties = st.text_area("Parties Involved")
terms = st.text_area("Terms & Conditions (Use semicolons for bullet points)")
dates = st.text_input("Effective Date")

if "generated_text" not in st.session_state:
    st.session_state.generated_text = ""
if "show_edit" not in st.session_state:
    st.session_state.show_edit = False

# ---- Generate ----
if st.button("Generate Document"):
    if not all([document_type, parties, terms, dates]):
        st.warning("Please fill in all fields before generating.")
    else:
        with st.spinner("Generating your document..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json={
                        "document_type": document_type,
                        "parties": parties,
                        "terms": terms,
                        "dates": dates,
                    },
                    timeout=60,
                )
                response.raise_for_status()
                st.session_state.generated_text = sanitize_text(
                    response.json()["document"]
                )
                st.success("Document Generated Successfully!")
            except requests.exceptions.RequestException as exc:
                st.error(f"Could not reach the backend: {exc}")

# ---- Preview + Edit + Download ----
if st.session_state.generated_text:
    styled_html = format_html_preview(st.session_state.generated_text)
    st.markdown(
        f"<div style='background:#111318; padding:20px; border-radius:8px; "
        f"max-height:400px; overflow-y:auto;'>{styled_html}</div>",
        unsafe_allow_html=True,
    )

    if st.button("Click to Edit Document"):
        st.session_state.show_edit = True

    if st.session_state.show_edit:
        edited_text = st.text_area(
            "Edit Document Below:",
            st.session_state.generated_text,
            height=300,
        )
        st.session_state.generated_text = edited_text

    file_stub = document_type.replace(" ", "_").lower() or "legal_document"

    st.download_button(
        "📄 Download as .TXT",
        data=st.session_state.generated_text,
        file_name=f"{file_stub}.txt",
        mime="text/plain",
    )
    st.download_button(
        "📝 Download as .DOCX",
        data=format_docx(st.session_state.generated_text, document_type, terms),
        file_name=f"{file_stub}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    st.download_button(
        "📕 Download as .PDF",
        data=format_pdf(st.session_state.generated_text, document_type, terms),
        file_name=f"{file_stub}.pdf",
        mime="application/pdf",
    )
else:
    st.info("Click 'Generate Document' to start")
