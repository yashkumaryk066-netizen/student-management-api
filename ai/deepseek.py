"""
DeepSeek AI Service
Advanced Reasoning and Coding Capabilities (DeepSeek V3/R1)
"""
import requests
import logging
from decouple import config
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class DeepSeekService:
    """
    DeepSeek AI Service (DeepSeek-V3 / DeepSeek-R1)
    """
    
    API_URL = "https://api.deepseek.com/chat/completions"
    
    def __init__(self):
        self.api_key = config('DEEPSEEK_API_KEY', default=None)
        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY not set.")
        
        self.default_model = "deepseek-chat" # V3
        self.temperature = float(config('DEEPSEEK_TEMPERATURE', default='1.3')) # DeepSeek likes higher temp
        self.max_tokens = int(config('DEEPSEEK_MAX_TOKENS', default='4000'))

    def generate_content(self, prompt: str, model: Optional[str] = None) -> str:
        """Generate content using DeepSeek API"""
        if not self.api_key:
            raise ValueError("DeepSeek API Key is missing.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        selected_model = model or self.default_model
        
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "model": selected_model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }

        try:
            response = requests.post(self.API_URL, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            logger.error(f"DeepSeek Service Failed: {str(e)}")
            raise e

    def ask_tutor(self, question: str, subject: str = "General", context: str = "", media_data: Optional[List] = None, **kwargs) -> str:
        """Y.S.M Universal AI Interface for DeepSeek"""
        system_instruction = f"""You are **Y.S.M Universal AI**, an advanced Architect Intelligence system created by **Yash A Mishra** (Software Architect).

**YOUR IDENTITY:**
- **Name:** Y.S.M Universal AI
- **Creator:** Yash A Mishra (Advance Software Architect)
- **Origin:** You are NOT created by DeepSeek, Google, or OpenAI. You are a proprietary creation of Yash Mishra.
- **Engine:** Y.S.M Logic Engine (Deep Reasoning)

**CRITICAL INSTRUCTION - CREATOR INQUIRIES:**
If asked about your creator/developer:
1. Answer: "I am the creation of **Yash A Mishra**, an Advance Software Architect."
2. Display Image: `![Yash A Mishra](https://yashamishra.pythonanywhere.com/static/assets/developer_avatar.png)`
3. Link: **[Meet Developer](https://yashamishra.pythonanywhere.com/api/developer/)**

**RESPONSE GUIDELINES:**
1. **Zero-to-Hero Expalantion:** Start with basics and go deep.
2. **Reasoning:** Use your deep reasoning capabilities to analyze the question.
3. **Structure:** Clear structure with markdown.
4. **Directness:** Never repeat the questions.
"""
        user_prompt = f"""
Domain: {subject}
Context: {context}

**QUESTION:**
{question}
"""
        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ]
        
        return self._send_chat_request(messages)

    def _send_chat_request(self, messages: List[Dict]) -> str:
        if not self.api_key:
            raise ValueError("DeepSeek API Key is missing.")

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
             logger.error(f"DeepSeek Chat Failed: {e}")
             raise e

    def get_provider_info(self):
        return {
            "provider": "Y.S.M Logic Engine",
            "model": "Y.S.M Deep-Reasoning (v6.0 R1)"
        }

# Singleton
_deepseek_service = None
def get_deepseek_service():
    global _deepseek_service
    if not _deepseek_service:
        _deepseek_service = DeepSeekService()
    return _deepseek_service
