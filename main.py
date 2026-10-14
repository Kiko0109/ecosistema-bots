import os
import logging
import threading
from flask import Flask, jsonify, request
import google.generativeai as genai
import telebot

# Configuración de logs
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

# Configuración de los bots de Telegram (usando telebot)
def iniciar_bot(token, nombre_bot):
    if not token:
        logger.warning(f"No se encontró token para {nombre_bot}.")
        return
    
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, f"¡Hola! Soy {nombre_bot} del Ecosistema 66 y estoy en línea.")

    @bot.message_handler(func=lambda message: True)
    def echo_all(message):
        # Aquí puedes integrar la respuesta con Gemini si lo deseas más adelante
        bot.reply_to(message, f"[{nombre_bot}] Recibido: {message.text}")

    logger.info(f"Iniciando polling para {nombre_bot}...")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logger.error(f"Error en {nombre_bot}: {e}")

# Rutas del servidor web (Flask) para Render
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

# Función para arrancar los bots en segundo plano para que no bloqueen a Flask
def arrancar_hilos_bots():
    tokens = [
        (BOT_TOKEN_CAJERO, "Bot Cajero"),
        (BOT_TOKEN_NOTIFICACIONES, "Bot Notificaciones"),
        (BOT_TOKEN_BACKEND, "Bot Backend")
    ]
    
    for token, nombre in tokens:
        if token:
            hilo = threading.Thread(target=iniciar_bot, args=(token, nombre), daemon=True)
            hilo.start()

if __name__ == '__main__':
    # Arrancamos los bots en segundo plano
    arrancar_hilos_bots()
    
    # Arrancamos el servidor Flask requerido por Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
