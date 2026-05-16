"""Unit tests for document retriever"""

import pytest
import tempfile
from app.indexer import DocumentIndexer
from app.retriever import DocumentRetriever


@pytest.fixture
def indexed_document():
    """Create and index a test document"""
    # Create a test document
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""Python Programming Guide
        
        Python is a high-level, interpreted programming language known for its simplicity and readability.
        Created by Guido van Rossum in 1991, Python has become one of the most popular programming languages.
        
        Key Features of Python:
        - Easy to learn and read
        - Dynamically typed
        - Supports multiple programming paradigms
        - Extensive standard library
        - Large community support
        
        Python is widely used in:
        - Web development
        - Data science
        - Machine learning
        - Artificial intelligence
        - Automation and scripting
        - Scientific computing
        """)
        temp_file = f.name
    
    # Index the document
    indexer = DocumentIndexer()
    result = indexer.index_documents(temp_file, "python_guide.txt")
    
    yield result, indexer
    
    # Cleanup
    indexer.delete_document(result["document_id"])


def test_retriever_initialization():
    """Test that retriever initializes correctly"""
    retriever = DocumentRetriever()
    assert retriever is not None
    assert retriever.embeddings is not None
    assert retriever.vector_store is not None


def test_retrieve_documents(indexed_document):
    """Test document retrieval"""
    result, _ = indexed_document
    retriever = DocumentRetriever()
    
    chunks, scores = retriever.retrieve(
        query="What is Python?",
        document_id=result["document_id"],
        top_k=3
    )
    
    assert len(chunks) > 0
    assert len(scores) == len(chunks)
    assert all(0 <= score <= 1 for score in scores)


def test_retrieve_with_metadata(indexed_document):
    """Test document retrieval with metadata"""
    result, _ = indexed_document
    retriever = DocumentRetriever()
    
    results = retriever.retrieve_with_metadata(
        query="Programming features",
        document_id=result["document_id"],
        top_k=3
    )
    
    assert len(results) > 0
    for item in results:
        assert "chunk" in item
        assert "similarity" in item
        assert "metadata" in item


def test_retrieval_quality(indexed_document):
    """Test that retrieval returns relevant results"""
    result, _ = indexed_document
    retriever = DocumentRetriever()
    
    chunks, scores = retriever.retrieve(
        query="What is Python used for?",
        document_id=result["document_id"],
        top_k=1
    )
    
    # Check that we got results with reasonable similarity
    assert len(chunks) > 0
    assert scores[0] > 0.5  # Should have decent similarity


if __name__ == "__main__":
    pytest.main([__file__, "-v"])