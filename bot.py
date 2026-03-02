import os
import sqlite3
import threading
from flask import Flask
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, ConversationHandler

# --- Flask Server for 24/7 ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"

def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- Database ---
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (id INTEGER PRIMARY KEY, balance REAL DEFAULT 0, blocked INTEGER DEFAULT 0)''')
conn.commit()

ADMIN_ID = 123456789  # <--- আপনার আইডি এখানে দিন
TOKEN = "YOUR_BOT_TOKEN" # <--- বটফাদার থেকে পাওয়া টোকেন দিন

# --- Keyboards ---
main_kb = [['IG Work Start', 'Rules & Price Update'], ['Withdraw', 'Refresh']]
ig_kb = [['IG 2fa', 'IGMother Account 2fa'], ['IG Cookies', 'Refresh']]

# --- Logic ---
def start(update, context):
    user_id = update.message.from_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()
    update.message.reply_text("Welcome!", reply_markup=ReplyKeyboardMarkup(main_kb, resize_keyboard=True))

def handle_text(update, context):
    text = update.message.text
    user_id = update.message.from_user.id

    if text == 'IG Work Start':
        update.message.reply_text("Select Option:", reply_markup=ReplyKeyboardMarkup(ig_kb, resize_keyboard=True))
    
    elif text == 'Rules & Price Update':
        btn = [[InlineKeyboardButton("View Link", url="https://t.me/instafbhub/19")]]
        update.message.reply_text("Hi", reply_markup=InlineKeyboardMarkup(btn))

    elif text == 'IG 2fa':
        update.message.reply_text("দয়া করে আপনার Excel ফাইলটি পাঠান।")

    elif text == 'Refresh':
        update.message.reply_text("Main Menu", reply_markup=ReplyKeyboardMarkup(main_kb, resize_keyboard=True))

    elif text == 'Withdraw':
        btns = [
            [InlineKeyboardButton("Bkash", callback_data='w'), InlineKeyboardButton("Nagad", callback_data='w')],
            [InlineKeyboardButton("Save Payment Method", callback_data='save')]
        ]
        update.message.reply_text("Select Method:", reply_markup=InlineKeyboardMarkup(btns))

def handle_docs(update, context):
    if update.message.document.file_name.endswith(('.xls', '.xlsx')):
        update.message.forward(ADMIN_ID)
        context.bot.send_message(ADMIN_ID, f"User ID: {update.message.from_user.id}")
        update.message.reply_text("Success!")

def main():
    threading.Thread(target=run).start()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    dp.add_handler(MessageHandler(Filters.document, handle_docs))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
