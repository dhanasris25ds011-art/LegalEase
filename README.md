LegalEase — AI Legal Document Generator
Folder structure
LegalEase/
├── ai_core/
│   ├── __init__.py
│   └── gemini_generator.py     # Gemini 1.5 Pro wrapper — builds prompt, calls API
├── legalEaseAPI/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entrypoint
│   └── routes.py                # /generate POST endpoint
├── frontend/
│   ├── app.py                  # Streamlit UI
│   └── utils.py                # sanitize_text, format_docx, format_pdf, format_html_preview
├── Image/
│   └── Logo.png                # put your logo here (used in UI + docx/pdf export)
├── requirements.txt
├── .env.example                # rename to .env and add your key
└── README.md
Setup
Open the LegalEase folder in VS Code.
Create a virtual environment:
python -m venv venv
venv\Scripts\activate        # Windows
Install dependencies:
pip install -r requirements.txt
Rename .env.example to .env and paste your Gemini API key:
GEMINI_API_KEY=your_actual_key_here
Get a key from https://aistudio.google.com/app/apikey
Add your own logo as Image/Logo.png (any PNG works; app still runs without it).
Run (two terminals, both from the LegalEase root folder)
Terminal 1 — backend:

uvicorn legalEaseAPI.main:app --reload
Runs on http://127.0.0.1:8000

Terminal 2 — frontend:

streamlit run frontend/app.py
Opens at http://localhost:8501

How it flows
User fills Document Type, Parties, Terms, Effective Date in Streamlit.
app.py POSTs the form as JSON to http://localhost:8000/generate.
FastAPI's routes.py validates it with the DocumentRequest Pydantic model and calls GeminiDocumentGenerator.generate_document(...).
gemini_generator.py builds a structured prompt and calls Gemini 1.5 Pro's generate_content().
The generated text comes back to Streamlit, gets sanitized, previewed in a dark HTML card, and can be edited inline.
Download buttons convert the text to .txt / .docx (via python-docx) / .pdf (via fpdf2), both branded with your logo and a footer.
Notes
Both servers must be running for "Generate Document" to work (Streamlit talks to FastAPI over localhost).
sanitize_text strips non-ASCII characters — needed because fpdf's classic font encoding is latin-1 only.
Semicolon-separated lines in Terms & Conditions auto-render as a table (docx) / bullet list (pdf).
