import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

for model in client.models.list():
    print(model.name, "-", model.supported_actions)