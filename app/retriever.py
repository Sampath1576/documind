"""Document retrieval pipeline - Semantic search in vector store"""

import logging
import time
from typing import List, Dict, Tuple

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

import mlflow

from .config import settings

logger = logging.getLogger(__name__)


class DocumentRetriever:
    """Handles semantic search and document retrieval"""

    def __init__(self):
        """Initialize retriever with embeddings and vector store"""
        logger.info("Initializing DocumentRetriever...")
        
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
        
        logger.info("DocumentRetriever initialized successfully")

    def retrieve(
        self,
        query: str,
        document_id: str = None,
        top_k: int = None
    ) -> Tuple[List[str], List[float]]:
        """
        Retrieve most relevant chunks for a query
        
        Args:
            query: User's question
            document_id: Filter to specific document (optional)
            top_k: Number of chunks to retrieve
        
        Returns:
            Tuple of (chunks, similarity_scores)
        """
        
        if not top_k:
            top_k = settings.TOP_K
        
        logger.info(f"Retrieving {top_k} chunks for query: {query[:100]}...")
        
        embedding_start = time.time()
        
        try:
            # Search for similar chunks
            if document_id:
                where_filter = {"document_id": {"$eq": document_id}}
                results = self.vector_store.similarity_search_with_scores(
                    query,
                    k=top_k,
                    where=where_filter
                )
            else:
                results = self.vector_store.similarity_search_with_scores(
                    query,
                    k=top_k
                )
            
            embedding_time = time.time() - embedding_start
            
            # Extract chunks and scores
            chunks = [doc.page_content for doc, score in results]
            scores = [float(1 - score) for doc, score in results]  # Convert distance to similarity
            
            logger.info(
                f"Retrieved {len(chunks)} chunks, "
                f"top similarity: {scores[0]:.4f}" if scores else "No results"
            )
            
            # Log metrics
            mlflow.log_metric("retrieval_embedding_time_ms", embedding_time * 1000)
            if scores:
                mlflow.log_metric("top_similarity_score", scores[0])
                mlflow.log_metric("mean_similarity_score", sum(scores) / len(scores))
            
            return chunks, scores
        
        except Exception as e:
            logger.error(f"Error during retrieval: {str(e)}")
            raise

    def retrieve_with_metadata(
        self,
        query: str,
        document_id: str = None,
        top_k: int = None
    ) -> List[Dict]:
        """Retrieve chunks with metadata"""
        
        if not top_k:
            top_k = settings.TOP_K
        
        try:
            # Search for similar chunks
            if document_id:
                where_filter = {"document_id": {"$eq": document_id}}
                results = self.vector_store.similarity_search_with_scores(
                    query,
                    k=top_k,
                    where=where_filter
                )
            else:
                results = self.vector_store.similarity_search_with_scores(
                    query,
                    k=top_k
                )
            
            # Format results with metadata
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "chunk": doc.page_content,
                    "similarity": float(1 - score),
                    "metadata": doc.metadata
                })
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"Error during retrieval with metadata: {str(e)}")
            raise