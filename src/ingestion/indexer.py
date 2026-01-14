import os
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from llama_index.core.node_parser import LangchainNodeParser

from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding

class AMLIndexer:
    def __init__(self, data_dir: str, db_path: str):
        self.data_dir = data_dir
        self.db_path = db_path
        # Use local embeddings to avoid API key requirements for dev
        Settings.embed_model = "local:BAAI/bge-small-en-v1.5"
        
        self.db = chromadb.PersistentClient(path=db_path)
        self.chroma_collection = self.db.get_or_create_collection("aml_sar_collection")
        
    def load_and_index(self):
        # 1. Load documents
        # SimpleDirectoryReader handles CSV, TXT, PDF out of the box in LlamaIndex
        reader = SimpleDirectoryReader(input_dir=self.data_dir)
        documents = reader.load_data()
        
        # 2. Setup Recursive Chunking via LangChain integration
        parser = LangchainNodeParser(
            RecursiveCharacterTextSplitter(
                chunk_size=1024,
                chunk_overlap=128
            )
        )
        nodes = parser.get_nodes_from_documents(documents)
        
        # 3. Setup Vector Store
        vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # 4. Create Index
        index = VectorStoreIndex(
            nodes, 
            storage_context=storage_context,
            show_progress=True
        )
        
        return index

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    indexer = AMLIndexer(
        data_dir="c:/Users/paulc/Documents/Projets/AML SARs/data",
        db_path="c:/Users/paulc/Documents/Projets/AML SARs/chroma_db"
    )
    indexer.load_and_index()
    print("Indexing complete.")
