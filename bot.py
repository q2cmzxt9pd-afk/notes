import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from database import Database

# Настройка базы данных
DB = Database()

# Состояния для диалога
WAITING_NOTE = 1

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    keyboard = [
        [KeyboardButton("📝 Новая заметка"), KeyboardButton("📋 Мои заметки")],
        [KeyboardButton("❌ Удалить заметку"), KeyboardButton("ℹ️ Помощь")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        "Я - твой персональный бот для заметок!\n"
        "Используй кнопки ниже:",
        reply_markup=reply_markup
    )

async def new_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напиши текст заметки:")
    return WAITING_NOTE

async def save_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    note_text = update.message.text
    
    note_id = DB.add_note(user_id, note_text)
    
    keyboard = [
        [KeyboardButton("📝 Новая заметка"), KeyboardButton("📋 Мои заметки")],
        [KeyboardButton("🏠 Главное меню")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(f"✅ Заметка #{note_id} сохранена!", reply_markup=reply_markup)
    return ConversationHandler.END

async def list_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    notes = DB.get_user_notes(user_id)
    
    if not notes:
        await update.message.reply_text("📭 У тебя пока нет заметок")
        return
    
    response = "📋 Твои заметки:\n\n"
    for note in notes[:10]:
        note_id, content, created_at = note
        response += f"#{note_id} - {content}\n"
        response += f"📅 {created_at[:16]}\n\n"
    
    await update.message.reply_text(response)

async def delete_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        note_id = context.args[0]
        user_id = update.message.from_user.id
        
        if DB.delete_note(user_id, note_id):
            await update.message.reply_text(f"✅ Заметка #{note_id} удалена")
        else:
            await update.message.reply_text("❌ Заметка не найдена")
    else:
        await update.message.reply_text("Используй: /delete <номер заметки>\nНапример: /delete 5")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📝 **Бот-заметки** - твой цифровой блокнот!

**Основные команды:**
/new - Создать новую заметку
/list - Показать все заметки  
/delete <номер> - Удалить заметку
/help - Эта справка

**Как использовать:**
1. Нажми "📝 Новая заметка"
2. Напиши текст
3. Готово! Заметка сохранена
    """
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "📝 Новая заметка":
        await new_note(update, context)
    elif text == "📋 Мои заметки":
        await list_notes(update, context)
    elif text == "❌ Удалить заметку":
        await update.message.reply_text("Используй команду: /delete <номер заметки>")
    elif text == "ℹ️ Помощь":
        await help_command(update, context)
    elif text == "🏠 Главное меню":
        await start(update, context)

def main():
    # Получаем токен из переменных окружения
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не установлен!")
        return
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation Handler для создания заметок
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('new', new_note),
            MessageHandler(filters.Regex('^(📝 Новая заметка)$'), new_note)
        ],
        states={
            WAITING_NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_note)],
        },
        fallbacks=[]
    )
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("list", list_notes))
    application.add_handler(CommandHandler("delete", delete_note))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    print("✅ Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()