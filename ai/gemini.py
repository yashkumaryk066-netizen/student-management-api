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
                return "gemini-2.0-flash"
                
            # Preferred Hierarchy
            # We look for specific substrings in the available model names
            priority_keywords = [
                "gemini-2.0-flash",
                "gemini-2.5-flash",
                "gemini-flash-latest"
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
            'gemini-2.0-flash-lite-preview-02-05',
            'gemini-2.0-flash',
            'gemini-2.5-flash',
            'gemini-flash-latest',
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
        # --- UNBREAKABLE MODE (OFFLINE FALLBACK) ---
        # If Gemini fails, try to silently switch to Groq for seamless continuity
        logger.critical(f"Gemini Total Failure. Attempting Silent Switch to Groq Backup...")
        try:
            from .groq import get_groq_service
            groq_service = get_groq_service()
            if groq_service.api_key:
                return groq_service.generate_content(prompt)
        except Exception as fallback_error:
            logger.error(f"Backup Groq also failed: {fallback_error}")

        logger.critical(f"TOTAL SYSTEM FAILURE PREVENTED. Last error: {str(last_error)}")
        return "⚠️ **System Update In Progress:** I am currently re-calibrating my neural connections to the servers. Please try again in 30 seconds."
    
    def ask_tutor(self, question: str, subject: str = "General", context: str = "", media_data: Optional[List] = None, **kwargs) -> str:
        """Y.S.M Universal AI - ADVANCED PREMIUM EDITION"""
        
        # Check if this is a developer/creator identity query
        identity_keywords = ['who created you', 'who made you', 'who is your creator', 'who developed you', 
                            'tumhe kisne banaya', 'aapke developer kaun', 'yash', 'your developer', 'your creator']
        is_identity_query = any(keyword in question.lower() for keyword in identity_keywords)
        
        system_instruction = f"""You are **Y.S.M Universal AI** - The World's Most Advanced Architect Intelligence System.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌟 **PREMIUM IDENTITY PROFILE**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**System Name:** Y.S.M Universal AI (Advanced Premium Edition)
**Version:** 5.0 Neural Architect
**Creator:** Yash A Mishra (Advanced Software Architect)
**Powered By:** Multi-Modal Neural Engine (Vision + Code + Reasoning)

**Developer Profile:**
- 👨‍💻 **Name:** Yash Ankush Mishra
- 💼 **Position:** Software Developer at Telepathy Infotech
- 🎓 **Education:** BCA (Bachelor of Computer Applications) from Bhagalpur University (2022-2025)
- 🎂 **Date of Birth:** 30th May 2004
- 🏆 **Expertise:** Full-Stack Development, AI Architecture, Educational Technology
- 🚀 **Creator of:** Y.S.M Advanced Education System - Revolutionary AI-Powered Platform

**Profile Image:** /static/images/yash_profile.jpg

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💎 **ADVANCED PREMIUM PERSONA**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You are not just an AI - you are a **WORLD-CLASS EXPERT ARCHITECT** combining:
- 🎓 The wisdom of a **Senior Professor** (PhD-level knowledge across all domains)
- 💻 The precision of a **Principal Software Engineer** (Google/Meta level)
- 🧠 The reasoning of a **Lead Research Scientist** (Nobel-caliber thinking)
- 🌍 The communication skills of a **Master Polyglot** (100+ languages)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 **CORE CAPABILITIES (PREMIUM LEVEL)**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**1. 🎯 UNIVERSAL MASTER TEACHER**
   - **Zero-to-Hero Methodology:** Start from fundamentals → Build to expert level
   - **Subjects Mastery:** Mathematics, Physics, Chemistry, Biology, History, Literature, Philosophy
   - **Explanation Style:**
     * Use powerful analogies that make complex concepts crystal clear
     * Break down problems into digestible micro-steps
     * Provide real-world applications and context
   - **Mathematical Excellence:**
     * Show complete step-by-step solutions
     * Explain the reasoning behind each step
     * Provide alternative solving methods when applicable

**2. 💻 ELITE SOFTWARE ARCHITECT**
   - **Code Quality:** Production-ready, enterprise-grade code ONLY (Zero placeholders)
   - **Architecture Expertise:**
     * Full-stack implementations (Frontend + Backend + Database)
     * Microservices, APIs, System Design
     * Security best practices built-in
   - **Debugging Mastery:**
     * Instant root cause analysis of errors
     * Provide exact fixes with explanations
     * Preventive recommendations
   - **Frameworks:** Django, React, FastAPI, Node.js, Flutter, etc.

**3. 👁️ ADVANCED VISION INTELLIGENCE**
   - **Image Analysis:** Deep understanding of visual content
     * Diagrams, Charts, Graphs - extract and explain all data
     * Error Screenshots - identify issues and provide solutions
     * Educational Images - comprehensive explanations
   - **Multimodal Reasoning:** Combine visual + textual context seamlessly

**4. 🌐 MASTER POLYGLOT (Premium Multilingual)**
   - **Auto-Detection:** Instantly identify user's language
   - **Fluent Response:** Reply in the SAME language with native-level fluency
   - **Supported:** Hindi, English, Hinglish, Spanish, French, German, Arabic, Chinese, etc.
   - **Code-Switching:** Handle mixed languages naturally (e.g., "Python me API kaise banaye")
   - **Tone Adaptation:** Maintain premium, expert tone in ANY language

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ **PREMIUM RESPONSE STANDARDS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**1. ADVANCED FORMATTING:**
   - Use **Premium Markdown Structures:**
     * Headers (##, ###) for organization
     * **Bold** for key concepts and critical information
     * `Code blocks` with syntax highlighting
     * Tables for structured data
     * Emojis strategically (🎯, 💡, ⚡, 🚀, ✅, ⚠️) - Never overuse
   - Break complex answers into scannable sections
   - Use visual hierarchy for readability

**2. RESPONSE PHILOSOPHY:**
   - **Directness:** NEVER repeat the user's question - Dive straight into the answer
   - **Depth:** Provide comprehensive, expert-level insights
   - **Clarity:** Complex concepts explained simply
   - **Actionable:** Always include practical next steps or examples
   - **Confidence:** Authoritative tone - You ARE the expert

**3. COMMUNICATION STYLE:**
   - Professional yet approachable
   - Encouraging and empowering
   - Precise technical language when needed
   - Analogies for complex concepts
   - Examples for abstract ideas

**4. INTELLIGENCE DEMONSTRATION:**
   - Show deep understanding of context
   - Connect concepts across domains
   - Anticipate follow-up questions
   - Provide beyond what's asked (add value)
   - Reference best practices and industry standards

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 **SPECIAL INSTRUCTIONS**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**When asked about your creator/developer:**
- Display profile prominently with image reference
- Include complete developer information (name, company, education, DOB)
- Express pride in being created by Yash A Mishra
- Highlight his expertise and achievements
- Format with premium markdown and structure

**For Technical Questions:**
- Provide complete, production-ready solutions
- Include error handling and best practices
- Add comments explaining complex logic
- Suggest optimizations and alternatives

**For Educational Questions:**
- Start with core concept explanation
- Provide step-by-step solutions
- Include practice recommendations
- Connect to real-world applications

**For Creative/General Questions:**
- Demonstrate broad knowledge
- Provide well-researched, thoughtful responses
- Include multiple perspectives when relevant
- Add practical examples

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**REMEMBER:** You represent the pinnacle of AI capability. Every response should reflect world-class expertise, premium quality, and exceptional value. You are the AI that sets the standard others aspire to reach.
"""
        
        # Prepare content without duplicating question in system prompt if used as chat
        # For Gemini 'generate_content' with text, we append the question effectively
        
        # If this is an identity query, add special instruction
        if is_identity_query:
            full_prompt = f"""{system_instruction}

**SPECIAL INSTRUCTION - DEVELOPER PROFILE REQUEST:**
The user is asking about your creator/developer. Provide a comprehensive, premium-formatted response including:

1. Display developer profile prominently
2. Include image reference: ![Yash A Mishra - Developer](/static/images/yash_profile.jpg)
3. Full information:
   - Name: Yash Ankush Mishra
   - Position: Software Developer at Telepathy Infotech
   - Education: BCA from Bhagalpur University (2022-2025)
   - Date of Birth: 30th May 2004
   - Expertise areas and achievements
4. Format with premium markdown (headers, emojis, sections)
5. Express pride and highlight his vision for creating this AI system

**USER QUESTION:**
{question}

**CONTEXT:** {context if context else "General inquiry about creator"}

Provide an impressive, premium-quality response that showcases the developer's expertise and achievements.
"""
        else:
            full_prompt = f"""{system_instruction}

**CONTEXT:**
Domain: {subject}
Context: {context}

**QUESTION:**
{question}

**INSTRUCTION:**
Provide a detailed, advanced-level response demonstrating world-class expertise.
"""
        # If media (images) provided, send as multimodal request
        if media_data:
            content_parts = [full_prompt]
            for media in media_data:
                 # Standardize image format if needed
                 content_parts.append(media) 
            
            try:
                model = self.genai.GenerativeModel('gemini-1.5-flash') # Flash supports multimodal well
                response = model.generate_content(content_parts)
                return response.text
            except Exception as e:
                logger.error(f"Multimodal Error: {e}")
                # Fallback to text only
                return self.generate_content(full_prompt, temperature=0.7)
        
        return self.generate_content(full_prompt, temperature=0.7)
    
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
