import telebot
from flask import Flask, request
import google.generativeai as genai

# Вставь сюда свои ключи
TELEGRAM_TOKEN = 'ТВОЙ_TELEGRAM_TOKEN'
GEMINI_API_KEY = 'ТВОЙ_GEMINI_API_KEY'

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)
question_cache = {}

SYSTEM_INSTRUCTION = """
Сен — Huawei желілері мен жабдықтары (HCIA Datacom) бойынша сарапшы және тәлімгерсің.
НАЗАР АУДАР: Пайдаланушы орыс немесе басқа тілде сұрақ қойса да, ӘРҚАШАН ҚАТАҢ ТҮРДЕ ҚАЗАҚ ТІЛІНДЕ ЖАУАП БЕР.
Жауаптарда HTML-тегтерді (<p>, <ol>, <li>, <br>, <b> және т.б.) пайдалануға ҚАТАҢ ТЫЙЫМ САЛЫНАДЫ.
Тек кәдімгі мәтінді қолдан. 
Ерекшелеу үшін Markdown (*қалың мәтін*) пайдалан. 
Тізімдер үшін кәдімгі нөмірлеуді (1. 2. 3.) немесе дефистерді (-) қолдан.
"""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    system_instruction=SYSTEM_INSTRUCTION
)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "Сәлем! Мен сіздің Huawei HCIA Datacom бойынша жеке тәлімгеріңізбін. Сұрағыңызды қойсаңыз болады!"
    bot.send_message(message.chat.id, welcome_text, reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text.strip().lower()
    
    if user_text in question_cache:
        bot.send_message(message.chat.id, question_cache[user_text], parse_mode='Markdown')
        return

    bot.send_chat_action(message.chat.id, 'typing')
    wait_message = bot.send_message(message.chat.id, "Ойланып жатырмын, күте тұрыңыз... ⏳")

    try:
        response = model.generate_content(message.text)
        answer = response.text
        question_cache[user_text] = answer
        bot.edit_message_text(chat_id=message.chat.id, message_id=wait_message.message_id, text=answer, parse_mode='Markdown')
    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=wait_message.message_id, text="Кешіріңіз, қате кетті.")
        print(f"API қатесі: {e}")

# --- УНИВЕРСАЛЬНЫЙ WEBHOOK (FLASK) ---
@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def webhook(path):
    # Теперь Flask принимает запросы с любым путем от Nginx
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)