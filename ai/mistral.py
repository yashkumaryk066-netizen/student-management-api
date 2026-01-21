"""
Mistral AI Integration Service
High-performance European AI provider (Free tier available)
"""
import os
import logging
from typing import Dict, List, Optional
from decouple import config

logger = logging.getLogger(__name__)


class MistralService:
    """
    Mistral AI Service - European AI Provider
    Supports Mistral 7B, Mixtral 8x7B models
    """
    
    def __init__(self):
        """Initialize Mistral service"""
        try:
            self.api_key = config('MISTRAL_API_KEY')
        except Exception:
            logger.warning("MISTRAL_API_KEY not found - will use free inference API")
            self.api_key = None
        
        # Initialize Mistral client
        try:
            from mistralai.client import MistralClient
            self.client = MistralClient(api_key=self.api_key) if self.api_key else None
        except ImportError:
            logger.warning("mistralai package not installed. Install: pip install mistralai")
            self.client = None
        
        # Model configuration
        self.default_model = config('MISTRAL_MODEL', default='mistral-small-latest')
        self.temperature = float(config('MISTRAL_TEMPERATURE', default='0.7'))
        self.max_tokens = int(config('MISTRAL_MAX_TOKENS', default='2000'))
    
    def generate_content(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate content using Mistral AI
        
        Args:
            prompt: User prompt
            model: Mistral model to use
            temperature: Creativity level
            max_tokens: Max response length
            
        Returns:
            Generated text
        """
        if not self.client:
            # Fallback to HuggingFace Inference API for Mistral
            return self._generate_via_huggingface(prompt)
        
        try:
            from mistralai.models.chat_completion import ChatMessage
            
            messages = [
                ChatMessage(role="user", content=prompt)
            ]
            
            response = self.client.chat(
                model=model or self.default_model,
                messages=messages,
                temperature=temperature if temperature is not None else self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Mistral API error: {str(e)}")
            raise Exception(f"Mistral AI error: {str(e)}")
    
    def _generate_via_huggingface(self, prompt: str) -> str:
        """Fallback: Use HuggingFace Inference API for Mistral models"""
        try:
            import requests
            
            API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
            headers = {}
            
            # Check if HF token available
            hf_token = config('HUGGINGFACE_API_KEY', default=None)
            if hf_token:
                headers["Authorization"] = f"Bearer {hf_token}"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": self.max_tokens,
                    "temperature": self.temperature
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '').strip()
            
            return str(result)
            
        except Exception as e:
            logger.error(f"HuggingFace fallback error: {e}")
            raise Exception("Mistral AI unavailable. Please configure MISTRAL_API_KEY or HUGGINGFACE_API_KEY")
    
    def ask_tutor(self, question: str, subject: str = "General", context: str = "", **kwargs) -> str:
        """AI Tutor using Mistral"""
        system_context = f"""You are Y.S.M AI - an expert tutor in {subject}.
Provide clear, detailed explanations with examples.
Break down complex topics into simple steps."""
        
        full_prompt = f"""{system_context}

Context: {context}

Question: {question}

Provide a comprehensive answer:"""
        
        return self.generate_content(full_prompt)
    
    def generate_quiz(self, topic: str, num_questions: int = 5, difficulty: str = "medium") -> str:
        """Generate quiz using Mistral"""
        prompt = f"""Generate {num_questions} {difficulty} level multiple choice questions about {topic}.

Return as JSON array:
[
    {{
        "question": "Question text",
        "options": ["A", "B", "C", "D"],
        "correct_answer": "A",
        "explanation": "Why this is correct"
    }}
]"""
        
        return self.generate_content(prompt)
    
    def summarize_content(self, text: str, max_length: int = 200) -> str:
        """Summarize content"""
        prompt = f"""Summarize this in {max_length} words:

{text}"""
        return self.generate_content(prompt)
    
    def explain_concept(self, concept: str, grade_level: str = "high school") -> str:
        """Explain concepts"""
        prompt = f"""Explain "{concept}" for {grade_level} students with simple language and examples."""
        return self.generate_content(prompt)
    
    def translate_content(self, text: str, target_language: str) -> str:
        """Translate content"""
        prompt = f"Translate to {target_language}:\n\n{text}"
        return self.generate_content(prompt)


# Singleton instance
_mistral_service = None

def get_mistral_service() -> MistralService:
    """Get or create Mistral service instance"""
    global _mistral_service
    if _mistral_service is None:
        _mistral_service = MistralService()
    return _mistral_service
