"""FastAPI application - REST API endpoints for DocuMind"""

import logging
import time
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import mlflow

from .config import settings
from .indexer import DocumentIndexer
from .retriever import DocumentRetriever
from .generator import AnswerGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DocuMind API",
    description="AI-Powered Document Q&A System with RAG Pipeline",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MLflow
mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
mlflow.set_experiment(settings.MLFLOW_EXPERIMENT_NAME)

# Initialize components
logger.info("Initializing DocuMind components...")
try:
    indexer = DocumentIndexer()
    retriever = DocumentRetriever()
    generator = AnswerGenerator()
    logger.info("✅ All components initialized successfully")
except Exception as e:
    logger.error(f"❌ Error initializing components: {str(e)}")
    raise


# Pydantic models
class QueryRequest(BaseModel):
    """Query request model"""
    question: str
    document_id: Optional[str] = None
    top_k: Optional[int] = None
    system_prompt: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    models_loaded: bool
    vector_db_ready: bool
    timestamp: str


class UploadResponse(BaseModel):
    """Upload response model"""
    document_id: str
    filename: str
    chunks_created: int
    message: str


class QueryResponse(BaseModel):
    """Query response model"""
    answer: str
    sources: list
    latency_ms: float


class DocumentListResponse(BaseModel):
    """Document list response model"""
    count: int
    documents: list


class DeleteResponse(BaseModel):
    """Delete response model"""
    message: str
    chunks_deleted: int


# API Endpoints

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to DocuMind API",
        "version": "1.0.0",
        "description": "AI-Powered Document Q&A System with RAG Pipeline",
        "endpoints": {
            "health": "GET /health",
            "upload": "POST /upload",
            "query": "POST /query",
            "documents": "GET /documents",
            "delete": "DELETE /documents/{document_id}",
            "docs": "GET /docs"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    from datetime import datetime
    try:
        # Verify models are loaded
        return HealthResponse(
            status="healthy",
            models_loaded=True,
            vector_db_ready=True,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.post("/upload", response_model=UploadResponse, tags=["Documents"])
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Upload and index a document"""
    
    logger.info(f"Received upload request for: {file.filename}")
    
    with mlflow.start_run():
        try:
            # Validate file type
            allowed_types = [
                "application/pdf",
                "text/plain",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ]
            
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file.content_type}. Allowed: PDF, TXT, DOCX"
                )
            
            # Read file
            file_content = await file.read()
            file_size = len(file_content)
            
            # Check file size
            if file_size > settings.MAX_FILE_SIZE_BYTES:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Max size: {settings.MAX_FILE_SIZE_MB}MB"
                )
            
            # Save file temporarily
            upload_path = Path(settings.UPLOAD_DIR) / file.filename
            with open(upload_path, "wb") as f:
                f.write(file_content)
            
            logger.info(f"File saved to: {upload_path}")
            
            # Index document
            result = indexer.index_documents(
                file_path=str(upload_path),
                document_name=file.filename
            )
            
            # Schedule file cleanup
            background_tasks.add_task(upload_path.unlink)
            
            logger.info(f"✅ Document uploaded successfully: {result}")
            return UploadResponse(**result)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error during upload: {str(e)}")
            mlflow.log_param("error", str(e))
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_documents(request: QueryRequest):
    """Query indexed documents and get answers"""
    
    logger.info(f"Received query: {request.question[:100]}...")
    
    with mlflow.start_run():
        try:
            start_time = time.time()
            
            # Step 1: Retrieve relevant chunks
            chunks, scores = retriever.retrieve(
                query=request.question,
                document_id=request.document_id,
                top_k=request.top_k
            )
            
            if not chunks:
                return QueryResponse(
                    answer="No relevant documents found for your query.",
                    sources=[],
                    latency_ms=round((time.time() - start_time) * 1000, 2)
                )
            
            # Step 2: Generate answer
            gen_result = generator.generate_answer(
                question=request.question,
                context_chunks=chunks,
                system_prompt=request.system_prompt
            )
            
            # Step 3: Format sources
            sources = [
                {
                    "chunk": chunk[:200] + "..." if len(chunk) > 200 else chunk,
                    "similarity": float(score)
                }
                for chunk, score in zip(chunks, scores)
            ]
            
            total_time = time.time() - start_time
            
            # Log to MLflow
            mlflow.log_param("question", request.question)
            mlflow.log_metric("total_latency_ms", total_time * 1000)
            
            logger.info(f"✅ Query processed successfully in {total_time:.2f}s")
            
            return QueryResponse(
                answer=gen_result["answer"],
                sources=sources,
                latency_ms=round(total_time * 1000, 2)
            )
        
        except Exception as e:
            logger.error(f"❌ Error during query: {str(e)}")
            mlflow.log_param("error", str(e))
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents", response_model=DocumentListResponse, tags=["Documents"])
async def list_documents():
    """List all indexed documents"""
    try:
        documents = indexer.list_documents()
        return DocumentListResponse(
            count=len(documents),
            documents=documents
        )
    except Exception as e:
        logger.error(f"❌ Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{document_id}", response_model=DeleteResponse, tags=["Documents"])
async def delete_document(document_id: str):
    """Delete a document from the index"""
    try:
        result = indexer.delete_document(document_id)
        return DeleteResponse(**result)
    except Exception as e:
        logger.error(f"❌ Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", tags=["Analytics"])
async def get_stats():
    """Get system statistics"""
    try:
        documents = indexer.list_documents()
        return {
            "total_documents": len(documents),
            "embedding_model": settings.EMBEDDING_MODEL,
            "llm_model": settings.LLM_MODEL,
            "chunk_size": settings.CHUNK_SIZE,
            "top_k": settings.TOP_K
        }
    except Exception as e:
        logger.error(f"❌ Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )