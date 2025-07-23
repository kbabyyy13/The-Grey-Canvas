#!/usr/bin/env python3
import sys

import pdfplumber


def extract_text_from_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""

            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

            return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None


if __name__ == "__main__":
    pdf_path = "attached_assets/FirstBlogPost_1751629384607.pdf"
    extracted_text = extract_text_from_pdf(pdf_path)

    if extracted_text:
        print("=== EXTRACTED TEXT ===")
        print(extracted_text)
        print("=== END EXTRACTED TEXT ===")
    else:
        print("Failed to extract text from PDF")
