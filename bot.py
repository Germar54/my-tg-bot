import os, sqlite3, threading
from flask import Flask
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, ConversationHandler

# --- Flask Server (Render এর জন্য) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"
def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- Database ---
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (id INTEGER PRIMARY KEY, balance REAL DEFAULT 0, blocked INTEGER DEFAULT 0)''')
conn.commit()

# --- Config ---
TOKEN = "আপনার_বট_টোকেন"
ADMIN_ID = 123456789 # আপনার টেলিগ্রাম আইডি

# Keyboards
main_kb = [['IG Work Start', 'Rules & Price Update'], ['Withdraw', 'Refresh']]
ig_kb = [['IG 2fa', 'IGMother Account 2fa'], ['IG Cookies', 'Refresh']]

# --- Handlers ---
def start(update, context):
    uid = update.message.from_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (uid,))
    conn.commit()
    update.message.reply_text("Welcome!", reply_markup=ReplyKeyboardMarkup(main_kb, resize_keyboard=True))

def handle_text(update, context):
    text = update.message.text
    uid = update.message.from_user.id

    if text == 'IG Work Start':
        update.message.reply_text("Select Menu:", reply_markup=ReplyKeyboardMarkup(ig_kb, resize_keyboard=True))
    
    elif text == 'Rules & Price Update':
        btn = [[InlineKeyboardButton("View Link", url="https://t.me/instafbhub/19")]]
        update.message.reply_text("Hi", reply_markup=InlineKeyboardMarkup(btn))

    elif text == 'IG 2fa':
        update.message.reply_text("আপনার Excel (.xls/.xlsx) ফাইলটি পাঠান।")

    elif text == 'IGMother Account 2fa':
        btns = [[InlineKeyboardButton("File", callback_data='f'), InlineKeyboardButton("Single Account", callback_data='s')]]
        update.message.reply_text("Choose:", reply_markup=InlineKeyboardMarkup(btns))

    elif text == 'Refresh':
        update.message.reply_text("Main Menu", reply_markup=ReplyKeyboardMarkup(main_kb, resize_keyboard=True))

# --- File Handling ---
def handle_docs(update, context):
    doc = update.message.document
    if doc.file_name.endswith(('.xls', '.xlsx')):
        context.bot.send_document(ADMIN_ID, doc.file_id, caption=f"File from: `{update.message.from_user.id}`", parse_mode='Markdown')
        update.message.reply_text("Sent to Admin!")

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
  
