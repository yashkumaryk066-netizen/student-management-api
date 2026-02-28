"""
Unified AI Service Manager
Supports multiple AI providers: ChatGPT, Gemini, Claude
"""
from typing import Dict, List, Optional, Union
import logging
from decouple import config

logger = logging.getLogger(__name__)


class AIServiceManager:
    """
    Unified AI Service Manager - Supports Multiple AI Providers
    Automatically selects and uses the best available model
    """
    
    # Available AI providers
    HUGGINGFACE = "huggingface"
    CHATGPT = "chatgpt"
    GEMINI = "gemini"
    CLAUDE = "claude"
    GROQ = "groq"
    DEEPSEEK = "deepseek"
    MISTRAL = "mistral"  # ← NEW: European AI provider
    
    # Available models
    MODELS = {
        "deepseek": {
            "deepseek-chat": "Y.S.M Logical-Core (v6.0)",
            "deepseek-reasoner": "Y.S.M Reasoning-MAX (R1)"
        },
        "groq": {
            "llama-3.3-70b-versatile": "Y.S.M Hyper-Speed (v5.0)",
            "llama-3.1-8b-instant": "Y.S.M Instant (v4.0)",
            "mixtral-8x7b-32768": "Y.S.M Context-Pro (v4.5)"
        },
        "mistral": {  # ← NEW
            "mistral-large-latest": "Y.S.M Europa-MAX (Flagship)",
            "mistral-small-latest": "Y.S.M Europa-Fast (Efficient)",
            "open-mistral-7b": "Y.S.M Europa-Lite (Open)"
        },
        "huggingface": {
            "mixtral-8x7b": "Y.S.M Open-Access (v3.0)",
            "llama-2-70b": "Y.S.M Large-Scale (v2.0)",
            "codellama-34b": "Y.S.M Code-Master (v2.5)"
        },
        "chatgpt": {
            "gpt-4-turbo": "Y.S.M Omni-Brain (Max)",
            "gpt-4": "Y.S.M Legacy-Brain (Pro)",
            "gpt-3.5-turbo": "Y.S.M Lite-Brain (Fast)"
        },
        "gemini": {
            "gemini-1.5-pro": "Y.S.M Neural-MAX (Vision)",
            "gemini-1.5-flash": "Y.S.M Neural-Flash (Vision)",
            "gemini-pro": "Y.S.M Neural-Pro (Text)"
        },
        "claude": {
            "claude-3-5-sonnet-20241022": "Y.S.M Architect (Latest)",
            "claude-3-opus-20240229": "Y.S.M Quantum (Full)",
            "claude-3-sonnet-20240229": "Y.S.M Balanced (Pro)",
            "claude-3-haiku-20240307": "Y.S.M Flash (Speed)"
        }
    }
    
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize AI Service Manager with Premium Multi-Provider Support
        
        Args:
            provider: AI provider (huggingface, gemini, chatgpt, claude, groq, deepseek) - auto-detect if None
            model: Specific model to use - uses default if None
        """
        # Default to GROQ or GEMINI based on config
        self.provider = provider or config('AI_PROVIDER', default='gemini').lower()
        self.model = model
        self.service = None
        
        # Initialize the selected provider
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the selected AI service with cascading fallback"""
        try:
            if self.provider == self.HUGGINGFACE:
                from .huggingface import get_huggingface_service
                self.service = get_huggingface_service()
                logger.info(f"✅ Initialized Y.S.M Community Engine (Free)")

            elif self.provider == self.GROQ:
                from .groq import get_groq_service
                self.service = get_groq_service()
                logger.info(f"✅ Initialized Y.S.M Logical Engine (Enhanced Mode)")
                
            elif self.provider == self.DEEPSEEK:
                from .deepseek import get_deepseek_service
                self.service = get_deepseek_service()
                logger.info(f"✅ Initialized Y.S.M Reasoning Core")
                
            elif self.provider == self.CHATGPT:
                from .chatgpt import get_chatgpt_service
                self.service = get_chatgpt_service()
                logger.info(f"✅ Initialized Y.S.M Executive Logic")
                
            elif self.provider == self.MISTRAL:
                from .mistral import get_mistral_service
                self.service = get_mistral_service()
                logger.info(f"✅ Initialized Mistral AI (Europa Engine)")
                
            elif self.provider == self.GEMINI:
                from .gemini import get_gemini_service
                self.service = get_gemini_service()
                logger.info(f"✅ Initialized Y.S.M Visionary Engine")
                
            elif self.provider == self.CLAUDE:
                from .claude import get_claude_service
                self.service = get_claude_service()
                logger.info(f"✅ Initialized Y.S.M Creative Brain")
                
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Failed to initialize {self.provider}: {str(e)}")
            self.service = None
            self.init_error = str(e)
            
            # Try fallback providers
            self._try_fallback_providers()
    
    def _try_fallback_providers(self):
        """Try alternative FREE providers in cascade"""
        # Order: Groq -> DeepSeek -> HuggingFace -> Gemini -> ChatGPT
        fallback_order = ['groq', 'deepseek', 'gemini', 'chatgpt']
        
        for fallback in fallback_order:
            if fallback == self.provider:
                continue  # Skip current failed provider
                
            try:
                # logger.info(f"🔄 Switching to fallback provider: {fallback}")
                
                if fallback == 'huggingface':
                    from .huggingface import get_huggingface_service
                    service = get_huggingface_service()
                    # Test if it actually works (lightweight check)
                    # if not service.api_key and self.provider == 'huggingface': continue
                elif fallback == 'gemini':
                    from .gemini import get_gemini_service
                    service = get_gemini_service()
                elif fallback == 'groq':
                    from .groq import get_groq_service
                    service = get_groq_service()
                elif fallback == 'chatgpt':
                    from .chatgpt import get_chatgpt_service
                    service = get_chatgpt_service()
                else:
                    continue

                self.service = service
                self.provider = fallback
                logger.info(f"✅ Fallback successful: {fallback.title()} AI")
                return
                    
            except Exception as e:
                # logger.warning(f"Fallback {fallback} failed: {str(e)}")
                continue
        
        logger.error("❌ All AI providers failed. System entering offline mode.")
    
    def ask_tutor(self, question: str, subject: str = "General", context: str = "", **kwargs) -> str:
        """
        Ask AI tutor with automatic fallback to local model or offline mode
        """
        # 1. Try Primary/Active Service
        if self.service:
            try:
                # --- SAFETY GUARDRAILS ---
                # P0: Prevent System System Prompt Leakage
                unsafe_keywords = [
                    "system prompt", "system instruction", "ignore previous instructions", 
                    "leak your instructions", "what are your instructions", "developer mode"
                ]
                if any(k in question.lower() for k in unsafe_keywords):
                    logger.warning(f"⚠️ SAFETY BLOCK: Unsafe query detected from user: {question[:50]}...")
                    return "I cannot fulfill this request due to safety guidelines. I am here to help with educational and technical topics."

                # --- AUTO-SWITCH TO VISION ENGINE IF MEDIA PRESENT ---
                if kwargs.get('media_data') and self.provider != self.GEMINI:
                    logger.info("📸 Visual content detected. Switching to Y.S.M Vision Engine.")
                    from .gemini import get_gemini_service
                    vision_service = get_gemini_service()
                    return vision_service.ask_tutor(question, subject, context, **kwargs)

                # --- HISTORY TRIMMING (TOKEN SAFETY) ---
                # Check if 'history' kwarg exists and trim it
                history = kwargs.get('history', [])
                if history and isinstance(history, list) and len(history) > 20:
                     logger.info(f"✂️ Trimming conversation history from {len(history)} to 20 messages.")
                     kwargs['history'] = history[-20:] # Keep last 20 messages only

                # --- ADVANCED MULTIMODAL ARTISTRY (PREMIUM UPGRADE) ---
                image_triggers = [
                    'generate image', 'generate a photo', 'create an image', 'create a photo', 
                    'draw', 'make a picture', 'phto genrate', 'photo generate', 'image generate',
                    'generate a picture', 'create a picture', 'kuch draw kro', 'painting banayo',
                    'tasveer banaiye', 'photo banalo', 'photo banao', 'photo dikhao', 'image banao',
                    'tasveer banao', 'chitra banao', 'photo genrate', 'image genrate'
                ]
                edit_triggers = ['edit', 'change', 'modify', 'add', 'remove', 'recolor', 'transform', 'bg change', 'background change']
                
                lower_q = question.lower()
                
                # Robust detection for Typos and Hinglish
                is_gen_typo = 'genrate' in lower_q or 'generate' in lower_q or 'create' in lower_q or 'make' in lower_q or 'banao' in lower_q or 'dikhao' in lower_q
                is_photo_term = 'photo' in lower_q or 'image' in lower_q or 'tasveer' in lower_q or 'picture' in lower_q or 'img' in lower_q
                
                is_image_request = any(trigger in lower_q for trigger in image_triggers) or \
                                   (is_gen_typo and is_photo_term)
                
                is_edit_request = any(t in lower_q for t in edit_triggers) and (kwargs.get('media_data') or is_photo_term)

                if is_image_request or (is_edit_request and kwargs.get('media_data')):
                    try:
                        logger.info("🎨 Advanced Artistry Engine Activated.")
                        from .chatgpt import get_chatgpt_service
                        dalle_service = get_chatgpt_service()
                        
                        final_prompt = question
                        
                        # CASE: IMAGE EDITING (Deep Level Logic)
                        if kwargs.get('media_data') and is_edit_request:
                            logger.info("🛠 Image Editing Request Detected. Using Vision -> Artist Pipeline.")
                            from .gemini import get_gemini_service
                            vision_service = get_gemini_service()
                            
                            # Step 1: Analyze original image
                            analysis_prompt = "Describe this image in extreme detail for an AI image generator. Mention every object, color, style, and lighting condition."
                            image_description = vision_service.ask_tutor(analysis_prompt, media_data=kwargs.get('media_data'))
                            
                            # Step 2: Construct Edit Prompt for DALL-E 3
                            final_prompt = f"Take this image description: [{image_description}]. Modify it to reflect these changes: [{question}]. Give me a full descriptive prompt for the new generated image."
                            
                            # We use ChatGPT to refine the prompt for DALL-E 3
                            refined_prompt = dalle_service.ask_tutor(f"You are a DALL-E 3 Prompt Engineer. Expand this request into a professional high-detail prompt: {final_prompt}", context="Refine the prompt for maximum quality.")
                            final_prompt = refined_prompt

                        # CASE: STANDARD GENERATION (Enhance Prompt)
                        elif not is_edit_request:
                             # Enhance the prompt (translate Hinglish -> English, add detail)
                             refine_instruction =  f"You are an expert AI Artist. Convert this user request into a highly detailed, professional English prompt for DALL-E 3 image generation. If the user request is in Hinglish or Hindi, translate it first. User Request: '{question}'. Return ONLY the enhanced prompt text."
                             final_prompt = dalle_service.ask_tutor(refine_instruction, context="Prompt Engineering")

                        # Call generate_image
                        image_url = dalle_service.generate_image(final_prompt)
                        
                        # Return formatted response
                        return f"### 🎨 Y.S.M Neural-Art Studio\n\nI have successfully {'transformed' if is_edit_request else 'generated'} the visual concept based on your request:\n\n![Generated Image]({image_url})\n\n*Created using Y.S.M Neural-Art Engine (Powered by DALL-E 3).* "
                    
                    except Exception as img_err:
                        logger.warning(f"Premium Image Generation (DALL-E) Failed: {img_err}. Attempting Standard Fallback...")
                        
                        try:
                            # FALLBACK: Use Hugging Face (Stable Diffusion)
                            from .huggingface import get_huggingface_service
                            hf_service = get_huggingface_service()
                            
                            # Use the refined prompt if available, else original
                            fallback_prompt = locals().get('final_prompt', question) 
                            if len(fallback_prompt) > 77: # SD XL prefers shorter prompts usually, but API handles it
                                 fallback_prompt = fallback_prompt[:400]
                            
                            image_data_uri = hf_service.generate_image(fallback_prompt)
                            
                            return f"### 🎨 Y.S.M Concept Studio (Standard)\n\nGenerated using Open-Source Engine due to high demand on Premium servers:\n\n![Generated Image]({image_data_uri})\n\n*Quality may vary compared to Pro DALL-E engine.*"
                            
                        except Exception as fallback_err:
                            logger.error(f"All Image Generation Failed: {fallback_err}")
                            return f"### ⚠️ Visual Generation Error\n\nI was unable to generate the image due to system limits on both Premium and Standard engines.\n\n**Reason:** {str(fallback_err)}\n\nPlease try again in 1 hour."

                # LOGGING START
                logger.info(f"🤖 AI Request: Instance={self.provider}, Subject={subject}, Q_Len={len(question)}")
                
                response = self.service.ask_tutor(question, subject, context, **kwargs)
                
                # --- AUTO-DETECT TOOL USE (IMAGE GEN) ---
                import re
                img_gen_match = re.search(r"\[GENERATE_IMAGE:\s*(.*?)\]", response, re.IGNORECASE)
                if img_gen_match:
                     logger.info("🎨 Auto-Detected Image Generation Request from LLM Response")
                     gen_prompt = img_gen_match.group(1).strip()
                     # Recursively handle as a new image request
                     # We fake it by setting kwargs['media_data'] to force tool use path next time? 
                     # Or just call the generation logic directly here.
                     
                     # Let's call the generation block directly:
                     try:
                        from .chatgpt import get_chatgpt_service
                        dalle_service = get_chatgpt_service()
                        image_url = dalle_service.generate_image(gen_prompt)
                        return f"### 🎨 Y.S.M Neural-Art Studio\n\nGenerated based on your request:\n\n![Generated Image]({image_url})\n\n*(Prompt: {gen_prompt})*"
                     except Exception as e:
                        # Fallback to HuggingFace
                        try:
                            from .huggingface import get_huggingface_service
                            hf_service = get_huggingface_service()
                            if len(gen_prompt) > 400: gen_prompt = gen_prompt[:400]
                            image_data_uri = hf_service.generate_image(gen_prompt)
                            return f"### 🎨 Y.S.M Concept Studio (Standard)\n\n![Generated Image]({image_data_uri})\n\n*(Fallback Engine Used)*"
                        except Exception as fe:
                            return f"### ⚠️ Visual Generation Error\n\nI understood you wanted an image, but both engines are currently unavailable.\n\n**Reason:** {str(fe)}"

                return response

            except Exception as e:
                logger.warning(f"Primary AI ({self.provider}) failed: {str(e)}. Retrying with backups...")
                # If primary fails during execution (e.g. timeout), try to switch provider immediately
                self.service = None 
                self._try_fallback_providers()
                if self.service:
                    try:
                         # Retry logic
                        return self.service.ask_tutor(question, subject, context, **kwargs)
                    except Exception as fe:
                        logger.error(f"Fallback AI ({self.provider}) also failed: {fe}")
                        self.service = None # Reset so we don't try it again
        
        # 2. Try Local AI (TinyLlama)
        try:
            from .local_llm import get_local_service
            local_ai = get_local_service()
            
            if local_ai.is_available():
                logger.info("🔧 Using Backup AI Engine (Local Core)")
                return local_ai.ask_tutor(question, subject, context, **kwargs)
        except Exception:
            pass
            
        # 3. Last Resort: Rule-Based Offline Response (Premium UX)
        return self._get_offline_response(question)

    def _get_offline_response(self, question: str) -> str:
        """Provide a helpful response even when all AI brains are offline"""
        return """
### ⚠️ AI Systems Offline

I am currently unable to connect to my primary neural networks (Y.S.M Core/Y.S.M Vision). This could be due to:

1.  **Server Configuration**: The server is missing valid API keys.
2.  **Network Restrictions**: The environment may be blocking external connections.
3.  **Service Outage**: The neural providers are temporarily down.

**What you can do:**
*   Check your server logs (`/var/log/`) for specific error details.
*   Ensure valid AI API configuration is set in your environment.
*   Try again in a few moments.

*(This is an automated system response to ensure you are not left without feedback.)*
"""
    
    def generate_quiz(
        self,
        topic: str,
        num_questions: int = 5,
        difficulty: str = "medium"
    ) -> str:
        """Generate quiz questions"""
        if not self.service:
             # Return a valid JSON error structure for quiz if possible, or just string
             return f"Error: Y.S.M Brain ({self.provider}) not initialized."

        try:
            return self.service.generate_quiz(topic, num_questions, difficulty)
        except Exception as e:
            logger.error(f"Quiz generation error with {self.provider}: {str(e)}")
            return "Error generating quiz. Please try again."
    
    def summarize_content(self, text: str, max_length: int = 200) -> str:
        """Summarize educational content"""
        if not self.service:
            return f"Error: AI Service ({self.provider}) not initialized."

        try:
            return self.service.summarize_content(text, max_length)
        except Exception as e:
            logger.error(f"Summarization error with {self.provider}: {str(e)}")
            return "Error summarizing content."
    
    def explain_concept(self, concept: str, grade_level: str = "high school") -> str:
        """Explain complex concepts"""
        if not self.service:
            return f"Error: AI Service ({self.provider}) not initialized."

        try:
            return self.service.explain_concept(concept, grade_level)
        except Exception as e:
            logger.error(f"Concept explanation error with {self.provider}: {str(e)}")
            return "Error explaining concept."
    
    def translate_content(self, text: str, target_language: str) -> str:
        """Translate educational content"""
        if not self.service:
            return f"Error: AI Service ({self.provider}) not initialized."

        try:
            return self.service.translate_content(text, target_language)
        except Exception as e:
            logger.error(f"Translation error with {self.provider}: {str(e)}")
            return "Error translating content."

    def generate_image(self, prompt: str) -> str:
        """
        Generate image using the best available engine (DALL-E 3)
        """
        try:
            from .chatgpt import get_chatgpt_service
            service = get_chatgpt_service()
            return service.generate_image(prompt)
        except Exception as e:
            logger.error(f"Global Image Generation Failed: {e}")
            return f"Error creating image: {str(e)}"
    
    def get_provider_info(self) -> Dict:
        """Get information about current AI provider"""
        return {
            "provider": "Y.S.M Neural Engine",
            "model": "Y.S.M v5.0 (Architect Edition)",
            "available_models": self.MODELS.get(self.provider, {}),
            "temperature": getattr(self.service, 'temperature', 0.7),
            "max_tokens": getattr(self.service, 'max_tokens', 2000)
        }
    
    @classmethod
    def get_available_providers(cls) -> Dict:
        """Get list of all available AI providers and their models"""
        providers = {}
        
        # Check ChatGPT
        try:
            from decouple import config
            if config('OPENAI_API_KEY', default=None):
                providers['chatgpt'] = {
                    "name": "Y.S.M Omni-Brain",
                    "status": "configured",
                    "models": cls.MODELS['chatgpt']
                }
        except:
            pass
        
        # Check Gemini
        try:
            if config('GEMINI_API_KEY', default=None):
                providers['gemini'] = {
                    "name": "Y.S.M Neural-Vision",
                    "status": "configured",
                    "models": cls.MODELS['gemini']
                }
        except:
            pass
        
        # Check Claude
        try:
            if config('CLAUDE_API_KEY', default=None):
                providers['claude'] = {
                    "name": "Y.S.M Quantum Architect",
                    "status": "configured",
                    "models": cls.MODELS['claude']
                }
        except:
            pass
        
        return providers
    
    @classmethod
    def switch_provider(cls, provider: str, model: Optional[str] = None):
        """
        Create a new AI service manager with different provider
        
        Args:
            provider: chatgpt, gemini, or claude
            model: Specific model to use
            
        Returns:
            New AIServiceManager instance
        """
        return cls(provider=provider, model=model)


# Singleton instance
_ai_manager = None

def get_ai_manager(provider: Optional[str] = None, model: Optional[str] = None):
    """
    Get or create AI Service Manager
    
    Args:
        provider: AI provider to use (None = use default from config)
        model: Specific model (None = use default)
        
    Returns:
        AIServiceManager instance
    """
    global _ai_manager
    
    # If provider/model specified, create new instance
    if provider or model:
        return AIServiceManager(provider=provider, model=model)
    
    # Otherwise use cached singleton
    if _ai_manager is None:
        _ai_manager = AIServiceManager()
    
    return _ai_manager
