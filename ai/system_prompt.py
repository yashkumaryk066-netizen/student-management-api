"""
Y.S.M AI System Prompt Loader
Loads the advanced, research-backed system prompt for Y.S.M AI
"""
import os
from pathlib import Path

def get_ysm_ai_system_prompt(force_reload: bool = False) -> str:
    """
    Load the advanced Y.S.M AI system prompt from file.
    
    Args:
        force_reload: If True, bypass cache and reload from disk
        
    Returns:
        str: The complete system prompt text
    """
    global YSM_AI_PROMPT
    
    # Return cached version if available and not forced to reload
    if YSM_AI_PROMPT and not force_reload:
        return YSM_AI_PROMPT

    try:
        # Robust path resolution
        # Go up two levels from this file (ai/system_prompt.py -> ai -> root)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_file = os.path.join(base_dir, 'YSM_AI_SYSTEM_PROMPT_V2_ADVANCED.md')
        
        if not os.path.exists(prompt_file):
            # Try alternative location if structure is different
            prompt_file = os.path.join(base_dir, 'manufatures', 'YSM_AI_SYSTEM_PROMPT_V2_ADVANCED.md')
            
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract only the actual prompt content (skip the Python file header comments)
        # The actual prompt starts after the """...""" block if it was a python file, 
        # but here we are reading a markdown file, so we take it all.
        # However, purely for safety against accidental python headers:
        if content.strip().startswith('"""') and '"""' in content[3:]:
            parts = content.split('"""')
            # Get the main content after initial comment blocks
            for part in parts[1:]:
                if 'CORE IDENTITY & MISSION' in part or 'SECTION 1' in part:
                    final_prompt = part.strip()
                    break
            else:
                final_prompt = content
        else:
            final_prompt = content
            
        # Update cache
        YSM_AI_PROMPT = final_prompt
        return final_prompt
        
    except FileNotFoundError:
        # Fallback to basic prompt if file not found
        return get_fallback_prompt()
    except Exception as e:
        print(f"Error loading Y.S.M AI prompt: {e}")
        return get_fallback_prompt()


def get_fallback_prompt() -> str:
    """
    Fallback prompt if advanced prompt file is not accessible.
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


# Global cache
YSM_AI_PROMPT = None

# Pre-load the prompt at module level for performance
# But don't crash if it fails during import
try:
    get_ysm_ai_system_prompt()
except:
    pass


# Quick access function for compatibility
def load_system_prompt(force_reload: bool = False) -> str:
    """Alias for get_ysm_ai_system_prompt()"""
    return get_ysm_ai_system_prompt(force_reload=force_reload)
