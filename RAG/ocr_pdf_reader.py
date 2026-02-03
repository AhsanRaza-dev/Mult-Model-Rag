"""
Custom PDF reader with OCR support for image-based PDFs.
"""
import os
from pathlib import Path
from typing import Dict, List, Optional
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document

# Set Tesseract path (common Windows installation paths)
TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\UsEr\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
]

for path in TESSERACT_PATHS:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        break

class OCRPDFReader(BaseReader):
    """PDF reader with OCR support for scanned/image-based PDFs."""
    
    def __init__(self, use_ocr: bool = True):
        """
        Args:
            use_ocr: Whether to use OCR for text extraction
        """
        self.use_ocr = use_ocr
    
    def load_data(
        self,
        file_path: Path,
        extra_info: Optional[Dict] = None,
    ) -> List[Document]:
        """Load data from PDF file with OCR support."""
        
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
        
        documents = []
        
        try:
            # Open PDF with PyMuPDF
            pdf_doc = fitz.open(file_path)
            
            print(f"Processing {len(pdf_doc)} pages with OCR...")
            
            for page_num in range(len(pdf_doc)):
                page = pdf_doc[page_num]
                
                # Try to extract text normally first
                text = page.get_text()
                
                # If no text found and OCR is enabled, use OCR
                if len(text.strip()) == 0 and self.use_ocr:
                    text = self._ocr_page(page)
                
                # Create metadata
                metadata = {
                    "page_label": str(page_num + 1),
                    "file_name": file_path.name,
                    "file_path": str(file_path),
                    "file_type": "application/pdf",
                    "file_size": file_path.stat().st_size,
                }
                
                if extra_info:
                    metadata.update(extra_info)
                
                # Create document
                if text.strip():  # Only add if we got some text
                    documents.append(Document(text=text, metadata=metadata))
                
                # Progress indicator
                if (page_num + 1) % 10 == 0:
                    print(f"  Processed {page_num + 1}/{len(pdf_doc)} pages...")
            
            pdf_doc.close()
            print(f"Completed! Extracted text from {len(documents)} pages.")
            
        except Exception as e:
            print(f"Error processing PDF: {e}")
            raise
        
        return documents
    
    def _ocr_page(self, page) -> str:
        """Extract text from a PDF page using OCR."""
        try:
            # Convert page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Run OCR
            text = pytesseract.image_to_string(img)
            
            return text
            
        except Exception as e:
            print(f"OCR error: {e}")
            return ""
