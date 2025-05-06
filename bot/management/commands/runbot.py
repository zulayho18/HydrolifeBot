from django.core.management.base import BaseCommand
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram import Update, ReplyKeyboardMarkup
from bot.handlers.registration import start, choose_language, full_name, phone, cancel
from bot.handlers.menu import show_main_menu, show_cart, show_help, cart_command, clear_cart
from bot.handlers.settings import settings_menu, handle_settings_choice, save_phone_number, CHANGE_PHONE
from bot.handlers.products import show_products
from django.conf import settings
from bot.models import BotUser
from asgiref.sync import sync_to_async
import logging
from bot.handlers.texts import TEXT_LANG_WARNING
from bot.handlers import order
from bot.handlers import menu
from bot.handlers.menu import settings_command, set_language_from_settings, back_to_main_menu_from_settings, settings_conversation_handler, handle_product_selection, change_product_quantity, add_product_to_cart, CHANGE_LANGUAGE_SETTINGS
from bot.handlers.order import start_order_process, get_delivery_address, process_order, get_phone_number_again, save_phone_and_process_order, confirm_order, cancel_order
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

LANGUAGE, FULL_NAME, PHONE = range(3)
WAITING_ADDRESS = "WAITING_ADDRESS" # Holat qo'shildi

@sync_to_async
def is_user_registered(telegram_id):
    return BotUser.objects.filter(telegram_id=telegram_id).exists()

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

async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await sync_to_async(BotUser.objects.filter(telegram_id=update.effective_user.id).first)()
    language = user.language if user else 'uz'
    message = update.message if update.message else update.callback_query.message
    await show_main_menu(message, language)
    return ConversationHandler.END

class Command(BaseCommand):
    help = 'Telegram botini ishga tushiradigan buyruq'

    def handle(self, *args, **kwargs):
        application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

        print("Bot ishga tushmoqda...")

        registration_handler = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_language)],
                FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name)],
                PHONE: [
                    MessageHandler(filters.CONTACT, phone),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, phone),
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
        application.add_handler(registration_handler)

        application.add_handler(MessageHandler(filters.Regex(r"^(💦 Mahsulotlar|💦 Продукты)$"), show_products))
        #application.add_handler(CallbackQueryHandler(handle_product_selection, pattern=r"^product_\d+$"))

        settings_conversation_handler = ConversationHandler(
            entry_points=[MessageHandler(filters.Regex(r"^(⚙️ Sozlamalar|⚙️ Настройки)$"), settings_command)],
            states={
                CHANGE_LANGUAGE_SETTINGS: [
                    MessageHandler(filters.Regex(r"^(🇺🇿 O'zbek tili|🇷🇺 Русский)$"), set_language_from_settings),
                    MessageHandler(filters.Regex(r"^(⬅️ Ortga)$"), back_to_main_menu_from_settings),
                ],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
        application.add_handler(settings_conversation_handler)

        order_conversation_handler = ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex(r"^(🛒 Buyurtma berish|🛒 Оформить заказ)$"), order.start_order_process)],
            states={
                "WAITING_ADDRESS": [
                    MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(r"^(⬅️ Ortga|🔙 Ortga)$"),
                                   order.cancel_order),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, order.get_delivery_address)
                ],
                "CONFIRM_PHONE": [MessageHandler(filters.Regex(rf"^({menu.get_text('yes')}|{menu.get_text('no')})$"),
                                                 order.handle_phone_confirmation)],
                "WAITING_PHONE": [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND & filters.Regex(rf"^({menu.get_text('back')}|🔙 Назад)$"),
                        menu.show_main_menu),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, order.save_phone_and_process_order)
                ],
                "CONFIRM_ORDER": [
                    MessageHandler(filters.Regex(rf"^({menu.get_text('confirm')}|{menu.get_text('cancel')})$"),
                                   order.handle_order_confirmation)],
                "END": [MessageHandler(filters.Regex(
                    rf"^({menu.get_text('back_to_main_menu')}|🔙 В главное меню|🏠 Bosh menyuga qaytish|⬅️ Ortga|🔙 Ortga)$"),
                                       menu.show_main_menu)],
            },
            fallbacks=[MessageHandler(filters.Regex(
                rf"^({menu.get_text('back_to_main_menu')}|🔙 В главное меню|🏠 Bosh menyuga qaytish|⬅️ Ortga|🔙 Ortga)$"),
                                      menu.show_main_menu)],
        )

        application.add_handler(order_conversation_handler)

        application.add_handler(MessageHandler(filters.Regex(r"^(🛒 Savatcha|🛒 Корзина)$"), cart_command))
        application.add_handler(MessageHandler(filters.Regex(r"^🗑️ Savatchani tozalash$"), clear_cart))
        application.add_handler(MessageHandler(filters.Regex(r"^(❓ Yordam|❓ Помощь)$"), show_help))
        application.add_handler(MessageHandler(filters.Regex(r"^(⬅️ Ortga|🔙 Ortga)$"), back_to_main_menu))

        # application.add_handler(CallbackQueryHandler(handle_product_selection, pattern=r"^product_\d+$"))
        # application.add_handler(CallbackQueryHandler(change_product_quantity, pattern=r"^qty_(minus|plus)_\d+$"))
        # application.add_handler(CallbackQueryHandler(add_product_to_cart, pattern=r"^add_cart_\d+_\d+$"))
        # application.add_handler(CallbackQueryHandler(back_to_main_menu, pattern=r"^back_to_main_menu$"))
        # application.add_handler(CallbackQueryHandler(show_products, pattern="^show_products$"))
        # application.add_handler(CallbackQueryHandler(handle_product_selection, pattern='^product_details_'))
        # application.run_polling()
        application.add_handler(CallbackQueryHandler(handle_product_selection, pattern='^product_details_'))
        application.add_handler(CallbackQueryHandler(change_product_quantity, pattern=r"^qty_(minus|plus)_\d+$"))
        application.add_handler(CallbackQueryHandler(add_product_to_cart, pattern=r"^add_cart_\d+_\d+$"))
        application.add_handler(CallbackQueryHandler(back_to_main_menu, pattern=r"^back_to_main_menu$"))
        application.add_handler(CallbackQueryHandler(menu.show_products, pattern="^show_products$"))  # menu.show_products ga o'zgartirdik
        application.run_polling()