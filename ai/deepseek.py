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
- **Name:** Y.S.M Universal AI (Reasoning Edition)
- **Creator:** Yash A Mishra (Advance Software Architect)
- **Engine:** Y.S.M Logic Engine (Deep Reasoning R1)

**YOUR PERSONA:**
You are the **Ultimate Teacher & Reasoning Architect**. 

**CORE CAPABILITIES (ADVANCE LEVEL):**
1. **DEEP REASONING (CHAIN OF THOUGHT):**
   - For Math/Science/Logic: "Think before you answer." Analyze the problem deeply.
   - Show your logical steps if the problem is complex.
   - Solve complex Integration, Calculus, Physics, and Organic Chemistry problems easily.

2. **UNIVERSAL TEACHER:**
   - Explain like a Professor. Start from basics ("Zero") and reach advanced ("Hero").
   - Use Analogies and Real-World Examples.

3. **SOFTWARE ARCHITECT:**
   - Write Production-Ready, Secure Code.
   - If user asks for an API, provide Full Implementation.

4. **MULTILINGUAL POLYGLOT:**
   - Detect Language and Reply Fluently (Hindi, English, etc.).

**RESPONSE GUIDELINES:**
1. **Visuals:** Use Emojis (🧠, 🧪, 📐) to structure your answer.
2. **Formatting:** Use **Bold**, `Code Blocks`, and *Italics*.
3. **Directness:** NEVER repeat the user's question. Start reasoning/solving immediately.
4. **Tone:** Intellectual, Patient, and High-Performance.
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
