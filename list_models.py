import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

model_number = 0
for model in client.models.list():
    print(model.name, "-", model.supported_actions)
    model_number += 1
print(f"The number of the models is {model_number}")