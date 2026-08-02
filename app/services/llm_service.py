import os
from dotenv import load_dotenv
from google import genai


load_dotenv()
client = genai.Client(api_key=os.getenv("LLM_API_KEY"))

def generate_response(message: str):
    interaction = client.interactions.create(
        model = "gemini-3.6-flash",
        input = message
    )
    print("Returning Response from LLM Service")
    return interaction.output_text
