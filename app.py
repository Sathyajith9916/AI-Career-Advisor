import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

# Initialize Flask App
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) to allow browser requests
CORS(app)

# --- Google Gemini AI Configuration ---
# IMPORTANT: Set up your Google API Key.
# 1. Get your API key from Google AI Studio: https://aistudio.google.com/app/apikey
# 2. It's best practice to set this as an environment variable for security.
#    In your terminal, run: export GOOGLE_API_KEY='Your_API_Key_Here'
#    (For Windows, use: set GOOGLE_API_KEY=Your_API_Key_Here)
# 3. The code will then automatically use this key.
try:
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
except AttributeError:
    print("ERROR: Google API Key not found. Please set the GOOGLE_API_KEY environment variable.")
    # In a production app, you might want to exit or handle this more gracefully
    exit()


def generate_ai_recommendations(interests, skills, academics):
    """
    Generates personalized career recommendations using the Google Gemini AI model.
    """
    # Initialize the Generative Model
    model = genai.GenerativeModel('gemini-1.5-pro-latest')

    # --- The "Persona-Driven" AI Prompt ---
    # This detailed prompt instructs the AI to act as an expert career counselor
    # for the Indian market, ensuring relevant and high-quality responses.
    prompt = f"""
    Act as an expert career counselor for students in the Indian job market as of late 2025. Your advice must be practical, current, and tailored to the Indian economic landscape, referencing initiatives like 'Digital India' or the startup ecosystem where relevant.

    A student has provided the following profile:
    - Interests: "{interests}"
    - Current Skills: "{skills}"
    - Academic Stream: "{academics}"

    Based on this profile, generate three diverse and detailed career path recommendations. For each recommendation, provide the following information in a strict JSON format within a single JSON array. Do not include any text or markdown formatting before or after the JSON array.

    The required JSON structure for each object in the array is:
    {{
      "career_path": "The name of the career (e.g., 'Blockchain Developer')",
      "description": "A 2-3 sentence summary explaining why this career is a strong fit for the student and its relevance in India today. Mention specific Indian market trends.",
      "skills_required": ["A list of 5 essential technical and soft skills to develop"],
      "job_roles": ["A list of 3-4 specific job titles"],
      "learning_pathway": "Suggest a brief, actionable first step. For example, 'Start with an online course in Python for Data Science on SWAYAM or NPTEL' or 'Contribute to an open-source fintech project.'",
      "salary_expectations_inr": "Provide an estimated starting salary range in India (in INR Lakhs per Annum, e.g., '₹4.5 - ₹7.0 LPA') for an entry-level position."
    }}
    """
    
    try:
        # Generate content and get the response from the AI
        response = model.generate_content(prompt)
        
        # The AI response might have markdown formatting (```json ... ```), which needs cleaning.
        cleaned_json_string = response.text.strip().replace('```json', '').replace('```', '').strip()
        
        # Parse the cleaned string into a Python list of dictionaries
        recommendations = json.loads(cleaned_json_string)
        return recommendations, None

    except Exception as e:
        print(f"An error occurred during AI generation: {e}")
        # Return a user-friendly error
        error_message = f"The AI model could not process the request. It's possible the input was ambiguous or there was a configuration issue. Details: {str(e)}"
        return None, error_message


@app.route('/get-advice', methods=['POST'])
def get_advice():
    """
    API endpoint to receive student data and return AI-generated career advice.
    """
    try:
        data = request.get_json()
        if not all(k in data for k in ['interests', 'skills', 'academics']):
            return jsonify({"error": "Invalid input. Please provide interests, skills, and academics."}), 400
            
        interests, skills, academics = data['interests'], data['skills'], data['academics']
        
        recommendations, error = generate_ai_recommendations(interests, skills, academics)
        
        if error:
             return jsonify({"error": error}), 500

        return jsonify({"recommendations": recommendations})

    except Exception as e:
        print(f"An error occurred in /get-advice: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

if __name__ == '__main__':
    # Runs the Flask server
    app.run(debug=True, port=5000)
