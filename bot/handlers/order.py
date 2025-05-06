from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from bot.handlers.texts import get_text
from bot.models import BotUser
from asgiref.sync import sync_to_async
from bot.handlers.menu import get_user_cart_items
from bot.models import Order, OrderItem, Cart, Product
import logging
@sync_to_async
def get_user_phone_number(user_id: int):
    user = BotUser.objects.filter(telegram_id=user_id).first()
    return user.phone_number if user else None

async def start_order_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'uz')

    await update.message.reply_text(get_text("enter_address", language), reply_markup=ReplyKeyboardMarkup([["⬅️ Ortga"]], resize_keyboard=True))
    return "WAITING_ADDRESS" # Keyingi holat - manzil kiritishni kutish

async def get_delivery_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    delivery_address = update.message.text
    context.user_data['delivery_address'] = delivery_address
    user_id = update.effective_user.id

    # sync_to_async ni filtrlash va birinchi obyektni olish uchun alohida qo'llang
    get_user = sync_to_async(BotUser.objects.filter(telegram_id=user_id).first)
    user = await get_user()

    if user:
        if user.phone_number:
            # Telefon raqami allaqachon mavjud, tasdiqlashga o'tamiz
            await update.message.reply_text(
                f"{get_text('confirm_phone_number', context.user_data.get('language', 'uz'))}: {user.phone_number}\n{get_text('is_phone_correct', context.user_data.get('language', 'uz'))}",
                reply_markup=ReplyKeyboardMarkup([[get_text('yes', context.user_data.get('language', 'uz')), get_text('no', context.user_data.get('language', 'uz'))]], resize_keyboard=True)
            )
            return "CONFIRM_PHONE"
        else:
            # Telefon raqami yo'q, so'raymiz
            await update.message.reply_text(
                get_text('enter_phone_number_order', context.user_data.get('language', 'uz')),
                reply_markup=ReplyKeyboardMarkup([[get_text('back', context.user_data.get('language', 'uz'))]],
                                                resize_keyboard=True)
            )
            return "WAITING_PHONE"
    else:
        # Foydalanuvchi topilmadi, ro'yxatdan o'tishni so'raymiz yoki bosh menyuga qaytaramiz
        await update.message.reply_text(
            get_text('not_registered_warning', context.user_data.get('language', 'uz')),
            reply_markup=ReplyKeyboardMarkup([[get_text('back_to_main_menu', context.user_data.get('language', 'uz'))]], resize_keyboard=True)
        )
        return ConversationHandler.END
async def process_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"context.user_data: {context.user_data}")
    user_id = update.effective_user.id
    delivery_address = context.user_data.get('delivery_address')
    phone_number = context.user_data.get('phone_number') # Telefon raqamini context.user_data'dan olish
    language = context.user_data.get('language', 'uz')

    logging.info(f"process_order: Foydalanuvchi ID: {user_id}, Telefon raqami: {phone_number}, Manzil: {delivery_address}")

    cart_items = await get_user_cart_items(user_id)

    if not cart_items:
        await update.message.reply_text(get_text("cart_empty", language), reply_markup=ReplyKeyboardMarkup([[get_text("back", language)]], resize_keyboard=True))
        return "END"
    else:
        order_details = get_text("order_details", language) + "\n\n"
        total_price = 0
        for item in cart_items:
            order_details += f"{item['name']} - {item['quantity']} x {item['price']} = {item['quantity'] * item['price']}\n"
            total_price += item['quantity'] * item['price']

        order_details += f"\n{get_text('total_price', language)}: {total_price}\n"
        order_details += f"{get_text('delivery_address', language)}: {delivery_address}\n"
        order_details += f"{get_text('phone_number', language)}: {phone_number}\n\n"
        order_details += get_text("confirm_order_text", language)

        reply_markup = ReplyKeyboardMarkup([[get_text("confirm", language), get_text("cancel", language)]], resize_keyboard=True)
        await update.message.reply_text(order_details, reply_markup=reply_markup)
        return "CONFIRM_ORDER"
async def get_phone_number_again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', 'uz')
    await update.message.reply_text(
        get_text('enter_phone_number_again', language),
        reply_markup=ReplyKeyboardMarkup([[get_text('back', language)]], resize_keyboard=True)
    )
    return "WAITING_PHONE" # Telefon raqamini kutish holatiga qaytish

# async def save_phone_and_process_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_user.id
#     phone_number = update.message.text
#     language = context.user_data.get('language', 'uz')
#
#     logging.info(f"save_phone_and_process_order boshlandi. Telefon raqami: {phone_number}, context.user_data oldin: {context.user_data}")
#
#     context.user_data['phone_number'] = phone_number
#
#     logging.info(f"context.user_data keyin: {context.user_data}")
#
#     await update.message.reply_text(get_text('phone_number_saved', language))
#     return "CONFIRM_PHONE" # Keyingi holatga o'tish
#
#     await update.message.reply_text(get_text('phone_number_saved', language))
#
#     # Telefon raqamini bazaga saqlash (asinxron operatsiya uchun sync_to_async ishlatiladi)
#     try:
#         await sync_to_async(BotUser.objects.filter(telegram_id=user_id).aupdate)(phone_number=phone_number)
#         await update.message.reply_text(get_text("phone_number_saved_order", language),
#                                         reply_markup=ReplyKeyboardMarkup([[get_text("back", language)]],
#                                                                          resize_keyboard=True))
#     except Exception as e:
#         logging.error(f"Telefon raqamini saqlashda xatolik: {e}")
#         await update.message.reply_text(get_text("error_saving_phone", language),
#                                         reply_markup=ReplyKeyboardMarkup([[get_text("back", language)]],
#                                                                          resize_keyboard=True))
#         return ConversationHandler.END # Xatolik yuz berganda konversatsiyani yakunlash
#
#     # Buyurtmani rasmiylashtirishga o'tish (process_order funksiyasini chaqirish)
#     return await process_order(update, context)

async def save_phone_and_process_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    phone_number = update.message.text
    language = context.user_data.get('language', 'uz')

    logging.info(f"save_phone_and_process_order boshlandi. Foydalanuvchi ID: {user_id}, Kiritilgan raqam: {phone_number}, context.user_data: {context.user_data}")

    await update.message.reply_text(
        f"{get_text('confirm_phone_number', language)}: {phone_number}\n{get_text('is_phone_correct', language)}?",
        reply_markup=ReplyKeyboardMarkup([[get_text('yes', language), get_text('no', language)]], resize_keyboard=True)
    )

    # Telefon raqamini bazaga saqlash (asinxron operatsiya uchun sync_to_async ishlatiladi)
    try:
        await sync_to_async(BotUser.objects.filter(telegram_id=user_id).aupdate)(phone_number=phone_number)
        await update.message.reply_text(get_text("phone_number_saved_db", language))
    except Exception as e:
        logging.error(f"Telefon raqamini saqlashda xatolik: {e}")
        await update.message.reply_text(get_text("error_saving_phone", language))

    return "CONFIRM_PHONE" # Keyingi holatga o'tish - telefonni tasdiqlash
@sync_to_async
def save_order_to_database(user, delivery_address, cart_items):
    order = Order.objects.create(user=user, delivery_address=delivery_address)
    for item in cart_items:
        try:
            product = Product.objects.get(name_uz=item['name'] if user.language == 'uz' else item['name']) # Mahsulotni nomidan topish (ehtiyot bo'ling!)
            OrderItem.objects.create(order=order, product=product, quantity=item['quantity'], price=item['price'])
        except Product.DoesNotExist:
            # Agar mahsulot topilmasa, xatolikni qaytarish yoki loglash mumkin
            print(f"Xatolik: Mahsulot topilmadi: {item['name']}")
            order.delete() # Agar biron bir mahsulot topilmasa, buyurtmani bekor qilish
            return None # Buyurtma ID o'rniga None qaytarish
    return order.id

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', 'uz')
    user_id = update.effective_user.id

    cart_items = await get_user_cart_items(user_id)
    delivery_address = context.user_data.get('delivery_address')
    user = await sync_to_async(BotUser.objects.filter(telegram_id=user_id).first)()

    if cart_items and delivery_address and user:
        order_id = await save_order_to_database(user, delivery_address, cart_items)
        if order_id:
            await update.message.reply_text(
                get_text("order_accepted", language).format(order_id=order_id),
                reply_markup=ReplyKeyboardMarkup([[get_text("back_to_main_menu", language)]], resize_keyboard=True)
            )
            # Savatchani tozalash (ixtiyoriy)
            await sync_to_async(Cart.objects.filter(user__telegram_id=user_id).delete)()
            return "END" # Suhbatni yakunlash
        else:
            await update.message.reply_text(get_text("order_creation_error", language), reply_markup=ReplyKeyboardMarkup([[get_text("back", language)]], resize_keyboard=True))
            return "END"
    else:
        await update.message.reply_text(get_text("order_error", language), reply_markup=ReplyKeyboardMarkup([[get_text("back", language)]], resize_keyboard=True))
        return "END"



async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get('language', 'uz')
    await update.message.reply_text(get_text("order_cancelled", language), reply_markup=ReplyKeyboardMarkup([[get_text("back_to_main_menu", language)]], resize_keyboard=True))
    return ConversationHandler.END

async def handle_order_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.text
    language = context.user_data.get('language', 'uz')

    if user_choice == get_text('confirm', language):
        # Buyurtmani tasdiqlash
        return await confirm_order(update, context)
    elif user_choice == get_text('cancel', language):
        # Buyurtmani bekor qilish
        return await cancel_order(update, context)
    else:
        # Noto'g'ri javob
        await update.message.reply_text(
            get_text('incorrect_choice', language),
            reply_markup=ReplyKeyboardMarkup([[get_text('confirm', language), get_text('cancel', language)]], resize_keyboard=True)
        )
        return "CONFIRM_ORDER"


# async def handle_phone_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_choice = update.message.text
#     language = context.user_data.get('language', 'uz')
#
#     if user_choice == get_text('yes', language):
#         # Telefon raqami to'g'ri, buyurtmani rasmiylashtirishga o'tamiz
#         return await process_order(update, context)
#     elif user_choice == get_text('no', language):
#         # Telefon raqami noto'g'ri, qayta kiritishni so'raymiz
#         await update.message.reply_text(
#             get_text('enter_phone_number_again', language),
#             reply_markup=ReplyKeyboardMarkup([[get_text('back', language)]], resize_keyboard=True)
#         )
#         return "WAITING_PHONE"
#     else:
#         # Noto'g'ri javob
#         await update.message.reply_text(get_text('incorrect_choice', language), reply_markup=ReplyKeyboardMarkup([[get_text('yes', language), get_text('no', language)]], resize_keyboard=True))
     #   return "CONFIRM_PHONE"

async def handle_phone_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.text
    language = context.user_data.get('language', 'uz')

    if user_choice == get_text('yes', language):
        await update.message.reply_text(get_text('phone_number_confirmed', language))
        return await process_order(update, context) # Telefon tasdiqlandi, buyurtmani rasmiylashtirishga o'tish
    elif user_choice == get_text('no', language):
        await update.message.reply_text(get_text('phone_number_not_confirmed', language))
        await update.message.reply_text(get_text('enter_phone_number_again', language),
                                        reply_markup=ReplyKeyboardMarkup([[get_text('back', language)]],
                                                                         resize_keyboard=True))
        return "WAITING_PHONE" # Telefon tasdiqlanmadi, qayta so'rash
    else:
        await update.message.reply_text(get_text('invalid_choice', language))
        return "CONFIRM_PHONE"