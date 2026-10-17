#!/usr/bin/env bash
set -uo pipefail
G='\033[1;32m'; R='\033[1;31m'; Y='\033[1;33m'; C='\033[1;36m'; N='\033[0m'

echo -e "${C}→ Installation des dépendances système...${N}"
sudo apt-get update -qq
sudo apt-get install -y -qq python3-venv python3-pip wget libgtk-3-0 libwebkit2gtk-4.0-37

echo -e "${C}→ Création du Venv...${N}"
mkdir -p ~/.nexus_omega
if [ ! -d "$HOME/.nexus_omega/venv" ]; then
    python3 -m venv ~/.nexus_omega/venv
fi
source ~/.nexus_omega/venv/bin/activate

echo -e "${C}→ Installation des moteurs (Llama-cpp, FastAPI, PyWebView)...${N}"
pip install --upgrade pip -q
pip install llama-cpp-python fastapi uvicorn pywebview -q

echo -e "${C}→ Téléchargement du modèle (Phi-3)...${N}"
MODEL_PATH="$HOME/.nexus_omega/models/Phi-3-mini-4k-instruct-q4.gguf"
mkdir -p ~/.nexus_omega/models
if [ ! -f "$MODEL_PATH" ]; then
    wget -q --show-progress -O "$MODEL_PATH" "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf"
fi

echo -e "${G}[✓] Installation terminée.${N}"
