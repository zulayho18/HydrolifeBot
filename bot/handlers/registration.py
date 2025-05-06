from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from bot.models import BotUser
from asgiref.sync import sync_to_async
from bot.handlers.texts import get_text, TEXT_LANG_WARNING, TEXT_ENTER_FIRST_NAME, TEXT_ENTER_LAST_NAME, BTN_SEND_CONTACT, LANGUAGE_CODE
from .menu import show_main_menu
# Bosqichlar
LANGUAGE, FULL_NAME, PHONE = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    user = await sync_to_async(BotUser.objects.filter(telegram_id=telegram_id).first)()

    if user:
        await update.message.reply_text(f"Salom, {user.full_name}! Bosh menyuga xush kelibsiz.")
        await show_main_menu(update, user.language)
        return ConversationHandler.END
    else:
        await update.message.reply_text("Botga xush kelibsiz!")
        await update.message.reply_text(
            TEXT_LANG_WARNING,
            reply_markup=ReplyKeyboardMarkup([["O'zbek", "Русский"]], resize_keyboard=True)
        )
        return LANGUAGE


async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.message.text.lower()
    if "o'z" in lang or "uz" in lang:
        context.user_data['lang'] = 1  # O‘zbek tili
    elif "рус" in lang or "ru" in lang:
        context.user_data['lang'] = 2  # Rus tili
    else:
        await update.message.reply_text(TEXT_LANG_WARNING)
        return LANGUAGE

    await update.message.reply_text(
        TEXT_ENTER_FIRST_NAME[context.user_data['lang']]
    )
    return FULL_NAME


async def full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['full_name'] = update.message.text
    reply_markup = ReplyKeyboardMarkup([
        [KeyboardButton(text=BTN_SEND_CONTACT[context.user_data['lang']], request_contact=True)]
    ], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        TEXT_ENTER_LAST_NAME[context.user_data['lang']],
        reply_markup=reply_markup
    )
    return PHONE# Keyingi bosqich davlatini qaytarish (PHONE)



async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        context.user_data['phone'] = update.message.contact.phone_number
    elif update.message.text:
        context.user_data['phone'] = update.message.text
    else:
        await update.message.reply_text("Telefon raqam noto‘g‘ri.")
        return PHONE

    await sync_to_async(BotUser.objects.create)(
        telegram_id=update.effective_user.id,
        fio=context.user_data.get('full_name'),
        phone_number=context.user_data['phone'],
        language=LANGUAGE_CODE[context.user_data['lang']],
    )

    # To‘g‘ri chaqiruv: faqat 2 ta argument
    await show_main_menu(update, LANGUAGE_CODE[context.user_data['lang']])
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ro‘yxatdan o‘tish bekor qilindi.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    language_code = context.user_data.get('language', 'uz')

    if text == "🇺🇿 O'zbek tili":
        language_code = 'uz'
    elif text == "🇷🇺 Русский":
        language_code = 'ru'
    else:
        await update.message.reply_text(get_text("language_selection_error", language_code))
        return # Til tanlash holatida qolamiz

    user = await sync_to_async(BotUser.objects.filter(telegram_id=user_id).first)()
    if user:
        user.language = language_code
        await sync_to_async(user.save)()
        await update.message.reply_text(get_text("language_changed_success", language_code))
        await show_main_menu(update, language_code)  # Bosh menyuga qaytish
        return ConversationHandler.END # Yoki tegishli holatga o'tish
    else:
        await update.message.reply_text(get_text("not_registered_warning", 'uz'))
        return ConversationHandler.END