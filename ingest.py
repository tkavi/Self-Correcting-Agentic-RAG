# ingest.py
import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# loading env var
load_dotenv()

# default values set in-line
embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
vector_db_path = os.getenv("VECTOR_DB_PATH", "./chroma_db")

# test data path
pdf_path = "./test_data/CMS-0057-F.pdf"

if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"Could not find the file at {pdf_path}.")

# 1. loading test pdf
loader = PyPDFLoader(pdf_path)
docs = loader.load()
print(f"Successfully loaded {len(docs)} pages from PDF.")

# 2. chunking the data
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    length_function=len
)

split_docs = text_splitter.split_documents(docs)
print(f"Created {len(split_docs)} distinct text chunks.")

# 3. embedding and storing in vector db
embedding = OllamaEmbeddings(model=embedding_model)

db = Chroma.from_documents(
    documents=split_docs,
    embedding=embedding,
    persist_directory=vector_db_path,
    collection_name="rag_collection"
)

print(f"Vector database stored permanently at: {vector_db_path}")