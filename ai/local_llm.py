"""
Local AI Service using TinyLlama
This is the BACKUP/OFFLINE engine when external APIs fail
"""
import logging
from typing import Optional
from decouple import config

logger = logging.getLogger(__name__)


class LocalAIService:
    """
    100% Independent AI using TinyLlama (GGUF)
    No internet, no API keys, no external dependencies
    """
    
    def __init__(self):
        """Initialize local AI with TinyLlama model"""
        self.model = None
        self.model_loaded = False
        self.model_path = config('LOCAL_MODEL_PATH', default='/home/tele/.cache/tinyllama.gguf')
        
        # Try to load the model
        self._initialize_model()
    
    def _initialize_model(self):
        """Load TinyLlama model using llama-cpp-python"""
        try:
            from llama_cpp import Llama
            
            logger.info(f"Loading Local AI Model from: {self.model_path}")
            
            # Load model with CPU optimization
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=2048,  # Context window
                n_threads=4,  # CPU threads
                n_gpu_layers=0,  # No GPU (PythonAnywhere has no GPU)
                verbose=False
            )
            
            self.model_loaded = True
            logger.info("✅ Local AI Engine Online (TinyLlama)")
            
        except ImportError:
            logger.warning("llama-cpp-python not installed. Local AI disabled.")
            logger.info("To enable: pip install llama-cpp-python")
            
        except FileNotFoundError:
            logger.warning(f"Model file not found: {self.model_path}")
            logger.info("Download TinyLlama: https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF")
            
        except Exception as e:
            logger.error(f"Local AI initialization failed: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if local AI is ready"""
        return self.model_loaded and self.model is not None
    
    def ask_tutor(self, question: str, subject: str = "General", context: str = "", **kwargs) -> str:
        """
        Local AI Response (Backup Mode)
        """
        if not self.is_available():
            return "⚠️ Backup AI is not available. Please check model installation."
        
        try:
            # Build prompt
            prompt = f"""You are a helpful AI assistant.

Subject: {subject}
Context: {context}

User Question: {question}

Your Answer:"""
            
            # Generate response
            response = self.model(
                prompt,
                max_tokens=512,
                temperature=0.7,
                top_p=0.95,
                stop=["User:", "\n\n\n"]
            )
            
            answer = response['choices'][0]['text'].strip()
            
            return f"🔧 [Backup AI Mode] {answer}"
            
        except Exception as e:
            logger.error(f"Local AI generation failed: {str(e)}")
            return f"Error in backup AI: {str(e)}"
    
    def generate_quiz(self, topic: str, num_questions: int = 5, difficulty: str = "medium") -> str:
        """Fallback quiz generation"""
        if not self.is_available():
            return "Backup AI not available for quiz generation"
        
        prompt = f"Generate {num_questions} {difficulty} quiz questions about {topic}."
        return self.ask_tutor(prompt, subject="Quiz Generation")
    
    def summarize_content(self, text: str, max_length: int = 200) -> str:
        """Fallback summarization"""
        if not self.is_available():
            return "Backup AI not available for summarization"
        
        prompt = f"Summarize this text in {max_length} words:\n\n{text}"
        return self.ask_tutor(prompt, subject="Summarization")
    
    def explain_concept(self, concept: str, grade_level: str = "high school") -> str:
        """Fallback concept explanation"""
        if not self.is_available():
            return "Backup AI not available for concept explanation"
        
        prompt = f"Explain '{concept}' for {grade_level} students."
        return self.ask_tutor(prompt, subject="Education")
    
    def translate_content(self, text: str, target_language: str) -> str:
        """Fallback translation"""
        if not self.is_available():
            return "Backup AI not available for translation"
        
        prompt = f"Translate to {target_language}: {text}"
        return self.ask_tutor(prompt, subject="Translation")


# Singleton instance
_local_service = None

def get_local_service() -> LocalAIService:
    """Get or create local AI service instance"""
    global _local_service
    if _local_service is None:
        _local_service = LocalAIService()
    return _local_service
