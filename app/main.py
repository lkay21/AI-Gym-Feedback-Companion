import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from app.db_instance import db
from app.auth_module.routes import auth_bp
from app.database.models import UserProfile
from app.chatbot.ai_recommendations import get_ai_recommendation
from app.fitness.benchmark_loader import load_fitness_benchmarks
from app.logger import get_logger

logger = get_logger(__name__)

# Get Info From ENV - Load from project root
# Get the project root directory (parent of app directory)
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'

# Try loading from project root first, then fallback to current directory
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    # Fallback: try current directory
    load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configures Flask application (initializes with configuration settings,
# sets up database, registers any blueprints)
def create_app():
    """
    Create and configure the Flask application.
    
    Initializes:
    - Database instance
    - Auth blueprint
    - Fitness benchmarks (integration verification)
    - API routes for frontend
    
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "devkey")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Register auth blueprint
    app.register_blueprint(auth_bp)
    
    # Load fitness benchmarks on startup for integration verification
    try:
        benchmarks = load_fitness_benchmarks()
        logger.info("Fitness benchmarks loaded successfully on startup")
        app.benchmarks = benchmarks
    except Exception as e:
        logger.error(f"Failed to load fitness benchmarks: {str(e)}")
        raise

    # Frontend routes
    @app.route('/')
    def index():
        """Render login page."""
        return render_template('login.html')
    
    @app.route('/chat')
    def chat():
        """Render chat page."""
        return render_template('chat.html')
    
    # API route for chat
    @app.route('/api/chat', methods=['POST'])
    def chat_api():
        """
        Handle chat API requests.
        
        Accepts a JSON payload with:
        - message: User's fitness question
        - profile: User profile data (name, age, gender, height, weight, fitness_goals)
        
        Returns:
        - 200: {'response': AI-generated fitness recommendation}
        - 400: Missing message in request
        - 500: API configuration error or processing error
        """
        try:
            data = request.get_json()
            message = data.get('message')
            profile_data = data.get('profile', {})
            
            if not message:
                logger.warning("Chat request received without message")
                return jsonify({'error': 'Message is required'}), 400
            
            # Create structured user profile object from request data
            logger.debug(f"Creating user profile from request data: {profile_data}")
            profile = UserProfile.from_dict(profile_data)
            logger.info(f"User profile created: {profile}")
            
            # Get AI recommendation using the AI module
            logger.debug(f"Requesting AI recommendation for user: {profile.name}")
            response_text = get_ai_recommendation(
                profile=profile,
                message=message,
                api_key=GEMINI_API_KEY
            )
            logger.info(f"AI recommendation generated successfully for user: {profile.name}")
            
            return jsonify({'response': response_text}), 200
            
        except ValueError as e:
            error_msg = str(e)
            if "GEMINI_API_KEY" in error_msg:
                logger.error("AI service not configured: GEMINI_API_KEY missing")
                return jsonify({'error': 'AI service is not configured. Please set GEMINI_API_KEY in your environment variables.'}), 500
            logger.error(f"ValueError in chat API: {error_msg}")
            return jsonify({'error': error_msg}), 500
        except Exception as e:
            logger.error(f"Unexpected error in chat API: {str(e)}", exc_info=True)
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    return app


# Future: RAG and LangChain Integration for Advanced Features
# ============================================================================
# The following functions are placeholders for future enhancements:
# - Vector DB integration for RAG (Retrieval Augmented Generation)
# - LangChain integration for multi-turn dialogue management
# - User prompt history tracking and context management
# ============================================================================

def contextualize_model(query: str, k: int = 5) -> list:
    """
    Placeholder for future RAG contextualization.
    
    Will retrieve k most relevant context pieces for a query from vector DB.
    
    Args:
        query: User's question
        k: Number of relevant contexts to retrieve
        
    Returns:
        list: Relevant context chunks (empty until implemented)
    """
    pass


def add_to_vector_db(prompt: str, profile: UserProfile) -> None:
    """
    Placeholder for future vector DB integration.
    
    Will store user prompts and interactions for retrieval and RAG.
    
    Args:
        prompt: User's prompt/question
        profile: UserProfile object for context
    """
    pass


def main():
    """
    Main entry point for the application.
    
    Creates the Flask app, initializes the database, and starts the server.
    """
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    

if __name__ == "__main__":
    main()