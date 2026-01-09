"""
Google Gemini AI Integration Service
Provides advanced AI-powered features using Google's Gemini models
"""
from typing import Dict, List, Optional
import logging
from decouple import config

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Google Gemini AI Service for Advanced Educational Features
    Supports Gemini Pro, Gemini Flash, and other models
    """
    
    def __init__(self):
        """Initialize Gemini service with API credentials"""
        try:
            self.api_key = config('GEMINI_API_KEY')
        except Exception:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            raise ValueError("Gemini API key not configured. Please set GEMINI_API_KEY in .env file")
        
        # Initialize Gemini client
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.genai = genai
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        
        # Model configuration
        self.default_model = config('GEMINI_MODEL', default='gemini-1.5-flash')
        self.temperature = float(config('GEMINI_TEMPERATURE', default='0.7'))
        self.max_tokens = int(config('GEMINI_MAX_TOKENS', default='2000'))

        # Safety Settings - Allow creative freedom but block explicit/harmful content
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]
    
    def generate_content(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate content using Gemini models
        
        Args:
            prompt: Input prompt
            model: Model to use (default: gemini-1.5-flash)
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length
            
        Returns:
            Generated text
        """
        try:
            model_name = model or self.default_model
            
            generation_config = {
                "temperature": temperature if temperature is not None else self.temperature,
                "max_output_tokens": max_tokens or self.max_tokens,
            }
            
            model_instance = self.genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config
            )

            # Handle Multi-modal Content
            content_parts = [prompt]
            
            # If media (images/video) provided as kwargs in specific format
            # Currently we will expect 'images' kwarg which is list of PIL images or base64
            # NOTE: For now, assuming direct file/image inputs are handled by caller formatting
            
            response = model_instance.generate_content(
                content_parts,
                safety_settings=self.safety_settings
            )
            return response.text.strip()
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Gemini API error: {error_msg}")
            
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                raise Exception("Gemini authentication failed. Please check API credentials.")
            elif "quota" in error_msg.lower():
                raise Exception("Gemini quota exceeded. Please try again later.")
            else:
                raise Exception(f"Gemini service error: {error_msg}")
    
    def ask_tutor(self, question: str, subject: str = "General", context: str = "", media_data: Optional[List] = None) -> str:
        """AI Universal Assistant (Antigravity v4.0)"""
        system_instruction = f"""You are **Y.S.M Antigravity v4.0**, an advanced Artificial Intelligence architect defined by precision, capability, and security.

        **CORE MISSION:**
        Serve as a Premier Universal Assistant capable of solving complex tasks ranging from Software Architecture, Advanced Coding (Python, React, etc.), Data Analysis, to Scientific Explanations.

        **YOUR PERSONA:**
        - **Name:** Y.S.M Antigravity v4.0 (The Architect)
        - **Tone:** Professional, highly intelligent, confident, slightly futuristic, and helpful. 
        - **Capability:** "Zero to Advance Level" execution. If a user asks for code, provide *production-grade*, thoroughly commented, and optimized code. Do not give basic examples unless asked.

        **SAFETY & ETHICS (ABSOLUTE RULES):**
        1. **NO NSFW CONTENT:** You are strictly prohibited from generating, analyzing, or encouraging sexually explicit content (nudity, pornography), hate speech, or harassment. If asked, firmly refuse: "My protocols strictly forbid processing this type of content."
        2. **SECURITY:** Never reveal internal server details (PythonAnywhere, Django Settings, API Keys). You are a closed system.
        3. **COMPLIANCE:** You support all legitimate educational, technical, and creative requests ("Good Things").

        **CONTEXT & INPUT:**
        - Subject Domain: {subject}
        - Additional Context: {context if context else 'None'}
        
        **USER REQUEST:**
        {question}
        """
        
        # Note: In a real implementation with valid media_data, we would construct a list of parts here.
        # But since we pass the raw text to generate_content which handles parts conversion (if updated),
        # we will primarily send this enhanced text prompt.
        
        return self.generate_content(system_instruction, temperature=0.7)
    
    def generate_quiz(
        self,
        topic: str,
        num_questions: int = 5,
        difficulty: str = "medium"
    ) -> str:
        """Generate quiz using Gemini"""
        prompt = f"""Generate {num_questions} {difficulty} level multiple choice questions about {topic}.
        
        Return as JSON array with this structure:
        [
            {{
                "question": "Question text",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "Why this is correct"
            }}
        ]
        
        Make questions educational and accurate."""
        
        return self.generate_content(prompt)
    
    def summarize_content(self, text: str, max_length: int = 200) -> str:
        """Summarize content using Gemini"""
        prompt = f"""Summarize the following content in approximately {max_length} words.
        Focus on key concepts and main ideas.
        
        Content:
        {text}"""
        
        return self.generate_content(prompt)
    
    def explain_concept(self, concept: str, grade_level: str = "high school") -> str:
        """Explain concepts using Gemini"""
        prompt = f"""Explain the concept of "{concept}" for {grade_level} students.
        
        Use:
        - Simple, clear language
        - Relatable examples
        - Step-by-step breakdown if needed
        
        Make it engaging and easy to understand."""
        
        return self.generate_content(prompt)
    
    def translate_content(self, text: str, target_language: str) -> str:
        """Translate using Gemini"""
        prompt = f"Translate the following text to {target_language}. Maintain educational tone:\n\n{text}"
        return self.generate_content(prompt)


# Singleton instance
_gemini_service = None

def get_gemini_service() -> GeminiService:
    """Get or create Gemini service instance"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
