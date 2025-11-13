import os
from flask import Flask
from .db_instance import db
from .auth_module.routes import auth_bp


# Get Infor From ENV
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configures Flask application (initializes with configuration settings,
# sets up database, registers any blueprints)
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "devkey")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Register auth blueprint
    app.register_blueprint(auth_bp)

    return app

def make_llm_call():
    pass

def contextualize_model():
    pass

def main():
    app = create_app()
    app.run(debug=True)

if __name__ == "__main__":
    main()