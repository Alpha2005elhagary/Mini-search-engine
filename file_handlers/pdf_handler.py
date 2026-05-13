# pdf_handler.py - Extract text from PDF
from PyPDF2 import PdfReader

def read_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except:
        return ""








# # pdf_handler.py - Optimized for PDF with tables
# import re

# try:
#     from PyPDF2 import PdfReader
#     HAS_PYPDF2 = True
# except ImportError:
#     try:
#         import pypdf
#         HAS_PYPDF2 = True
#     except ImportError:
#         HAS_PYPDF2 = False
#         print("⚠️ PyPDF2 not installed. PDF support limited.")

# def read_pdf(file_path):
#     if not HAS_PYPDF2:
#         return extract_pdf_fallback(file_path)
    
#     try:
#         reader = PdfReader(file_path)
#         text = []
        
#         for page in reader.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 # Clean PDF artifacts
#                 page_text = clean_pdf_text(page_text)
#                 text.append(page_text)
        
#         return ' '.join(text)
#     except Exception as e:
#         print(f"PDF error: {e}")
#         return ""

# def clean_pdf_text(text):
#     """Clean PDF extraction artifacts"""
#     # Remove page numbers and headers
#     lines = text.split('\n')
#     cleaned = []
    
#     for line in lines:
#         # Skip page numbers and chapter markers
#         if re.match(r'^\s*\d+\s*$', line):  # Just a number
#             continue
#         if re.match(r'^===== Page \d+ =====$', line):  # Page markers
#             continue
#         if re.match(r'^CHAPTER \d+', line):  # Chapter headers
#             continue
#         if len(line.strip()) < 2:
#             continue
        
#         # Clean the line
#         line = re.sub(r'[^\w\s\.\-]', ' ', line)
#         cleaned.append(line)
    
#     return ' '.join(cleaned)

# def extract_pdf_fallback(file_path):
#     """Fallback for when PDF library is not available"""
#     try:
#         # Try to read as text (some PDFs have embedded text)
#         with open(file_path, 'rb') as f:
#             content = f.read().decode('utf-8', errors='ignore')
#             return clean_pdf_text(content)
#     except:
#         return "PDF content - install PyPDF2 for full extraction"