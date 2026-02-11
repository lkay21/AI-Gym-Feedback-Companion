"""
AI recommendation module for the AI Fitness Planner.

Handles all AI-powered fitness recommendations using the Gemini API.
Accepts structured user profiles and user messages, and returns
personalized fitness advice.
"""

from google import genai
from app.database.models import UserProfile


def get_ai_recommendation(profile: UserProfile, message: str, api_key: str) -> str:
    """
    Get AI-powered fitness recommendation based on user profile and message.
    
    This function constructs a prompt from the user profile and message,
    then uses the Gemini API to generate personalized fitness advice.
    
    Args:
        profile: UserProfile object with user information
        message: User's question or fitness request
        api_key: Gemini API key for authentication
        
    Returns:
        str: AI-generated fitness recommendation
        
    Raises:
        ValueError: If API key is not provided
        Exception: If API call fails or response is invalid
    """
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment variables")
    
    client = genai.Client(api_key=api_key)
    
    model_name = "gemini-1.5-flash"
    system_instruction = (
        "You are a fitness focused personal trainer AI. "
        "Provide detailed and personalized fitness advice based on user prompts. "
        "Ensure your responses are clear and relate to what you discern the user is most focused on. "
        "Respond in a friendly but professional tone. "
        "Respond with speed but do not sacrifice detail or clarity."
    )
    
    
    # Build context from user profile
    context_parts = []
    if profile.name:
        context_parts.append(f"User's name: {profile.name}")
    if profile.age:
        context_parts.append(f"Age: {profile.age}")
    if profile.gender:
        context_parts.append(f"Gender: {profile.gender}")
    if profile.height:
        context_parts.append(f"Height: {profile.height}")
    if profile.weight:
        context_parts.append(f"Weight: {profile.weight}")
    if profile.fitness_goals:
        goals_str = ", ".join(profile.fitness_goals)
        context_parts.append(f"Fitness Goals: {goals_str}")
    
    # Combine context with user message
    if context_parts:
        full_prompt = f"User Profile:\n" + "\n".join(context_parts) + f"\n\nUser Question: {message}"
    else:
        full_prompt = message
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=full_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        
        # Extract response text
        if hasattr(response, 'text') and response.text:
            return response.text
        elif hasattr(response, 'candidates') and response.candidates:
            if response.candidates[0].content and response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text
        else:
            raise ValueError("No response text available from the model")
            
    except Exception as e:
        raise Exception(f"Failed to generate AI response: {str(e)}")
