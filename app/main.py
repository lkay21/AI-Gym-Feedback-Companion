import os
from pathlib import Path
from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from app.db_instance import db
from app.auth_module.routes import auth_bp
from app.profile_module.routes import profile_bp
from app.auth_module.models import User  # Import User model so tables are created
from app.chat_module.routes import chat_bp as chat_module_bp
from app.fitness.benchmark_loader import load_fitness_benchmarks
from app.logger import get_logger
from app.exercises.routes import exercises_bp
from app.exercises.models import VideoAsset  # Import VideoAsset so table is created

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
    # Session configuration
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours in seconds
    _secure = os.getenv("SESSION_COOKIE_SECURE", "true").strip().lower() in ("1", "true", "yes")
    app.config['SESSION_COOKIE_SECURE'] = _secure
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    _default_origins = [
        "http://localhost:8081",
        "http://localhost:19006",
        "http://127.0.0.1:8081",
        "http://127.0.0.1:19006",
        "https://your-alb-url.amazonaws.com",
    ]
    _cors_raw = os.getenv("CORS_ORIGINS", "").strip()
    if _cors_raw:
        cors_origins = [o.strip() for o in _cors_raw.split(",") if o.strip()]
    else:
        cors_origins = _default_origins

    cors_opts = {
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-User-Id"],
        "supports_credentials": True,
        "origins": cors_origins,
    }
    CORS(app, resources={r"/auth/*": cors_opts, r"/api/*": dict(cors_opts)})

    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    # Chat module routes: health-onboarding, chat endpoints, plan generation
    app.register_blueprint(chat_module_bp, url_prefix='/api/chat')
    # Register profile blueprint
    app.register_blueprint(profile_bp)
    # Register CV/exercise blueprint
    app.register_blueprint(exercises_bp, url_prefix='/api/cv')

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

    @app.route('/health')
    def health():
        return {"status": "ok"}

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