"""Unit tests for document indexer"""

import pytest
import tempfile
from pathlib import Path
from app.indexer import DocumentIndexer
from app.config import settings


@pytest.fixture
def temp_pdf():
    """Create a temporary PDF file for testing"""
    # Create a simple text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""This is a test document about machine learning.
        
        Machine learning is a subset of artificial intelligence that focuses on learning from data.
        It enables computers to learn and improve from experience without being explicitly programmed.
        
        Types of machine learning include:
        1. Supervised Learning
        2. Unsupervised Learning
        3. Reinforcement Learning
        
        Applications of machine learning are found in various domains such as:
        - Healthcare: Disease prediction and diagnosis
        - Finance: Fraud detection and risk assessment
        - Transportation: Autonomous vehicles
        - E-commerce: Recommendation systems
        """)
        return f.name


def test_indexer_initialization():
    """Test that indexer initializes correctly"""
    indexer = DocumentIndexer()
    assert indexer is not None
    assert indexer.embeddings is not None
    assert indexer.vector_store is not None


def test_document_loading(temp_pdf):
    """Test document loading"""
    indexer = DocumentIndexer()
    documents = indexer.load_document(temp_pdf)
    assert len(documents) > 0
    assert documents[0].page_content is not None


def test_document_chunking(temp_pdf):
    """Test document chunking"""
    indexer = DocumentIndexer()
    documents = indexer.load_document(temp_pdf)
    chunks = indexer.chunk_documents(documents)
    assert len(chunks) > 0
    for chunk in chunks:
        assert len(chunk.page_content) >= settings.MIN_CHUNK_SIZE


def test_document_indexing(temp_pdf):
    """Test complete document indexing pipeline"""
    indexer = DocumentIndexer()
    result = indexer.index_documents(temp_pdf, "test_document")
    
    assert result["document_id"] is not None
    assert result["filename"] == "test_document"
    assert result["chunks_created"] > 0
    assert result["message"] == "Document indexed successfully"
    
    # Cleanup
    indexer.delete_document(result["document_id"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])