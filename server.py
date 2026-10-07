import os
import logging
import requests
from flask import Flask, jsonify, request
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Carga de variables de entorno desde Render
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
DATABASE_CHAT_ID = os.environ.get('DATABASE_CHAT_ID')

BOT_TOKEN_CAJERO = os.environ.get('BOT_TOKEN_CAJERO')
BOT_TOKEN_NOTIFICACIONES = os.environ.get('BOT_TOKEN_NOTIFICACIONES')
BOT_TOKEN_BACKEND = os.environ.get('BOT_TOKEN_BACKEND')

# Inicialización de Gemini
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("IA Gemini configurada correctamente.")
    except Exception as e:
        logger.error(f"Error al configurar Gemini: {e}")

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "online",
        "system": "Ecosistema Multi-Bot + Gemini AI",
        "database_channel": DATABASE_CHAT_ID
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
