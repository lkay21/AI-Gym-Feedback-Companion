import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from app.db_instance import db
from app.auth_module.routes import auth_bp
from app.profile_module.routes import profile_bp
from app.auth_module.models import User  # Import User model so tables are created
from app.chat_module.routes import chat_bp as chat_module_bp
from app.fitness.benchmark_loader import load_fitness_benchmarks
from app.chatbot.ai_recommendations import get_ai_recommendation
from app.logger import get_logger
from app.core.error_handling import register_error_handlers
from app.core.errors import AppError, ValidationError, DatabaseError
from app.database.models import UserProfile

# Initialize logger
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

# Get Gemini API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configures Flask application (initializes with configuration settings,
# sets up database, registers any blueprints)
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "devkey")
    # Use instance folder for database
    instance_path = os.path.join(project_root, 'app', 'instance')
    os.makedirs(instance_path, exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "users.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024
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
    register_error_handlers(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    # Chat module routes: health-onboarding, chat endpoints, plan generation
    app.register_blueprint(chat_module_bp, url_prefix='/api/chat')
    # Register profile blueprint
    app.register_blueprint(profile_bp)

    # Load fitness benchmarks on startup for integration verification
    try:
        benchmarks = load_fitness_benchmarks()
        app.benchmarks = benchmarks
    except Exception as exc:
        raise RuntimeError(f"Failed to load fitness benchmarks: {exc}") from exc

    # Frontend routes
    @app.route('/')
    def index():
        return render_template('login.html')
    
    @app.route('/chat')
    def chat():
        return render_template('chat.html')

    # API route for scaffolding test (tests AI recommendation flow)
    @app.route('/api/scaffolding/chat', methods=['POST'])
    def chat_api():
        try:
            data = request.get_json() or {}
            message = data.get('message')
            profile_data = data.get('profile', {})

            if not message:
                logger.warning("Chat request received without message")
                raise ValidationError("Message is required")

            logger.debug(f"Creating user profile from request data: {profile_data}")
            profile = UserProfile.from_dict(profile_data)
            logger.info(f"User profile created: {profile}")

            logger.debug(f"Requesting AI recommendation for user: {profile.name}")
            response_text = get_ai_recommendation(
                profile=profile,
                message=message,
                api_key=GEMINI_API_KEY
            )
            logger.info(f"AI recommendation generated successfully for user: {profile.name}")

            return jsonify({'response': response_text}), 200

        except ValueError as exc:
            error_msg = str(exc)
            if "GEMINI_API_KEY" in error_msg:
                logger.error("AI service not configured: GEMINI_API_KEY missing")
                raise DatabaseError(
                    "AI service is not configured. Please set GEMINI_API_KEY in your environment variables."
                )
            logger.error(f"ValueError in chat API: {error_msg}")
            raise DatabaseError(error_msg)
        except AppError:
            raise
        except Exception as exc:
            logger.error(f"Unexpected error in chat API: {exc}", exc_info=True)
            raise DatabaseError("An unexpected error occurred") from exc

    return app


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
    

if __name__ == "__main__":
    # prompt = input("Enter your fitness prompt: ")
    # make_llm_call(prompt)
    main()