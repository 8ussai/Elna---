from langchain_community.document_loaders import (PyMuPDFLoader, UnstructuredPowerPointLoader)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from backend.backendConfig import CHROMA_DB_DIR

embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,   
    chunk_overlap=150, 
    length_function=len,
)

def get_document_loader(file_path: str):
    file_extension = file_path.split('.')[-1].lower()
    
    if file_extension == 'pdf':
        return PyMuPDFLoader(file_path)
    elif file_extension in ['pptx', 'ppt']:
        return UnstructuredPowerPointLoader(file_path)
    else:
        return None 

def index_course_material(file_path: str, material_id: int, course_id: int):
    try:
        loader = get_document_loader(file_path)
        
        if loader is None:
            print(f"[RAG] Skipping AI indexing for {file_path}. Format not supported by AI.")
            return False

        print(f"[RAG] Starting AI indexing for material ID: {material_id} (Format: {file_path.split('.')[-1]})...")

        documents = loader.load()

        for doc in documents:
            doc.metadata["material_id"] = material_id
            doc.metadata["course_id"] = course_id

        chunks = text_splitter.split_documents(documents)
        print(f"[RAG] File split into {len(chunks)} chunks.")

        Chroma.from_documents(
            documents=chunks,
            embedding=embeddings_model,
            persist_directory=CHROMA_DB_DIR
        )
        
        print(f"[RAG] Successfully indexed material {material_id} into Vector DB")
        return True

    except Exception as e:
        print(f"[RAG] Error indexing material {material_id}: {str(e)}")
        return False