"""
Google Gemini API client for chatbot responses
"""
import os
import google.generativeai as genai
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'

if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Use models/ prefix for model names
# Available models: gemini-2.0-flash, gemini-2.5-flash, gemini-2.5-pro
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash")


class GeminiClient:
    """Client for interacting with Google Gemini API"""
    
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment variables")
        
        genai.configure(api_key=GEMINI_API_KEY)
        # Remove models/ prefix if present for GenerativeModel (it adds it automatically)
        model_name = GEMINI_MODEL.replace("models/", "") if GEMINI_MODEL.startswith("models/") else GEMINI_MODEL
        self.model_name = GEMINI_MODEL  # Keep full name for reference
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=self._get_system_instruction()
        )
    
    def _get_system_instruction(self) -> str:
        """Get the system instruction for the AI model"""
        return (
            "You are a friendly and knowledgeable fitness-focused personal trainer AI assistant. "
            "Your role is to provide personalized fitness advice, workout recommendations, nutrition guidance, "
            "and motivation to help users achieve their health and fitness goals. "
            "\n\n"
            "Guidelines:\n"
            "- Provide clear, actionable, and safe fitness advice\n"
            "- Consider the user's profile information (age, height, weight, fitness goals) when giving recommendations\n"
            "- Be encouraging and supportive while maintaining professionalism\n"
            "- If you don't know something, admit it rather than guessing\n"
            "- Always prioritize safety and recommend consulting healthcare professionals for medical concerns\n"
            "- Use a conversational, friendly tone\n"
            "- Break down complex concepts into easy-to-understand explanations\n"
            "- Provide specific, practical advice when possible"
        )
    
    def generate_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate AI response to user message
        
        Args:
            user_message: The user's message/query
            conversation_history: List of previous messages in format [{"role": "user", "content": "..."}, ...]
            user_profile: User profile data (age, height, weight, fitness_goals, etc.)
        
        Returns:
            AI response text
        """
        try:
            # Build the prompt with context
            prompt_parts = []
            
            # Add user profile context if available
            if user_profile:
                profile_context = self._build_profile_context(user_profile)
                if profile_context:
                    prompt_parts.append(profile_context)
            
            # Add conversation history if available
            if conversation_history:
                # Format history for Gemini (it expects a list of content parts)
                for msg in conversation_history[-10:]:  # Last 10 messages for context
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    if role == 'user':
                        prompt_parts.append(f"User: {content}")
                    elif role == 'assistant':
                        prompt_parts.append(f"Assistant: {content}")
            
            # Add current user message
            prompt_parts.append(f"User: {user_message}")
            prompt_parts.append("Assistant:")
            
            # Generate response
            response = self.model.generate_content(
                contents=prompt_parts,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                }
            )
            
            # Extract response text
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            elif hasattr(response, 'candidates') and response.candidates:
                if response.candidates[0].content and response.candidates[0].content.parts:
                    return response.candidates[0].content.parts[0].text.strip()
            
            raise ValueError("No response text available from the model")
            
        except Exception as e:
            error_msg = str(e)
            # Handle specific Gemini API errors
            if "safety" in error_msg.lower() or "blocked" in error_msg.lower():
                raise Exception("Your message was blocked by content filters. Please rephrase your question.")
            elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
                raise Exception("API quota exceeded. Please try again later.")
            elif "invalid" in error_msg.lower() or "api key" in error_msg.lower():
                raise Exception("Invalid API configuration. Please check your Gemini API key.")
            else:
                raise Exception(f"Failed to generate AI response: {error_msg}")
    
    def _build_profile_context(self, profile: Dict[str, Any]) -> str:
        """Build context string from user profile"""
        context_parts = []
        
        if profile.get('name'):
            context_parts.append(f"Name: {profile['name']}")
        if profile.get('age'):
            context_parts.append(f"Age: {profile['age']} years old")
        if profile.get('gender'):
            context_parts.append(f"Gender: {profile['gender']}")
        if profile.get('height'):
            context_parts.append(f"Height: {profile['height']}")
        if profile.get('weight'):
            context_parts.append(f"Weight: {profile['weight']}")
        if profile.get('fitness_goals'):
            goals = profile['fitness_goals']
            if isinstance(goals, list):
                goals_str = ", ".join(goals)
            else:
                goals_str = str(goals)
            context_parts.append(f"Fitness Goals: {goals_str}")
        if profile.get('activity_level'):
            context_parts.append(f"Activity Level: {profile['activity_level']}")
        
        if context_parts:
            return "User Profile Information:\n" + "\n".join(f"- {part}" for part in context_parts) + "\n"
        return ""