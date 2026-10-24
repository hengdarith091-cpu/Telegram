import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request

TOKEN = '8803556544:AAE4RIFsClLV5qD2PNNHgLwcMMme6Xp7HG4'
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# 🔴 ជំនួសកន្លែងនេះដោយតួលេខ Chat ID របស់អ្នក (ក្រោយពេលឆែករួច)
ADMIN_CHAT_ID = "@Darith9999"

RENDER_URL = "https://telegram-1-9f5w.onrender.com"
WEBHOOK_URL = f"{RENDER_URL}/{TOKEN}"

VIP_CHANNEL_LINK = "https://t.me/+RqTiOTj0znwwZjNl"

@app.route('/')
def home():
    return "Bot is running with Admin Approval System!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    else:
        return "Invalid content type", 403

# 🛠️ មុខងារពិសេស៖ ឆែករកលេខ Chat ID ផ្ទាល់ខ្លួន
@bot.message_handler(commands=['myid'])
def send_my_id(message):
    bot.reply_to(message, f"Telegram Chat ID របស់អ្នកគឺ: {message.chat.id}")

# មុខងារពេលអតិថិជនផ្ញើសារ /start
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
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "អតិថិជន"
    
    # 1. ឆ្លើយតបប្រាប់អតិថិជនថាកំពុងរង់ចាំ Admin ពិនិត្យ
    bot.reply_to(
        message, 
        "✅ បានទទួលវិក្កយបត្រ (Slip) របស់អ្នកហើយ!\nសូមរង់ចាំ Admin ពិនិត្យ និងផ្ទៀងផ្ទាត់បន្តិច។"
    )
    
    # 2. បង្កើតប៊ូតុងយល់ព្រម ឬបដិសេធសម្រាប់ Admin
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("✅ យល់ព្រម (Approve)", callback_data=f"approve_{user_id}"),
        InlineKeyboardButton("❌ បដិសេធ (Reject)", callback_data=f"reject_{user_id}")
    )
    
    # 3. ផ្ញើរូប Slip និងព័ត៌មានទៅកាន់ Admin ផ្ទាល់
    try:
        file_id = message.photo[-1].file_id
        caption_admin = f"📩 មានការស្នើសុំចូល VIP ថ្មី!\n- ឈ្មោះ: {user_name}\n- User ID: {user_id}"
        bot.send_photo(ADMIN_CHAT_ID, file_id, caption=caption_admin, reply_markup=markup)
    except Exception as e:
        print(f"Error sending to admin: {e}")

# មុខងារពេល Admin ចុចលើប៊ូតុង
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data
    if data.startswith("approve_"):
        target_user_id = data.split("_")[1]
        try:
            # ផ្ញើ Link VIP ទៅកាន់អតិថិជន
            success_text = (
                "🎉 ការទូទាត់ប្រាក់របស់អ្នកត្រូវបាន Admin ផ្ទៀងផ្ទាត់ និងអនុម័តជោគជ័យ!\n\n"
                "សូមចុចទីនេះដើម្បីចូលឆានែល VIP:\n" + VIP_CHANNEL_LINK
            )
            bot.send_message(target_user_id, success_text)
            
            # កែប្រែសាររបស់ Admin ថាបានអនុម័តរួច
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=call.message.caption + "\n\nSTATUS: ✅ បានអនុម័តរួចរាល់ (Approved)",
                reply_markup=None
            )
            bot.answer_callback_query(call.id, "បានអនុម័ត និងផ្ញើ Link ជូនអតិថិជនជោគជ័យ!")
        except Exception as e:
            bot.answer_callback_query(call.id, f"Error: {e}")
            
    elif data.startswith("reject_"):
        target_user_id = data.split("_")[1]
        try:
            # ជូនដំណឹងទៅអតិថិជនថាត្រូវបានបដិសេធ
            bot.send_message(
                target_user_id, 
                "❌ សូមអភ័យទោស! វិក្កយបត្រ (Slip) របស់អ្នកមិនត្រឹមត្រូវ ឬមិនអាចផ្ទៀងផ្ទាត់បានទេ។ សូមទាក់ទង Admin ផ្ទាល់។"
            )
            
            # កែប្រែសាររបស់ Admin ថាបានបដិសេធ
            bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                caption=call.message.caption + "\n\nSTATUS: ❌ បានបដិសេធ (Rejected)",
                reply_markup=None
            )
            bot.answer_callback_query(call.id, "បានបដិសេធវិក្កយបត្រនេះរួចហើយ!")
        except Exception as e:
            bot.answer_callback_query(call.id, f"Error: {e}")

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
