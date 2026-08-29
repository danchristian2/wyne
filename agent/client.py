import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODELS = ["gemini-3.1-flash-lite", "gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.7-flash"]