"""
AI Integration Package
Provides access to multiple AI services: ChatGPT, Gemini, Claude
"""

from .chatgpt import ChatGPTService, get_chatgpt_service
from .gemini import GeminiService, get_gemini_service
from .claude import ClaudeService, get_claude_service
from .manager import AIServiceManager, get_ai_manager

__all__ = [
    # ChatGPT
    'ChatGPTService',
    'get_chatgpt_service',
    # Gemini
    'GeminiService',
    'get_gemini_service',
    # Claude
    'ClaudeService',
    'get_claude_service',
    # Unified Manager
    'AIServiceManager',
    'get_ai_manager',
]
