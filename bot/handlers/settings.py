from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from bot.handlers.texts import get_text
from .menu import show_main_menu
from bot.models import BotUser
from asgiref.sync import sync_to_async
from django.db.models import QuerySet
CHANGE_PHONE = 1

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_lang = context.user_data.get("lang", "uz")
    keyboard = [
        [get_text("language", user_lang)],
        [get_text("change_phone", user_lang)],
        [get_text("back", user_lang)],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(get_text("settings", user_lang), reply_markup=reply_markup)

async def handle_settings_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_lang = context.user_data.get("lang", "uz")
    text = update.message.text

    if text == get_text("change_phone", user_lang):
        await update.message.reply_text(get_text("enter_phone", user_lang), reply_markup=ReplyKeyboardRemove())
        return CHANGE_PHONE
    elif text == get_text("language", user_lang):
        await update.message.reply_text("Tilni tanlash funksiyasi hali yozilmagan.")
        return ConversationHandler.END
    elif text == get_text("back", user_lang):
        await update.message.reply_text(get_text("main_menu", user_lang))
        return ConversationHandler.END
    else:
        await update.message.reply_text(get_text("unknown_command", user_lang))
        return ConversationHandler.END

async def save_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    user_lang = context.user_data.get("lang", "uz")
    context.user_data["phone"] = phone
    await update.message.reply_text(get_text("phone_saved", user_lang))
    await settings_menu(update, context)
    return ConversationHandler.END


LANGUAGE_SELECTION, CHANGE_PHONE, SETTINGS_BACK = range(3)

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(
        [["🇺🇿 O‘zbek tili", "🇷🇺 Русский"], ["⬅️ Ortga"]],
        resize_keyboard=True
    )
    await update.message.reply_text(
        "Iltimos, tilni tanlang:",
        reply_markup=reply_markup
    )
    return LANGUAGE_SELECTION

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.text
    user_id = update.effective_user.id

    if user_choice == "🇺🇿 O‘zbek tili":
        await sync_to_async(BotUser.objects.filter(telegram_id=user_id).update)(language='uz')
        context.user_data['lang'] = 'uz'
        await update.message.reply_text("Til o‘zbek tiliga o‘zgartirildi!")
    elif user_choice == "🇷🇺 Русский":
        await sync_to_async(BotUser.objects.filter(telegram_id=user_id).update)(language='ru')
        context.user_data['lang'] = 'ru'
        await update.message.reply_text("Язык изменен на русский!")
    elif user_choice == "⬅️ Orqaga":
        await show_main_menu(update, context.user_data.get("lang", "uz"))
        return ConversationHandler.END
    else:
        await update.message.reply_text("Iltimos, mavjud tugmalardan birini tanlang.")
        return LANGUAGE_SELECTION

    await settings_menu(update, context)
    return LANGUAGE_SELECTION

async def handle_settings_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.text

    if user_choice == "⬅️ Ortga":
        await settings_menu(update, context)  # Sozlamalarga qaytish
        return LANGUAGE_SELECTION
    else:
        await update.message.reply_text("Iltimos, yangi telefon raqamni kiriting:")
        return CHANGE_PHONE

async def save_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_phone = update.message.text

    if not new_phone.isdigit():
        await update.message.reply_text("Telefon raqam noto‘g‘ri. Iltimos, faqat raqamlarni kiriting.")
        return CHANGE_PHONE

    context.user_data['phone'] = new_phone  # Foydalanuvchi ma'lumotlarini yangilash
    await update.message.reply_text(f"Telefon raqam muvaffaqiyatli o‘zgartirildi: {new_phone}")
    await settings_menu(update, context)  # Sozlamalarga qaytish
    return LANGUAGE_SELECTION


