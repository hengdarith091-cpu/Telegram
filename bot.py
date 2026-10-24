import os
import threading
import telebot
from flask import Flask

TOKEN = '8803556544:AAE4RIFsClLV5qD2PNNHgLwcMMme6Xp7HG4'
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    text_msg = (
        "ស្កែនមកកាន់ប្រព័ន្ធទូទាត់ប្រាក់ ប្រជុំរឿង VIP!\n\n"
        "តម្លៃសមាជិក: 1.00$\n"
        "សូមស្កេន QR Code ខាងលើដើម្បីទូទាត់ប្រាក់ ហើយផ្ញើ Slip មកទីនេះ!"
    )
    try:
        # ពិនិត្យមើលថាតើមាន file qr.jpg មែនឬអត់
        if os.path.exists('qr.jpg'):
            with open('qr.jpg', 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption=text_msg)
        else:
            bot.reply_to(message, text_msg + "\n\n(ចំណាំ៖ រកមិនទាន់ឃើញไฟล์ qr.jpg ទេ)")
    except Exception as e:
        bot.reply_to(message, f"មានបញ្ហា Error: {str(e)}")

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
