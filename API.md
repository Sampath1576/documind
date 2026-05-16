# API Reference

## Base URL

```
http://localhost:8000
```

## Authentication

Currently no authentication required. In production, add:
- API key validation
- Rate limiting
- JWT tokens

## Response Format

All responses are JSON with the following structure:

```json
{
  "status": "success|error",
  "data": {},
  "error": null
}
```

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check if the service is healthy

**Parameters:** None

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "vector_db_ready": true,
  "timestamp": "2026-05-16T10:00:00"
}
```

**Status Codes:**
- 200: Healthy
- 503: Service Unavailable

---

### 2. Upload Document

**Endpoint:** `POST /upload`

**Description:** Upload and index a document

**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (File, required): PDF or TXT file (max 50MB)

**Example:**
```bash
curl -X POST \
  -F "file=@document.pdf" \
  http://localhost:8000/upload
```

**Response:**
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "chunks_created": 42,
  "embedding_time_s": 3.45,
  "total_time_s": 4.12,
  "message": "Document indexed successfully"
}
```

**Status Codes:**
- 200: Success
- 400: Invalid file type
- 413: File too large
- 500: Processing error

---

### 3. Query Documents

**Endpoint:** `POST /query`

**Description:** Query indexed documents and get answers

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "question": "What are the main findings?",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "top_k": 4,
  "system_prompt": null
}
```

**Parameters:**
- `question` (string, required): User's question
- `document_id` (string, optional): Filter to specific document
- `top_k` (integer, optional): Number of chunks to retrieve (1-10, default: 4)
- `system_prompt` (string, optional): Custom system prompt

**Example:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main conclusion?",
    "top_k": 4
  }'
```

**Response:**
```json
{
  "answer": "The main conclusion is that...",
  "sources": [
    {
      "chunk": "Chapter 1: Introduction...",
      "similarity": 0.92
    },
    {
      "chunk": "Chapter 2: Methodology...",
      "similarity": 0.88
    }
  ],
  "latency_ms": 2340
}
```

**Status Codes:**
- 200: Success
- 400: Invalid request
- 500: Processing error

---

### 4. List Documents

**Endpoint:** `GET /documents`

**Description:** Get list of all indexed documents

**Parameters:** None

**Example:**
```bash
curl http://localhost:8000/documents
```

**Response:**
```json
{
  "count": 3,
  "documents": [
    {
      "document_id": "550e8400-e29b-41d4-a716-446655440000",
      "document_name": "research_paper.pdf"
    },
    {
      "document_id": "660e8400-e29b-41d4-a716-446655440001",
      "document_name": "article.txt"
    }
  ]
}
```

**Status Codes:**
- 200: Success
- 500: Database error

---

### 5. Delete Document

**Endpoint:** `DELETE /documents/{document_id}`

**Description:** Delete a document from the index

**Parameters:**
- `document_id` (string, path): ID of document to delete

**Example:**
```bash
curl -X DELETE http://localhost:8000/documents/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "message": "Document 550e8400-e29b-41d4-a716-446655440000 deleted successfully",
  "chunks_deleted": 42
}
```

**Status Codes:**
- 200: Success
- 404: Document not found
- 500: Database error

---

### 6. System Statistics

**Endpoint:** `GET /stats`

**Description:** Get system statistics and configuration

**Parameters:** None

**Example:**
```bash
curl http://localhost:8000/stats
```

**Response:**
```json
{
  "total_documents": 3,
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "llm_model": "claude-3-haiku-20240307",
  "chunk_size": 500,
  "top_k": 4
}
```

**Status Codes:**
- 200: Success
- 500: Error

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error description"
}
```

### Common Error Codes

| Code | Message | Solution |
|------|---------|----------|
| 400 | Bad Request | Check request format and parameters |
| 413 | Payload Too Large | Reduce file size (max 50MB) |
| 500 | Internal Server Error | Check server logs, restart service |
| 503 | Service Unavailable | Service is down, wait and retry |

---

## Rate Limiting

Current implementation has no rate limiting. For production:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/query")
@limiter.limit("10/minute")
async def query_documents(request: QueryRequest):
    ...
```

---

## Webhooks

Future enhancement: Add webhooks for:
- Document indexing complete
- Query complete
- Error occurred

---

## Interactive Documentation

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

Both are auto-generated from the OpenAPI schema.
