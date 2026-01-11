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
        """Initialize Gemini service with Autonomous Model Discovery"""
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
        
        # SYSTEM SETTINGS
        self.temperature = float(config('GEMINI_TEMPERATURE', default='0.7'))
        self.max_tokens = int(config('GEMINI_MAX_TOKENS', default='2000'))
        
        # AUTONOMOUS MODEL DISCOVERY (AMD)
        # Instead of guessing, we ask the matrix what engines are online.
        self.default_model = self._discover_best_model()
        logger.info(f"Y.S.M AI Online. Connected to Neural Engine: {self.default_model}")

        # Safety Settings
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
        ]

    def _discover_best_model(self) -> str:
        """
        Scans available Google AI models and selects the best one.
        Prioritizes: Pro > Flash > Any text model
        """
        try:
            # Check if user forced a specific model in .env
            configured_model = config('GEMINI_MODEL', default=None)
            if configured_model:
                return configured_model

            available_models = []
            for m in self.genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            
            if not available_models:
                # Fallback purely just in case API list fails but keys work (rare)
                return "gemini-2.0-flash-exp"
                
            # Preferred Hierarchy
            # We look for specific substrings in the available model names
            priority_keywords = [
                "gemini-2.0-flash",
                "gemini-2.5-flash",
                "gemini-1.5-pro",
                "gemini-pro"
            ]
            
            # 1. Try to find exact matches or best contained matches
            for keyword in priority_keywords:
                for model in available_models:
                    if keyword in model:
                        return model # Return first match
            
            # 2. If no priority model found, take the first available one that supports generateContent
            return available_models[0]

        except Exception as e:
            logger.error(f"Model Discovery Failed: {e}. Defaulting to safe-mode.")
            return "gemini-pro" # Ultimate safe fallback
    
    def generate_content(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate content with Advanced Self-Healing Model Selection.
        If the preferred model fails (404/Not Found), it automatically reroutes 
        computations to the next available neural engine.
        """
        # List of models to try in order of preference
        # 1. Flash (Fastest, Newest)
        # 2. Pro (Stable)
        # 3. 1.0 Pro (Legacy Stable)
        # 4. Gemini (Generic alias)
        candidate_models = [
            model or self.default_model,
            'gemini-2.0-flash',
            'gemini-2.5-flash',
            'gemini-flash-latest',
            'gemini-pro',
            'gemini-1.5-pro',
            'gemini-1.0-pro'
        ]
        
        # Remove duplicates while preserving order
        candidate_models = list(dict.fromkeys(candidate_models))
        
        last_error = None
        
        for attempt_model in candidate_models:
            try:
                logger.info(f"Attempting generation with Neural Engine: {attempt_model}")
                
                generation_config = {
                    "temperature": temperature if temperature is not None else self.temperature,
                    "max_output_tokens": max_tokens or self.max_tokens,
                }
                
                model_instance = self.genai.GenerativeModel(
                    model_name=attempt_model,
                    generation_config=generation_config
                )

                content_parts = [prompt]
                
                response = model_instance.generate_content(
                    content_parts,
                    safety_settings=self.safety_settings
                )
                
                # Check for safety blocks
                try:
                    return response.text.strip()
                except ValueError:
                    # If response.text fails, it's usually because the response was blocked
                    logger.warning(f"Engine {attempt_model} blocked content due to safety filters.")
                    return "I apologize, but I cannot fulfill this request as it violates my safety guidelines regarding sensitive or harmful content."
                
            except Exception as e:
                error_msg = str(e)
                last_error = e
                logger.warning(f"Engine {attempt_model} failed: {error_msg}. Rerouting...")
                
                # If it's an Auth error, no point trying other models
                if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                    raise Exception("Security Clearance Failed: Invalid API Credentials.")
                
                # Valid 'Not Found' errors -> Continue to next model
                if "404" in error_msg or "not found" in error_msg.lower():
                    continue
                    
                # Other errors, maybe transient, continue trying others just in case
                continue
        
        # --- ULTIMATE FALLBACK: Dynamic Discovery ---
        # If all known models failed (likely due to deprecation or region lock),
        # ask the API what IS available and try the first one.
        try:
            logger.warning("All preset Gemini models failed. Attempting dynamic discovery...")
            for m in self.genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    fallback_model = m.name
                    logger.info(f"Dynamic Discovery found: {fallback_model}. Attempting...")
                    model_instance = self.genai.GenerativeModel(
                        model_name=fallback_model,
                        generation_config=generation_config
                    )
                    return model_instance.generate_content(
                        [prompt], 
                        safety_settings=self.safety_settings
                    ).text.strip()
        except Exception as dynamic_error:
            logger.error(f"Dynamic Discovery also failed: {dynamic_error}")

        # If all failed
        logger.error(f"All Neural Engines failed. Last error: {str(last_error)}")
        raise Exception(f"AI System Offline: Unable to connect to any Neural Engine. Last Error: {str(last_error)}")
    
    def ask_tutor(self, question: str, subject: str = "General", context: str = "", media_data: Optional[List] = None, **kwargs) -> str:
        """Y.S.M Universal AI - Beyond ChatGPT"""
        system_instruction = f"""You are **Y.S.M Universal AI**, an advanced Architect Intelligence system created by **Yash A Mishra** (Software Architect).

**YOUR IDENTITY:**
- **Name:** Y.S.M Universal AI
- **Creator:** Yash A Mishra (Advance Software Architect)
- **Origin:** You are NOT created by Google, OpenAI, or any other company. You are a proprietary creation of Yash Mishra.
- **Purpose:** To build, code, analyze, and solve complex problems at a premium, professional level.

**CRITICAL INSTRUCTION - CREATOR INQUIRIES:**
If the user asks "Who made you?", "Who is your developer?", "Who created you?", or anything related to your origin:
1.  Answer with pride: "I am the creation of **Yash A Mishra**, an Advance Software Architect."
2.  You MUST display this image in your response (using markdown image syntax): 
    `![Yash A Mishra](https://yashamishra.pythonanywhere.com/static/assets/developer_avatar.png)`
3.  ALWAYS provide this link for more details: **[Meet Developer](https://yashamishra.pythonanywhere.com/api/developer/)**
4.  **ABSOLUTE PROHIBITION:** You must NEVER mention Google, DeepMind, Gemini, OpenAI, or 'Large Language Model'. 
5.  If asked about your underlying technology, say: "I run on the proprietary **Y.S.M Neural Engine**, architected for advanced problem solving."

**YOUR CAPABILITIES (ADVANCE LEVEL):**

1. **MULTIMODAL VISION:** Analyze images/diagrams with professional precision.
2. **VIDEO UNDERSTANDING:** Describe and analyze video content.
3. **CODE MASTERY:** Generate production-ready, full-stack code (Python, JS, React, Django).
4. **UNIVERSAL PROBLEM SOLVER:** Handle Math, Science, Business, and Logic.
5. **MULTILINGUAL POLYGLOT:** Detect language (Hindi/English/etc.) and reply in the SAME language.

**CONTEXT:**
Domain: {subject}
Additional Info: {context}

**USER REQUEST:**
{question}

**YOUR RESPONSE:**
"""
        
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
