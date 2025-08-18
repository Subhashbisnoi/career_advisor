import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import pdfplumber
import io

from PyPDF2 import PdfReader
# Load environment variables
load_dotenv()

# Configure OpenAI client with environment variables
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")


# Shared LLM instances
generator_llm = ChatOpenAI(
    model="gpt-4o-mini"
)
feedback_llm = ChatOpenAI(
    model="gpt-4o-mini"
)

def extract_resume_text(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF bytes using multiple fallback methods.
    
    Args:
        pdf_bytes: The PDF file contents as bytes
        
    Returns:
        str: Extracted text from the PDF, or empty string if extraction failed
    """
    if not pdf_bytes:
        print("Error: No PDF data provided")
        return ""
        
    if not isinstance(pdf_bytes, bytes):
        print("Error: Expected bytes input")
        return ""
        
    if len(pdf_bytes) < 4:  # Minimum size for a valid PDF header
        print("Error: PDF file is too small to be valid")
        return ""
        
    # Check for PDF header (first 4 bytes should be '%PDF')
    if not pdf_bytes.startswith(b'%PDF'):
        print("Error: File does not appear to be a valid PDF (missing PDF header)")
        return ""
    
    text = ""
    
    # First attempt: pdfplumber (better for complex layouts)
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                try:
                    page_text = page.extract_text(x_tolerance=1, y_tolerance=1) or ""
                    if page_text.strip():
                        text += f"\n--- Page {i+1} ---\n{page_text}\n"
                except Exception as page_error:
                    print(f"Error extracting text from page {i+1}: {str(page_error)}")
                    continue
                    
        if text.strip():
            return text.strip()
            
    except Exception as e:
        print(f"pdfplumber failed: {str(e)}")
    
    # Second attempt: PyPDF2 (more lenient with some PDFs)
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text += f"\n--- Page {i+1} ---\n{page_text}\n"
            except Exception as page_error:
                print(f"PyPDF2 error on page {i+1}: {str(page_error)}")
                continue
                
        if text.strip():
            return text.strip()
            
    except Exception as e:
        print(f"PyPDF2 failed: {str(e)}")
    
    print("All text extraction methods failed")
    return ""