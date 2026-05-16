"""Gradio web interface for DocuMind"""

import requests
import gradio as gr
from typing import Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8000"


def upload_document(file) -> str:
    """Upload a document"""
    if file is None:
        return "❌ Please select a file to upload."
    
    try:
        with open(file, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{API_URL}/upload", files=files, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            return f"""✅ **Document Indexed Successfully!**

📄 **Filename:** {data['filename']}
🔢 **Chunks Created:** {data['chunks_created']}
⏱️ **Time:** {data['total_time_s']}s
🆔 **Document ID:** `{data['document_id']}`

**Copy the Document ID above and paste it in the Query tab to search this specific document.**"""
        else:
            error = response.json().get('detail', 'Unknown error')
            return f"❌ **Error:** {error}"
    except requests.exceptions.ConnectionError:
        return "❌ **Error:** Cannot connect to API server. Make sure FastAPI is running on http://localhost:8000"
    except Exception as e:
        return f"❌ **Error:** {str(e)}"


def query_document(question: str, document_id: str, top_k: int) -> Tuple[str, str]:
    """Query a document"""
    if not question.strip():
        return "❌ Please enter a question.", "No sources retrieved."
    
    try:
        payload = {
            "question": question,
            "document_id": document_id if document_id.strip() else None,
            "top_k": top_k
        }
        
        response = requests.post(f"{API_URL}/query", json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            
            sources_text = "**📚 Retrieved Sources:**\n\n"
            for i, source in enumerate(data["sources"], 1):
                similarity_pct = source['similarity'] * 100
                sources_text += f"**Source {i}** (🎯 Relevance: {similarity_pct:.1f}%)\n"
                sources_text += f"> {source['chunk']}\n\n"
            
            return data["answer"], sources_text
        else:
            error = response.json().get("detail", "Unknown error")
            return f"❌ **Error:** {error}", "No sources retrieved."
    except requests.exceptions.ConnectionError:
        return "❌ **Error:** Cannot connect to API server. Make sure FastAPI is running.", "No sources retrieved."
    except Exception as e:
        return f"❌ **Error:** {str(e)}", "No sources retrieved."


def get_documents() -> str:
    """Get list of indexed documents"""
    try:
        response = requests.get(f"{API_URL}/documents", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['count'] == 0:
                return "📭 No documents indexed yet. Upload a document in the **Upload** tab."
            
            docs_text = f"📚 **Total Documents:** {data['count']}\n\n"
            for doc in data['documents']:
                doc_id = doc.get('document_id', 'Unknown')
                doc_name = doc.get('document_name', 'Unknown')
                docs_text += f"📄 **{doc_name}**\n"
                docs_text += f"🆔 ID: `{doc_id}`\n\n"
            return docs_text
        else:
            return "❌ Error fetching documents"
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to API server. Make sure FastAPI is running."
    except Exception as e:
        return f"❌ Error: {str(e)}"


def delete_document(doc_id: str) -> str:
    """Delete a document"""
    if not doc_id.strip():
        return "❌ Please enter a Document ID to delete."
    
    try:
        response = requests.delete(f"{API_URL}/documents/{doc_id}", timeout=30)
        if response.status_code == 200:
            data = response.json()
            return f"✅ **Success!** {data['message']}\n\n🗑️ **Chunks Deleted:** {data['chunks_deleted']}"
        else:
            error = response.json().get("detail", "Unknown error")
            return f"❌ Error: {error}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


# Create Gradio interface
with gr.Blocks(title="DocuMind - Document Q&A", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 📚 **DocuMind** - AI-Powered Document Q&A System
    
    Upload documents and ask questions about their content using AI-powered RAG (Retrieval-Augmented Generation).
    
    **How to use:**
    1. Upload a PDF or TXT document in the **Upload** tab
    2. Copy the Document ID that appears
    3. Go to the **Ask Questions** tab and paste the ID
    4. Ask your questions about the document
    """)
    
    with gr.Tab("📤 Upload Document"):
        gr.Markdown("### Upload a PDF or Text File")
        with gr.Row():
            file_input = gr.File(label="Select a PDF or Text File", file_types=["pdf", "txt"])
        
        with gr.Row():
            upload_btn = gr.Button("🚀 Upload & Index", scale=1, size="lg")
        
        upload_output = gr.Markdown(label="Upload Status")
        upload_btn.click(
            fn=upload_document,
            inputs=[file_input],
            outputs=[upload_output]
        )
    
    with gr.Tab("❓ Ask Questions"):
        gr.Markdown("### Query Your Documents")
        
        with gr.Row():
            question_input = gr.Textbox(
                label="🔍 Your Question",
                placeholder="e.g., What are the main findings? What is the summary?",
                lines=3
            )
        
        with gr.Row():
            document_id_input = gr.Textbox(
                label="📄 Document ID (optional)",
                placeholder="Paste the Document ID from the Upload tab to search specific document",
                lines=1
            )
            top_k_input = gr.Slider(
                label="📊 Number of Sources",
                minimum=1,
                maximum=10,
                value=4,
                step=1
            )
        
        with gr.Row():
            query_btn = gr.Button("🔎 Search & Generate Answer", size="lg")
        
        with gr.Row():
            answer_output = gr.Markdown(label="✨ Answer")
        
        with gr.Row():
            sources_output = gr.Markdown(label="📚 Retrieved Sources")
        
        query_btn.click(
            fn=query_document,
            inputs=[question_input, document_id_input, top_k_input],
            outputs=[answer_output, sources_output]
        )
    
    with gr.Tab("📚 Manage Documents"):
        gr.Markdown("### View and Manage Your Documents")
        
        with gr.Row():
            refresh_btn = gr.Button("🔄 Refresh Document List", size="lg")
        
        docs_output = gr.Markdown(label="Indexed Documents")
        refresh_btn.click(
            fn=get_documents,
            outputs=[docs_output]
        )
        
        gr.Markdown("### Delete a Document")
        with gr.Row():
            delete_id_input = gr.Textbox(
                label="📄 Document ID to Delete",
                placeholder="Enter the Document ID"
            )
        
        with gr.Row():
            delete_btn = gr.Button("🗑️ Delete Document", size="lg")
        
        delete_output = gr.Markdown(label="Delete Status")
        delete_btn.click(
            fn=delete_document,
            inputs=[delete_id_input],
            outputs=[delete_output]
        )
    
    with gr.Tab("ℹ️ About"):
        gr.Markdown("""
        ## About DocuMind
        
        **DocuMind** is an AI-powered document Q&A system that uses advanced techniques to understand your documents:
        
        ### 🏗️ How It Works
        
        1. **📤 Upload** - You upload a document (PDF or TXT)
        2. **✂️ Chunking** - The document is split into manageable pieces
        3. **🧠 Embedding** - Each chunk is converted into a numerical representation (embedding)
        4. **🔍 Semantic Search** - When you ask a question, we find the most relevant chunks
        5. **💬 Answer Generation** - Claude AI generates an answer based on the retrieved chunks
        
        ### ✨ Key Features
        
        - ✅ **GPU-Free** - Runs on CPU, no expensive hardware needed
        - ✅ **Fast** - Get answers in seconds
        - ✅ **Accurate** - Answers based on your actual documents
        - ✅ **Multi-Document** - Upload and query multiple documents
        - ✅ **Transparent** - See the source chunks used for each answer
        - ✅ **Production-Ready** - Built with industry best practices
        
        ### 🔧 Technologies
        
        - **LangChain** - LLM orchestration
        - **ChromaDB** - Vector database for semantic search
        - **Sentence-Transformers** - Document embeddings
        - **Claude AI** - Answer generation
        - **FastAPI** - REST API backend
        - **Gradio** - Web interface
        
        ### 📖 Retrieval-Augmented Generation (RAG)
        
        RAG is a technique that combines information retrieval with text generation. Instead of just using an LLM's training knowledge, RAG retrieves relevant information from your documents and uses it to generate accurate, context-grounded answers.
        
        **Benefits:**
        - Answers grounded in your actual documents
        - Reduces hallucination
        - Easy to update with new information
        - No model fine-tuning needed
        - Cost-effective
        
        ### 🔗 Links
        
        - [GitHub Repository](https://github.com/Sampath1576/documind)
        - [LangChain Docs](https://python.langchain.com)
        - [ChromaDB Docs](https://docs.trychroma.com)
        - [Anthropic Claude API](https://docs.anthropic.com)
        """)


if __name__ == "__main__":
    logger.info("🚀 Starting Gradio app...")
    logger.info(f"📡 API Server: {API_URL}")
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )