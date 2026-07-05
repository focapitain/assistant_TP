import json
from core.config import client, MODEL_NAME

SYSTEM_PROMPT_MONITOR = """
Tu es un inspecteur de code chargé de détecter la triche par IA.
Tu analyses le code écrit par un élève totalement DEBUTANT en Python.

RÈGLES D'ANALYSE :
- Un débutant fait des erreurs simples, utilise des structures basiques (for, if, listes).
- Si le code utilise des fonctions avancées non demandées (ex: list comprehensions complexes, lambda, programmation asynchrone), c'est suspect.
- Tu dois impérativement répondre au format JSON strict suivant sans texte autour :
{
    "status": "SÛR" ou "SUSPECT",
    "score_triche": un entier entre 0 et 100,
    "raison": "Une courte phrase explicative"
}
"""

def monitor_code(current_code, exercise_context):
    prompt_user = f"""
    CONSIGNE : {exercise_context}
    CODE DE L'ÉLÈVE :
    ```python
    {current_code}
    ```
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_MONITOR},
                {"role": "user", "content": prompt_user}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"status": "ERREUR", "score_triche": 0, "raison": str(e)}
