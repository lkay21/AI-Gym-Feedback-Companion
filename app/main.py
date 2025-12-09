import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from app.db_instance import db
from app.auth_module.routes import auth_bp
import google.generativeai as genai
# from google import genai
# from google.genai.types import GenerateContentConfig, HttpOptions

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
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "devkey")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Register auth blueprint
    app.register_blueprint(auth_bp)

    # Frontend routes - Prototype Pages
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/login')
    @app.route('/login.html')
    def login():
        return render_template('login.html')
    
    @app.route('/signup')
    @app.route('/signup.html')
    def signup():
        return render_template('signup.html')
    
    @app.route('/chat')
    @app.route('/chat.html')
    def chat():
        return render_template('chat.html')
    
    @app.route('/dashboard')
    @app.route('/dashboard.html')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/snapshot')
    @app.route('/snapshot.html')
    def snapshot():
        return render_template('snapshot.html')
    
    @app.route('/workout-plan')
    @app.route('/workout-plan.html')
    def workout_plan():
        return render_template('workout-plan.html')
    
    @app.route('/insights')
    @app.route('/insights.html')
    def insights():
        return render_template('insights.html')
    
    # Dummy API endpoints for prototype interactivity
    @app.route('/api/steps', methods=['GET', 'POST'])
    def steps_api():
        if request.method == 'POST':
            data = request.get_json()
            # Dummy response - in real app this would save to DB
            return jsonify({
                'success': True,
                'steps': data.get('steps', 0),
                'calories': int(data.get('steps', 0) * 0.04)
            })
        return jsonify({'steps': 7855, 'weekly_average': 8933, 'calories': 120})
    
    @app.route('/api/form-score', methods=['POST'])
    def form_score_api():
        # Simulate form analysis with random score
        import random
        score = round(random.uniform(6.0, 10.0), 1)
        feedbacks = [
            "Keep your back straight and your arm at a 90 degree angle!",
            "Great form! Try to slow down the eccentric movement.",
            "Watch your knee alignment during the lift.",
            "Excellent posture! Focus on breathing rhythm.",
            "Try to engage your core more throughout the movement."
        ]
        return jsonify({
            'success': True,
            'score': score,
            'feedback': random.choice(feedbacks),
            'rating': 'Excellent' if score >= 9 else 'Good' if score >= 7.5 else 'Fair' if score >= 6 else 'Needs Work'
        })
    
    @app.route('/api/workout/complete', methods=['POST'])
    def complete_workout_api():
        data = request.get_json()
        return jsonify({
            'success': True,
            'workout': data.get('workout'),
            'message': 'Workout completed! Great job!'
        })
    
    @app.route('/api/insights', methods=['GET'])
    def insights_api():
        import random
        return jsonify({
            'steps': random.randint(20000, 30000),
            'training_minutes': random.randint(60, 120),
            'goal_progress': random.randint(40, 70),
            'workout_breakdown': {
                'strength': 46,
                'cardio': 18,
                'hiit': 15,
                'mobility': 21
            }
        })
    
    # API route for chat
    @app.route('/api/chat', methods=['POST'])
    def chat_api():
        try:
            data = request.get_json()
            message = data.get('message')
            profile = data.get('profile', {})
            
            if not message:
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
            
            # Get AI response
            response_text = make_llm_call(full_prompt)
            
            return jsonify({'response': response_text}), 200
            
        except ValueError as e:
            if "GEMINI_API_KEY" in str(e):
                return jsonify({'error': 'AI service is not configured. Please set GEMINI_API_KEY in your environment variables.'}), 500
            print(f"Error in chat API: {str(e)}")
            return jsonify({'error': str(e)}), 500
        except Exception as e:
            print(f"Error in chat API: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    return app

# Simple Prompt LLM Call Function, Call on Element Submission via Frontend
def make_llm_call(prompt):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in environment variables")
    
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

    try:
        response = model.generate_content(
            contents=prompt
        )
        
        # Check if response has text
        if hasattr(response, 'text') and response.text:
            return response.text
        elif hasattr(response, 'candidates') and response.candidates:
            # Try to get text from candidates
            if response.candidates[0].content and response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text
        else:
            raise ValueError("No response text available from the model")
            
    except Exception as e:
        print(f"Error generating content: {str(e)}")
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
    app.run(debug=True)
    

if __name__ == "__main__":
    # prompt = input("Enter your fitness prompt: ")
    # make_llm_call(prompt)
    main()