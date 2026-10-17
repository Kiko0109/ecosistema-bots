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

# Mapeo de los 7 bots con personalidades humanas y cercanas
BOTS_CONFIG = [
    {"name": "Cajero", "env": "BOT_TOKEN_CAJERO", "prompt": "Eres una persona real y corriente charlando por chat. Responde de forma muy natural, breve, casual y amigable."},
    {"name": "Notificaciones", "env": "BOT_TOKEN_NOTIFICACIONES", "prompt": "Eres una persona conversando de forma fluida, cercana y normal en español."},
    {"name": "Backend", "env": "BOT_TOKEN_BACKEND", "prompt": "Hablas como cualquier persona en una app de mensajería: casual, directo y natural."},
    {"name": "Yan", "env": "BOT_TOKEN_YAN", "prompt": "Eres Yan, una persona real chateando. Responde de manera espontánea, coloquial y totalmente humana, sin sonar a robot."},
    {"name": "Kiko", "env": "BOT_TOKEN_KIKO", "prompt": "Eres Kiko. Hablas de forma súper casual, cercana y corriente, como un amigo más."},
    {"name": "Bot 6", "env": "BOT_TOKEN_6", "prompt": "Responde de forma natural, relajada y conversacional."},
    {"name": "Bot 7", "env": "BOT_TOKEN_7", "prompt": "Hablas de forma completamente fluida, humana y sencilla."}
]

def obtener_respuesta_ia(mensaje_usuario, prompt_sistema):
    """Genera una conversación fluida y natural usando Gemini."""
    if not model:
        return "¡Qué onda! ¿Todo bien por ahí o qué?"
    try:
        chat = model.start_chat(history=[])
        prompt_completo = f"{prompt_sistema}\n\nUsuario: {mensaje_usuario}\nResponde de forma natural, corta y humana:"
        response = chat.send_message(prompt_completo)
        return response.text.strip()
    except Exception as e:
        print(f"Error Gemini: {e}")
        return "¡Ey! ¿Qué tal todo?"

def iniciar_bot(config):
    token = os.getenv(config["env"])
    if not token:
        print(f"⚠️ Token no encontrado para: {config['name']} ({config['env']})")
        return

    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.send_message(message.chat.id, "¡Hola! ¿Qué se cuenta? ¿Todo bien?")

    @bot.message_handler(func=lambda message: True)
    def handle_all_messages(message):
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
