import os
import threading
import telebot
from flask import Flask

TOKEN = '8803556544:AAG0WJhcLfdVXkh57DEkNZVKjpSVJKcsQxM'
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "សួស្តី! Bot កំពុងដំណើរការនៅលើ Render ហើយ។")

def run_bot():
    try:
        bot.infinity_polling()
    except Exception as e:
        print(e)

if __name__ == '__main__':
    # រត់ Telegram Bot ក្នុង Thread ដាច់ដោយឡែក
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    # រត់ Flask Web Server ដើម្បីបំពេញតម្រូវការ Port របស់ Render
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
