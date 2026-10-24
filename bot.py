import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '8803556544:AAGrWTMTuMsZzeoKVTJK0xgrh57pIGGyQWI'
bot = telebot.TeleBot(TOKEN)

ADMIN_CHAT_ID = 5691292245  
VIP_CHANNEL_ID = -1004481942954  # លេខ ID ឆានែល VIP របស់ ហាន់នី

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    welcome_text = (
        "ស្វាគមន៍មកកាន់ប្រព័ន្ធទូទាត់ប្រាក់ ប្រជុំរឿង VIP!\n\n"
        "តម្លៃសមាជិក៖ 1.00$\n"
        "សូមស្កេន QR Code ខាងលើដើម្បីទូទាត់ប្រាក់ ហើយផ្ញើ Slip មកទីនេះ!"
    )
    try:
        with open('qr.jpg', 'rb') as photo:
            bot.send_photo(chat_id, photo, caption=welcome_text)
    except Exception as e:
        bot.send_message(chat_id, welcome_text)

@bot.message_handler(content_types=['photo'])
def handle_slip(message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    
    bot.reply_to(message, "✅ បានទទួលវិក្កយបត្រ (Slip) របស់អ្នកហើយ!\nសូមរង់ចាំ Admin ពិនិត្យ និងផ្ទៀងផ្ទាត់បន្តិច។")
    
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("✅ Yes (យល់ព្រម)", callback_data=f"approve_{chat_id}"),
        InlineKeyboardButton("❌ No (បដិសេដ)", callback_data=f"reject_{chat_id}")
    )
    
    caption_admin = f"📩 មាន Slip ថ្មីផ្ញើមកពីអតិថិជន៖ {user_name} (ID: {chat_id})\nសូមពិនិត្យមើលរូបភាព Slip ខាងក្រោម៖"
    bot.send_photo(ADMIN_CHAT_ID, message.photo[-1].file_id, caption=caption_admin, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data
    
    if data.startswith("approve_"):
        user_id = data.split("_")[1]
        try:
            # បង្កើតលីងអញ្ជើញចូលឆានែល (កំណត់ឱ្យប្រើបានតែម្តងគត់)
            invite_link = bot.create_chat_invite_link(VIP_CHANNEL_ID, member_limit=1).invite_link
            
            bot.send_message(user_id, f"🎉 ការទូទាត់ប្រាក់របស់អ្នកត្រូវបានផ្ទៀងផ្ទាត់ និងអនុម័តជោគជ័យ!\n\nសូមចុចទីនេះដើម្បីចូលឆានែល VIP:\n{invite_link}")
            bot.answer_callback_query(call.id, "បានអនុម័ត និងផ្ញើលីងជូនអតិថិជនជោគជ័យ!")
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=f"✅ បានអនុម័ត (Approved) និងផ្ញើលីងជូនអតិថិជនរួចរាល់。")
        except Exception as e:
            bot.answer_callback_query(call.id, f"មានបញ្ហា: {e}")
            print(f"Error approval: {e}")
            
    elif data.startswith("reject_"):
        user_id = data.split("_tokenId" if False else "reject_")[1] # Clean split
        try:
            # Fixed split logic for user_id extraction in reject
            pass
        except:
            pass

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_query(call):
    user_id = call.data.split("_")[1]
    try:
        bot.send_message(user_id, "❌ សូមអភ័យទោស ការទូទាត់ប្រាក់ (Slip) របស់អ្នកមិនត្រឹមត្រូវ ឬមិនអាចផ្ទៀងផ្ទាត់បានទេ។ សូមត្រួតពិនិត្យ និងផ្ញើមកម្ដងទៀត!")
        bot.answer_callback_query(call.id, "បានបដិសេដសំណើនេះរួចរាល់!")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=f"❌ បានបដិសេដ (Rejected) ការទូទាត់នេះរួចរាល់។")
    except Exception as e:
        bot.answer_callback_query(call.id, f"មានបញ្ហា: {e}")

bot.infinity_polling()