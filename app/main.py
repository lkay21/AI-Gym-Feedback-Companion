import os
from urllib import response
from flask import Flask
from dotenv import load_dotenv
from app.db_instance import db
from app.auth_module.routes import auth_bp
import google.generativeai as genai
# from google import genai
# from google.genai.types import GenerateContentConfig, HttpOptions

# Get Info From ENV
load_dotenv()
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

# Simple Prompt LLM Call Function, Call on Element Submission via Frontend
def make_llm_call(prompt):

    genai.configure(api_key=GEMINI_API_KEY)

    model_name = "gemini-2.5-flash"
    system_instruction = [
        "You are a fitness focused personal trainer AI.",
        "Provide detailed and personalized fitness advice based on user prompts.",
        "Ensure your responses are clear and relate to what you discern the user is most focused on.",
        "Respond in a friendly but professional tone.",
        "Respond with speed but do not sacrifice detail or clarity."
    ]

    model = genai.GenerativeModel(
        model_name = model_name,
        system_instruction = system_instruction
    )

    # Next Steps:
    # Set up Vector DB for RAG that keeps user prompt history and relevant user external input context
    # Integration with LangChain and Multi-Turn Dialogue Management
    # contextualize_model()

    response = model.generate_content(
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