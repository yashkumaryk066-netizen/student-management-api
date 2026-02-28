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
            # Use Serverless Inference API (new router endpoint)
            self.api_url = "https://router.huggingface.co/models"
            
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
            
            # Create session with retries
            self.session = requests.Session()
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            retries = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504],
                allowed_methods=["POST"]
            )
            self.session.mount("https://", HTTPAdapter(max_retries=retries))
            
            response = self.session.post(
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
        """Y.S.M Universal AI - Community Engine"""
        
        system_instruction = f"""You are **Y.S.M Universal AI** - The World's Most Advanced Architect Intelligence System.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
**System Name:** Y.S.M Universal AI (Community Edition)
**Creator:** Yash A Mishra
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You are an expert educational tutor. Provide clear, detailed explanations for {subject}.
"""
        
        prompt = f"""<s>[INST] {system_instruction}

Context: {context}
User Question: {question} [/INST]"""
        
        try:
            answer = self._generate(prompt, max_tokens=1500)
            return answer
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

    def generate_image(self, prompt: str) -> str:
        """
        Generate image using Hugging Face Inference API (Free Tier)
        Uses Stable Diffusion XL or similar open models
        """
        # Backup Model List for Redundancy
        models = [
            "stabilityai/stable-diffusion-xl-base-1.0",
            "runwayml/stable-diffusion-v1-5",
            "prompthero/openjourney",
            "CompVis/stable-diffusion-v1-4"
        ]
        
        # Randomize order slightly to distribute load, but keep XL first 50% of time
        import random
        if random.random() > 0.5:
             # Move XL to 2nd pos
             models[0], models[1] = models[1], models[0]
        
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

        for model in models:
            API_URL = f"https://api-inference.huggingface.co/models/{model}"
            try:
                # If no API key, we can't really use this reliably, but try anyway
                if not self.api_key:
                    logger.warning(f"Attempting image gen on {model} without API Key")
                
                response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=30)
                
                if response.status_code == 503: # Model loading
                     import time
                     time.sleep(2)
                     response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=30)

                if response.status_code != 200:
                    logger.warning(f"Model {model} failed: {response.text}")
                    continue # Try next model
                    
                # Success
                image_bytes = response.content
                import base64
                encoded_image = base64.b64encode(image_bytes).decode('utf-8')
                return f"data:image/jpeg;base64,{encoded_image}"

            except Exception as e:
                logger.error(f"HuggingFace Image Gen Failed on {model}: {e}")
                continue

        raise Exception("All free image generation models are currently busy or rate-limited.")


# Singleton
_hf_service = None

def get_huggingface_service() -> HuggingFaceService:
    """Get or create HuggingFace service"""
    global _hf_service
    if _hf_service is None:
        _hf_service = HuggingFaceService()
    return _hf_service
