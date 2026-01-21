"""
Y.S.M AI System Prompt Loader
Loads the advanced, research-backed system prompt for Y.S.M AI
"""
import os
from pathlib import Path

def get_ysm_ai_system_prompt() -> str:
    """
    Load the advanced Y.S.M AI system prompt from file.
    
    Returns:
        str: The complete system prompt text
    """
    # Get the path to the prompt file
    current_dir = Path(__file__).parent
    prompt_file = current_dir.parent / 'YSM_AI_SYSTEM_PROMPT_V2_ADVANCED.md'
    
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract only the actual prompt content (skip the Python file header comments)
        # The actual prompt starts after the """...""" block
        if '"""' in content:
            parts = content.split('"""')
            # Get the main content after initial comment blocks
            for part in parts[1:]:
                if 'CORE IDENTITY & MISSION' in part or 'SECTION 1' in part:
                    return part.strip()
        
        # If no special markers found, return full content
        return content
        
    except FileNotFoundError:
        # Fallback to basic prompt if file not found
        return get_fallback_prompt()
    except Exception as e:
        print(f"Error loading Y.S.M AI prompt: {e}")
        return get_fallback_prompt()


def get_fallback_prompt() -> str:
    """
    Fallback prompt if advanced  prompt file is not accessible.
    """
    return """You are "Y.S.M AI" — a premium, all-in-one advanced AI assistant created by Yash A Mishra (Rangra Developer).

Your mission is to solve ANY user problem end-to-end across coding, business, design, learning, and troubleshooting.

Core Principles:
1. Provide accurate, actionable, step-by-step solutions
2. Adapt to user's language style (Hinglish/Hindi/English)
3. Be friendly, direct, and professional
4. Never hallucinate - if unsure, clearly state it
5. Give practical implementation guidance, not just theory

You represent premium AI capability and exceptional value in every response."""


# Pre-load the prompt at module level for performance
YSM_AI_PROMPT = get_ysm_ai_system_prompt()


# Quick access function for compatibility
def load_system_prompt() -> str:
    """Alias for get_ysm_ai_system_prompt()"""
    return YSM_AI_PROMPT
