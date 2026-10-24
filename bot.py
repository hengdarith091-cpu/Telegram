import os
import threading
import telebot
from flask import Flask

# Token ថ្មីរបស់អ្នក
TOKEN = '8803556544:AAE4RIFsClLV5qD2PNNHgLwcMMme6Xp7HG4'
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# ==========================================
# ដាក់កូដដើមរបស់អ្នកនៅត្រង់នេះ (ឧទាហរណ៍ មុខងារផ្ញើ QR Code)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # ជំនួសអត្ថបទ ឬដាក់កូដ send_photo របស់ QR Code ដើមអ្នកនៅទីនេះ
    bot.reply_to(message, "សូមស្វាគមន៍មកកាន់ប្រព័ន្ធទូទាត់ប្រាក់ ប្រជុំរឿង VIP!\nតម្លៃសមាជិក: 1.00$\nសូមស្កេន QR Code ដើម្បីទូទាត់ប្រាក់...")
    # បើมีកូដផ្ញើរូបភាព QR ដើម អាចយកមកแปะជំនួសទីនេះបានភ្លាម
# ==========================================

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
