"""
Anthropic Claude AI Integration Service
Provides advanced AI-powered features using Claude models
"""
from typing import Dict, List, Optional
import logging
from decouple import config

logger = logging.getLogger(__name__)


class ClaudeService:
    """
    Anthropic Claude AI Service for Advanced Educational Features
    Supports Claude 3 Opus, Sonnet, and Haiku models
    """
    
    def __init__(self):
        """Initialize Claude service with API credentials"""
        try:
            self.api_key = config('CLAUDE_API_KEY')
        except Exception:
            logger.warning("CLAUDE_API_KEY not found in environment variables")
            raise ValueError("Claude API key not configured. Please set CLAUDE_API_KEY in .env file")
        
        # Initialize Anthropic client
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
        
        # Model configuration
        self.default_model = config('CLAUDE_MODEL', default='claude-3-5-sonnet-20241022')
        self.temperature = float(config('CLAUDE_TEMPERATURE', default='0.7'))
        self.max_tokens = int(config('CLAUDE_MAX_TOKENS', default='2000'))
    
    def generate_content(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate content using Claude models
        
        Args:
            prompt: Input prompt
            model: Model to use (default: claude-3-5-sonnet)
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length
            
        Returns:
            Generated text
        """
        try:
            response = self.client.messages.create(
                model=model or self.default_model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature if temperature is not None else self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Claude API error: {error_msg}")
            
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                raise Exception("Claude authentication failed. Please check API credentials.")
            elif "rate_limit" in error_msg.lower() or "quota" in error_msg.lower():
                raise Exception("Claude rate limit exceeded. Please try again later.")
            else:
                raise Exception(f"Claude service error: {error_msg}")
    
    def ask_tutor(self, question: str, subject: str = "General", context: str = "") -> str:
        """AI Tutor using Claude"""
        prompt = f"""You are an expert educational tutor specializing in {subject}.
        Provide clear, detailed, and engaging explanations. Use examples where helpful.
        
        {f'Context: {context}' if context else ''}
        
        Question: {question}
        
        Please provide a comprehensive educational answer."""
        
        return self.generate_content(prompt)
    
    def generate_quiz(
        self,
        topic: str,
        num_questions: int = 5,
        difficulty: str = "medium"
    ) -> str:
        """Generate quiz using Claude"""
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
        """Summarize content using Claude"""
        prompt = f"""Summarize the following content in approximately {max_length} words.
        Focus on key concepts and main ideas.
        
        Content:
        {text}"""
        
        return self.generate_content(prompt)
    
    def explain_concept(self, concept: str, grade_level: str = "high school") -> str:
        """Explain concepts using Claude"""
        prompt = f"""Explain the concept of "{concept}" for {grade_level} students.
        
        Use:
        - Simple, clear language
        - Relatable examples
        - Step-by-step breakdown if needed
        
        Make it engaging and easy to understand."""
        
        return self.generate_content(prompt)
    
    def translate_content(self, text: str, target_language: str) -> str:
        """Translate using Claude"""
        prompt = f"Translate the following text to {target_language}. Maintain educational tone:\n\n{text}"
        return self.generate_content(prompt)


# Singleton instance
_claude_service = None

def get_claude_service() -> ClaudeService:
    """Get or create Claude service instance"""
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudeService()
    return _claude_service
