from fpdf import FPDF
import json
from typing import Dict, Any

class ReportGenerator:
    @staticmethod
    def generate_json_report(investigation_data: Dict[str, Any]) -> str:
        return json.dumps(investigation_data, indent=4, default=str)

    @staticmethod
    def generate_pdf_report(investigation_data: Dict[str, Any]) -> bytes:
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "ARGUS Investigation Report", ln=True, align="C")
        pdf.ln(10)

        # Investigation Details
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Investigation: {investigation_data['title']}", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, f"Status: {investigation_data['status']} | Created: {investigation_data['created_at']}", ln=True)
        pdf.multi_cell(0, 10, f"Description: {investigation_data.get('description', 'N/A')}")
        pdf.ln(5)

        # Notes
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Investigator Notes:", ln=True)
        pdf.set_font("Arial", "", 10)
        if investigation_data['notes']:
            for note in investigation_data['notes']:
                pdf.multi_cell(0, 10, f"- {note['content']} (Added: {note['created_at']})")
        else:
            pdf.cell(0, 10, "No notes added.", ln=True)
        pdf.ln(5)

        # Attached Documents
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Attached Documents & Entities:", ln=True)
        pdf.set_font("Arial", "", 10)
        
        if investigation_data['documents']:
            for doc in investigation_data['documents']:
                pdf.set_font("Arial", "B", 10)
                pdf.cell(0, 10, f"Document: {doc['filename']}", ln=True)
                pdf.set_font("Arial", "", 10)
                for entity in doc['entities']:
                    pdf.cell(0, 8, f"  - {entity['type'].capitalize()}: {entity['value']}", ln=True)
        else:
            pdf.cell(0, 10, "No documents attached.", ln=True)

        return bytes(pdf.output())