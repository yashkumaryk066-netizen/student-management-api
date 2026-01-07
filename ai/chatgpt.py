"""
ChatGPT AI Integration Service
Provides advanced AI-powered features using OpenAI's GPT models
"""
import os
import openai
from typing import Dict, List, Optional, Union
import logging
from decouple import config

logger = logging.getLogger(__name__)


class ChatGPTService:
    """
    Premium ChatGPT Service for Advanced AI-Powered Features
    Supports multiple use cases: tutoring, content generation, analysis, and more
    """
    
    def __init__(self):
        """Initialize ChatGPT service with API credentials"""
        try:
            self.api_key = config('OPENAI_API_KEY')
        except Exception:
            logger.warning("OPENAI_API_KEY not found in environment variables")
            raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in .env file")
        
        # Initialize OpenAI client (v2.x pattern)
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)
        
        # Default model configuration
        self.default_model = config('OPENAI_MODEL', default='gpt-4-turbo-preview')
        self.temperature = float(config('OPENAI_TEMPERATURE', default='0.7'))
        self.max_tokens = int(config('OPENAI_MAX_TOKENS', default='2000'))
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Union[str, Dict]:
        """
        Generate chat completion using GPT models
        
        Args:
            messages: List of message objects with 'role' and 'content'
            model: Model to use (default: gpt-4-turbo-preview)
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length
            stream: Whether to stream the response
            
        Returns:
            Generated text or full response object
        """
        try:
            response = self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                temperature=temperature if temperature is not None else self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                stream=stream
            )
            
            if stream:
                return response
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"ChatGPT API error: {error_msg}")
            
            # Handle specific error types based on message content
            if "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                raise Exception("AI service authentication failed. Please check API credentials.")
            elif "rate_limit" in error_msg.lower() or "quota" in error_msg.lower():
                raise Exception("AI service rate limit exceeded. Please try again later.")
            elif "invalid" in error_msg.lower():
                raise Exception(f"Invalid AI request: {error_msg}")
            else:
                raise Exception(f"AI service error: {error_msg}")
    
    def ask_tutor(self, question: str, subject: str = "General", context: str = "") -> str:
        """
        AI Tutor - Answer student questions with detailed explanations
        
        Args:
            question: Student's question
            subject: Subject area (Math, Science, etc.)
            context: Additional context or background
            
        Returns:
            Detailed educational response
        """
        system_prompt = f"""You are an expert educational tutor specializing in {subject}. 
        Provide clear, detailed, and engaging explanations. Use examples where helpful.
        Break down complex topics into simple steps. Encourage learning and curiosity."""
        
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        
        if context:
            messages.append({"role": "user", "content": f"Context: {context}"})
        
        messages.append({"role": "user", "content": question})
        
        return self.chat_completion(messages)
    
    def generate_quiz(
        self,
        topic: str,
        num_questions: int = 5,
        difficulty: str = "medium",
        question_type: str = "multiple_choice"
    ) -> str:
        """
        Generate educational quizzes automatically
        
        Args:
            topic: Quiz topic
            num_questions: Number of questions
            difficulty: easy, medium, or hard
            question_type: multiple_choice, true_false, or short_answer
            
        Returns:
            JSON formatted quiz questions
        """
        prompt = f"""Generate {num_questions} {difficulty} level {question_type} questions about {topic}.
        
        Return as JSON array with this structure:
        [
            {{
                "question": "Question text",
                "options": ["A", "B", "C", "D"],  // for multiple choice
                "correct_answer": "A",
                "explanation": "Why this is correct"
            }}
        ]
        
        Make questions educational and accurate."""
        
        messages = [
            {"role": "system", "content": "You are an expert quiz generator for educational purposes."},
            {"role": "user", "content": prompt}
        ]
        
        return self.chat_completion(messages, temperature=0.8)
    
    def summarize_content(self, text: str, max_length: int = 200) -> str:
        """
        Summarize long educational content
        
        Args:
            text: Content to summarize
            max_length: Maximum summary length in words
            
        Returns:
            Concise summary
        """
        prompt = f"""Summarize the following content in approximately {max_length} words.
        Focus on key concepts and main ideas.
        
        Content:
        {text}
        """
        
        messages = [
            {"role": "system", "content": "You are an expert at creating concise, accurate summaries."},
            {"role": "user", "content": prompt}
        ]
        
        return self.chat_completion(messages, max_tokens=max_length * 2)
    
    def grade_assignment(
        self,
        assignment_text: str,
        rubric: str,
        max_score: int = 100
    ) -> Dict[str, Union[int, str, List]]:
        """
        AI-powered assignment grading with feedback
        
        Args:
            assignment_text: Student's submission
            rubric: Grading criteria
            max_score: Maximum possible score
            
        Returns:
            Score, feedback, and strengths/weaknesses
        """
        prompt = f"""Grade this assignment based on the provided rubric.
        
        RUBRIC:
        {rubric}
        
        ASSIGNMENT:
        {assignment_text}
        
        Provide response in JSON format:
        {{
            "score": <number out of {max_score}>,
            "overall_feedback": "General comments",
            "strengths": ["strength 1", "strength 2"],
            "areas_for_improvement": ["area 1", "area 2"],
            "detailed_comments": "Detailed explanation of grading"
        }}
        """
        
        messages = [
            {"role": "system", "content": "You are a fair and constructive educational grader."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.chat_completion(messages, temperature=0.3)
        
        # Parse JSON response
        import json
        try:
            return json.loads(response)
        except:
            return {
                "score": 0,
                "overall_feedback": response,
                "error": "Could not parse grading response"
            }
    
    def explain_concept(self, concept: str, grade_level: str = "high school") -> str:
        """
        Explain complex concepts in age-appropriate language
        
        Args:
            concept: Concept to explain
            grade_level: Target education level
            
        Returns:
            Clear explanation with examples
        """
        prompt = f"""Explain the concept of "{concept}" for {grade_level} students.
        
        Use:
        - Simple, clear language
        - Relatable examples
        - Step-by-step breakdown if needed
        - Visual descriptions where helpful
        
        Make it engaging and easy to understand."""
        
        messages = [
            {"role": "system", "content": f"You are an expert educator who explains concepts to {grade_level} students."},
            {"role": "user", "content": prompt}
        ]
        
        return self.chat_completion(messages)
    
    def translate_content(self, text: str, target_language: str) -> str:
        """
        Translate educational content to different languages
        
        Args:
            text: Text to translate
            target_language: Target language (e.g., "Hindi", "Spanish")
            
        Returns:
            Translated text
        """
        prompt = f"Translate the following text to {target_language}. Maintain educational tone and accuracy:\n\n{text}"
        
        messages = [
            {"role": "system", "content": "You are an expert translator specializing in educational content."},
            {"role": "user", "content": prompt}
        ]
        
        return self.chat_completion(messages)
    
    def generate_lesson_plan(
        self,
        topic: str,
        duration_minutes: int = 45,
        grade_level: str = "high school"
    ) -> str:
        """
        Generate comprehensive lesson plans
        
        Args:
            topic: Lesson topic
            duration_minutes: Class duration
            grade_level: Target grade level
            
        Returns:
            Structured lesson plan
        """
        prompt = f"""Create a {duration_minutes}-minute lesson plan on "{topic}" for {grade_level} students.
        
        Include:
        1. Learning Objectives (2-3 specific goals)
        2. Materials Needed
        3. Introduction (5 min)
        4. Main Activity (25-30 min)
        5. Assessment/Practice (10 min)
        6. Conclusion & Homework (5 min)
        7. Differentiation strategies
        
        Make it practical and engaging."""
        
        messages = [
            {"role": "system", "content": "You are an experienced curriculum designer and educator."},
            {"role": "user", "content": prompt}
        ]
        
        return self.chat_completion(messages, max_tokens=3000)
    
    def analyze_student_writing(self, writing_sample: str) -> Dict:
        """
        Analyze student writing for grammar, style, and structure
        
        Args:
            writing_sample: Student's written work
            
        Returns:
            Detailed analysis with suggestions
        """
        prompt = f"""Analyze this student writing sample for:
        1. Grammar and spelling
        2. Sentence structure
        3. Clarity and coherence
        4. Vocabulary usage
        5. Overall organization
        
        Provide constructive feedback in JSON format:
        {{
            "grammar_score": <0-10>,
            "structure_score": <0-10>,
            "clarity_score": <0-10>,
            "vocabulary_score": <0-10>,
            "key_issues": ["issue 1", "issue 2"],
            "suggestions": ["suggestion 1", "suggestion 2"],
            "positive_points": ["strength 1", "strength 2"]
        }}
        
        WRITING SAMPLE:
        {writing_sample}
        """
        
        messages = [
            {"role": "system", "content": "You are an expert writing instructor and editor."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.chat_completion(messages, temperature=0.4)
        
        import json
        try:
            return json.loads(response)
        except:
            return {"error": "Could not parse analysis", "raw_response": response}
    
    def custom_prompt(self, prompt: str, system_message: str = None) -> str:
        """
        Send custom prompts for flexible AI interactions
        
        Args:
            prompt: User's prompt
            system_message: Optional system context
            
        Returns:
            AI response
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        return self.chat_completion(messages)


# Singleton instance
_chatgpt_service = None

def get_chatgpt_service() -> ChatGPTService:
    """Get or create ChatGPT service instance"""
    global _chatgpt_service
    if _chatgpt_service is None:
        _chatgpt_service = ChatGPTService()
    return _chatgpt_service
