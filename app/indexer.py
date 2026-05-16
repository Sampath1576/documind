"""Document indexing pipeline - Load, chunk, embed, and store documents"""

import logging
import time
from pathlib import Path
from typing import List, Dict
import uuid

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

import mlflow

from .config import settings

logger = logging.getLogger(__name__)


class DocumentIndexer:
    """Handles document loading, chunking, embedding, and storage"""

    def __init__(self):
        """Initialize indexer with embeddings and vector store"""
        logger.info("Initializing DocumentIndexer...")
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL,
            model_kwargs={"device": settings.EMBEDDING_DEVICE}
        )
        
        # Initialize vector store
        self.vector_store = Chroma(
            persist_directory=settings.CHROMA_DB_PATH,
            embedding_function=self.embeddings
        )
        
        # Text splitter configuration
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )
        
        logger.info("DocumentIndexer initialized successfully")

    def load_document(self, file_path: str) -> List[Dict]:
        """Load document and return list of documents"""
        file_path = Path(file_path)
        file_extension = file_path.suffix.lower().strip(".")
        
        logger.info(f"Loading document: {file_path}")
        
        try:
            if file_extension == "pdf":
                loader = PyPDFLoader(str(file_path))
                documents = loader.load()
            elif file_extension == "txt":
                loader = TextLoader(str(file_path))
                documents = loader.load()
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            logger.info(f"Loaded {len(documents)} documents from {file_path}")
            return documents
        
        except Exception as e:
            logger.error(f"Error loading document: {str(e)}")
            raise

    def chunk_documents(self, documents: List) -> List:
        """Split documents into chunks"""
        logger.info(f"Chunking {len(documents)} documents...")
        
        chunks = self.text_splitter.split_documents(documents)
        
        # Filter out very small chunks
        chunks = [c for c in chunks if len(c.page_content) >= settings.MIN_CHUNK_SIZE]
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks

    def index_documents(
        self,
        file_path: str,
        document_name: str = None
    ) -> Dict:
        """Complete indexing pipeline: load → chunk → embed → store"""
        
        document_id = str(uuid.uuid4())
        if not document_name:
            document_name = Path(file_path).name
        
        logger.info(f"Starting indexing for: {document_name} (ID: {document_id})")
        
        with mlflow.start_run():
            start_time = time.time()
            
            try:
                # Step 1: Load document
                documents = self.load_document(file_path)
                
                # Step 2: Chunk documents
                chunks = self.chunk_documents(documents)
                
                # Step 3: Add metadata
                for chunk in chunks:
                    chunk.metadata["document_id"] = document_id
                    chunk.metadata["document_name"] = document_name
                
                # Step 4: Embed and store in ChromaDB
                embedding_start = time.time()
                
                ids = [f"{document_id}_{i}" for i in range(len(chunks))]
                texts = [chunk.page_content for chunk in chunks]
                metadatas = [chunk.metadata for chunk in chunks]
                
                self.vector_store.add_documents(
                    documents=chunks,
                    ids=ids
                )
                
                embedding_time = time.time() - embedding_start
                total_time = time.time() - start_time
                
                # Log metrics to MLflow
                mlflow.log_params({
                    "document_name": document_name,
                    "embedding_model": settings.EMBEDDING_MODEL,
                    "chunk_size": settings.CHUNK_SIZE,
                    "chunk_overlap": settings.CHUNK_OVERLAP,
                })
                
                mlflow.log_metrics({
                    "num_chunks": len(chunks),
                    "embedding_time_s": embedding_time,
                    "total_indexing_time_s": total_time,
                })
                
                result = {
                    "document_id": document_id,
                    "filename": document_name,
                    "chunks_created": len(chunks),
                    "embedding_time_s": round(embedding_time, 2),
                    "total_time_s": round(total_time, 2),
                    "message": "Document indexed successfully"
                }
                
                logger.info(f"Indexing completed: {result}")
                return result
            
            except Exception as e:
                logger.error(f"Error during indexing: {str(e)}")
                mlflow.log_param("error", str(e))
                raise

    def delete_document(self, document_id: str) -> Dict:
        """Delete all chunks associated with a document"""
        logger.info(f"Deleting document: {document_id}")
        
        try:
            # Get all documents with this ID
            results = self.vector_store.get(
                where={"document_id": {"$eq": document_id}}
            )
            
            if results["ids"]:
                self.vector_store.delete(ids=results["ids"])
                logger.info(f"Deleted {len(results['ids'])} chunks for document {document_id}")
            
            return {
                "message": f"Document {document_id} deleted successfully",
                "chunks_deleted": len(results["ids"]) if results["ids"] else 0
            }
        
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise

    def list_documents(self) -> List[Dict]:
        """List all indexed documents"""
        try:
            all_docs = self.vector_store.get()
            
            # Group by document_id
            doc_map = {}
            for metadata in all_docs.get("metadatas", []):
                doc_id = metadata.get("document_id")
                if doc_id not in doc_map:
                    doc_map[doc_id] = metadata
            
            return list(doc_map.values())
        
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            raise