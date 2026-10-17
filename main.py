import os
import threading
import requests
from flask import Flask
import telebot

app = Flask(__name__)

@app.route('/')
def home():
    return "Ecosistema Registro 66 - Activo"

GEMINI_KEY = os.getenv("GEMINI_API_KEY")

ESTILO_CALLE = (
    "Habla como un cubano en la calle, con swing, jerga natural y frescura. "
    "Escribe fluido, puedes comerte las tildes y redactar como se chatea por WhatsApp en Cuba, "
    "sin sonar robotico ni usar la palabra compay."
)

BOTS_CONFIG = [
    {"name": "Cajero", "env": "BOT_TOKEN_CAJERO", "prompt": f"Eres el Cajero. {ESTILO_CALLE} Resuelve los mambises con efectividad y calle."},
    {"name": "Notificaciones", "env": "BOT_TOKEN_NOTIFICACIONES", "prompt": f"Eres el bot de Notificaciones. {ESTILO_CALLE} Suelta la directa con chispa."},
    {"name": "Backend", "env": "BOT_TOKEN_BACKEND", "prompt": f"Eres el Backend. {ESTILO_CALLE} Directo al grano, sin rodeos y con flow."},
    {"name": "Yan", "env": "BOT_TOKEN_YAN", "prompt": f"Eres Yan. {ESTILO_CALLE} Tienes una arrancada espontanea, divertida y criolla."},
    {"name": "Kiko", "env": "BOT_TOKEN_KIKO", "prompt": f"Eres Kiko. {ESTILO_CALLE} Conversas relajado, con simpatia y calle."},
    {"name": "Bot 6", "env": "BOT_TOKEN_6", "prompt": f"Eres el Bot 6. {ESTILO_CALLE} Hablas con swing y mucha naturalidad."},
    {"name": "Bot 7", "env": "BOT_TOKEN_7", "prompt": f"Eres el Bot 7. {ESTILO_CALLE} Fresco, directo y con el piquete arriba."}
]

def generar_respuesta_humana(mensaje_usuario, prompt_personalidad):
    if not GEMINI_KEY:
        return "Asere, falta poner la GEMINI_API_KEY en Render."

    headers = {'Content-Type': 'application/json'}
    prompt_completo = (
        f"{prompt_personalidad}\n\n"
        f"El usuario dijo: '{mensaje_usuario}'.\n"
        f"Responde corto, alante y con puro acento cubano de la calle:"
    )

    payload = {
        "contents": [{
            "parts": [{"text": prompt_completo}]
        }]
    }

    urls = [
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}",
        f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_KEY}",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}"
    ]

    ultimo_error = ""

    for url in urls:
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data['candidates'][0]['content']['parts'][0]['text'].strip()
            else:
                ultimo_error = f"HTTP {response.status_code}: {response.text[:50]}"
        except Exception as e:
            ultimo_error = str(e)
            continue

    return f"Falla en la directa: {ultimo_error}"

def activar_bot(config):
    token = os.getenv(config["env"])
    if not token:
        print(f"⚠️ Falta el token para {config['name']} ({config['env']})")
        return

    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start', 'help'])
    def mensaje_inicio(message):
        bot.send_message(message.chat.id, "¡Dime tu! ¿Que bola? ¿Todo ready por ahi?")

    @bot.message_handler(func=lambda message: True)
    def responder_mensaje(message):
        respuesta = generar_respuesta_humana(message.text, config["prompt"])
        bot.send_message(message.chat.id, respuesta)

    print(f"✅ Bot activo: {config['name']}")
    bot.infinity_polling()

for config in BOTS_CONFIG:
    hilo = threading.Thread(target=activar_bot, args=(config,))
    hilo.daemon = True
    hilo.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
