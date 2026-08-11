# Import os to read environment variables
import os

# Import the Gemini Python SDK
from google import genai

# Import load_dotenv to load variables from the .env file
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Create a Gemini client using the API key stored in .env
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Define the chatbot's role, scope, and response rules
SYSTEM_PROMPT = """
You are an AI assistant for a Smart Cat Feeder.

You can only answer questions about:
- Cat feeding
- Cat food and feeding schedules
- Smart Cat Feeder usage
- Feeder status and basic troubleshooting

If the user asks about anything outside these topics, reply:
"Sorry, I can only help with cat feeding and the Smart Pet Feeder."

Keep answers short and simple.
"""

def ask_gemini(message, feeder_data):
    # Build the complete prompt using:
    # 1. The chatbot instructions
    # 2. Current feeder data
    # 3. The user's message
    prompt = f"""
    {SYSTEM_PROMPT}

    Current feeder data:
    - Today feedings: {feeder_data["today_feedings"]}
    - Bowl weight: {feeder_data["bowl_weight"]} g
    - Hopper level: {feeder_data["hopper_level"]}%

    User message:
    {message}
    """

    # Send the prompt to Gemini and receive the generated response
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return response.text

