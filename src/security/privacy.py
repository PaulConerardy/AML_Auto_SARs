import spacy
import re

class PrivacyGuard:
    def __init__(self):
        # Load a small English model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # If not found, we'll need to download it or use a simpler method
            print("Spacy model 'en_core_web_sm' not found. Please run 'python -m spacy download en_core_web_sm'")
            self.nlp = None

    def anonymize(self, text: str) -> str:
        if not text:
            return text
            
        # 1. Regex for common patterns (Account numbers, etc.)
        # Basic pattern for account numbers like TX12345 or 10-digit numbers
        text = re.sub(r'\b[A-Z]{2}\d{5}\b', "[ID]", text)
        text = re.sub(r'\b\d{10,}\b', "[ACCOUNT]", text)
        
        # 2. Spacy NER for Names, Organizations, Locations
        if self.nlp:
            doc = self.nlp(text)
            for ent in reversed(doc.ents):
                if ent.label_ in ["PERSON", "ORG", "GPE"]:
                    text = text[:ent.start_char] + f"[{ent.label_}]" + text[ent.end_char:]
                    
        return text

if __name__ == "__main__":
    guard = PrivacyGuard()
    sample = "John Doe from Acme Corp (Account: 1234567890) made a transaction TX00001 in New York."
    print(f"Original: {sample}")
    print(f"Anonymized: {guard.anonymize(sample)}")
