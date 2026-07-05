import os
from dotenv import load_dotenv
from openai import OpenAI

# Charger la clé du fichier .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("La clé GEMINI_API_KEY est manquante dans le fichier .env")

# On utilise la bibliothèque OpenAI mais configurée pour parler à Google Gemini 
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Modèle gratuit dans la limite de 15 requêtes/min
MODEL_NAME = "gemini-2.5-flash"
