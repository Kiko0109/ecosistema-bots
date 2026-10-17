import os
import threading
import requests
from flask import Flask
import telebot

# Servidor Flask para mantener el servicio activo en Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Ecosistema Registro 66 - Activo"

# Configuración de Gemini API Key de Render
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Estilo base: humano, corto, cubano de la calle y enfocado en el proyecto
ESTILO_GRUPO = (
    "Habla como un cubano real en Telegram/WhatsApp: con swing, jerga de calle y naturalidad. "
    "Responde ULTRA CORTO (maximo 1 o 2 oraciones). Comete algunas tildes a proposito para parecer humano en celular. "
    "NO saludes de forma robotica ('Hola, ¿en que te puedo ayudar?'), NO uses listas ni viñetas, ni la palabra compay."
)

BOTS_CONFIG = [
    {
        "name": "Cajero",
        "env": "BOT_TOKEN_CAJERO",
        "prompt": f"Eres el Cajero de Proyecto 66. {ESTILO_GRUPO} Hablas de la criptomoneda del proyecto, como aportar liquidez, comprar tokens y las ventajas de invertir temprano. Animas a la gente a mover mambises y meterle liquidez."
    },
    {
        "name": "Notificaciones",
        "env": "BOT_TOKEN_NOTIFICACIONES",
        "prompt": f"Eres el Promotor Cripto. {ESTILO_GRUPO} Anuncias las actualizaciones del juego, subidas de volumen, quemas de tokens o novedades de la pagina. Sueltas los anuncios con chispa para generar interes y FOMO."
    },
    {
        "name": "Backend",
        "env": "BOT_TOKEN_BACKEND",
        "prompt": f"Eres el Especialista Tecnico/Blockchain. {ESTILO_GRUPO} Das confianza sobre la seguridad del contrato inteligente, la liquidez y la transparencia del juego. Cuando alguien duda, respondes con seguridad y firmeza."
    },
    {
        "name": "Yan",
        "env": "BOT_TOKEN_YAN",
        "prompt": f"Eres Yan, el Animador del Juego. {ESTILO_GRUPO} Hablas de lo divertido que esta el juego de la pagina, retas a los miembros a jugar, ganar recompensas en el token y armar la jodedera criolla."
    },
    {
        "name": "Kiko",
        "env": "BOT_TOKEN_KIKO",
        "prompt": f"Eres Kiko, el Anfitrion de Inversores. {ESTILO_GRUPO} Le das la bienvenida a los nuevos miembros, les explicas brevemente de que trata la comunidad y como unirse a la jugada del token y la pagina con confianza."
    },
    {
        "name": "Bot 6",
        "env": "BOT_TOKEN_6",
        "prompt": f"Eres el Holder/Inversor Entusiasta. {ESTILO_GRUPO} Te comportas como un miembro activo que ya invirtio en la moneda y juega en la pagina. Celebras las compras, la liquidez y animas a los demas a no quedarse atras."
    },
    {
        "name": "Bot 7",
        "env": "BOT_TOKEN_7",
        "prompt": f"Eres el Capitan/Visionario. {ESTILO_GRUPO} Hablas del futuro del proyecto, las metas del token y cómo la comunidad junta va a hacer escalar la moneda para que coja presion de verdad."
    }
]

def generar_respuesta_humana(mensaje_usuario, prompt_personalidad):
    if not GEMINI_KEY:
        return "Asere, falta poner la GEMINI_API_KEY en Render."

    headers = {'Content-Type': 'application/json'}
    
    prompt_completo = (
        f"{prompt_personalidad}\n\n"
        "REGLAS ESTRUCTURALES OBLIGATORIAS:\n"
        "1. Responde de forma ultra natural, espontanea y realista, como un cubano chateando por WhatsApp/Telegram.\n"
        "2. NO uses formato de carta, NO saludes formalmente, NO uses viñetas ni listas numeradas.\n"
        "3. Se breve: maximo 1 o 2 oraciones, directo al grano y con la jerga de la calle.\n\n"
        f"Mensaje recibido en el grupo: '{mensaje_usuario}'\n"
        "Respuesta:"
    )

    payload = {
        "contents": [{
            "parts": [{"text": prompt_completo}]
        }]
    }

    # Intentos por API REST v1beta y v1 directa por HTTP
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

# Lanzar los 7 bots en paralelo con hilos
for config in BOTS_CONFIG:
    hilo = threading.Thread(target=activar_bot, args=(config,))
    hilo.daemon = True
    hilo.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
