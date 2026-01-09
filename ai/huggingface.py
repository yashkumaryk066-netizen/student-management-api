"""
Hugging Face Inference API Integration
Completely FREE AI service with no rate limits
"""
import logging
import requests
from typing import Optional
from decouple import config

logger = logging.getLogger(__name__)


class HuggingFaceService:
    """
    Hugging Face Inference API Service
    FREE Alternative to ChatGPT/Gemini
    """
    
    def __init__(self):
        """Initialize HuggingFace service"""
        try:
            # API key is optional for public models
            self.api_key = config('HUGGINGFACE_API_KEY', default='')
            self.api_url = "https://api-inference.huggingface.co/models"
            
            # Use a reliable free model that works without authentication
            self.default_model = config(
                'HUGGINGFACE_MODEL',
                default='microsoft/Phi-3-mini-4k-instruct'
            )
            
            # Set headers (works with or without key)
            if self.api_key:
                self.headers = {"Authorization": f"Bearer {self.api_key}"}
                logger.info(f"HuggingFace initialized with API key")
            else:
                self.headers = {}
                logger.info(f"HuggingFace initialized in public mode (no key)")
            
            logger.info(f"Model: {self.default_model}")
            
        except Exception as e:
            logger.error(f"HuggingFace init error: {str(e)}")
            raise
    
    def _generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call HuggingFace API"""
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                f"{self.api_url}/{self.default_model}",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '').strip()
                return str(result)
            else:
                raise Exception(f"API Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            raise Exception(f"HuggingFace generation failed: {str(e)}")
    
    def ask_tutor(self, question: str, subject: str = "General", context: str = "", **kwargs) -> str:
        """AI tutor using HuggingFace"""
        
        prompt = f"""<s>[INST] You are an expert AI assistant.

Subject: {subject}
Context: {context}

User Question: {question}

Provide a clear, helpful, and accurate response. [/INST]"""
        
        try:
            answer = self._generate(prompt, max_tokens=1500)
            return f"🤗 {answer}"
        except Exception as e:
            logger.error(f"HuggingFace ask_tutor error: {str(e)}")
            raise
    
    def generate_quiz(self, topic: str, num_questions: int = 5, difficulty: str = "medium") -> str:
        """Generate quiz"""
        prompt = f"Generate {num_questions} {difficulty} level quiz questions about {topic} with answers."
        return self._generate(prompt)
    
    def summarize_content(self, text: str, max_length: int = 200) -> str:
        """Summarize content"""
        prompt = f"Summarize this text in {max_length} words:\n\n{text}"
        return self._generate(prompt, max_tokens=300)
    
    def explain_concept(self, concept: str, grade_level: str = "high school") -> str:
        """Explain concepts"""
        prompt = f"Explain '{concept}' for {grade_level} students in simple terms."
        return self._generate(prompt)
    
    def translate_content(self, text: str, target_language: str) -> str:
        """Translate content"""
        prompt = f"Translate to {target_language}: {text}"
        return self._generate(prompt)


# Singleton
_hf_service = None

def get_huggingface_service() -> HuggingFaceService:
    """Get or create HuggingFace service"""
    global _hf_service
    if _hf_service is None:
        _hf_service = HuggingFaceService()
    return _hf_service
