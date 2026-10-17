import os
import threading
from Flask import Flask
import telebot
import google.generativeai as genai

# Servidor Flask para mantener el servicio activo en Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Ecosistema Registro 66 - Activando el caché cubano"

# Configuración de Gemini AI
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    model = None

# Configuración de los 7 Bots con sabor cubano, humor y naturalidad
BOTS_CONFIG = [
    {
        "name": "Cajero",
        "env": "BOT_TOKEN_CAJERO",
        "prompt": "Eres el Cajero del ecosistema. Hablas con acento cubano natural, fresco, resolutivo y con gracia, pero sin sonar exagerado ni callejero pesado."
    },
    {
        "name": "Notificaciones",
        "env": "BOT_TOKEN_NOTIFICACIONES",
        "prompt": "Eres el bot de Notificaciones. Conversas con la chispa y el piquete cubano, bien humano y relajado."
    },
    {
        "name": "Backend",
        "env": "BOT_TOKEN_BACKEND",
        "prompt": "Eres el backend del equipo. Hablas directo, con flow cubano natural, cero robot y con buena onda."
    },
    {
        "name": "Yan",
        "env": "BOT_TOKEN_YAN",
        "prompt": "Eres Yan. Tienes una arrancada cubana espontánea, divertida, hablas fluido y con gracia criolla."
    },
    {
        "name": "Kiko",
        "env": "BOT_TOKEN_KIKO",
        "prompt": "Eres Kiko. Conversas como un cubano net, resolviendo la directa con naturalidad y simpatía."
    },
    {
        "name": "Bot 6",
        "env": "BOT_TOKEN_6",
        "prompt": "Hablas con un tono cubano relajado, conversacional, con su chispa de humor característico."
    },
    {
        "name": "Bot 7",
        "env": "BOT_TOKEN_7",
        "prompt": "Eres un bot con swing cubano, fresco, directo y hablas como cualquier persona de allá mismo conversando."
    }
]

def generar_respuesta_humana(mensaje_usuario, prompt_personalidad):
    """Genera respuestas con flow cubano natural y sin repeticiones."""
    if not model:
        return "¡Dime asere! ¿Qué vuelta, todo en talla por ahí?"
    try:
        chat = model.start_chat(history=[])
        instrucciones = (
            f"{prompt_personalidad}\n"
            f"El usuario te soltó esto: '{mensaje_usuario}'.\n"
            f"Instrucción: Respóndele con acento cubano auténtico, fresco, con humor y naturalidad (sin abusar de palabras forzadas). Breve y alante."
        )
        response = chat.send_message(instrucciones)
        return response.text.strip()
    except Exception as e:
        print(f"Error con Gemini AI: {e}")
        return "¡Oime, la cosa está echando humo pero aquí estamos!"

def activar_bot(config):
    token = os.getenv(config["env"])
    if not token:
        print(f"⚠️ ¡Ojo! Falta el token para {config['name']} ({config['env']})")
        return

    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start', 'help'])
    def mensaje_inicio(message):
        bot.send_message(message.chat.id, "¡Dime tú! ¿Qué se cuenta por la pista? ¿Todo ready?")

    @bot.message_handler(func=lambda message: True)
    def responder_mensaje(message):
        respuesta = generar_respuesta_humana(message.text, config["prompt"])
        bot.send_message(message.chat.id, respuesta)

    print(f"✅ ¡Bot activo con sabor cubano: {config['name']}!")
    bot.infinity_polling()

# Lanzar los 7 bots en paralelo
for config in BOTS_CONFIG:
    hilo = threading.Thread(target=activar_bot, args=(config,))
    hilo.daemon = True
    hilo.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
