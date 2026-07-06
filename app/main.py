from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.ai_teacher import ask_teacher

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
    """Affiche l'interface du TP à l'étudiant"""
    return templates.TemplateResponse("index.html", {"request": request, "consigne": CONSIGNE_TP})

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
