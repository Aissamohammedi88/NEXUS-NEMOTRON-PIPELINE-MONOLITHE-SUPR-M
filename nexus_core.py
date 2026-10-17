import os
import threading
import time
import uvicorn
import webview
from fastapi import FastAPI
from pydantic import BaseModel
from llama_cpp import Llama

# Configuration
MODEL_PATH = os.path.expanduser("~/.nexus_omega/models/Phi-3-mini-4k-instruct-q4.gguf")
PORT = 8420

# --- LE BACKEND (FASTAPI) ---
app = FastAPI()
llm = None

class Prompt(BaseModel):
    text: str

@app.post("/api/chat")
def chat(prompt: Prompt):
    global llm
    if not llm: return {"error": "Modèle non chargé"}
    
    # Formatage strict pour Phi-3
    formatted = f"<|user|>\n{prompt.text}<|end|>\n<|assistant|>\n"
    res = llm(formatted, max_tokens=1024, stop=["<|end|>"], echo=False)
    return {"response": res['choices'][0]['text'].strip()}

def run_server():
    global llm
    print("Chargement du modèle en mémoire...")
    llm = Llama(model_path=MODEL_PATH, n_ctx=4096, n_threads=os.cpu_count(), verbose=False)
    print("Modèle prêt. Lancement de l'API.")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="error")

# --- LE FRONTEND (HTML/CSS/JS INJECTÉ) ---
HTML_UI = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <style>
        :root { --bg: #0a0a0f; --panel: #12121a; --accent: #00ff88; --text: #e0e0e0; }
        * { box-sizing: border-box; font-family: 'Segoe UI', system-ui, sans-serif; margin: 0; padding: 0; }
        body { background: var(--bg); color: var(--text); height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
        
        header { padding: 15px 25px; border-bottom: 1px solid #222; display: flex; align-items: center; gap: 15px; background: var(--panel); }
        .logo { font-weight: 900; letter-spacing: 2px; color: var(--accent); font-size: 1.2rem; }
        .status { font-size: 0.8rem; color: #888; display: flex; align-items: center; gap: 5px; }
        .dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); box-shadow: 0 0 10px var(--accent); }

        #chat-container { flex: 1; padding: 30px; overflow-y: auto; display: flex; flex-direction: column; gap: 20px; }
        
        .message { max-width: 80%; padding: 15px 20px; border-radius: 12px; line-height: 1.6; font-size: 0.95rem; animation: fadeIn 0.3s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        
        .user { background: #1e1e2e; align-self: flex-end; border-bottom-right-radius: 2px; }
        .ai { background: rgba(0, 255, 136, 0.05); border: 1px solid rgba(0, 255, 136, 0.2); align-self: flex-start; border-bottom-left-radius: 2px; }
        
        .input-area { padding: 20px 30px; background: var(--panel); border-top: 1px solid #222; display: flex; gap: 15px; }
        input { flex: 1; padding: 15px 20px; border-radius: 8px; border: 1px solid #333; background: #000; color: #fff; outline: none; transition: 0.2s; }
        input:focus { border-color: var(--accent); }
        button { padding: 15px 25px; border-radius: 8px; border: none; background: var(--accent); color: #000; font-weight: bold; cursor: pointer; transition: 0.2s; }
        button:hover { opacity: 0.8; }
        button:disabled { background: #333; color: #888; cursor: not-allowed; }
    </style>
</head>
<body>
    <header>
        <div class="logo">NEXUS OMEGA</div>
        <div class="status"><div class="dot"></div> Phi-3 Local Engine</div>
    </header>
    
    <div id="chat-container">
        <div class="message ai">Système initialisé. Je suis Nexus, votre IA locale. Que construisons-nous aujourd'hui ?</div>
    </div>

    <div class="input-area">
        <input type="text" id="user-input" placeholder="Posez votre question..." autocomplete="off" autofocus>
        <button id="send-btn" onclick="sendMessage()">Envoyer</button>
    </div>

    <script>
        const container = document.getElementById('chat-container');
        const input = document.getElementById('user-input');
        const btn = document.getElementById('send-btn');

        input.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });

        async function sendMessage() {
            const text = input.value.trim();
            if (!text) return;

            // 1. Afficher le message utilisateur
            addMessage(text, 'user');
            input.value = '';
            btn.disabled = true;
            btn.innerText = '...';

            // 2. Indicateur de réflexion
            const loadingId = 'loading-' + Date.now();
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message ai';
            loadingDiv.id = loadingId;
            loadingDiv.innerHTML = '<i>Nexus réfléchit...</i>';
            container.appendChild(loadingDiv);
            container.scrollTop = container.scrollHeight;

            try {
                // 3. Appel API au serveur Python local
                const res = await fetch('http://127.0.0.1:8420/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: text})
                });
                const data = await res.json();
                
                // 4. Remplacer l'indicateur par la vraie réponse
                document.getElementById(loadingId).innerText = data.response || "Erreur de génération.";
            } catch (e) {
                document.getElementById(loadingId).innerText = "Erreur de connexion avec le moteur local.";
            } finally {
                btn.disabled = false;
                btn.innerText = 'Envoyer';
                container.scrollTop = container.scrollHeight;
                input.focus();
            }
        }

        function addMessage(text, sender) {
            const div = document.createElement('div');
            div.className = `message ${sender}`;
            div.innerText = text;
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    # Lancement du serveur API dans un thread séparé
    threading.Thread(target=run_server, daemon=True).start()
    
    # Attente que le serveur démarre
    time.sleep(3)
    
    # Lancement de la fenêtre native (PyWebView)
    print("Ouverture de la fenêtre native...")
    window = webview.create_window(
        title='Nexus Vortex Omega',
        html=HTML_UI,
        width=1200,
        height=800,
        background_color='#0a0a0f'
    )
    webview.start()
