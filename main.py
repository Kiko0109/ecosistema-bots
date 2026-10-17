import os
import threading
from flask import Flask
import telebot
import google.generativeai as genai

# Configuración de Flask para mantener Render activo
app = Flask(__name__)

@app.route('/')
def home():
    return "Ecosistema Registro 66 Activo"

# Configuración de Gemini AI
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

# Mapeo de los 7 bots con sus variables de entorno y personalidades
BOTS_CONFIG = [
    {"name": "Cajero", "env": "BOT_TOKEN_CAJERO", "prompt": "Eres el bot Cajero. Habla de forma amable, natural y casual como una persona real."},
    {"name": "Notificaciones", "env": "BOT_TOKEN_NOTIFICACIONES", "prompt": "Hablas de forma fluida, humana y cercana en español."},
    {"name": "Backend", "env": "BOT_TOKEN_BACKEND", "prompt": "Responde de forma casual y amigable, como un chat común."},
    {"name": "Yan", "env": "BOT_TOKEN_YAN", "prompt": "Eres Yan. Hablas de forma totalmente natural, casual y humana, sin dar respuestas de robot."},
    {"name": "Kiko", "env": "BOT_TOKEN_KIKO", "prompt": "Eres Kiko. Respondes de forma casual, cercana y amigable como una persona normal."},
    {"name": "Bot 6", "env": "BOT_TOKEN_6", "prompt": "Hablas de forma casual y espontánea en español."},
    {"name": "Bot 7", "env": "BOT_TOKEN_7", "prompt": "Hablas de forma natural y amigable como cualquier persona en WhatsApp o Telegram."}
]

def obtener_respuesta_ia(mensaje_usuario, prompt_sistema):
    """Genera una respuesta natural con Gemini sin textos robóticos."""
    if not model:
        return "¡Hola! Todo bien por acá, ¿y tú cómo estás?"
    try:
        prompt_completo = f"{prompt_sistema}\nEl usuario dijo: '{mensaje_usuario}'. Responde como una persona normal, breve y natural:"
        response = model.generate_content(prompt_completo)
        return response.text.strip()
    except Exception as e:
        print(f"Error Gemini: {e}")
        return "¡Hola! Todo bien, ¿qué tal?"

def iniciar_bot(config):
    token = os.getenv(config["env"])
    if not token:
        print(f"⚠️ Token no encontrado para: {config['name']} ({config['env']})")
        return

    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        # Respuesta inicial limpia y directa sin cita
        respuesta = f"¡Hola! ¿Cómo estás?"
        bot.send_message(message.chat.id, respuesta)

    @bot.message_handler(func=lambda message: True)
    def handle_all_messages(message):
        # Generar respuesta casual de IA y enviarla limpia al chat
        respuesta = obtener_respuesta_ia(message.text, config["prompt"])
        bot.send_message(message.chat.id, respuesta)

    print(f"✅ Bot encendido: {config['name']}")
    bot.infinity_polling()

# Iniciar los 7 bots en hilos independientes
for config in BOTS_CONFIG:
    t = threading.Thread(target=iniciar_bot, args=(config,))
    t.daemon = True
    t.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
