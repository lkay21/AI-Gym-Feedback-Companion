import os
from urllib import response
from flask import Flask
from dotenv import load_dotenv
from db_instance import db
from auth_module.routes import auth_bp
from google import genai
from google.genai.types import GenerateContentConfig, HttpOptions

# Get Info From ENV
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"GEMINI_API_KEY: {GEMINI_API_KEY}")

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

# Simple Prompt LLM Call Function, Call on Element Submission via Frontend
def make_llm_call(prompt):
    client = genai.Client(http_options=HttpOptions(api_version="v1"))

    # Next Steps:
    # Set up Vector DB for RAG that keeps user prompt history and relevant user external input context
    # contextualize_model()

    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt
    )
    print(response.text)    

# RAG with LangChain for best contextualization?
def contextualize_model():
    pass

def main():
    app = create_app()
    app.run(debug=True)

if __name__ == "__main__":
    # prompt = input("Enter your fitness prompt: ")
    # make_llm_call(prompt)
    main()