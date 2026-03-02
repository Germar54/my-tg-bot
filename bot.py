import os, sqlite3, threading
from flask import Flask
from telegram import (ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, 
                      Update, ParseMode, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, 
                          CallbackContext, CallbackQueryHandler, ConversationHandler)

# --- Flask Server for Render (Keep Alive) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is running!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- Database Setup ---
conn = sqlite3.connect('bot_data.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (id INTEGER PRIMARY KEY, balance REAL DEFAULT 0, method TEXT, address TEXT, blocked INTEGER DEFAULT 0)''')
conn.commit()

# --- Configuration ---
TOKEN = "8535441292:AAGbaOFGoMdXbh36w1IPwFBMvsymI__iOi4"
ADMIN_ID = 8474225355 # আপনার টেলিগ্রাম আইডি

# States
SINGLE_ACC, WITHDRAW_ADDR, WITHDRAW_AMT = range(3)

# --- Keyboards ---
main_kb = [['IG Work Start', 'Rules & Price Update'], ['Withdraw', 'Refresh']]
ig_kb = [['IG 2fa', 'IGMother Account 2fa'], ['IG Cookies', 'Refresh']]

# --- Start & Main Menu ---
def start(update, context):
    user_id = update.message.from_user.id
    cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
    conn.commit()
    
    cursor.execute("SELECT blocked FROM users WHERE id=?", (user_id,))
    if cursor.fetchone()[0] == 1: return
    
    update.message.reply_text("Welcome!", reply_markup=ReplyKeyboardMarkup(main_kb, resize_keyboard=True))

# --- Rules & Price ---
def rules(update, context):
    btn = [[InlineKeyboardButton("View Link", url="https://t.me/instafbhub/19")]]
    update.message.reply_text("Hi", reply_markup=InlineKeyboardMarkup(btn))

# --- IG Work Logic ---
def ig_start(update, context):
    update.message.reply_text("Select an option:", reply_markup=ReplyKeyboardMarkup(ig_kb, resize_keyboard=True))

def ig_mother(update, context):
    btns = [[InlineKeyboardButton("File", callback_data='ig_file'), 
             InlineKeyboardButton("Single Account", callback_data='ig_single')]]
    update.message.reply_text("Select type:", reply_markup=InlineKeyboardMarkup(btns))

# --- Withdraw Logic ---
def withdraw_menu(update, context):
    btns = [
        [InlineKeyboardButton("Bkash", callback_data='w_Bkash'), InlineKeyboardButton("Nagad", callback_data='w_Nagad')],
        [InlineKeyboardButton("Rocket", callback_data='w_Rocket'), InlineKeyboardButton("Binance", callback_data='w_Binance')],
        [InlineKeyboardButton("Save Payment Method", callback_data='w_save')]
    ]
    update.message.reply_text("Choose Withdrawal Method:", reply_markup=InlineKeyboardMarkup(btns))

def callback_handler(update, context):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    if data.startswith('w_'):
        method = data.split('_')[1]
        if method == 'save':
            query.edit_message_text("Enter withdrawal amount:")
            return WITHDRAW_AMT
        else:
            context.user_data['method'] = method
            query.edit_message_text(f"Enter your {method} number/address:")
            return WITHDRAW_ADDR

    elif data == 'ig_single':
        query.edit_message_text("Please enter: USA Pass, USA Username, USA 2FA code (Space separated)")
        return SINGLE_ACC

    elif data == 'ig_file':
        query.edit_message_text("Please send your Excel file (.xls/.xlsx)")

    elif data.startswith('accept_'):
        uid, amt = data.split('_')[1:]
        context.bot.send_message(uid, "Withdrawal Successful.")
        query.edit_message_text(f"Accepted Withdrawal for {uid}")

# --- Data Handlers ---
def handle_docs(update, context):
    user_id = update.message.from_user.id
    doc = update.message.document
    if doc.file_name.endswith(('.xls', '.xlsx')):
        context.bot.send_document(ADMIN_ID, doc.file_id, caption=f"File from: `{user_id}`", parse_mode='Markdown')
        update.message.reply_text("File sent to Admin!")
    else:
        update.message.reply_text("Invalid file. Send .xls or .xlsx only.")

def single_acc_receive(update, context):
    user_id = update.message.from_user.id
    details = update.message.text
    context.bot.send_message(ADMIN_ID, f"New Single Account from `{user_id}`:\n\n`{details}`", parse_mode='MarkdownV2')
    update.message.reply_text("Account details sent!", reply_markup=ReplyKeyboardMarkup(main_kb, resize_keyboard=True))
    return ConversationHandler.END

# --- Admin Panel ---
def admin_commands(update, context):
    if update.message.from_user.id != ADMIN_ID: return
    cmd = update.message.text.split()
    
    if cmd[0] == '/check':
        uid = cmd[1]
        cursor.execute("SELECT balance FROM users WHERE id=?", (uid,))
        bal = cursor.fetchone()
        update.message.reply_text(f"User: {uid}\nBalance: {bal[0] if bal else 0} Taka")
    
    elif cmd[0] == '/payment':
        uid, amt = cmd[1], float(cmd[2])
        cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amt, uid))
        conn.commit()
        update.message.reply_text("Balance Updated.")

# --- Main Functions ---
def main():
    threading.Thread(target=run).start()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.regex('^Rules & Price Update$'), rules))
    dp.add_handler(MessageHandler(Filters.regex('^IG Work Start$'), ig_start))
    dp.add_handler(MessageHandler(Filters.regex('^IGMother Account 2fa$'), ig_mother))
    dp.add_handler(MessageHandler(Filters.regex('^Withdraw$'), withdraw_menu))
    dp.add_handler(MessageHandler(Filters.regex('^Refresh$'), start))
    dp.add_handler(MessageHandler(Filters.document, handle_docs))
    dp.add_handler(MessageHandler(Filters.regex('^/'), admin_commands))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
