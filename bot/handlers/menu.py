
from telegram import Update,ReplyKeyboardMarkup,KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto,Message
from telegram.ext import ContextTypes, CallbackContext
from bot.models import Product, Cart, BotUser
from asgiref.sync import sync_to_async
from bot.handlers.texts import get_text
import logging
from telegram.ext import ConversationHandler, MessageHandler, filters, CommandHandler
import os
from django.conf import settings
from django.apps import apps


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CHANGE_LANGUAGE_SETTINGS = 10


async def show_main_menu(update: Update | Message, language: str):
    logging.info("Bosh menyu ko'rsatilmoqda.")
    menu_buttons = [
        [KeyboardButton(get_text("products", language)), KeyboardButton(get_text("cart", language))],
        [KeyboardButton(get_text("settings", language)), KeyboardButton(get_text("help", language))],
    ]
    reply_markup = ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)
    reply_markup = ReplyKeyboardMarkup(menu_buttons, resize_keyboard=True)
    if isinstance(update, Update):
        await update.message.reply_text(
            get_text("main_menu_text", language), reply_markup=reply_markup
        )
    elif isinstance(update, Message):
        await update.reply_text(
            get_text("main_menu_text", language), reply_markup=reply_markup
        )
    logging.info("Bosh menyu ko'rsatildi.")

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await sync_to_async(BotUser.objects.filter(telegram_id=update.effective_user.id).first)()
    if not user:
        await update.message.reply_text("Siz ro‘yxatdan o‘tmagansiz.")
        return

    cart_items = await sync_to_async(Cart.objects.filter(user=user).all)()
    if cart_items:
        message = "Savatchangiz:\n\n"
        for item in cart_items:
            message += f"{item.product.name_uz} - {item.quantity} dona, Narxi: {item.product.price} so'm\n"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Savatchangiz bo‘sh.")

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    operator_phone = "123456789"
    user = await sync_to_async(BotUser.objects.filter(telegram_id=update.effective_user.id).first)()
    language = user.language if user else 'uz'
    text = "Operator bilan bog‘lanish uchun telefon raqam: {operator_phone}" if language == 'uz' else "Для связи с оператором номер телефона: {operator_phone}"
    await update.message.reply_text(text.format(operator_phone=operator_phone))

async def back_to_main_menu(update: Update, context: CallbackContext):
    user = await sync_to_async(BotUser.objects.filter(telegram_id=update.effective_user.id).first)()
    if user:
        await show_main_menu(update, user.language)
        return # Bosh menyu holatiga qaytish (agar ConversationHandler ishlatilsa)
    else:
        await update.message.reply_text(get_text("not_registered_warning", 'uz'))
        return # Ro'yxatdan o'tmaganlik holati

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup(
        [["🇺🇿 O'zbek tili"], ["🇷🇺 Русский"], ["⬅️ Ortga"]],
        resize_keyboard=True
    )
    await update.message.reply_text(get_text("choose_language_settings", context.user_data.get('language', 'uz')), reply_markup=reply_markup)
    return CHANGE_LANGUAGE_SETTINGS

async def set_language_from_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    language_code = 'uz'

    if text == "🇺🇿 O'zbek tili":
        language_code = 'uz'
    elif text == "🇷🇺 Русский":
        language_code = 'ru'
    else:
        await update.message.reply_text(get_text("language_selection_error", context.user_data.get('language', 'uz')))
        return CHANGE_LANGUAGE_SETTINGS

    user = await sync_to_async(BotUser.objects.filter(telegram_id=user_id).first)()
    if user:
        user.language = language_code
        await sync_to_async(user.save)()
        await update.message.reply_text(get_text("language_changed_success", language_code))
        # Sozlamalar menyusiga qaytish (yoki bosh menyuga)
        await show_main_menu(update, context, language_code) # Agar sozlamalar menyusi alohida bo'lsa
        # await show_main_menu(update, language_code) # Agar bosh menyuga qaytmoqchi bo'lsangiz
        return ConversationHandler.END # Yoki sozlamalar menyusi holatiga qaytish
    else:
        await update.message.reply_text(get_text("not_registered_warning", 'uz'))
        return ConversationHandler.END

async def back_to_main_menu_from_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await sync_to_async(BotUser.objects.filter(telegram_id=update.effective_user.id).first)()
    if user:
        await show_main_menu(update, user.language)
        return ConversationHandler.END
    else:
        await update.message.reply_text(get_text("not_registered_warning", 'uz'))
        return ConversationHandler.END

async def cart_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'uz')

    cart_items = await get_user_cart_items(user_id)

    if cart_items:
        cart_text = get_text("cart_items_header", language) + "\n\n"
        total_price = 0
        for item in cart_items:
            cart_text += f"{item['name']} - {item['quantity']} x {item['price']} = {item['quantity'] * item['price']}\n"
            total_price += item['quantity'] * item['price']
        cart_text += f"\n{get_text('total_price', language)}: {total_price}"
        reply_markup = ReplyKeyboardMarkup([["🗑️ Savatchani tozalash", get_text("order", language)], [get_text("back", language)]], resize_keyboard=True) # "Buyurtma berish" tugmasi qo'shildi
    else:
        cart_text = get_text("cart_empty", language)
        reply_markup = ReplyKeyboardMarkup([[get_text("back", language)]], resize_keyboard=True)

    await update.message.reply_text(cart_text, reply_markup=reply_markup)
    return

async def clear_cart(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'uz')

    # Foydalanuvchining savatchasidagi barcha elementlarni o'chirish
    await sync_to_async(Cart.objects.filter(user__telegram_id=user_id).delete)()

    await update.message.reply_text(get_text("cart_cleared", language), reply_markup=ReplyKeyboardMarkup([[get_text("back", language)]], resize_keyboard=True))
    return # Savatcha holatida qolamiz yoki boshqa holatga o'tamiz (agar kerak bo'lsa)

# get_user_cart_items funksiyasini yaratishingiz kerak
@sync_to_async
def get_user_cart_items(user_id: int):
    cart_items = Cart.objects.filter(user__telegram_id=user_id).select_related('product')
    items_list = []
    for item in cart_items:
        items_list.append({
            'name': item.product.name_uz if item.user.language == 'uz' else item.product.name_ru,
            'quantity': item.quantity,
            'price': item.product.price
        })
    return items_list

settings_conversation_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex(r"^(⚙️ Sozlamalar|⚙️ Настройки)$"), settings_command)],
    states={
        CHANGE_LANGUAGE_SETTINGS: [
            MessageHandler(filters.Regex(r"^(🇺🇿 O'zbek tili|🇷🇺 Русский)$"), set_language_from_settings),
            MessageHandler(filters.Regex(r"^(⬅️ Ortga)$"), back_to_main_menu_from_settings),
        ],
    },
    fallbacks=[CommandHandler("cancel", back_to_main_menu)], # Bekor qilish tugmasi uchun (agar kerak bo'lsa)
)



async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("show_products funksiyasi ishga tushdi.")
    user = await sync_to_async(BotUser.objects.filter(telegram_id=update.effective_user.id).first)()
    language = user.language if user else 'uz'
    ProductModel = apps.get_model('bot', 'Product')
    keyboard = []
    products = await sync_to_async(list)(ProductModel.objects.all())
    for product in products:
        button_text = product.name_uz if language == 'uz' else product.name_ru
        callback_data = f"product_details_{product.id}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    keyboard.append([InlineKeyboardButton(get_text("back", language), callback_data="back_to_main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(get_text("choose_product", language), reply_markup=reply_markup)
    elif update.callback_query and update.callback_query.message:
        await update.callback_query.message.edit_text(get_text("choose_product", language), reply_markup=reply_markup)
        await update.callback_query.answer() # Callback query tugaganini bildirish
    else:
        logging.warning("Xabar obyekti topilmadi.")

    logging.info("show_products funksiyasi yakunlandi.")
    return

async def handle_product_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  # Tugma bosilganini tasdiqlash

    user = await sync_to_async(BotUser.objects.filter(telegram_id=update.effective_user.id).first)()
    language = user.language if user else 'uz'

    #product_id = query.data.split("_")[1]  # callback_data dan mahsulot ID'sini olamiz
    product_id = query.data.split("_")[-1]  # Oxirgi elementni olamiz
    try:
        product = await sync_to_async(Product.objects.get)(id=product_id)
    except Product.DoesNotExist:
        await query.message.reply_text(get_text("product_not_found", language))  # language dan foydalanamiz
        return

    def escape_markdown(text):
        if text:
            return text.replace('*', '\\*').replace('_', '\\_').replace('[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('`', '\\`')
        return ""

    name = escape_markdown(product.name_uz if language == 'uz' else product.name_ru)
    description = escape_markdown(product.description_uz if language == 'uz' else product.description_ru)

    caption = f"*{name}*\n\n"
    caption += f"{get_text('price', language)}: {product.price} so'm\n\n"
    if description:
        caption += f"{description}\n\n"

    keyboard = [
        [InlineKeyboardButton("-", callback_data=f"qty_minus_{product.id}"),
         InlineKeyboardButton("1", callback_data=f"qty_current_{product.id}"), # Boshlang'ich miqdor
         InlineKeyboardButton("+", callback_data=f"qty_plus_{product.id}")],
        [InlineKeyboardButton(get_text("add_to_cart", language), callback_data=f"add_cart_{product.id}_1")], # Boshlang'ich miqdor
        [InlineKeyboardButton(get_text("back_to_products", language), callback_data="show_products")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if product.image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(product.image))
            with open(image_path, 'rb') as photo_file:
                media = InputMediaPhoto(media=photo_file, caption=caption, parse_mode="Markdown")
                await query.edit_message_media(media=media, reply_markup=reply_markup)
        else:
            await query.edit_message_caption(caption=caption, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception as e:
        await query.message.reply_text(
            caption + f"\n\nRasmni yuklashda/tahrirlashda xatolik yuz berdi: {e}",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    return # Mahsulot sonini tanlash holati (keyin yaratamiz)

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("show_products funksiyasi ishga tushdi.")
    user = await BotUser.objects.filter(telegram_id=update.effective_user.id).afirst()
    language = user.language if user else 'uz'
    print(f"Til: {language}")

    @sync_to_async
    def get_all_products():
        return list(Product.objects.all())

    products = await get_all_products()
    print(f"Mahsulotlar: {products}")

    keyboard = []
    for product in products:
        button_text = product.name_uz if language == 'uz' else product.name_ru
        print(f"Mahsulot nomi ({language}): {button_text}, ID: {product.id}")
        callback_data = f"product_{product.id}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    keyboard.append([InlineKeyboardButton(get_text("back", language), callback_data="back_to_main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = update.message if update.message else update.callback_query.message
    await message.reply_text(get_text("choose_product", language), reply_markup=reply_markup)
    logging.info("show_products funksiyasi yakunlandi.")
    return
async def change_product_quantity(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    operation = data[1]  # minus yoki plus
    product_id = int(data[2])
    user_id = update.effective_user.id

    # context.user_data da har bir mahsulot uchun alohida miqdorni saqlaymiz
    if f"product_{product_id}_qty" not in context.user_data:
        context.user_data[f"product_{product_id}_qty"] = 1

    current_quantity = context.user_data[f"product_{product_id}_qty"]

    if operation == "plus":
        current_quantity += 1
    elif operation == "minus" and current_quantity > 1:
        current_quantity -= 1

    context.user_data[f"product_{product_id}_qty"] = current_quantity

    try:
        product = await sync_to_async(Product.objects.get)(id=product_id)
    except Product.DoesNotExist:
        await query.message.reply_text(get_text("product_not_found", await sync_to_async(BotUser.objects.filter(telegram_id=user_id).first)().language if await sync_to_async(BotUser.objects.filter(telegram_id=user_id).first)() else 'uz'))
        return

    user = await sync_to_async(BotUser.objects.filter(telegram_id=user_id).first)()
    language = user.language if user else 'uz'

    def escape_markdown(text):
        if text:
            return text.replace('*', '\\*').replace('_', '\\_').replace('[', '\\[').replace(']', '\\]').replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('`', '\\`')
        return ""

    name = escape_markdown(product.name_uz if language == 'uz' else product.name_ru)
    description = escape_markdown(product.description_uz if language == 'uz' else product.description_ru)

    caption = f"*{name}*\n\n"
    caption += f"{get_text('price', language)}: {product.price} so'm\n\n"
    if description:
        caption += f"{description}\n\n"

    keyboard = [
        [InlineKeyboardButton("-", callback_data=f"qty_minus_{product.id}"),
         InlineKeyboardButton(str(current_quantity), callback_data=f"qty_current_{product.id}"),
         InlineKeyboardButton("+", callback_data=f"qty_plus_{product.id}")],
        [InlineKeyboardButton(get_text("add_to_cart", language), callback_data=f"add_cart_{product.id}_{current_quantity}")],
        [InlineKeyboardButton(get_text("back_to_products", language), callback_data="show_products")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if product.image:
            image_path = os.path.join(settings.MEDIA_ROOT, str(product.image))
            with open(image_path, 'rb') as photo_file:
                media = InputMediaPhoto(media=photo_file, caption=caption, parse_mode="Markdown")
                await query.edit_message_media(media=media, reply_markup=reply_markup) # edit_message_media ishlatamiz
        else:
            await query.edit_caption(caption=caption, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception as e:
        await query.message.reply_text(f"Rasmni yangilashda xatolik yuz berdi: {e}")

    return # Mahsulot sonini tanlash holati
async def add_product_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    product_id = data[2]
    quantity = int(data[3])
    user_id = update.effective_user.id

    user = await sync_to_async(BotUser.objects.filter(telegram_id=user_id).first)()
    if not user:
        await query.message.reply_text(get_text("not_registered_warning", 'uz')) # Tilni aniqlash kerak
        return

    product = await sync_to_async(Product.objects.get)(id=product_id)

    # Savatchaga mahsulotni qo'shish yoki mavjud bo'lsa sonini yangilash
    cart_item, created = await sync_to_async(Cart.objects.get_or_create)(user=user, product=product, defaults={'quantity': quantity})
    if not created:
        cart_item.quantity += quantity
        await sync_to_async(cart_item.save)()

    user_language = user.language if user else 'uz'
    await query.message.reply_text(get_text("product_added_to_cart", user_language).format(product_name=product.name_uz if user_language == 'uz' else product.name_ru, quantity=quantity))

    keyboard = [
        [InlineKeyboardButton(get_text("view_cart", user_language), callback_data="show_cart")],
        [InlineKeyboardButton(get_text("back_to_products", user_language), callback_data="show_products")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_reply_markup(reply_markup=reply_markup)
    await query.message.edit_reply_markup(reply_markup=reply_markup)

    # context.user_data dan mahsulot sonini olib tashlaymiz
    if f"product_{product_id}_qty" in context.user_data:
        del context.user_data[f"product_{product_id}_qty"]

    return # Savatcha holati yoki mahsulotlar menyusi holati