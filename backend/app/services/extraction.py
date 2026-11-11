import fitz  # PyMuPDF
import docx
import pytesseract
from PIL import Image
import os

class TextExtractor:
    @staticmethod
    def extract_text(file_path: str, mime_type: str) -> str:
        """Extracts text based on the file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == ".pdf":
                return TextExtractor._extract_pdf(file_path)
            elif ext == ".docx":
                return TextExtractor._extract_docx(file_path)
            elif ext == ".txt":
                return TextExtractor._extract_txt(file_path)
            elif ext in [".png", ".jpg", ".jpeg"]:
                return TextExtractor._extract_image(file_path)
            else:
                raise ValueError(f"Unsupported file type: {ext}")
        except Exception as e:
            raise RuntimeError(f"Extraction failed: {str(e)}")

    @staticmethod
    def _extract_pdf(file_path: str) -> str:
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text.strip()

    @staticmethod
    def _extract_docx(file_path: str) -> str:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs]).strip()

    @staticmethod
    def _extract_txt(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()

    @staticmethod
    def _extract_image(file_path: str) -> str:
        # Use Tesseract OCR for images
        img = Image.open(file_path)
        return pytesseract.image_to_string(img).strip()