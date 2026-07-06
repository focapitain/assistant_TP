import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
from core.ai_teacher import ask_teacher
from core.ai_monitor import monitor_code
from IPython import get_ipython

class TPChatInterface:
    def __init__(self, exercise_context):
        self.context = exercise_context
        
        # Correction Problème 1 : On crée un container d'affichage avec du style CSS pour le retour à la ligne
        self.out = widgets.Output()
        # Ce style force le texte à revenir à la ligne automatiquement si la fenêtre est trop petite
        self.out.layout = widgets.Layout(
            width='100%', 
            max_height='400px', 
            overflow='auto',
            border='1px solid #ddd',
            padding='10px',
            margin='0 0 10px 0'
        )
        
        # Barre de saisie et bouton
        self.text_input = widgets.Text(
            placeholder="Pose ta question au tuteur IA ici...", 
            layout=widgets.Layout(width='75%')
        )
        self.btn_send = widgets.Button(
            description="Demander de l'aide", 
            button_style='info',
            layout=widgets.Layout(width='20%')
        )
        
        self.btn_send.on_click(self.on_submit)
        self.text_input.on_submit(self.on_submit)

    def get_all_notebook_code(self):
        """Correction Problème 2 : Récupère l'intégralité des cellules de code exécutées dans le TP"""
        ipython = get_ipython()
        if ipython and ipython.user_ns.get('_ih'):
            history = ipython.user_ns['_ih']
            
            # On filtre pour ne garder que le vrai code de l'élève (on ignore les commandes vides ou l'init du chat)
            clean_code_cells = []
            for cell in history:
                cell_clean = cell.strip()
                if cell_clean and not cell_clean.startswith('from ui.chat_widget') and not cell_clean.startswith('import sys'):
                    clean_code_cells.append(cell_clean)
            
            if clean_code_cells:
                # On fusionne toutes les cellules de code séparées par une ligne vide
                return "\n\n# --- Nouvelle cellule ---\n".join(clean_code_cells)
                
        return "# Aucun code exécuté pour le moment."

    def on_submit(self, b):
        question = self.text_input.value.strip()
        if not question:
            return
        
        self.text_input.value = ""
        
        # On récupère TOUT le code du notebook d'un coup
        all_code = self.get_all_notebook_code()
        
        with self.out:
            # On utilise du HTML pour styliser proprement les messages et garantir le retour à la ligne
            display(HTML(f"<p style='word-wrap: break-word; white-space: pre-wrap;'><b>👤 Élève :</b> {question}</p>"))
            display(HTML("<p id='loading'><i>🤖 L'enseignant réfléchit...</i></p>"))
            
            # Appels aux IA (Google Gemini)
            answer = ask_teacher(question, all_code, self.context)
            analysis = monitor_code(all_code, self.context)
            
            # Nettoyer l'indicateur de chargement
            clear_output(wait=True)
            
            # Affichage final de la discussion avec style CSS 'word-wrap' anti-coupure
            display(HTML(f"<div style='word-wrap: break-word; white-space: pre-wrap; margin-bottom: 10px;'><b>👤 Élève :</b> {question}</div>"))
            display(HTML(f"<div style='word-wrap: break-word; white-space: pre-wrap; margin-bottom: 15px; background-color: #f4f9f9; padding: 8px; border-left: 3px solid #5bc0de;'><b>🤖 Enseignant :</b> {answer}</div>"))
            
            # Affichage des logs prof secrets (Alerte si suspicion de triche)
            if analysis.get("status") == "SUSPECT" and analysis.get("score_triche", 0) > 50:
                display(HTML(f"<div style='color: #d9534f; font-size: 0.9em; border: 1px dashed #d9534f; padding: 5px; margin-top: 5px;'>⚠️ [LOG PROF - ALERTE TRICHE] Score : {analysis['score_triche']}%<br>Raison : {analysis['raison']}</div>"))
            
            display(HTML("<hr style='border: 0; border-top: 1px solid #eee;'>"))

    def render(self):
        # On affiche d'abord la boîte de dialogue, puis la ligne de saisie en dessous
        display(self.out, widgets.HBox([self.text_input, self.btn_send]))
