import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Connexion à l'API Gemini via l'interface OpenAI de Google
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
MODEL_NAME = "gemini-2.5-flash"

SYSTEM_PROMPT = """
Tu es un enseignant Socratique expert en Python. Ton unique mission est d'aider l'élève sur son TP.
Ne donne JAMAIS le code de la solution tout fait. 
Donne uniquement des indices courts, pointe les erreurs logiques et pose des questions pour le faire réfléchir par lui-même.
"""

def ask_teacher(student_question: str, current_code: str, context: str) -> str:
    prompt_user = f"CONSIGNE DU TP : {context}\n\nCODE ACTUEL DE L'ÉLÈVE :\n{current_code}\n\nQUESTION DE L'ÉLÈVE : {student_question}"
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_user}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content
