import logging
import re
from telegram import Update, ChatPermissions
from telegram.ext import Updater, CommandHandler
import os

# Get environment variables
TOKEN = os.getenv("BOT_TOKEN") or "8123613122:AAEWLMbOSMJEoW1VVlDTfaBTG-ec6cf_PoQ"
APP_URL = os.getenv("APP_URL") or "https://Telegram-spam-bot-1.onrender.com"

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Basic command to confirm it's working
def start(update, context):
    update.message.reply_text("Webhook bot is now live!")

dispatcher.add_handler(CommandHandler("start", start))

# Start webhook listener
updater.start_webhook(
    listen="0.0.0.0",
    port=8080,
    url_path=TOKEN
)

# Set webhook URL
updater.bot.set_webhook(APP_URL + "/" + TOKEN)

updater.idle()

# === CONFIGURATION ===
BOT_TOKEN = "8123613122:AAEWLMbOSMJEoW1VVlDTfaBTG-ec6cf_PoQ"
ADMIN_ID = 6871731402

# === LOGGING ===
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# === GLOBAL VARIABLES ===
offense_count = defaultdict(int)
blacklist = set()
whitelist = set()
violators = {}

# === HELPER FUNCTIONS ===
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def contains_link(text: str) -> bool:
    return bool(re.search(r"https?://|t\.me/|@\w+", text))

def warn_user(update: Update, context: CallbackContext, reason: str):
    user = update.effective_user
    chat_id = update.effective_chat.id
    offense_count[user.username] += 1
    remaining = 5 - offense_count[user.username]
    context.bot.send_message(chat_id=chat_id,
                             text=f"⚠️ @{user.username or user.id}, warning for {reason}. Offense {offense_count[user.username]}/5")

def ban_user(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = update.effective_chat.id
    context.bot.kick_chat_member(chat_id=chat_id, user_id=user.id)
    context.bot.send_message(chat_id=chat_id, text=f"🚫 @{user.username or user.id} has been banned for repeated violations.")
    violators[user.username] = offense_count[user.username]

# === HANDLERS ===
def handle_message(update: Update, context: CallbackContext):
    message = update.message
    user = message.from_user

    if user.username in whitelist:
        return

    # Check for link or forwarded message
    is_spam = contains_link(message.text or '') or message.forward_date

    if is_spam:
        try:
            context.bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
        except Exception as e:
            print(f"Error deleting message: {e}")

        if user.username in blacklist:
            return

        warn_user(update, context, "spamming")

        if offense_count[user.username] >= 5:
            ban_user(update, context)

def get_uid(update: Update, context: CallbackContext):
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        update.message.reply_text(f"User ID of @{target.username}: {target.id}")
    else:
        update.message.reply_text("❗ Reply to a user's message to get their UID.")

def whitelist_user(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        whitelist.add(target.username)
        blacklist.discard(target.username)
        update.message.reply_text(f"✅ @{target.username} has been whitelisted.")
    else:
        update.message.reply_text("❗ Reply to a user's message to whitelist them.")

def blacklist_user(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return

    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user
        blacklist.add(target.username)
        whitelist.discard(target.username)
        update.message.reply_text(f"⛔️ @{target.username} has been blacklisted.")
    else:
        update.message.reply_text("❗ Reply to a user's message to blacklist them.")

def violators_list(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return

    if not violators:
        update.message.reply_text("✅ No current violators.")
        return

    msg = "🚨 Violators List:\n"
    for user, count in violators.items():
        msg += f"@{user}: {count}/5 offenses\n"
    update.message.reply_text(msg)

def start(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return
    update.message.reply_text("✅ Anti-Spam Bot is active and running.")

# === MAIN FUNCTION ===
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("getuid", get_uid))
    dp.add_handler(CommandHandler("whitelist", whitelist_user))
    dp.add_handler(CommandHandler("blacklist", blacklist_user))
    dp.add_handler(CommandHandler("violators", violators_list))
    dp.add_handler(MessageHandler(Filters.text | Filters.forwarded, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()