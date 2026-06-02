import os
from pdf2image import convert_from_path
import pytesseract
from pdfminer.high_level import extract_text
from fpdf import FPDF
from googletrans import Translator
from deep_translator import GoogleTranslator
from googletrans import Translator

# Set up Tesseract OCR (if not in PATH, set full path here)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Ensure a Unicode font is available
FONT_PATH = "NotoSansTamil-Regular.ttf"
# FONT_PATH = "Kalyani Regular.otf"

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file (if selectable)."""
    return extract_text(pdf_path)  # Works for selectable text PDFs

def extract_text_from_images(pdf_path):
    """Extract text from PDF images using OCR (if scanned PDF)."""
    images = convert_from_path(pdf_path)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img, lang="eng+tam")  # Add more languages if needed
    return text

def translate_text(text, target_lang):
    translator = Translator()
    max_length = 5000  # Google Translate API limit
    translated_text = ""

    for i in range(0, len(text), max_length):
        chunk = text[i:i+max_length]  # Take 5000-character chunks
        translated_text += translator.translate(chunk, dest=target_lang).text + " "

    return translated_text.strip()

def create_pdf(output_pdf, text):
    """Generate a new PDF with the extracted (and translated) text."""
    pdf = FPDF()
    pdf.add_page()
    
    # Add a Unicode font
    pdf.add_font("NotoSansTamil", "", FONT_PATH, uni=True)
    pdf.set_font("NotoSansTamil", "", 12)

    # Add translated text
    pdf.multi_cell(0, 10, text)

    # Save the output PDF
    pdf.output(output_pdf)
    print(f"Translated PDF saved as: {output_pdf}")

def convert_and_translate_pdf(input_pdf, output_pdf, target_lang="ta"):
    """Extract, translate, and create a translated PDF."""
    text = extract_text_from_pdf(input_pdf)
    
    if not text.strip():  # If no selectable text, use OCR
        print("No selectable text found, using OCR...")
        text = extract_text_from_images(input_pdf)
    
    translated_text = translate_text(text, target_lang)
    create_pdf(output_pdf, translated_text)

# Run the conversion process
convert_and_translate_pdf("5.pdf", "translated_output5.pdf", "ta")  # Change "ta" to your language code
