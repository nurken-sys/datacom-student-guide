import google.generativeai as genai

# Твой ключ
GOOGLE_API_KEY = "ТВОЙ_GEMINI_API_KEY"
genai.configure(api_key=GOOGLE_API_KEY)

print("Твоему ключу доступны следующие модели для чата:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)