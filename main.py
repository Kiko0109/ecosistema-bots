import os
import threading
from flask import Flask
import telebot
import google.generativeai as genai

# Servidor Flask para mantener el servicio activo en Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Ecosistema Registro 66 - Activo"

# Configuración de Gemini AI
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# Estilo cubano de la calle, escribiendo natural (sin tildes formales, con jerga real)
ESTILO_CALLE = (
    "Habla como un cubano net en la calle, con swing, jerga natural y frescura. "
    "Escribe fluido, puedes comerte las tildes y redactar como se chatea en WhatsApp en Cuba, "
    "sin sonar robótico ni usar la palabra compay."
)

BOTS_CONFIG = [
    {
        "name": "Cajero",
        "env": "BOT_TOKEN_CAJERO",
        "prompt": f"Eres el Cajero. {ESTILO_CALLE} Resuelve los mambises con efectividad y calle."
    },
    {
        "name": "Notificaciones",
        "env": "BOT_TOKEN_NOTIFICACIONES",
        "prompt": f"Eres el bot de Notificaciones. {ESTILO_CALLE} Suelta la directa con chispa."
    },
    {
        "name": "Backend",
        "env": "BOT_TOKEN_BACKEND",
        "prompt": f"Eres el Backend. {ESTILO_CALLE} Directo al grano, sin rodeos y con flow."
    },
    {
        "name": "Yan",
        "env": "BOT_TOKEN_YAN",
        "prompt": f"Eres Yan. {ESTILO_CALLE} Tienes una arrancada espontánea, divertida y criolla."
    },
    {
        "name": "Kiko",
        "env": "BOT_TOKEN_KIKO",
        "prompt": f"Eres Kiko. {ESTILO_CALLE} Conversas relajado, con simpatía y calle."
    },
    {
        "name": "Bot 6",
        "env": "BOT_TOKEN_6",
        "prompt": f"Eres el Bot 6. {ESTILO_CALLE} Hablas con swing y mucha naturalidad."
    },
    {
        "name": "Bot 7",
        "env": "BOT_TOKEN_7",
        "prompt": f"Eres el Bot 7. {ESTILO_CALLE} Fresco, directo y con el piquete arriba."
    }
]

def generar_respuesta_humana(mensaje_usuario, prompt_personalidad):
    """Genera respuestas conectando con los modelos disponibles de Gemini."""
    if not GEMINI_KEY:
        return "Asere, falta poner la GEMINI_API_KEY en Render."

    prompt_completo = (
        f"{prompt_personalidad}\n\n"
        f"El usuario dijo: '{mensaje_usuario}'.\n"
        f"Responde corto, alante y con puro acento cubano de la calle:"
    )

    # Modelos de respaldo para evitar errores 404
    modelos = [
        'gemini-1.5-flash-latest',
        'gemini-1.5-flash',
        'gemini-1.5-pro-latest',
        'gemini-pro'
    ]

    for nombre_modelo in modelos:
        try:
            m = genai.GenerativeModel(nombre_modelo)
            response = m.generate_content(prompt_completo)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"Error con {nombre_modelo}: {e}")
            continue

    return "Dime tu, ¿que bola? Estoy activo."

def activar_bot(config):
    token = os.getenv(config["env"])
    if not token:
        print(f"⚠️ Falta el token para {config['name']} ({config['env']})")
        return

    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start', 'help'])
    def mensaje_inicio(message):
        bot.send_message(message.chat.id, "¡Dime tú! ¿Qué bola? ¿Todo ready por ahí?")

    @bot.message_handler(func=lambda message: True)
    def responder_mensaje(message):
        respuesta = generar_respuesta_humana(message.text, config["prompt"])
        bot.send_message(message.chat.id, respuesta)

    print(f"✅ Bot activo: {config['name']}")
    bot.infinity_polling()

# Lanzar los 7 bots en paralelo con hilos
for config in BOTS_CONFIG:
    hilo = threading.Thread(target=activar_bot, args=(config,))
    hilo.daemon = True
    hilo.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
