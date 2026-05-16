"""Answer generation pipeline - LLM-based response generation"""

import logging
import time
from typing import Dict

from anthropic import Anthropic

import mlflow

from .config import settings

logger = logging.getLogger(__name__)


class AnswerGenerator:
    """Generates answers using LLM based on retrieved context"""

    def __init__(self):
        """Initialize answer generator with LLM client"""
        logger.info("Initializing AnswerGenerator...")
        
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.LLM_MODEL
        
        logger.info(f"AnswerGenerator initialized with model: {self.model}")

    def _build_prompt(
        self,
        question: str,
        context_chunks: list,
        system_prompt: str = None
    ) -> str:
        """Build the final prompt for the LLM"""
        
        if not system_prompt:
            system_prompt = (
                "You are DocuMind, a precise document analysis assistant. "
                "Answer the user's question strictly based on the provided context. "
                "If the answer is not in the context, reply: "
                "'I could not find this information in the provided documents.' "
                "Do not hallucinate or use outside knowledge."
            )
        
        # Format context chunks
        context_text = ""
        for i, chunk in enumerate(context_chunks, 1):
            context_text += f"\n<doc_chunk_{i}>\n{chunk}\n</doc_chunk_{i}>\n"
        
        # Build final prompt
        prompt = f"""SYSTEM INSTRUCTIONS:
{system_prompt}

CONTEXT FROM DOCUMENTS:
{context_text}

USER QUESTION:
{question}

ANSWER:"""
        
        return prompt

    def generate_answer(
        self,
        question: str,
        context_chunks: list,
        system_prompt: str = None
    ) -> Dict:
        """
        Generate an answer based on question and context
        
        Args:
            question: User's question
            context_chunks: List of relevant document chunks
            system_prompt: Custom system prompt (optional)
        
        Returns:
            Dictionary with answer, latency, and metadata
        """
        
        logger.info(f"Generating answer for: {question[:100]}...")
        
        start_time = time.time()
        
        try:
            # Build prompt
            prompt = self._build_prompt(question, context_chunks, system_prompt)
            
            # Call LLM
            llm_start = time.time()
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=settings.LLM_MAX_TOKENS,
                temperature=settings.LLM_TEMPERATURE,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            llm_time = time.time() - llm_start
            total_time = time.time() - start_time
            
            answer = response.content[0].text.strip()
            
            # Log metrics
            mlflow.log_metrics({
                "llm_response_time_ms": llm_time * 1000,
                "total_generation_time_ms": total_time * 1000,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            })
            
            result = {
                "answer": answer,
                "llm_response_time_ms": round(llm_time * 1000, 2),
                "total_time_ms": round(total_time * 1000, 2),
                "tokens": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens
                }
            }
            
            logger.info(f"Answer generated successfully in {total_time:.2f}s")
            return result
        
        except Exception as e:
            logger.error(f"Error during answer generation: {str(e)}")
            mlflow.log_param("error", str(e))
            raise