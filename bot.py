import os
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

TOKEN = '8803556544:AAE4RIFsClLV5qD2PNNHgLwcMMme6Xp7HG4'
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# Link សម្រាប់ចូល Channel VIP របស់អ្នក
VIP_CHANNEL_LINK = "https://t.me/+RqTiOTj0znwwZjNl"

@app.route('/')
def home():
    return "Bot is running!"

# មុខងារពេលអតិថិជនវាយ /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    caption = (
        "ស្កែនមកកាន់ប្រព័ន្ធទូទាត់ប្រាក់ ប្រជុំរឿង VIP!\n\n"
        "តម្លៃសមាជិក: 1.00$\n"
        "សូមស្កេន QR Code ខាងលើដើម្បីទូទាត់ប្រាក់ ហើយផ្ញើ Slip មកទីនេះ!"
    )
    try:
        if os.path.exists('qr.jpg'):
            with open('qr.jpg', 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption=caption)
        else:
            bot.reply_to(message, caption)
    except Exception as e:
        bot.reply_to(message, caption)

# មុខងារពេលអតិថិជនផ្ញើរូបភាព (Slip) ចូលមក
@bot.message_handler(content_types=['photo'])
def handle_slip(message):
    # ឆ្លើយតបប្រាប់អតិថិជនថាបានទទួល Slip ហើយ
    bot.reply_to(
        message, 
        "✅ បានទទួលវិក្កយបត្រ (Slip) របស់អ្នកហើយ!\nសូមរង់ចាំ Admin ពិនិត្យ និងផ្ទៀងផ្ទាត់បន្តិច។"
    )
    
    # បើ ហាន់នី ចង់ឱ្យវាផ្ញើ Link ជូនភ្លាមៗ ឬបង្កើតប៊ូតុងផ្ទៀងផ្ទាត់ អាចដាក់កូដបន្ថែមត្រង់នេះបាន
    # ឧទាហរណ៍៖ បើចង់ឱ្យវាចេញ Link ជូនដោយស្វ័យប្រវត្តិពេលផ្ញើ Slip ចូលមក
    success_text = (
        "🎉 ការទូទាត់ប្រាក់របស់អ្នកត្រូវបានផ្ទៀងផ្ទាត់ និងអនុម័តជោគជ័យ!\n\n"
        "សូមចុចទីនេះដើម្បីចូលឆានែល VIP:\n" + VIP_CHANNEL_LINK
    )
    bot.send_message(message.chat.id, success_text)

def run_bot():
    try:
        bot.infinity_polling(skip_pending=True)
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
