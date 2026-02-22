import os
from pathlib import Path
from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from app.db_instance import db
from app.auth_module.routes import auth_bp
from app.logger import setup_logging, get_logger
import google.generativeai as genai
# from google import genai
# from google.genai.types import GenerateContentConfig, HttpOptions

# Initialize logging
setup_logging()
logger = get_logger(__name__)

# Get Info From ENV - Load from project root
# Get the project root directory (parent of app directory)
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'

# Try loading from project root first, then fallback to current directory
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    logger.debug(f"Loaded environment from: {env_path}")
else:
    # Fallback: try current directory
    load_dotenv()
    logger.debug("Loaded environment from current directory")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not found in environment variables")

# Configures Flask application (initializes with configuration settings,
# sets up database, registers any blueprints)
def create_app():
    app = Flask(__name__)
    logger.info("Creating Flask application")
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "devkey")
    # Use instance folder for database
    instance_path = os.path.join(project_root, 'app', 'instance')
    os.makedirs(instance_path, exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "users.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Session configuration
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours in seconds
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Enable CORS for React Native web and mobile apps
    CORS(app, resources={
        r"/auth/*": {
            "origins": ["http://localhost:8081", "http://localhost:19006", "http://127.0.0.1:8081", "http://127.0.0.1:19006"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        },
        r"/api/*": {
            "origins": ["http://localhost:8081", "http://localhost:19006", "http://127.0.0.1:8081", "http://127.0.0.1:19006"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    db.init_app(app)
    logger.info("Database initialized")

    # Register blueprints
    app.register_blueprint(auth_bp)
    logger.info("Auth blueprint registered")

    # Frontend routes
    @app.route('/')
    def index():
        logger.debug("Index page requested")
        return render_template('login.html')
    
    @app.route('/chat')
    def chat():
        logger.debug("Chat page requested")
        return render_template('chat.html')
    
    # API route for chat
    @app.route('/api/chat', methods=['POST'])
    def chat_api():
        try:
            data = request.get_json()
            message = data.get('message')
            profile = data.get('profile', {})
            
            logger.debug(f"Chat API request received from user")
            
            if not message:
                logger.warning("Chat API request missing message")
                return jsonify({'error': 'Message is required'}), 400
            
            # Build context from user profile if available
            context_parts = []
            if profile:
                if profile.get('name'):
                    context_parts.append(f"User's name: {profile['name']}")
                if profile.get('age'):
                    context_parts.append(f"Age: {profile['age']}")
                if profile.get('gender'):
                    context_parts.append(f"Gender: {profile['gender']}")
                if profile.get('height'):
                    context_parts.append(f"Height: {profile['height']}")
                if profile.get('weight'):
                    context_parts.append(f"Weight: {profile['weight']}")
            
            # Combine context with user message
            if context_parts:
                full_prompt = f"User Profile:\n" + "\n".join(context_parts) + f"\n\nUser Question: {message}"
            else:
                full_prompt = message
            
            logger.debug(f"Calling LLM with prompt length: {len(full_prompt)}")
            # Get AI response
            response_text = make_llm_call(full_prompt)
            logger.debug(f"LLM response received, length: {len(response_text)}")
            
            return jsonify({'response': response_text}), 200
            
        except ValueError as e:
            if "GEMINI_API_KEY" in str(e):
                logger.error("GEMINI_API_KEY not configured")
                return jsonify({'error': 'AI service is not configured. Please set GEMINI_API_KEY in your environment variables.'}), 500
            logger.error(f"ValueError in chat API: {str(e)}")
            return jsonify({'error': str(e)}), 500
        except Exception as e:
            logger.error(f"Unexpected error in chat API: {str(e)}", exc_info=True)
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    return app

# Simple Prompt LLM Call Function, Call on Element Submission via Frontend
def make_llm_call(prompt):
    logger.debug("make_llm_call invoked")
    
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not set")
        raise ValueError("GEMINI_API_KEY is not set in environment variables")
    
    try:
        logger.debug("Configuring Gemini API")
        genai.configure(api_key=GEMINI_API_KEY)

        # Use a valid Gemini model name
        model_name = "gemini-1.5-flash"
        system_instruction = (
            "You are a fitness focused personal trainer AI. "
            "Provide detailed and personalized fitness advice based on user prompts. "
            "Ensure your responses are clear and relate to what you discern the user is most focused on. "
            "Respond in a friendly but professional tone. "
            "Respond with speed but do not sacrifice detail or clarity."
        )

        logger.debug(f"Creating GenerativeModel with model: {model_name}")
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction
        )

        # Next Steps:
        # Set up Vector DB for RAG that keeps user prompt history and relevant user external input context
        # Integration with LangChain and Multi-Turn Dialogue Management
        # context = contextualize_model(prompt, k=5)

        # context_dicts = {
        #     "user_profile":{
        #         "name":
        #         "age":
        #         "weight":
        #         "height":
        #     },
        #     "context": context,
        #     "prompt": prompt
        # }

        # context_prompt = f"Given User Information and Previous Most Relevant Context, generate a personalized response. Context Dicts: {context_dicts}"

        logger.debug("Generating content from Gemini API")
        response = model.generate_content(
            contents=prompt
        )
        
        # Check if response has text
        if hasattr(response, 'text') and response.text:
            logger.info("Successfully generated LLM response")
            return response.text
        elif hasattr(response, 'candidates') and response.candidates:
            # Try to get text from candidates
            if response.candidates[0].content and response.candidates[0].content.parts:
                logger.info("Successfully generated LLM response from candidates")
                return response.candidates[0].content.parts[0].text
        else:
            logger.error("No response text available from the model")
            raise ValueError("No response text available from the model")
            
    except Exception as e:
        logger.error(f"Error generating content from Gemini API: {str(e)}", exc_info=True)
        raise Exception(f"Failed to generate AI response: {str(e)}")

    # add_to_vector_db(prompt)

# RAG with LangChain for best contextualization?
def contextualize_model(query, k):
    pass

# Add user prompt/data to vector DB for RAG
def add_to_vector_db():
    pass


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
    

if __name__ == "__main__":
    # prompt = input("Enter your fitness prompt: ")
    # make_llm_call(prompt)
    main()