import os
from threading import Thread
import telebot
from flask import Flask

# ដាក់ Token Bot របស់អ្នកនៅទីនេះ
TOKEN = '8803556544:AAGrb34ImMCmX2g2n0-ZDWtpszGPsZQAiBY'
bot = telebot.TeleBot(TOKEN)

# ----------------- ផ្នែកបង្កើត Web Server ក្លែងក្លាយដើម្បីកុំឱ្យ Render Timeout -----------------
app = Flask('')


@app.route('/')
def home():
  return 'Bot is running 24/7!'


def run():
  app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))


def keep_alive():
  t = Thread(target=run)
  t.start()


# ----------------- កូដ Bot របស់អ្នក -----------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
  bot.reply_to(message, 'សួស្តី! Bot កំពុងដំណើរការនៅលើ Render ហើយ។')


# ----------------- ចាប់ផ្តើមដំណើរការ -----------------
if __name__ == '__main__':
  keep_alive()  # បើក Server ឱ្យ Render ស្គាល់ Port
  bot.infinity_polling()  # រាន់ Bot Telegram
