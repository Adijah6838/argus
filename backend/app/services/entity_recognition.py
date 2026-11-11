import re
from typing import List, Dict

class EntityExtractor:
    @staticmethod
    def extract_entities(text: str) -> List[Dict]:
        """Extracts entities using deterministic Regex rules."""
        entities = []

        # 1. Emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        for match in re.findall(email_pattern, text):
            entities.append({"type": "email", "value": match, "confidence": 1.0})

        # 2. Dates (e.g., 10 November 2026, 2026-11-10, 11/10/2026)
        date_patterns = [
            r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b',
            r'\b\d{1,2}/\d{1,2}/\d{4}\b'
        ]
        for pattern in date_patterns:
            for match in re.findall(pattern, text, re.IGNORECASE):
                entities.append({"type": "date", "value": match, "confidence": 1.0})

        # 3. Monetary Amounts (e.g., $4,500, $15000.00, €500)
        amount_pattern = r'[\$€£]\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
        for match in re.findall(amount_pattern, text):
            entities.append({"type": "amount", "value": match, "confidence": 1.0})

        # 4. Organization Names (Mock rule: looks for "Company: X" or "Organization: X")
        org_pattern = r'(?:Company|Organization|Org):\s*([A-Za-z0-9\s]+)'
        for match in re.findall(org_pattern, text, re.IGNORECASE):
            entities.append({"type": "organization", "value": match.strip(), "confidence": 0.9})

        return entities