import ipywidgets as widgets
from IPython.display import display, clear_output
from core.ai_teacher import ask_teacher
from core.ai_monitor import monitor_code
from IPython import get_ipython

class TPChatInterface:
    def __init__(self, exercise_context):
        self.context = exercise_context
        self.out = widgets.Output()
        self.text_input = widgets.Text(placeholder="Pose ta question au tuteur IA ici...", layout=widgets.Layout(width='70%'))
        self.btn_send = widgets.Button(description="Demander de l'aide", button_style='info')
        
        self.btn_send.on_click(self.on_submit)
        self.text_input.on_submit(self.on_submit)

    def get_last_executed_code(self):
        ipython = get_ipython()
        if ipython and ipython.user_ns.get('_ih'):
            history = ipython.user_ns['_ih']
            if len(history) > 1:
                return history[-1]
        return "# Aucun code exécuté."

    def on_submit(self, b):
        question = self.text_input.value.strip()
        if not question:
            return
        
        self.text_input.value = ""
        current_code = self.get_last_executed_code()
        
        with self.out:
            print(f"👤 Élève : {question}")
            print("🤖 L'enseignant réfléchit...")
            
            answer = ask_teacher(question, current_code, self.context)
            analysis = monitor_code(current_code, self.context)
            
            clear_output(wait=True)
            print(f"👤 Élève : {question}")
            print(f"🤖 Enseignant : {answer}\n")
            
            # Affichage des logs prof secrets (Alerte si suspicion de triche)
            if analysis.get("status") == "SUSPECT" and analysis.get("score_triche", 0) > 50:
                print(f"⚠️ [LOG PROF - ALERTE TRICHE] Score : {analysis['score_triche']}%")
                print(f"Raison : {analysis['raison']}\n")
            print("-" * 50)

    def render(self):
        display(self.out, widgets.HBox([self.text_input, self.btn_send]))
