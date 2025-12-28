import PyPDF2
from docx import Document
import io
from typing import List, Dict
import aiofiles
import os

async def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

async def extract_text_from_docx(file_path: str) -> str:
    """Extract text from Word document"""
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
        return ""

async def process_document(file_path: str, filename: str) -> Dict[str, str]:
    """Process document and extract text"""
    file_ext = os.path.splitext(filename)[1].lower()
    
    if file_ext == '.pdf':
        text = await extract_text_from_pdf(file_path)
    elif file_ext in ['.doc', '.docx']:
        text = await extract_text_from_docx(file_path)
    else:
        text = ""
    
    return {
        "filename": filename,
        "text": text,
        "file_type": file_ext
    }

