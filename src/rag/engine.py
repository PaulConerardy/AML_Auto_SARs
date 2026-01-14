import os
from dotenv import load_dotenv
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.security.privacy import PrivacyGuard

load_dotenv()

class SARREngine:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db = chromadb.PersistentClient(path=db_path)
        self.chroma_collection = self.db.get_or_create_collection("aml_sar_collection")
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        
        # Initialize Privacy Guard
        self.privacy_guard = PrivacyGuard()
        
        # Load index
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        # Note: We need to pass the same embed_model used in indexing if we reload it
        # For now, we assume it's set in Settings or we use the default
        try:
            self.index = load_index_from_storage(storage_context)
        except:
            print("Warning: Could not load index. Ensure indexing is complete.")
            self.index = None

    def get_llm(self):
        model_name = os.getenv("MODEL_NAME", "gpt-4o")
        if "gpt" in model_name:
            return ChatOpenAI(model=model_name)
        elif "claude" in model_name:
            return ChatAnthropic(model=model_name)
        return ChatOpenAI(model="gpt-4o")

    def generate_sar(self, customer_id: str):
        if not self.index:
            return "Error: Vector index not initialized."
            
        # 1. Retrieval
        query = f"Retrieve all transactional evidence and KYC details for customer {customer_id} including any adverse media."
        query_engine = self.index.as_query_engine()
        evidence_nodes = query_engine.query(query)
        evidence_text = str(evidence_nodes)
        
        # 2. Anonymization (Safety First)
        safe_evidence = self.privacy_guard.anonymize(evidence_text)
        
        # 3. Generation (Prompting)
        prompt = ChatPromptTemplate.from_template("""
        You are an AML Compliance Officer drafting a Suspicious Activity Report (SAR).
        Follow the "Who, What, When, Where, Why" structure.
        
        Context/Evidence:
        {evidence}
        
        Instructions:
        - Summarize the suspicious activity.
        - Mention specific amounts and dates if available in the context.
        - Ensure the narrative is professional and regulatory-compliant.
        - Do not reveal any PII (use placeholders if needed).
        
        Drafting SAR Narrative:
        """)
        
        chain = prompt | self.get_llm() | StrOutputParser()
        
        draft = chain.invoke({"evidence": safe_evidence})
        return draft

if __name__ == "__main__":
    engine = SARREngine(db_path="c:/Users/paulc/Documents/Projets/AML SARs/chroma_db")
    # For testing, we might need dummy index if indexing failed
    print("SAR Engine initialized.")
