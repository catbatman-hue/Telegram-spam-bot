import os
from flask import Flask, request
from threading import Thread
from telegram import Update, ChatPermissions
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import logging

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6871731402"))
PORT = int(os.environ.get("PORT", 10000))

# In-memory stores
whitelist = set()
blacklist = set()
spam_count = {}
pending_action = {}

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Helper: check admin
def is_admin(user_id):
    return user_id == ADMIN_ID

# Start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 Bot is live and ready.")

# Command prep
def request_target(update: Update, context: CallbackContext, command: str):
    if not is_admin(update.effective_user.id):
        return update.message.reply_text("❌ You're not authorized.")
    pending_action[update.effective_user.id] = command
    update.message.reply_text(f"🕵️ Please *reply* to the user you want to `{command}`", parse_mode="Markdown")

# Handle reply
def handle_reply(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in pending_action:
        return
    command = pending_action.pop(user_id)

    if not update.message.reply_to_message:
        return update.message.reply_text("❌ You must reply to the user's message.")

    target = update.message.reply_to_message.from_user
    tid = target.id

    if command == "whitelist":
        whitelist.add(tid)
        update.message.reply_text(f"✅ {target.first_name} added to whitelist.")
    elif command == "blacklist":
        blacklist.add(tid)
        update.message.reply_text(f"⚠️ {target.first_name} added to blacklist.")
    elif command == "unlist":
        whitelist.discard(tid)
        blacklist.discard(tid)
        update.message.reply_text(f"✅ {target.first_name} removed from all lists.")
    elif command == "ban":
        context.bot.kick_chat_member(update.effective_chat.id, tid)
        update.message.reply_text(f"🚫 {target.first_name} has been banned.")
    elif command == "suspend":
        context.bot.restrict_chat_member(update.effective_chat.id, tid, ChatPermissions(can_send_messages=False))
        update.message.reply_text(f"⛔ {target.first_name} has been suspended.")
    elif command == "removed":
        context.bot.kick_chat_member(update.effective_chat.id, tid)
        update.message.reply_text(f"🗑️ {target.first_name} removed from group.")

# Spam detection
def monitor_spam(update: Update, context: CallbackContext):
    user = update.effective_user
    if user.id in whitelist:
        return

    message = update.message
    text = message.text or ""

    if message.forward_from or "http" in text or "www" in text:
        spam_count[user.id] = spam_count.get(user.id, 0) + 1
        count = spam_count[user.id]

        try:
            message.delete()
        except:
            pass

        if count >= 5:
            try:
                context.bot.kick_chat_member(update.effective_chat.id, user.id)
                update.message.reply_text(f"🚷 {user.first_name} removed for spam (5/5).")
            except:
                pass
        else:
            update.message.reply_text(f"⚠️ Spam detected! Warning {count}/5.")

# Handlers
dispatcher.add_handler(CommandHandler("start", start))
for cmd in ["whitelist", "blacklist", "unlist", "ban", "suspend", "removed"]:
    dispatcher.add_handler(CommandHandler(cmd, lambda u, c, cmd=cmd: request_target(u, c, cmd)))
dispatcher.add_handler(MessageHandler(Filters.reply & Filters.group, handle_reply))
dispatcher.add_handler(MessageHandler(Filters.text & Filters.group, monitor_spam))

# Flask app
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), updater.bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "✅ Bot running."

def run():
    app.run(host="0.0.0.0", port=PORT)

def set_webhook():
    print("Setting webhook...")
    url = os.getenv("APP_URL") or f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    success = updater.bot.set_webhook(url)
    print("Webhook set:", success)

if __name__ == "__main__":
    Thread(target=run).start()
    set_webhook()        spam_count[user.id] = spam_count.get(user.id, 0) + 1
        count = spam_count[user.id]

        try:
            update.message.delete()
        except:
            pass

        if count >= 5:
            try:
                context.bot.kick_chat_member(update.effective_chat.id, user.id)
                update.message.reply_text(f"🚫 {user.first_name} removed for spam.")
            except:
                pass
        else:
            update.message.reply_text(f"⚠️ Spam detected. {count}/5 warnings.")

# Basic commands
dispatcher.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("🤖 Bot is active!")))

# Admin commands
for cmd in ["whitelist", "blacklist", "ban", "suspend", "unlist", "removed"]:
    dispatcher.add_handler(CommandHandler(cmd, lambda u, c, cmd=cmd: request_target(u, c, cmd)))

dispatcher.add_handler(MessageHandler(Filters.reply & Filters.group, perform_action))
dispatcher.add_handler(MessageHandler(Filters.text & Filters.group, handle_spam))

# Flask webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), updater.bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "Running ✅"

def run():
    app.run(host="0.0.0.0", port=PORT)

def set_webhook():
    url = os.getenv("APP_URL") or f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    success = updater.bot.set_webhook(url)
    print("Webhook set:", success)

if __name__ == "__main__":
    Thread(target=run).start()
    set_webhook()    awaiting_command[update.effective_user.id] = command

# --- Admin Commands ---
@admin_only
def start(update: Update, context: CallbackContext):
    update.message.reply_text("✅ Anti-spam bot is live!")

@admin_only
def whitelist_cmd(update: Update, context: CallbackContext):
    ask_for_target(update, context, "whitelist")

@admin_only
def blacklist_cmd(update: Update, context: CallbackContext):
    ask_for_target(update, context, "blacklist")

@admin_only
def unlist_cmd(update: Update, context: CallbackContext):
    ask_for_target(update, context, "unlist")

@admin_only
def ban_cmd(update: Update, context: CallbackContext):
    ask_for_target(update, context, "ban")

@admin_only
def remove_cmd(update: Update, context: CallbackContext):
    ask_for_target(update, context, "remove")

@admin_only
def suspend_cmd(update: Update, context: CallbackContext):
    ask_for_target(update, context, "suspend")

def apply_action(update: Update, context: CallbackContext):
    from_user = update.effective_user.id
    if from_user not in awaiting_command:
        return

    command = awaiting_command.pop(from_user)
    target_user = (
        update.message.reply_to_message.from_user
        if update.message.reply_to_message else update.message.entities[1].user
        if update.message.entities and len(update.message.entities) > 1 else None
    )

    if not target_user:
        update.message.reply_text("⚠️ Please reply to or mention a valid user.")
        return

    uid = target_user.id

    if command == "whitelist":
        whitelist.add(uid)
        blacklist.discard(uid)
        update.message.reply_text(f"✅ Whitelisted {target_user.full_name}")
    elif command == "blacklist":
        blacklist.add(uid)
        whitelist.discard(uid)
        update.message.reply_text(f"🚫 Blacklisted {target_user.full_name}")
    elif command == "unlist":
        whitelist.discard(uid)
        blacklist.discard(uid)
        update.message.reply_text(f"❌ Removed {target_user.full_name} from all lists.")
    elif command == "ban":
        context.bot.kick_chat_member(update.effective_chat.id, uid)
        update.message.reply_text(f"🔨 Banned {target_user.full_name}")
    elif command == "remove":
        context.bot.kick_chat_member(update.effective_chat.id, uid)
        context.bot.unban_chat_member(update.effective_chat.id, uid)
        update.message.reply_text(f"👢 Removed {target_user.full_name}")
    elif command == "suspend":
        perms = ChatPermissions(can_send_messages=False)
        context.bot.restrict_chat_member(update.effective_chat.id, uid, permissions=perms)
        update.message.reply_text(f"🚷 Suspended {target_user.full_name}")

# --- Anti-spam logic ---
def is_spam(message):
    if message.forward_date:
        return True
    if "http://" in message.text or "https://" in message.text or "t.me/" in message.text:
        return True
    if message.from_user.username and any(char.isdigit() for char in message.from_user.username):
        return True
    return False

def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Handle interactive command targeting
    if user_id in awaiting_command:
        apply_action(update, context)
        return

    # Skip whitelisted or admin
    if user_id in whitelist or user_id == ADMIN_ID:
        return

    # Detect spam
    if is_spam(update.message):
        update.message.delete()
        spam_tracker[user_id] = spam_tracker.get(user_id, 0) + 1

        if spam_tracker[user_id] >= 5:
            context.bot.kick_chat_member(chat_id, user_id)
            context.bot.send_message(chat_id, f"🚫 User {update.effective_user.full_name} removed for spamming.")
            spam_tracker.pop(user_id)
        else:
            remaining = 5 - spam_tracker[user_id]
            context.bot.send_message(chat_id, f"⚠️ Spam detected. {remaining} strike(s) left before removal.")

# --- Flask routes ---
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), updater.bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "Bot is alive."

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

def set_webhook():
    url = f"{APP_URL}/{TOKEN}"
    success = updater.bot.set_webhook(url)
    print("Webhook set:", success)

# --- Register handlers ---
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("whitelist", whitelist_cmd))
dispatcher.add_handler(CommandHandler("blacklist", blacklist_cmd))
dispatcher.add_handler(CommandHandler("unlist", unlist_cmd))
dispatcher.add_handler(CommandHandler("ban", ban_cmd))
dispatcher.add_handler(CommandHandler("remove", remove_cmd))
dispatcher.add_handler(CommandHandler("suspend", suspend_cmd))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# --- Main ---
if __name__ == "__main__":
    Thread(target=run).start()
    set_webhook()    if update.effective_user.id != ADMIN_ID:
        return update.message.reply_text("❌ You're not authorized.")
    try:
        user_id = int(context.args[0])
        blacklist.add(user_id)
        update.message.reply_text(f"⛔ Blacklisted user: {user_id}")
    except:
        update.message.reply_text("❌ Usage: /blacklist <user_id>")

def unlist_cmd(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return update.message.reply_text("❌ You're not authorized.")
    try:
        user_id = int(context.args[0])
        whitelist.discard(user_id)
        blacklist.discard(user_id)
        update.message.reply_text(f"🧹 Removed user {user_id} from all lists.")
    except:
        update.message.reply_text("❌ Usage: /unlist <user_id>")

def removed_cmd(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return update.message.reply_text("❌ You're not authorized.")
    try:
        user_id = int(context.args[0])
        context.bot.kick_chat_member(chat_id=update.effective_chat.id, user_id=user_id)
        update.message.reply_text(f"🚫 Removed user: {user_id}")
    except:
        update.message.reply_text("❌ Failed to remove. Usage: /removed <user_id>")

def ban_cmd(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return update.message.reply_text("❌ You're not authorized.")
    try:
        user_id = int(context.args[0])
        context.bot.ban_chat_member(chat_id=update.effective_chat.id, user_id=user_id)
        update.message.reply_text(f"🔨 Banned user: {user_id}")
    except:
        update.message.reply_text("❌ Failed to ban. Usage: /ban <user_id>")

def suspend_cmd(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return update.message.reply_text("❌ You're not authorized.")
    try:
        user_id = int(context.args[0])
        permissions = ChatPermissions(can_send_messages=False)
        context.bot.restrict_chat_member(chat_id=update.effective_chat.id, user_id=user_id, permissions=permissions)
        update.message.reply_text(f"🛑 Suspended user: {user_id}")
    except:
        update.message.reply_text("❌ Failed to suspend. Usage: /suspend <user_id>")

# --- REGISTER COMMANDS ---
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("whitelist", whitelist_cmd))
dispatcher.add_handler(CommandHandler("blacklist", blacklist_cmd))
dispatcher.add_handler(CommandHandler("unlist", unlist_cmd))
dispatcher.add_handler(CommandHandler("removed", removed_cmd))
dispatcher.add_handler(CommandHandler("ban", ban_cmd))
dispatcher.add_handler(CommandHandler("suspend", suspend_cmd))

# --- WEBHOOK HANDLER ---
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
        update = Update.de_json(request.get_json(force=True), updater.bot)
        dispatcher.process_update(update)
        return "ok"

@app.route("/")
def home():
    return "✅ Bot is alive!"

# --- FLASK + WEBHOOK ---
def run():
    app.run(host="0.0.0.0", port=PORT)

def set_webhook():
    print("Setting webhook...")
    url = os.getenv("APP_URL") or f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    success = updater.bot.set_webhook(url)
    return success
    
def set_webhook():
    print("Setting webhook...")
    app_url = os.getenv("APP_URL") or f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}"
    full_url = f"{app_url}/{TOKEN}"
    success = updater.bot.set_webhook(full_url)
    return success

if __name__ == "__main__":
    Thread(target=run).start()
    success = set_webhook()
    print("Webhook set:", success)

app_url = os.getenv("APP_URL") or f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}"
updater.bot.set_webhook(app_url + "/" + TOKEN)

updater.idle()

# Set webhook URL
updater.bot.set_webhook(
    url=APP_URL + "/" + TOKEN,
    port=443
)

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

# ========= Command logic (paste after dispatcher setup) =========

# In-memory sets
whitelist_users = set()
blacklist_users = set()

# Your Telegram ID (admin only)
ADMINS = {6871731402}  # Add more admin IDs if needed

def is_admin(user_id):
    return user_id in ADMINS

def start(update, context):
    update.message.reply_text("✅ Webhook bot is live!")

def getuid(update, context):
    user = update.effective_user
    print(f"[LOG] /getuid requested by: {user.username} (ID: {user.id})")
    update.message.reply_text(f"🆔 Your Telegram ID is: {user.id}")

def whitelist(update, context):
    if not is_admin(update.effective_user.id):
        return update.message.reply_text("🚫 You're not authorized.")
    if not context.args:
        return update.message.reply_text("⚠️ Usage: /whitelist <user_id>")
    user_id = int(context.args[0])
    whitelist_users.add(user_id)
    blacklist_users.discard(user_id)
    update.message.reply_text(f"✅ Whitelisted user `{user_id}`", parse_mode="Markdown")

def blacklist(update, context):
    if not is_admin(update.effective_user.id):
        return update.message.reply_text("🚫 You're not authorized.")
    if not context.args:
        return update.message.reply_text("⚠️ Usage: /blacklist <user_id>")
    user_id = int(context.args[0])
    blacklist_users.add(user_id)
    whitelist_users.discard(user_id)
    update.message.reply_text(f"❌ Blacklisted user `{user_id}`", parse_mode="Markdown")

def unlist(update, context):
    if not is_admin(update.effective_user.id):
        return update.message.reply_text("🚫 You're not authorized.")
    if not context.args:
        return update.message.reply_text("⚠️ Usage: /unlist <user_id>")
    user_id = int(context.args[0])
    whitelist_users.discard(user_id)
    blacklist_users.discard(user_id)
    update.message.reply_text(f"🗑️ Removed user `{user_id}` from all lists", parse_mode="Markdown")

# Aliases
ban = suspend = removed = unlist

# Register handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("getuid", getuid))
dispatcher.add_handler(CommandHandler("whitelist", whitelist))
dispatcher.add_handler(CommandHandler("blacklist", blacklist))
dispatcher.add_handler(CommandHandler("unlist", unlist))
dispatcher.add_handler(CommandHandler("ban", ban))
dispatcher.add_handler(CommandHandler("suspend", suspend))
dispatcher.add_handler(CommandHandler("removed", removed))

if __name__ == '__main__':
    main()