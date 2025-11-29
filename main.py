"""
Learning Polish Bot - Main Entry Point
A bot to help users learn Polish language - 300 words with daily notifications
"""

import os
import sys
import json
import logging
from datetime import time
from dotenv import load_dotenv

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Add the script directory to Python path to ensure imports work
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from database import Database

# Load environment variables from the script directory
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database with absolute path
db_path = os.path.join(BASE_DIR, 'polish_bot.db')
db = Database(db_path)

# Load words database
words_db_path = os.path.join(BASE_DIR, 'words_database.json')
with open(words_db_path, 'r', encoding='utf-8') as f:
    WORDS_DATABASE = json.load(f)

TOTAL_WORDS = len(WORDS_DATABASE)


def format_word_message(word_data: dict) -> str:
    """Format word data into a beautiful message"""
    message = f"🇵🇱 **Слово дня — {word_data['word'].upper()}**\n\n"
    
    # Add transcription if available
    if word_data.get('transcription'):
        message += f"🔊 **Произношение:** [{word_data['transcription']}]\n\n"
    
    message += f"**Перевод:** {word_data['translation']}\n\n"
    message += f"**Описание:**\n{word_data['description']}\n\n"
    
    if word_data.get('examples'):
        message += "**Примеры использования:**\n"
        for example in word_data['examples']:
            message += f"• {example}\n"
        message += "\n"
    
    if word_data.get('fun_fact'):
        message += f"**Интересный факт:**\n{word_data['fun_fact']}"
    
    return message


def get_main_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Create main inline keyboard with buttons"""
    notifications_enabled = db.get_notifications_enabled(user_id)
    notif_text = "🔔 Уведомления: ВКЛ" if notifications_enabled else "🔕 Уведомления: ВЫКЛ"
    
    keyboard = [
        [InlineKeyboardButton("📖 Получить слово", callback_data="get_word")],
        [InlineKeyboardButton(notif_text, callback_data="toggle_notifications")],
        [InlineKeyboardButton("📊 Мой прогресс", callback_data="progress")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    
    # Add user to database if new
    is_new = db.add_user(user_id, username)
    
    if is_new:
        welcome_text = (
            f"Привет, {user.first_name}! 👋\n\n"
            "Добро пожаловать в **Learning Polish Bot**! 🇵🇱\n\n"
            "Я помогу тебе выучить 300 самых важных польских слов. "
            "Каждое утро в 9:00 (по польскому времени) я буду присылать тебе новое слово.\n\n"
            "**Также ты можешь:**\n"
            "📖 Запросить новое слово в любое время\n"
            "🔔 Включить/выключить утренние уведомления\n"
            "📊 Посмотреть свой прогресс\n\n"
            "После изучения всех 300 слов мы начнём заново!\n\n"
            "Готов начать изучение? Нажми кнопку ниже! 👇"
        )
    else:
        welcome_text = (
            f"С возвращением, {user.first_name}! 👋\n\n"
            "Рад видеть тебя снова! Продолжим изучение польского языка? 🇵🇱"
        )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard(user_id),
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "**📚 Помощь - Learning Polish Bot**\n\n"
        "**Команды:**\n"
        "/start - Начать работу с ботом\n"
        "/word - Получить следующее слово\n"
        "/progress - Посмотреть свой прогресс\n"
        "/help - Показать эту справку\n"
        "/restart - Начать изучение заново (сбросить прогресс)\n\n"
        "**Как это работает:**\n"
        "• Каждое утро в 9:00 (Warsaw time) бот отправляет новое польское слово\n"
        "• Всего 300 слов - самые важные и частотные\n"
        "• Можешь запросить новое слово в любое время кнопкой\n"
        "• После 300 слов всё начинается заново\n"
        "• Уведомления можно включить/выключить\n\n"
        "Удачи в изучении! 🇵🇱\n\n"
        "**ℹ️ Информация:**\n"
        "Разработчик: Zdunkevich Aliaksandr\n"
        "Дата: 29.11.2025\n"
        "Версия: 1.0"
    )
    
    if update.message:
        await update.message.reply_text(help_text, parse_mode='Markdown')
    else:
        await update.callback_query.message.reply_text(help_text, parse_mode='Markdown')


async def send_next_word(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Send next word to user"""
    # Get next word ID
    word_id = db.get_next_word_id(user_id, TOTAL_WORDS)
    
    # Get word data
    word_data = WORDS_DATABASE[word_id]
    
    # Format message
    message = format_word_message(word_data)
    
    # Send message
    await context.bot.send_message(
        chat_id=user_id,
        text=message,
        parse_mode='Markdown'
    )
    
    # Add to history
    db.add_word_to_history(user_id, word_id)
    
    return word_data['word']


async def word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /word command - send next word"""
    user_id = update.effective_user.id
    
    # Check if user exists
    if not db.user_exists(user_id):
        db.add_user(user_id, update.effective_user.username)
    
    word = await send_next_word(user_id, context)
    
    # Send keyboard
    await update.message.reply_text(
        f"Вот твоё слово! Хочешь ещё? 👇",
        reply_markup=get_main_keyboard(user_id)
    )


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /progress command"""
    user_id = update.effective_user.id
    
    if not db.user_exists(user_id):
        await update.message.reply_text("Сначала нажми /start чтобы начать!")
        return
    
    progress = db.get_user_progress(user_id, TOTAL_WORDS)
    
    progress_text = (
        f"📊 **Твой прогресс**\n\n"
        f"Изучено слов: **{progress['words_learned']} из {progress['total_words']}**\n"
        f"Прогресс: **{progress['percentage']}%**\n\n"
    )
    
    if progress['words_learned'] == 0:
        progress_text += "Ты ещё не начал изучение! Нажми кнопку ниже, чтобы получить первое слово. 👇"
    elif progress['words_learned'] == TOTAL_WORDS:
        progress_text += "🎉 Поздравляю! Ты изучил все 300 слов!\nТеперь они начнутся заново для повторения."
    else:
        remaining = TOTAL_WORDS - progress['words_learned']
        progress_text += f"Осталось: **{remaining} слов**\nПродолжай в том же духе! 💪"
    
    if update.message:
        await update.message.reply_text(
            progress_text,
            reply_markup=get_main_keyboard(user_id),
            parse_mode='Markdown'
        )
    else:
        await update.callback_query.message.reply_text(
            progress_text,
            reply_markup=get_main_keyboard(user_id),
            parse_mode='Markdown'
        )


async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /restart command - reset user progress"""
    user_id = update.effective_user.id
    
    if not db.user_exists(user_id):
        await update.message.reply_text("Сначала нажми /start чтобы начать!")
        return
    
    db.reset_user_progress(user_id)
    
    await update.message.reply_text(
        "✅ Твой прогресс сброшен!\n\n"
        "Теперь ты можешь начать изучение всех 300 слов заново. Удачи! 🇵🇱",
        reply_markup=get_main_keyboard(user_id)
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if not db.user_exists(user_id):
        db.add_user(user_id, update.effective_user.username)
    
    if query.data == "get_word":
        word = await send_next_word(user_id, context)
        await query.message.reply_text(
            f"Слово отправлено! Хочешь ещё? 👇",
            reply_markup=get_main_keyboard(user_id)
        )
    
    elif query.data == "toggle_notifications":
        new_state = db.toggle_notifications(user_id)
        status = "включены ✅" if new_state else "выключены ❌"
        
        await query.message.reply_text(
            f"Утренние уведомления {status}\n\n"
            f"{'Теперь каждое утро в 9:00 ты будешь получать новое слово!' if new_state else 'Ты больше не будешь получать автоматические уведомления.'}",
            reply_markup=get_main_keyboard(user_id)
        )
    
    elif query.data == "progress":
        await progress_command(update, context)
    
    elif query.data == "help":
        await help_command(update, context)


async def send_daily_words(context: ContextTypes.DEFAULT_TYPE):
    """Send daily words to all users with notifications enabled"""
    logger.info("Starting daily word distribution...")
    
    users = db.get_all_users_with_notifications()
    success_count = 0
    
    for user_id in users:
        try:
            await send_next_word(user_id, context)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to send word to user {user_id}: {e}")
    
    logger.info(f"Daily words sent to {success_count}/{len(users)} users")


def main():
    """Main function to start the bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("word", word_command))
    application.add_handler(CommandHandler("progress", progress_command))
    application.add_handler(CommandHandler("restart", restart_command))
    
    # Add callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Set up scheduler for daily messages (9:00 AM Warsaw time)
    scheduler = AsyncIOScheduler(timezone=pytz.timezone('Europe/Warsaw'))
    scheduler.add_job(
        send_daily_words,
        trigger=CronTrigger(hour=9, minute=0),
        args=[application],
        id='daily_words',
        name='Send daily Polish words',
        replace_existing=True
    )
    
    # Start scheduler
    scheduler.start()
    
    logger.info("🇵🇱 Learning Polish Bot started successfully!")
    logger.info("Daily words will be sent at 09:00 Warsaw time")
    
    # Start polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

