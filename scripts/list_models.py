import google.generativeai as genai
from decouple import config

api_key = config('GEMINI_API_KEY')
genai.configure(api_key=api_key)

print("--- AVAILABLE MODELS ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name} (Ver: {m.version})")
except Exception as e:
    print(f"Error listing models: {e}")
