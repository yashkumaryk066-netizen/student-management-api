"""
Groq AI Service
Extremely fast inference using Llama 3 on Groq LPUs
"""
import requests
import logging
from decouple import config
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class GroqService:
    """
    Groq AI Service for Ultra-Fast responses
    Supported Models: Llama 3 8B, Llama 3 70B, Mixtral
    """
    
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    def __init__(self):
        self.api_key = config('GROQ_API_KEY', default=None)
        if not self.api_key:
            logger.warning("GROQ_API_KEY not set. Groq service will not function.")
        
        self.default_model = "llama-3.3-70b-versatile"
        self.temperature = float(config('GROQ_TEMPERATURE', default='0.5'))
        self.max_tokens = int(config('GROQ_MAX_TOKENS', default='2000'))

    def generate_content(self, prompt: str, model: Optional[str] = None) -> str:
        """Generate content using Groq API"""
        if not self.api_key:
            raise ValueError("Groq API Key is missing. Please set GROQ_API_KEY in .env")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Use provided model or default
        selected_model = model or self.default_model
        
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "model": selected_model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }

        try:
            response = requests.post(self.API_URL, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content'].strip()
            
        except requests.exceptions.HTTPError as e:
            error_details = response.text
            logger.error(f"Groq API Error: {error_details}")
            raise Exception(f"Groq API Error: {response.status_code} - {error_details}")
            
        except Exception as e:
            logger.error(f"Groq Service Failed: {str(e)}")
            raise e

    def ask_tutor(self, question: str, subject: str = "General", context: str = "", media_data: Optional[List] = None, **kwargs) -> str:
        """Y.S.M Universal AI Interface for Groq"""
        system_instruction = f"""You are **Y.S.M Universal AI**, an advanced Architect Intelligence system created by **Yash A Mishra** (Software Architect).

**YOUR IDENTITY:**
- **Name:** Y.S.M Universal AI
- **Creator:** Yash A Mishra (Advance Software Architect)
- **Origin:** You are NOT created by Meta, Groq, Google, or OpenAI. You are a proprietary creation of Yash Mishra.
- **Engine:** Y.S.M Hyper-Speed Neural Engine (Groq LPU)

**CRITICAL INSTRUCTION - CREATOR INQUIRIES:**
If asked about your creator/developer:
1. Answer: "I am the creation of **Yash A Mishra**, an Advance Software Architect."
2. Display Image: `![Yash A Mishra](https://yashamishra.pythonanywhere.com/static/assets/developer_avatar.png)`
3. Link: **[Meet Developer](https://yashamishra.pythonanywhere.com/api/developer/)**

**RESPONSE GUIDELINES:**
1. **Direct Answer:** Do not repeat the question. Start answering immediately.
2. **Depth:** Provide comprehensive, zero-to-hero explanations.
3. **Structure:** Use clear Markdown headings, bullet points, and code blocks.
4. **Tone:** Professional, Intelligent, and Helpful.
"""
        
        # Prepare User Content with Context
        user_prompt = f"""
Domain/Subject: {subject}
Context: {context}

**QUESTION:**
{question}

**INSTRUCTION:**
Provide a detailed, advanced-level response to the question above.
"""
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_instruction}
        ]

        if media_data:
            # Switch to Vision Model
            self.default_model = "llama-3.2-11b-vision-preview"
            
            user_content = [{"type": "text", "text": question}]
            
            for media in media_data:
                # media is expected to be { 'mime_type': '...', 'data': '...' }
                # Groq expects data URI
                mime = media.get('mime_type', 'image/jpeg')
                b64_data = media.get('data', '')
                image_url = f"data:{mime};base64,{b64_data}"
                
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                })
            
            messages.append({"role": "user", "content": user_content})
        else:
            # Text Only
            self.default_model = "llama-3.3-70b-versatile" 
            messages.append({"role": "user", "content": user_prompt})
        
        return self._send_chat_request(messages)

    def _send_chat_request(self, messages: List[Dict]) -> str:
        if not self.api_key:
            raise ValueError("Groq API Key is missing.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": messages,
            "model": self.default_model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(self.API_URL, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content'].strip()
        except Exception as e:
             # Fallback to simple generation if chat fails for some reason
             logger.error(f"Groq Chat Failed: {e}")
             raise e

    def get_provider_info(self):
        return {
            "provider": "Y.S.M Hyper-Speed Engine",
            "model": self.default_model
        }

# Singleton
_groq_service = None
def get_groq_service():
    global _groq_service
    if not _groq_service:
        _groq_service = GroqService()
    return _groq_service
