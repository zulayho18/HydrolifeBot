# from bot.models import Product
# from asgiref.sync import sync_to_async
# from telegram import Update, ReplyKeyboardMarkup
# from telegram.ext import ContextTypes, ConversationHandler
# import logging
#
# logging.basicConfig(level=logging.DEBUG)
#
# # Bosqichlar
# SELECT_PRODUCT, SELECT_QUANTITY = range(2)
#
#
#
# @sync_to_async
# def get_products():
#     return list(Product.objects.filter(is_active=True))
#
#
# @sync_to_async
# def get_product_by_name(name):
#     try:
#         return Product.objects.get(name=name, is_active=True)
#     except Product.DoesNotExist:
#         return None
#
# # 1. Mahsulotlarni ko‘rsatish
# # show_products
# async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     products = await get_products()
#     logging.debug(f"Mahsulotlar soni: {len(products)}")  # Debug
#
#     if not products:
#         await update.message.reply_text("Mahsulotlar hozircha mavjud emas.")
#         return ConversationHandler.END
#
#     product_buttons = [[product.name] for product in products]
#     reply_markup = ReplyKeyboardMarkup(product_buttons + [["🔙 Ortga"]], resize_keyboard=True)
#     context.user_data['products'] = {product.name: product for product in products}
#
#     await update.message.reply_text("Iltimos, mahsulotlardan birini tanlang:", reply_markup=reply_markup)
#     return SELECT_PRODUCT
#
#
# # select_product
# async def select_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     product_name = update.message.text
#     selected_product = context.user_data['products'].get(product_name)
#
#     if not selected_product:
#         await update.message.reply_text("Bunday mahsulot topilmadi. Qaytadan urinib ko‘ring.")
#         return SELECT_PRODUCT
#
#     context.user_data['selected_product'] = selected_product
#
#     caption = f"{selected_product.name}\nNarxi: {selected_product.price} so'm\n\n{selected_product.description}"
#     if selected_product.image and hasattr(selected_product.image, 'url'):
#         await update.message.reply_photo(photo=selected_product.image.url, caption=caption)
#     else:
#         await update.message.reply_text(caption)
#
#     quantity_buttons = [[str(i) for i in range(1, 6)], [str(i) for i in range(6, 11)]]
#     reply_markup = ReplyKeyboardMarkup(quantity_buttons, resize_keyboard=True)
#     await update.message.reply_text("Nechta dona olishni xohlaysiz?", reply_markup=reply_markup)
#
#     return SELECT_QUANTITY
# # 3. Miqdor tanlash
# async def select_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     quantity = update.message.text
#     if quantity.isdigit() and 1 <= int(quantity) <= 10:
#         product = context.user_data.get('selected_product')
#         await update.message.reply_text(
#             f"Siz {product.name} mahsulotidan {quantity} dona tanladingiz. Buyurtma qabul qilindi!"
#         )
#         return ConversationHandler.END
#     else:
#         await update.message.reply_text("Iltimos, 1 dan 10 gacha bo‘lgan raqam kiriting.")
#         return SELECT_QUANTITY




# from bot.models import Product, BotUser
# from asgiref.sync import sync_to_async
# from telegram import Update, ReplyKeyboardMarkup
# from telegram.ext import ContextTypes, ConversationHandler
# import traceback
# import logging
# from django.conf import settings
#
# logging.basicConfig(level=logging.DEBUG)
#
# SELECT_PRODUCT = 0
#
# @sync_to_async
# def get_active_products():
#     return list(Product.objects.filter(is_active=True))
#
# @sync_to_async
# def get_product_by_name(name):
#     try:
#         return Product.objects.get(name_uz=name, is_active=True) or Product.objects.get(name_ru=name, is_active=True)
#     except Product.DoesNotExist:
#         return None
#
# async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user = await sync_to_async(BotUser.objects.filter(telegram_id=update.effective_user.id).first)()
#     language = user.language if user else 'uz'
#     products = await get_active_products()
#
#     if not products:
#         await update.message.reply_text("Hozirda mahsulotlar mavjud emas." if language == 'uz' else "Товаров пока нет.")
#         return ConversationHandler.END
#
#     product_buttons = [[product.name_uz if language == 'uz' else product.name_ru] for product in products]
#     reply_markup = ReplyKeyboardMarkup(product_buttons + [["🔙 Ortga" if language == 'uz' else "🔙 Назад"]], resize_keyboard=True)
#     context.user_data['products'] = {product.name_uz: product for product in products}
#     for product in products:
#         if product.name_ru:
#             context.user_data['products'][product.name_ru] = product
#
#     await update.message.reply_text("Iltimos, mahsulotlardan birini tanlang:" if language == 'uz' else "Пожалуйста, выберите один из товаров:", reply_markup=reply_markup)
#     return SELECT_PRODUCT
#
# async def select_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     logging.info("select_product funksiyasi ishga tushdi!")
#     user = await sync_to_async(BotUser.objects.filter(telegram_id=update.effective_user.id).first)()
#     language = user.language if user else 'uz'
#     product_name = update.message.text
#     logging.info(f"Foydalanuvchi {update.effective_user.id} tanladi: '{product_name}'")
#     try:
#         selected_product = context.user_data.get('products', {}).get(product_name)
#         logging.info(f"Tanlangan mahsulot obyekt: {selected_product}")
#
#         if not selected_product:
#             await update.message.reply_text("Bunday mahsulot topilmadi. Qaytadan urinib ko‘ring." if language == 'uz' else "Товар не найден. Попробуйте еще раз.")
#             return SELECT_PRODUCT
#
#         caption = f"{selected_product.name_uz if language == 'uz' else selected_product.name_ru}\n" \
#                   f"Narxi: {selected_product.price} so'm\n\n" \
#                   f"{selected_product.description_uz if language == 'uz' else selected_product.description_ru}"
#         if selected_product.image:
#             photo_url = settings.MEDIA_URL + str(selected_product.image)  # To'liq URL yaratish
#             logging.info(f"Yaratilgan rasm URL: {photo_url}")
#             await update.message.reply_photo(photo=photo_url, caption=caption)
#         else:
#             await update.message.reply_text(caption)
#
#         await update.message.reply_text("Boshqa amallar bajarish mumkin (masalan, savatchaga qo'shish tugmasi).", reply_markup=ReplyKeyboardMarkup([["🛒 Savatchaga qo'shish", "🔙 Bosh menyuga"]], resize_keyboard=True))
#         return ConversationHandler.END
#     except Exception as e:
#         logging.error(f"Mahsulotni tanlashda xatolik: {e}")
#         traceback.print_exc()
#         await update.message.reply_text("Kechirasiz, serverda xatolik yuz berdi.")
#         return ConversationHandler.END

# from bot.models import Product, BotUser
# from asgiref.sync import sync_to_async
# from telegram import Update, ReplyKeyboardMarkup
# from telegram.ext import ContextTypes, ConversationHandler
# import logging
# import traceback
# from django.conf import settings
# from django.apps import apps
#
# @sync_to_async
# def get_active_products_sync():
#     Product = apps.get_model('bot', 'Product')
#     return list(Product.objects.filter(is_active=True).order_by('-created_at').all())
#
# async def get_active_products():
#     return await get_active_products_sync()
#
# async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user = await sync_to_async(BotUser.objects.filter(telegram_id=update.effective_user.id).first)()
#     language = user.language if user else 'uz'
#     products = await get_active_products()
#
#     if not products:
#         await update.message.reply_text("Hozirda mahsulotlar mavjud emas." if language == 'uz' else "Товаров пока нет.")
#         return ConversationHandler.END
#
#     product_buttons = [[product.name_uz if language == 'uz' else product.name_ru] for product in products]
#     reply_markup = ReplyKeyboardMarkup(product_buttons + [["🔙 Ortga" if language == 'uz' else "🔙 Назад"]], resize_keyboard=True)
#     await update.message.reply_text("Iltimos, mahsulotlardan birini tanlang:" if language == 'uz' else "Пожалуйста, выберите один из товаров:", reply_markup=reply_markup)
#     return "SELECT_PRODUCT"
#
# async def select_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     logging.info(f"SELECT_PRODUCT funksiyasi boshlandi. Xabar: {update.message.text}")
#     user_choice = update.message.text
#     user = await sync_to_async(BotUser.objects.filter(telegram_id=update.effective_user.id).first)()
#     language = user.language if user else 'uz'
#     logging.info(f"Foydalanuvchi tili: {language}")
#     Product = apps.get_model('bot', 'Product')
#     try:
#         if user_choice.lower() == "hydrolife 18.9":
#             logging.info("Hydrolife 18.9 tanlandi.")
#             selected_product = await Product.objects.aget(name_uz="Hydrolife 18.9") if language == 'uz' else await Product.objects.aget(name_ru="Hydrolife 18.9")
#             photo_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQOh3bd4YMNOZsgt6PZiTpFR4i0wst88OzDeGjCRJxgSKCwk6X_gAGmM8IDNI7HO7jU8H4&usqp=CAU"
#             caption = f"{selected_product.name_uz if language == 'uz' else selected_product.name_ru}\nNarxi: {selected_product.price}"
#             await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption=caption)
#             logging.info(f"Hydrolife 18.9 rasmi yuborildi: {photo_url}")
#             return "SELECT_PRODUCT"
#             return ConversationHandler.END
#         elif user_choice.lower() == "kuler":
#             logging.info("Kuler sharti bajarildi.")
#             selected_product = await Product.objects.aget(name_uz="kuler") if language == 'uz' else await Product.objects.aget(name_ru="кулер")
#             photo_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRBeGBkeAdA4WpulTW0y-f4vxonhV__fqooaA&s"
#             caption = f"{selected_product.name_uz if language == 'uz' else selected_product.name_ru}\nNarxi: {selected_product.price}"
#             await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption=caption)
#             logging.info(f"Kuler rasmi yuborildi: {photo_url}")
#             return "SELECT_PRODUCT"
#             return ConversationHandler.END
#         else:
#             selected_product = await Product.objects.aget(name_uz=user_choice) if language == 'uz' else await Product.objects.aget(name_ru=user_choice)
#             caption = f"{selected_product.name_uz if language == 'uz' else selected_product.name_ru}\nNarxi: {selected_product.price}"
#             if selected_product.image:
#                 photo_url = settings.MEDIA_URL + str(selected_product.image)
#                 await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption=caption)
#                 logging.info(f"Rasm yuborildi: {photo_url}")
#             else:
#                 await context.bot.send_message(chat_id=update.effective_chat.id, text=caption)
#                 logging.info(f"Xabar yuborildi: {caption}")
#             return ConversationHandler.END
#     except Product.DoesNotExist:
#         logging.warning(f"Mahsulot topilmadi: {user_choice}")
#         await update.message.reply_text("Mahsulot topilmadi." if language == 'uz' else "Товар не найден.")
#         return ConversationHandler.END
#     except Exception as e:
#         logging.error(f"Kutilmagan xatolik: {traceback.format_exc()}")
#         await update.message.reply_text("Kechirasiz, serverda xatolik yuz berdi." if language == 'uz' else "Извините, произошла ошибка на сервере.")
#         return ConversationHandler.END

from bot.models import Product, BotUser
from asgiref.sync import sync_to_async
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
import logging
import traceback
from django.conf import settings
from django.apps import apps
from bot.handlers.texts import get_text
@sync_to_async
def get_active_products_sync():
    Product = apps.get_model('bot', 'Product')
    return list(Product.objects.filter(is_active=True).order_by('-created_at').all())

async def get_active_products():
    return await get_active_products_sync()

# async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     logging.info("show_products funksiyasi ishga tushdi.")
#     user = await sync_to_async(BotUser.objects.filter(telegram_id=update.effective_user.id).first)()
#     language = user.language if user else 'uz'
#     products = await sync_to_async(Product.objects.all())
#     keyboard = []
#     for product in products:
#         button_text = product.name_uz if language == 'uz' else product.name_ru
#         callback_data = f"product_details_{product.id}"
#         keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
#     keyboard.append([InlineKeyboardButton(get_text("back", language), callback_data="back_to_main_menu")])
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text(get_text("choose_product", language), reply_markup=reply_markup)
#     logging.info("show_products funksiyasi yakunlandi.")
#     return
# @sync_to_async
# def _get_user_language(telegram_id):
#     try:
#         user = BotUser.objects.get(telegram_id=telegram_id)
#         return user.language
#     except BotUser.DoesNotExist:
#         return 'uz'
#
# @sync_to_async
# def _get_all_products():
#     Product = apps.get_model('bot', 'Product')
#     return list(Product.objects.all())
#
# async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     logging.info("show_products funksiyasi ishga tushdi.")
#     language = await _get_user_language(update.effective_user.id)
#     products = await _get_all_products()
#     keyboard = []
#     for product in products:
#         button_text = product.name_uz if language == 'uz' else product.name_ru
#         callback_data = f"product_details_{product.id}"
#         keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
#     keyboard.append([InlineKeyboardButton(get_text("back", language), callback_data="back_to_main_menu")])
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text(get_text("choose_product", language), reply_markup=reply_markup)
#     logging.info("show_products funksiyasi yakunlandi.")
#     return
async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("show_products funksiyasi ishga tushdi.")
    user = await sync_to_async(BotUser.objects.filter(telegram_id=update.effective_user.id).first)()
    language = user.language if user else 'uz'
    ProductModel = apps.get_model('bot', 'Product')
    keyboard = []
    products = await sync_to_async(list)(ProductModel.objects.all()) # O'rab olamiz
    for product in products:
        button_text = product.name_uz if language == 'uz' else product.name_ru
        callback_data = f"product_details_{product.id}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    keyboard.append([InlineKeyboardButton(get_text("back", language), callback_data="back_to_main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(get_text("choose_product", language), reply_markup=reply_markup)
    logging.info("show_products funksiyasi yakunlandi.")
    return

async def handle_product_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Callback query qabul qilinganini tasdiqlash
    user = await sync_to_async(BotUser.objects.filter(telegram_id=query.from_user.id).first)()
    language = user.language if user else 'uz'
    product_id = query.data.split('_')[1] # callback_data dan mahsulot IDsini olish
    Product = apps.get_model('bot', 'Product')
    try:
        selected_product = await Product.objects.aget(id=product_id)
        caption = f"{selected_product.name_uz if language == 'uz' else selected_product.name_ru}\nNarxi: {selected_product.price}"
        if selected_product.image:
            photo_url = settings.MEDIA_URL + str(selected_product.image)
            await context.bot.send_photo(chat_id=query.message.chat_id, photo=photo_url, caption=caption)
            logging.info(f"Rasm yuborildi (callback): {photo_url}")
        else:
            await context.bot.send_message(chat_id=query.message.chat_id, text=caption)
            logging.info(f"Xabar yuborildi (callback): {caption}")
    except Product.DoesNotExist:
        logging.warning(f"Mahsulot topilmadi (callback): {product_id}")
        await query.message.reply_text("Mahsulot topilmadi." if language == 'uz' else "Товар не найден.")
    except Exception as e:
        logging.error(f"Kutilmagan xatolik (callback): {traceback.format_exc()}")
        await query.message.reply_text("Kechirasiz, serverda xatolik yuz berdi." if language == 'uz' else "Извините, произошла ошибка на сервере.")