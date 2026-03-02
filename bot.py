import os, sqlite3, threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# --- Flask Server ---
app = Flask('')
@app.route('/')
def home(): return "I am alive!"
def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- Database ---
conn = sqlite3.connect('data.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance REAL DEFAULT 0)''')
conn.commit()

TOKEN = "8535441292:AAGbaOFGoMdXbh36w1IPwFBMvsymI__iOi4"
ADMIN_ID = 8474225355# আপনার আইডি

# Keyboards
main_kb = [['IG Work Start', 'Rules & Price Update'], ['Withdraw', 'Refresh']]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (uid,))
    conn.commit()
    await update.message.reply_text("Welcome!", reply_markup=ReplyKeyboardMarkup(main_kb, resize_keyboard=True))

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == 'IG Work Start':
        kb = [['IG 2fa', 'IGMother Account 2fa'], ['IG Cookies', 'Refresh']]
        await update.message.reply_text("Select Menu:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))
    elif text == 'Rules & Price Update':
        btn = [[InlineKeyboardButton("View Link", url="https://t.me/instafbhub/19")]]
        await update.message.reply_text("Hi", reply_markup=InlineKeyboardMarkup(btn))
    elif text == 'Refresh':
        await update.message.reply_text("Main Menu", reply_markup=ReplyKeyboardMarkup(main_kb, resize_keyboard=True))

async def handle_docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document.file_name.endswith(('.xls', '.xlsx')):
        await context.bot.send_document(chat_id=ADMIN_ID, document=update.message.document.file_id, 
                                        caption=f"File from: {update.effective_user.id}")
        await update.message.reply_text("Admin-কে পাঠানো হয়েছে।")

def main():
    threading.Thread(target=run).start()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_docs))
    application.run_polling()

if __name__ == '__main__':
    main()
            
