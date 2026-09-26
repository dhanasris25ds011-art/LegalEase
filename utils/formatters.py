"""
utils/formatters.py

Core formatting utilities that turn raw Gemini text into
polished, branded output: .docx, .pdf, and an HTML preview.
"""
import io
import os
import re

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF

from config import WEB_LOGO_PATH

FOOTER_TEXT = "LegalEase Inc. | contact@legalease.com | All Rights Reserved."


def sanitize_text(text: str) -> str:
    """Removes special characters and typographic quotes for clean formatting."""
    if not text:
        return ""
    replacements = {
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-",
        "\u2026": "...",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    # Strip control characters but keep normal whitespace/newlines
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E]", "", text)
    return text.strip()


def _split_terms(terms_raw: str):
    """Splits a semicolon-separated terms string into a clean list."""
    return [t.strip() for t in terms_raw.split(";") if t.strip()]


# --------------------------------------------------------------------------
# DOCX
# --------------------------------------------------------------------------
def format_docx(text: str, doc_type: str, terms: str = "") -> bytes:
    """
    Builds a formatted Word document:
    - Logo on the first page
    - Times New Roman body font
    - Terms rendered as a table (if provided)
    - Footer text on the document
    """
    text = sanitize_text(text)
    document = Document()

    # Base style
    style = document.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)

    # Logo (centered), if it exists
    if os.path.exists(WEB_LOGO_PATH):
        logo_paragraph = document.add_paragraph()
        logo_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = logo_paragraph.add_run()
        run.add_picture(WEB_LOGO_PATH, width=Inches(1.5))

    # Title
    title = document.add_heading(doc_type, level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Body content (skip the title if Gemini repeated it as a heading)
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("##"):
            document.add_heading(line.lstrip("#").strip(), level=2)
        else:
            document.add_paragraph(line)

    # Terms table
    term_list = _split_terms(terms)
    if term_list:
        document.add_heading("Summary of Key Terms", level=2)
        table = document.add_table(rows=1, cols=2)
        table.style = "Light Grid Accent 1"
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "#"
        hdr_cells[1].text = "Term"
        for idx, term in enumerate(term_list, start=1):
            row_cells = table.add_row().cells
            row_cells[0].text = str(idx)
            row_cells[1].text = term

    # Footer
    section = document.sections[0]
    footer = section.footer
    footer_paragraph = footer.paragraphs[0]
    footer_paragraph.text = FOOTER_TEXT
    footer_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    buffer = io.BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


# --------------------------------------------------------------------------
# PDF
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# PDF
# --------------------------------------------------------------------------
def _break_long_tokens(text: str, max_len: int = 60) -> str:
    """Inserts a space into very long unbroken tokens (e.g. signature lines) so PDF rendering never fails."""
    def break_word(match):
        word = match.group(0)
        return " ".join(word[i:i + max_len] for i in range(0, len(word), max_len))
    return re.sub(r"\S{" + str(max_len + 1) + r",}", break_word, text)


class _LegalPDF(FPDF):
    title_text = ""

    def header(self):
        if os.path.exists(WEB_LOGO_PATH):
            logo_width = 25
            x = (self.w - logo_width) / 2
            self.image(WEB_LOGO_PATH, x=x, y=8, w=logo_width)
            self.set_y(8 + 22)
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, self.title_text, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, FOOTER_TEXT, align="C")


def format_pdf(text: str, doc_type: str, terms: str = "") -> bytes:
    """
    Builds a branded PDF with a centered logo header, bold section
    headings, bullet-style terms, and a footer on every page.
    """
    text = _break_long_tokens(sanitize_text(text))
    doc_type = sanitize_text(doc_type)

    pdf = _LegalPDF()
    pdf.title_text = doc_type
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    def write(line, height=7):
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, height, line, wrapmode="CHAR", new_x="LMARGIN", new_y="NEXT")

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue
        if line.startswith("##"):
            pdf.set_font("Helvetica", "B", 12)
            write(line.lstrip("#").strip(), 8)
            pdf.set_font("Helvetica", size=11)
        else:
            write(line)

    term_list = _split_terms(sanitize_text(terms))
    if term_list:
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 12)
        write("Summary of Key Terms", 8)
        pdf.set_font("Helvetica", size=11)
        for term in term_list:
            write(f"- {term}")

    return bytes(pdf.output())


# --------------------------------------------------------------------------
# HTML preview
# --------------------------------------------------------------------------
def format_html_preview(text: str) -> str:
    """Converts raw text into a stylized HTML block for Streamlit preview."""
    text = sanitize_text(text)
    html_lines = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            html_lines.append("<br>")
        elif line.startswith("##"):
            html_lines.append(f"<h3 style='color:#e8e8e8;'>{line.lstrip('#').strip()}</h3>")
        else:
            html_lines.append(f"<p style='color:#d0d0d0; line-height:1.5;'>{line}</p>")
    return "\n".join(html_lines)
