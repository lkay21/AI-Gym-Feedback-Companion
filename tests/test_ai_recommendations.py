"""
Unit tests for the AI recommendations module.

Tests cover:
- AI recommendation generation with mocked Gemini API
- Profile integration into prompts
- Error handling for missing API keys
- Response parsing and validation
"""

import unittest
from unittest.mock import patch, MagicMock
from app.database.models import UserProfile
from app.chatbot.ai_recommendations import get_ai_recommendation


class TestAIRecommendationBasic(unittest.TestCase):
    """Test basic AI recommendation functionality."""
    
    @patch('app.chatbot.ai_recommendations.genai')
    def test_get_recommendation_with_full_profile(self, mock_genai):
        """Test getting recommendation with complete user profile."""
        # Setup mock
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = "Here's your fitness recommendation..."
        mock_model.generate_content.return_value = mock_response
        
        # Create profile
        profile = UserProfile(
            name="John Doe",
            age=30,
            gender="male",
            height="5'10\"",
            weight="180 lbs",
            fitness_goals=["lose weight", "build muscle"]
        )
        
        # Call function
        response = get_ai_recommendation(
            profile=profile,
            message="What should I do for fitness?",
            api_key="test_key"
        )
        
        # Assertions
        self.assertEqual(response, "Here's your fitness recommendation...")
        mock_genai.configure.assert_called_once_with(api_key="test_key")
        mock_model.generate_content.assert_called_once()
    
    @patch('app.chatbot.ai_recommendations.genai')
    def test_get_recommendation_with_minimal_profile(self, mock_genai):
        """Test getting recommendation with minimal user profile."""
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = "Basic fitness advice"
        mock_model.generate_content.return_value = mock_response
        
        profile = UserProfile(name="Jane Doe")
        
        response = get_ai_recommendation(
            profile=profile,
            message="How do I start exercising?",
            api_key="test_key"
        )
        
        self.assertEqual(response, "Basic fitness advice")
        mock_model.generate_content.assert_called_once()
    
    @patch('app.chatbot.ai_recommendations.genai')
    def test_recommendation_includes_profile_data(self, mock_genai):
        """Test that profile data is included in the prompt."""
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = "Personalized recommendation"
        mock_model.generate_content.return_value = mock_response
        
        profile = UserProfile(
            name="Alice",
            age=25,
            weight="130 lbs",
            fitness_goals=["endurance"]
        )
        
        get_ai_recommendation(
            profile=profile,
            message="What workout for me?",
            api_key="test_key"
        )
        
        # Get the prompt that was sent
        call_args = mock_model.generate_content.call_args
        prompt = call_args[1]['contents'] if 'contents' in call_args[1] else call_args[0][0]
        
        # Check that profile data is in the prompt
        self.assertIn("Alice", prompt)
        self.assertIn("25", prompt)
        self.assertIn("130 lbs", prompt)
        self.assertIn("endurance", prompt)


class TestAIRecommendationErrorHandling(unittest.TestCase):
    """Test error handling in AI recommendations."""
    
    def test_missing_api_key(self):
        """Test that missing API key raises ValueError."""
        profile = UserProfile(name="Bob")
        
        with self.assertRaises(ValueError) as context:
            get_ai_recommendation(
                profile=profile,
                message="Test message",
                api_key=None
            )
        
        self.assertIn("GEMINI_API_KEY", str(context.exception))
    
    def test_empty_api_key(self):
        """Test that empty API key raises ValueError."""
        profile = UserProfile(name="Carol")
        
        with self.assertRaises(ValueError) as context:
            get_ai_recommendation(
                profile=profile,
                message="Test message",
                api_key=""
            )
        
        self.assertIn("GEMINI_API_KEY", str(context.exception))
    
    @patch('app.chatbot.ai_recommendations.genai')
    def test_api_call_failure(self, mock_genai):
        """Test that API call failures raise Exception."""
        mock_genai.configure.side_effect = Exception("API connection failed")
        
        profile = UserProfile(name="David")
        
        with self.assertRaises(Exception):
            get_ai_recommendation(
                profile=profile,
                message="Test message",
                api_key="test_key"
            )
    
    @patch('app.chatbot.ai_recommendations.genai')
    def test_no_response_text(self, mock_genai):
        """Test handling of responses without text."""
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = None
        mock_response.candidates = []
        # Make hasattr work correctly for our mock
        def mock_hasattr(obj, attr):
            if attr == 'text':
                return True  # has text attribute
            elif attr == 'candidates':
                return True  # has candidates attribute
            return hasattr(obj, attr)
        
        # Use side_effect to control the response behavior
        with patch('builtins.hasattr', side_effect=mock_hasattr):
            mock_model.generate_content.return_value = mock_response
            
            profile = UserProfile(name="Eve")
            
            with self.assertRaises(Exception) as context:
                get_ai_recommendation(
                    profile=profile,
                    message="Test message",
                    api_key="test_key"
                )
            
            self.assertIn("No response text", str(context.exception))


class TestAIRecommendationResponseParsing(unittest.TestCase):
    """Test response parsing from Gemini API."""
    
    @patch('app.chatbot.ai_recommendations.genai')
    def test_response_with_text_attribute(self, mock_genai):
        """Test parsing response with text attribute."""
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = "AI-generated response text"
        mock_model.generate_content.return_value = mock_response
        
        profile = UserProfile(name="Frank")
        
        response = get_ai_recommendation(
            profile=profile,
            message="Test",
            api_key="test_key"
        )
        
        self.assertEqual(response, "AI-generated response text")
    
    @patch('app.chatbot.ai_recommendations.genai')
    def test_response_with_candidates(self, mock_genai):
        """Test parsing response from candidates fallback."""
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Create mock candidates response
        mock_response = MagicMock()
        mock_response.text = None  # No text attribute
        mock_part = MagicMock()
        mock_part.text = "Response from candidates"
        mock_content = MagicMock()
        mock_content.parts = [mock_part]
        mock_candidate = MagicMock()
        mock_candidate.content = mock_content
        mock_response.candidates = [mock_candidate]
        mock_model.generate_content.return_value = mock_response
        
        profile = UserProfile(name="Grace")
        
        response = get_ai_recommendation(
            profile=profile,
            message="Test",
            api_key="test_key"
        )
        
        self.assertEqual(response, "Response from candidates")


class TestAIRecommendationPromptConstruction(unittest.TestCase):
    """Test prompt construction from profile and message."""
    
    @patch('app.chatbot.ai_recommendations.genai')
    def test_prompt_with_all_profile_fields(self, mock_genai):
        """Test that all profile fields are included in prompt."""
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = "Response"
        mock_model.generate_content.return_value = mock_response
        
        profile = UserProfile(
            name="Henry",
            age=35,
            gender="male",
            height="6'0\"",
            weight="200 lbs",
            fitness_goals=["strength", "endurance"]
        )
        
        get_ai_recommendation(
            profile=profile,
            message="How to train?",
            api_key="test_key"
        )
        
        call_args = mock_model.generate_content.call_args
        prompt = call_args[1]['contents'] if 'contents' in call_args[1] else call_args[0][0]
        
        # Verify all fields are in prompt
        self.assertIn("Henry", prompt)
        self.assertIn("35", prompt)
        self.assertIn("male", prompt)
        self.assertIn("6'0\"", prompt)
        self.assertIn("200 lbs", prompt)
        self.assertIn("strength", prompt)
        self.assertIn("endurance", prompt)
        self.assertIn("How to train?", prompt)
    
    @patch('app.chatbot.ai_recommendations.genai')
    def test_prompt_with_empty_profile(self, mock_genai):
        """Test prompt construction with minimal profile."""
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = "Response"
        mock_model.generate_content.return_value = mock_response
        
        profile = UserProfile(name=None)
        
        get_ai_recommendation(
            profile=profile,
            message="Fitness tips?",
            api_key="test_key"
        )
        
        call_args = mock_model.generate_content.call_args
        prompt = call_args[1]['contents'] if 'contents' in call_args[1] else call_args[0][0]
        
        # Should still include the message
        self.assertIn("Fitness tips?", prompt)


if __name__ == "__main__":
    unittest.main()
