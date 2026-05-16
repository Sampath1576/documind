"""Integration tests for the complete RAG pipeline"""

import pytest
import tempfile
from app.indexer import DocumentIndexer
from app.retriever import DocumentRetriever
from app.generator import AnswerGenerator


@pytest.fixture
def rag_pipeline():
    """Initialize the complete RAG pipeline"""
    # Create and index a test document
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""Artificial Intelligence in Healthcare
        
        Artificial Intelligence (AI) is revolutionizing healthcare by improving diagnostics, treatment planning, and patient outcomes.
        
        Applications of AI in Healthcare:
        1. Medical Imaging: AI algorithms can detect tumors, fractures, and other abnormalities in X-rays, CT scans, and MRI images.
        2. Drug Discovery: AI accelerates the identification of new therapeutic compounds.
        3. Patient Monitoring: Wearable devices and AI analyze patient data for early disease detection.
        4. Treatment Planning: AI helps oncologists develop personalized cancer treatment plans.
        5. Virtual Health Assistants: Chatbots provide initial patient consultations and health advice.
        
        Benefits:
        - Improved accuracy in diagnosis
        - Reduced healthcare costs
        - Faster treatment decisions
        - Better patient outcomes
        - Reduced clinician burden
        """)
        temp_file = f.name
    
    indexer = DocumentIndexer()
    result = indexer.index_documents(temp_file, "ai_healthcare.txt")
    
    retriever = DocumentRetriever()
    generator = AnswerGenerator()
    
    yield {
        "indexer": indexer,
        "retriever": retriever,
        "generator": generator,
        "document_id": result["document_id"]
    }
    
    # Cleanup
    indexer.delete_document(result["document_id"])


def test_end_to_end_rag(rag_pipeline):
    """Test the complete RAG pipeline from query to answer"""
    pipeline = rag_pipeline
    
    # Step 1: Retrieve
    chunks, scores = pipeline["retriever"].retrieve(
        query="What are the applications of AI in healthcare?",
        document_id=pipeline["document_id"],
        top_k=3
    )
    
    assert len(chunks) > 0
    assert scores[0] > 0.5
    
    # Step 2: Generate
    result = pipeline["generator"].generate_answer(
        question="What are the applications of AI in healthcare?",
        context_chunks=chunks
    )
    
    assert "answer" in result
    assert len(result["answer"]) > 0
    assert "tokens" in result
    assert result["tokens"]["input"] > 0
    assert result["tokens"]["output"] > 0


def test_retrieval_and_generation_consistency(rag_pipeline):
    """Test that generation uses retrieved context"""
    pipeline = rag_pipeline
    
    question = "How does AI improve medical imaging?"
    
    # Retrieve context
    chunks, _ = pipeline["retriever"].retrieve(
        query=question,
        document_id=pipeline["document_id"],
        top_k=2
    )
    
    # Generate answer
    result = pipeline["generator"].generate_answer(
        question=question,
        context_chunks=chunks
    )
    
    # Check that answer is not empty and mentions key terms
    answer = result["answer"].lower()
    assert len(answer) > 20
    assert "ai" in answer or "artificial" in answer or "detect" in answer or "algorithm" in answer


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])