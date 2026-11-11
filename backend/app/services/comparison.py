import re

class DocumentComparer:
    @staticmethod
    def parse_amount(val: str) -> float:
        """Converts '$4,500' to 4500.0"""
        clean = re.sub(r'[^\d.]', '', val)
        try:
            return float(clean)
        except ValueError:
            return 0.0

    @staticmethod
    def compare(doc_a_entities: dict, doc_b_entities: dict) -> dict:
        """Compares entities from two documents."""
        discrepancies = []
        
        # 1. Compare Amounts
        amounts_a = doc_a_entities.get("amount", [])
        amounts_b = doc_b_entities.get("amount", [])
        
        if amounts_a and amounts_b:
            val_a = DocumentComparer.parse_amount(amounts_a[0])
            val_b = DocumentComparer.parse_amount(amounts_b[0])
            
            if val_a != val_b:
                discrepancies.append({
                    "field": "Monetary Amount",
                    "doc_a_value": amounts_a[0],
                    "doc_b_value": amounts_b[0],
                    "difference": abs(val_a - val_b),
                    "note": "The amounts do not match."
                })

        # 2. Compare Dates
        dates_a = doc_a_entities.get("date", [])
        dates_b = doc_b_entities.get("date", [])
        
        if dates_a and dates_b and dates_a[0] != dates_b[0]:
            discrepancies.append({
                "field": "Date",
                "doc_a_value": dates_a[0],
                "doc_b_value": dates_b[0],
                "difference": "N/A",
                "note": "The dates do not match."
            })

        # Calculate a basic similarity score (0 to 100)
        score = 100
        if discrepancies:
            score -= (len(discrepancies) * 25) # Deduct 25 points per discrepancy
        score = max(0, score)

        return {
            "discrepancies_found": len(discrepancies),
            "similarity_score": score,
            "details": discrepancies
        }