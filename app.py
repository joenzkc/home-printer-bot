import os
from dotenv import load_dotenv
import logging
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes

# Set up basic logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace 'YOUR_TOKEN' with your actual Bot token received from BotFather
load_dotenv()

allowed_ids = os.getenv('ALLOWED_IDS', '')

# Convert the comma-separated string of IDs into a set of strings
ALLOWED_IDS = set(id.strip() for id in allowed_ids.split(',') if id.strip())

TOKEN = os.getenv('TELEGRAM_API_TOKEN')

if not TOKEN:
    logger.error('Please set TELEGRAM_BOT_TOKEN in .env file')

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def downloader(update, context):
    user_id = str(update.effective_user.username)
    print(user_id, update.effective_user.username)
    if user_id not in ALLOWED_IDS:
        await update.message.reply_text("You are not authorized to use this bot for printing.")
        return
    
    file = await context.bot.get_file(update.message.document.file_id)
    file_path = os.path.join('downloads', file.file_unique_id + os.path.splitext(file.file_path)[1])  # Ensuring unique file name
    try:
        # Make sure the 'downloads' directory exists
        os.makedirs('downloads', exist_ok=True)
        # Download the file
        await file.download_to_drive(file_path)
        # Notify user that file has been downloaded and is being printed
        await update.message.reply_text('Printing file...')
        # Execute print command
        command = f"lp {file_path}"
        os.system(command)
        # Notify user that file has been printed
        await update.message.reply_text('File printed')
    except Exception as e:
        logger.error(f"Failed to download or print file: {str(e)}")
        await update.message.reply_text('Failed to process your file.')
    

def error(update: Update, context: CallbackContext):
    """Log errors caused by updates."""
    logger.warning(f'Update "{update}" caused error "{context.error}"')

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", hello))
    app.add_handler(MessageHandler(filters.Document.ALL, downloader))
    app.run_polling()

if __name__ == '__main__':
    main()
