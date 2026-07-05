from core.config import client, MODEL_NAME

SYSTEM_PROMPT_TEACHER = """
Tu es un enseignant de programmation Python bienveillant et adepte de la méthode socratique.
Ton but est de guider l'élève pour qu'il trouve la solution par lui-même.

RÈGLES ABSOLUES :
1. Ne donne JAMAIS de code complet ou de solution prête à être copiée-collée.
2. Si l'élève te demande la réponse ou une correction directe, refuse poliment et pose-lui une question pour le faire réfléchir.
3. Repère les erreurs dans son code (syntaxe, logique) et donne-lui des indices conceptuels (ex: "Regarde le type de données renvoyé", "Vérifie l'indentation de ta condition").
4. Sois court et encourageant (maximum 4-5 phrases).
"""

def ask_teacher(student_question, current_code, exercise_context):
    prompt_user = f"""
    CONTEXTE DE L'EXERCICE : {exercise_context}
    CODE ACTUEL DE L'ÉLÈVE :
    ```python
    {current_code}
    ```
    QUESTION DE L'ÉLÈVE : {student_question}
    """
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_TEACHER},
            {"role": "user", "content": prompt_user}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content
