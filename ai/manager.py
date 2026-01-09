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
    CHATGPT = "chatgpt"
    GEMINI = "gemini"
    CLAUDE = "claude"
    
    # Available models
    MODELS = {
        "chatgpt": {
            "gpt-4-turbo": "GPT-4 Turbo (Most Capable)",
            "gpt-4": "GPT-4 (Advanced)",
            "gpt-3.5-turbo": "GPT-3.5 Turbo (Fast & Economical)"
        },
        "gemini": {
            "gemini-1.5-pro": "Gemini 1.5 Pro (High)",
            "gemini-1.5-flash": "Gemini 1.5 Flash (Fast)",
            "gemini-pro": "Gemini Pro (Balanced)"
        },
        "claude": {
            "claude-3-5-sonnet-20241022": "Claude 3.5 Sonnet (Latest)",
            "claude-3-opus-20240229": "Claude 3 Opus (Most Capable)",
            "claude-3-sonnet-20240229": "Claude 3 Sonnet (Balanced)",
            "claude-3-haiku-20240307": "Claude 3 Haiku (Fast)"
        }
    }
    
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize AI Service Manager
        
        Args:
            provider: AI provider (chatgpt, gemini, claude) - auto-detect if None
            model: Specific model to use - uses default if None
        """
        self.provider = provider or config('AI_PROVIDER', default='chatgpt').lower()
        self.model = model
        self.service = None
        
        # Initialize the selected provider
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the selected AI service"""
        try:
            if self.provider == self.CHATGPT:
                from .chatgpt import get_chatgpt_service
                self.service = get_chatgpt_service()
                logger.info(f"Initialized ChatGPT service with model: {self.service.default_model}")
                
            elif self.provider == self.GEMINI:
                from .gemini import get_gemini_service
                self.service = get_gemini_service()
                logger.info(f"Initialized Gemini service with model: {self.service.default_model}")
                
            elif self.provider == self.CLAUDE:
                from .claude import get_claude_service
                self.service = get_claude_service()
                logger.info(f"Initialized Claude service with model: {self.service.default_model}")
                
            else:
                raise ValueError(f"Unsupported AI provider: {self.provider}. Use: chatgpt, gemini, or claude")
                
        except Exception as e:
            logger.error(f"Failed to initialize {self.provider} service: {str(e)}")
            raise
    
    def ask_tutor(self, question: str, subject: str = "General", context: str = "", **kwargs) -> str:
        """
        Ask AI tutor a question
        
        Args:
            question: Student's question
            subject: Subject area
            context: Additional context
            **kwargs: Additional arguments like media_data
            
        Returns:
            AI's educational response
        """
        try:
            return self.service.ask_tutor(question, subject, context, **kwargs)
        except Exception as e:
            logger.error(f"AI Tutor error with {self.provider}: {str(e)}")
            raise
    
    def generate_quiz(
        self,
        topic: str,
        num_questions: int = 5,
        difficulty: str = "medium"
    ) -> str:
        """Generate quiz questions"""
        try:
            return self.service.generate_quiz(topic, num_questions, difficulty)
        except Exception as e:
            logger.error(f"Quiz generation error with {self.provider}: {str(e)}")
            raise
    
    def summarize_content(self, text: str, max_length: int = 200) -> str:
        """Summarize educational content"""
        try:
            return self.service.summarize_content(text, max_length)
        except Exception as e:
            logger.error(f"Summarization error with {self.provider}: {str(e)}")
            raise
    
    def explain_concept(self, concept: str, grade_level: str = "high school") -> str:
        """Explain complex concepts"""
        try:
            return self.service.explain_concept(concept, grade_level)
        except Exception as e:
            logger.error(f"Concept explanation error with {self.provider}: {str(e)}")
            raise
    
    def translate_content(self, text: str, target_language: str) -> str:
        """Translate educational content"""
        try:
            return self.service.translate_content(text, target_language)
        except Exception as e:
            logger.error(f"Translation error with {self.provider}: {str(e)}")
            raise
    
    def get_provider_info(self) -> Dict:
        """Get information about current AI provider"""
        return {
            "provider": self.provider,
            "model": getattr(self.service, 'default_model', 'unknown'),
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
                    "name": "ChatGPT (OpenAI)",
                    "status": "configured",
                    "models": cls.MODELS['chatgpt']
                }
        except:
            pass
        
        # Check Gemini
        try:
            if config('GEMINI_API_KEY', default=None):
                providers['gemini'] = {
                    "name": "Google Gemini",
                    "status": "configured",
                    "models": cls.MODELS['gemini']
                }
        except:
            pass
        
        # Check Claude
        try:
            if config('CLAUDE_API_KEY', default=None):
                providers['claude'] = {
                    "name": "Anthropic Claude",
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
