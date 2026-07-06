from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.ai_teacher import ask_teacher
import subprocess
import sys

app = FastAPI(title="Plateforme TP Industrielle")

# Configuration du moteur de rendu HTML (Jinja2)
templates = Jinja2Templates(directory="app/templates")


# Exercice du TP (Configuré de manière fixe pour le moment)
CONSIGNE_TP = "Écrivez une fonction filtrer_pairs(liste_nombres) qui prend en paramètre une liste d'entiers et qui renvoie une nouvelle liste contenant uniquement les nombres pairs."

# Modèle de validation pour les requêtes de chat
class ChatRequest(BaseModel):
    question: str
    code: str

# Modèle de validation pour les requêtes de triche
class PasteLogRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
async def get_tp_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "consigne": CONSIGNE_TP,
        },
    )

@app.post("/api/ask")
async def api_ask_teacher(data: ChatRequest):
    """Route asynchrone haute performance pour interroger le prof IA"""
    try:
        response_text = ask_teacher(data.question, data.code, CONSIGNE_TP)
        return {"status": "success", "response": response_text}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/log-paste")
async def api_log_paste(data: PasteLogRequest):
    """Enregistre le copier-coller côté serveur (Prêt pour une future base de données)"""
    print(f"🚨 [ALERTE SÉCURITÉ SERVEUR] Un élève a triché en collant ce texte : {data.text}")
    return {"status": "logged"}

class RunRequest(BaseModel):
    code: str

@app.post("/api/run")
async def api_run_code(data: RunRequest):
    """Route sécurisée pour exécuter le code de l'élève avec un test unitaire"""
    student_code = data.code
    
    # On injecte un script de test automatique à la fin du code de l'élève
    # pour valider s'il a réussi l'exercice
    test_script = """

# --- TEST AUTOMATIQUE DU PROF ---
try:
    test_liste = [1, 2, 3, 4, 5, 6, 10, 11]
    resultat = filtrer_pairs(test_liste)
    expected = [2, 4, 6, 10]
    
    print(f"👉 Test avec la liste : {test_liste}")
    print(f"📦 Votre fonction a retourné : {resultat}")
    
    if resultat == expected:
        print("✅ FÉLICITATIONS ! Votre fonction est correcte, vous avez réussi l'exercice !")
    else:
        print(f"❌ Oups ! Ce n'est pas tout à fait ça. On attendait {expected}, mais votre fonction a donné {resultat}.")
except NameError:
    print("❌ Erreur : La fonction 'filtrer_pairs' n'a pas été trouvée ou est mal orthographiée.")
except Exception as e:
    print(f"❌ Une erreur est survenue lors de l'exécution : {str(e)}")
"""
    
    full_code_to_run = student_code + test_script
    
    try:
        # On lance le code Python dans un sous-processus isolé avec une limite de temps (timeout) de 3 secondes
        process = subprocess.run(
            [sys.executable, "-c", full_code_to_run],
            capture_output=True,
            text=True,
            timeout=3.0
        )
        
        # Si le code Python a planté (erreur de syntaxe, indentation, etc.)
        if process.returncode != 0:
            output = process.stderr if process.stderr else process.stdout
            return {"status": "error", "output": output}
            
        return {"status": "success", "output": process.stdout}
        
    except subprocess.TimeoutExpired:
        return {"status": "error", "output": "❌ Erreur : Temps d'exécution dépassé (Boucle infinie détectée !)"}
    except Exception as e:
        return {"status": "error", "output": f"Erreur système : {str(e)}"}