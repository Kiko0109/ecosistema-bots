import os
import logging
import threading
from flask import Flask, jsonify
import google.generativeai as genai
import telebot

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Carga de variables de entorno desde Render
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
DATABASE_CHAT_ID = os.environ.get('DATABASE_CHAT_ID')

# Tokens de los 7 bots del ecosistema
BOT_TOKEN_1 = os.environ.get('BOT_TOKEN_CAJERO')
BOT_TOKEN_2 = os.environ.get('BOT_TOKEN_NOTIFICACIONES')
BOT_TOKEN_3 = os.environ.get('BOT_TOKEN_BACKEND')
BOT_TOKEN_YAN = os.environ.get('BOT_TOKEN_YAN')
BOT_TOKEN_KIKO = os.environ.get('BOT_TOKEN_KIKO')
BOT_TOKEN_6 = os.environ.get('BOT_TOKEN_6')
BOT_TOKEN_7 = os.environ.get('BOT_TOKEN_7')

# Inicialización de Gemini AI
model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("IA Gemini configurada correctamente.")
    except Exception as e:
        logger.error(f"Error al configurar Gemini: {e}")

# Función para iniciar la escucha de cada bot en Telegram
def iniciar_bot(token, nombre_bot):
    if not token:
        logger.warning(f"No se encontró token para {nombre_bot}.")
        return

    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, f"¡Hola! Soy {nombre_bot} del Ecosistema 66. ¿En qué te puedo ayudar hoy?")

    @bot.message_handler(func=lambda message: True)
    def hablar_como_persona(message):
        if model:
            try:
                prompt = (
                    f"Actúa como una persona normal y corriente charlando en un chat de Telegram. "
                    f"Tu nombre es {nombre_bot}. Responde de forma natural, casual y fluida al siguiente mensaje: '{message.text}'"
                )
                response = model.generate_content(prompt)
                texto_respuesta = response.text if response and response.text else "¡Hola! ¿Qué tal?"
                bot.reply_to(message, texto_respuesta)
            except Exception as e:
                logger.error(f"Error al generar respuesta con Gemini para {nombre_bot}: {e}")
                bot.reply_to(message, f"[{nombre_bot}]: ¡Hola! Todo bien por aquí.")
        else:
            bot.reply_to(message, f"[{nombre_bot}] Recibido: {message.text}")

    logger.info(f"Iniciando polling para {nombre_bot}...")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logger.error(f"Error en {nombre_bot}: {e}")

# Rutas del servidor Flask (para mantener el servicio activo en Render)
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "online",
        "system": "Ecosistema 7 Bots + Gemini AI",
        "database_channel": DATABASE_CHAT_ID
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# Función para encender todos los bots en hilos paralelos (en segundo plano)
def arrancar_hilos_bots():
    tokens = [
        (BOT_TOKEN_1, "Bot Cajero"),
        (BOT_TOKEN_2, "Bot Notificaciones"),
        (BOT_TOKEN_3, "Bot Backend"),
        (BOT_TOKEN_YAN, "Yan"),
        (BOT_TOKEN_KIKO, "Kiko"),
        (BOT_TOKEN_6, "Bot IA 6"),
        (BOT_TOKEN_7, "Bot IA 7")
    ]

    for token, nombre in tokens:
        if token:
            hilo = threading.Thread(target=iniciar_bot, args=(token, nombre), daemon=True)
            hilo.start()

if __name__ == '__main__':
    # Lanzar la escucha de los bots
    arrancar_hilos_bots()

    # Iniciar servidor web de Flask
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
