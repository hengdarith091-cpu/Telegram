import os
import telebot
from flask import Flask, request

TOKEN = '8803556544:AAE4RIFsClLV5qD2PNNHgLwcMMme6Xp7HG4'
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# URL របស់ Render របស់អ្នក
RENDER_URL = "https://telegram-1-9f5w.onrender.com"
WEBHOOK_URL = f"{RENDER_URL}/{TOKEN}"

@app.route('/')
def home():
    return "Bot is running with Webhook!"

# ទទួលសារ Webhook ពី Telegram
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    else:
        return "Invalid content type", 403

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
    bot.reply_to(
        message, 
        "✅ បានទទួលវិក្កយបត្រ (Slip) របស់អ្នកហើយ!\nសូមរង់ចាំ Admin ពិនិត្យ និងផ្ទៀងផ្ទាត់បន្តិច។"
    )
    success_text = (
        "🎉 ការទូទាត់ប្រាក់របស់អ្នកត្រូវបានផ្ទៀងផ្ទាត់ និងអនុម័តជោគជ័យ!\n\n"
        "សូមចុចទីនេះដើម្បីចូលឆានែល VIP:\nhttps://t.me/+RqTiOTj0znwwZjNl"
    )
    bot.send_message(message.chat.id, success_text)

if __name__ == '__main__':
    # កំណត់ Webhook ទៅ Telegram ស្វ័យប្រវត្តិពេល Server ដំណើរការ
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)

    # รត់ Flask Web Server
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
