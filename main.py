import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Telegram bot token
TOKEN = '8284328600:AAF7-V7XY6gQsaZGXqTBJqKHj7X89t5OlFs'
bot = telebot.TeleBot(TOKEN)

# Telegram chat IDs
ADMIN_IDS = [1875031707, 5902520531]

# Google Sheets setup
SHEET_NAME = "WithdrawRequests"
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1LjSTWYUTg4DD8lPBnv_Npk49fdwxup1fv5JUCtl2sJg/edit"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_url(SPREADSHEET_URL).worksheet(SHEET_NAME)

# Команда: /withdraw
@bot.message_handler(commands=['withdraw'])
def withdraw_command(message):
    msg = bot.send_message(message.chat.id, "Аты-жөніңізді енгізіңіз:")
    bot.register_next_step_handler(msg, process_name_step)

user_data = {}

def process_name_step(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"name": message.text}
    msg = bot.send_message(chat_id, "Kaspi нөміріңізді енгізіңіз:")
    bot.register_next_step_handler(msg, process_kaspi_step)

def process_kaspi_step(message):
    chat_id = message.chat.id
    user_data[chat_id]["kaspi"] = message.text
    msg = bot.send_message(chat_id, "Қанша ақша шешкіңіз келеді?")
    bot.register_next_step_handler(msg, process_amount_step)

def process_amount_step(message):
    chat_id = message.chat.id
    user_data[chat_id]["amount"] = message.text
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Sheets-ке жазу
    data = user_data[chat_id]
    sheet.append_row([now, data["name"], data["kaspi"], data["amount"]])

    # Хабарлама админдерге
    notif = f"📤 Ақша шешу:\n👤 {data['name']}\n📞 {data['kaspi']}\n💸 {data['amount']} ₸"
    for admin_id in ADMIN_IDS:
        bot.send_message(admin_id, notif)

    bot.send_message(chat_id, "✅ Сұранысыңыз қабылданды!")
    del user_data[chat_id]

# Ботты іске қосу
bot.polling(none_stop=True)
