import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
from core.ai_teacher import ask_teacher
from core.ai_monitor import monitor_code
from IPython import get_ipython
import json

class TPChatInterface:
    def __init__(self, exercise_context):
        self.context = exercise_context
        # Liste Python qui va stocker les éléments copiés-collés transmis par le JavaScript
        self.pastes_history = []
        
        # Zone d'affichage des messages
        self.out = widgets.Output()
        self.out.layout = widgets.Layout(
            width='100%', 
            max_height='400px', 
            overflow='auto',
            border='1px solid #ddd',
            padding='10px',
            margin='0 0 10px 0'
        )
        
        # Saisie élève
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

    def inject_paste_detector(self):
        """Injecte du JavaScript pour capturer le TEXTE copié-collé et le renvoyer à Python"""
        # On crée un pont pour que JS puisse parler à la variable Python 'self.pastes_history'
        # À travers l'exécution de cellules invisibles en arrière-plan
        js_code = f"""
        <script>
        (function() {{
            function handlePaste(e) {{
                // Récupérer le texte exact qui est dans le presse-papier de l'élève
                var pastedText = (e.clipboardData || window.clipboardData).getData('text');
                
                if (pastedText && pastedText.strip != "") {{
                    // On envoie le texte capturé à notre instance Python en bruit de fond
                    var command = "interface.register_paste(" + JSON.stringify(pastedText) + ")";
                    if (window.IPython && IPython.notebook) {{
                        IPython.notebook.kernel.execute(command);
                    }} else if (typeof vscode !== 'undefined' || document.querySelector('.cell')) {{
                        // Version compatible avec l'API interne de VS Code / JupyterLab
                        var kernel = Jupyter.notebook.kernel;
                        kernel.execute(command);
                    }}
                    
                    // Optionnel : un petit log discret ou visuel pour indiquer que le système a enregistré l'action
                    console.log("Texte copié capturé par la surveillante.");
                }}
            }}

            document.removeEventListener('paste', handlePaste);
            document.addEventListener('paste', handlePaste);
        }})();
        </script>
        """
        display(HTML(js_code))

    def register_paste(self, text):
        """Méthode appelée par le JavaScript pour enregistrer le texte collé"""
        if text.strip() and text not in self.pastes_history:
            self.pastes_history.append(text.strip())

    def get_all_notebook_code(self):
        ipython = get_ipython()
        if ipython and ipython.user_ns.get('_ih'):
            history = ipython.user_ns['_ih']
            clean_code_cells = []
            for cell in history:
                cell_clean = cell.strip()
                if cell_clean and not cell_clean.startswith('from ui.chat_widget') and not cell_clean.startswith('import sys') and not cell_clean.startswith('interface.register_paste'):
                    clean_code_cells.append(cell_clean)
            if clean_code_cells:
                return "\n\n# --- Nouvelle cellule ---\n".join(clean_code_cells)
        return "# Aucun code exécuté."

    def on_submit(self, b):
        question = self.text_input.value.strip()
        if not question:
            return
        
        self.text_input.value = ""
        all_code = self.get_all_notebook_code()
        
        # On prépare le rapport pour l'IA Surveillante en incluant l'historique des collages
        if self.pastes_history:
            paste_lines = []
            for p in self.pastes_history:
                # Nettoyer les retours à la ligne internes du texte copié pour le rapport
                p_clean = p.replace('\n', ' ')
                paste_lines.append(f'- "{p_clean}"')
            paste_report = "\n".join(paste_lines)
        else:
            paste_report = "Aucun copier-coller détecté."
            
        enriched_context = f"{self.context}\\n\\nHISTORIQUE DES COPIER-COLLER EFFECTUÉS PAR L'ÉLÈVE :\\n{paste_report}"
        
        with self.out:
            display(HTML(f"<div style='word-wrap: break-word; white-space: pre-wrap; margin-bottom: 10px;'><b>👤 Élève :</b> {question}</div>"))
            display(HTML("<p id='loading'><i>🤖 L'enseignant réfléchit...</i></p>"))
            
            # L'IA Enseignante reçoit le code global
            answer = ask_teacher(question, all_code, self.context)
            
            # L'IA Surveillante reçoit le code ET la liste de ce qui a été copié-collé pour juger de la gravité
            analysis = monitor_code(all_code, enriched_context)
            
            clear_output(wait=True)
            
            display(HTML(f"<div style='word-wrap: break-word; white-space: pre-wrap; margin-bottom: 10px;'><b>👤 Élève :</b> {question}</div>"))
            display(HTML(f"<div style='word-wrap: break-word; white-space: pre-wrap; margin-bottom: 15px; background-color: #f4f9f9; padding: 8px; border-left: 3px solid #5bc0de;'><b>🤖 Enseignant :</b> {answer}</div>"))
            
            # Si la surveillante juge que c'est une triche avérée (gros bloc ou code entier externe)
            if analysis.get("status") == "SUSPECT" and analysis.get("score_triche", 0) > 50:
                display(HTML(f"<div style='color: #fff; background-color: #d9534f; padding: 10px; border-radius: 4px; margin-top: 10px; font-weight: bold;'>⚠️ [IA SURVEILLANTE] Attention : Une quantité anormale de code externe ou de copier-coller massif a été détectée dans vos manipulations. Pour progresser, vous devez écrire votre logique vous-même. Ton enseignant a été notifié.</div>"))
            
            # Petit affichage de debug pour TOI (l'enseignant) pendant tes tests pour voir ce qu'elle a intercepté
            if self.pastes_history:
                display(HTML(f"<div style='color: #777; font-size: 0.8em; margin-top: 5px;'><i>[Debug Prof] Presse-papier intercepté : {list(self.pastes_history)}</i></div>"))
                
            display(HTML("<hr style='border: 0; border-top: 1px solid #eee;'>"))

    def render(self):
        display(self.out, widgets.HBox([self.text_input, self.btn_send]))
        self.inject_paste_detector()
