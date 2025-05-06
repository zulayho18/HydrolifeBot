# from django.db import models
#
# class BotUser(models.Model):
#     fio = models.CharField(max_length=255, verbose_name="F.I.O")
#     phone_number = models.CharField(max_length=20, verbose_name="Telefon raqam")
#     address = models.TextField(verbose_name="Manzil")
#     telegram_id = models.BigIntegerField(null=True, blank=True, verbose_name="Telegram ID")  # Telegram ID uchun BigIntegerField
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
#     updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")
#     language = models.CharField(max_length=20, verbose_name="Til", default="uz")  # Til maydoni
#
#     class Meta:
#         verbose_name = "Foydalanuvchi"
#         verbose_name_plural = "Foydalanuvchilar"
#         ordering = ['-created_at']
#
#     def __str__(self):
#         return self.fio
#
#
# class Product(models.Model):
#     name = models.CharField(max_length=200, verbose_name="Nomi")
#     description = models.TextField(verbose_name="Tavsifi")
#     price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narxi")
#     image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="Rasm")
#     is_active = models.BooleanField(default=True, verbose_name="Faol")
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         verbose_name = "Mahsulot"
#         verbose_name_plural = "Mahsulotlar"
#         ordering = ['-created_at']
#
#     def __str__(self):
#         return f"{self.name} - {self.price}"
#
#
# class Order(models.Model):
#     STATUS_CHOICES = [
#         ('new', 'Yangi'),
#         ('processing', 'Jarayonda'),
#         ('completed', 'Yakunlangan'),
#         ('cancelled', 'Bekor qilingan'),
#     ]
#
#     user = models.ForeignKey(
#         BotUser,
#         on_delete=models.CASCADE,
#         related_name='orders',
#         verbose_name="Foydalanuvchi"
#     )
#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         verbose_name="Mahsulot"
#     )
#     quantity = models.PositiveIntegerField(default=1, verbose_name="Miqdori")
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Holati")
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         verbose_name = "Buyurtma"
#         verbose_name_plural = "Buyurtmalar"
#         ordering = ['-created_at']
#
#     def __str__(self):
#         return f"{self.user} - {self.product} ({self.quantity})"
#
#     def total_price(self):
#         return self.product.price * self.quantity
#
#     total_price.short_description = "Umumiy narx"
#
#
# class Cart(models.Model):
#     user = models.ForeignKey(
#         BotUser,
#         on_delete=models.CASCADE,
#         related_name='cart_items',
#         verbose_name="Foydalanuvchi"
#     )
#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         verbose_name="Mahsulot"
#     )
#     quantity = models.PositiveIntegerField(default=1, verbose_name="Soni")
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
#
#     class Meta:
#         verbose_name = "Savatcha"
#         verbose_name_plural = "Savatchalar"
#         ordering = ['-created_at']
#
#     def __str__(self):
#         return f"{self.user.fio} - {self.product.name} ({self.quantity} dona)"

from django.db import models

class BotUser(models.Model):
    full_name = models.CharField(max_length=255, verbose_name="F.I.O")
    phone_number = models.CharField(max_length=20, verbose_name="Telefon raqam")
    address = models.TextField(verbose_name="Manzil")
    telegram_id = models.BigIntegerField(null=True, blank=True, verbose_name="Telegram ID")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")
    language = models.CharField(max_length=20, verbose_name="Til", default="uz")

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        ordering = ['-created_at']

    def __str__(self):
        return self.fio


class Product(models.Model):
    name_uz = models.CharField(max_length=200, verbose_name="Nomi (uz)")
    name_ru = models.CharField(max_length=200, verbose_name="Nomi (ru)", null=True, blank=True)
    description_uz = models.TextField(verbose_name="Tavsifi (uz)")
    description_ru = models.TextField(verbose_name="Tavsifi (ru)", null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narxi")
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="Rasm")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name_uz} - {self.price}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Yangi'),
        ('processing', 'Jarayonda'),
        ('completed', 'Yakunlangan'),
        ('cancelled', 'Bekor qilingan'),
    ]

    user = models.ForeignKey(
        BotUser,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Foydalanuvchi"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Mahsulot"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Miqdori")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Holati")
    delivery_address = models.TextField(verbose_name="Yetkazib berish manzili", null=True, blank=True) # Qo'shildi
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.product} ({self.quantity})"

    def total_price(self):
        return self.product.price * self.quantity

    total_price.short_description = "Umumiy narx"

class Cart(models.Model):
    user = models.ForeignKey(
        BotUser,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name="Foydalanuvchi"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Mahsulot"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Soni")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

    class Meta:
        verbose_name = "Savatcha"
        verbose_name_plural = "Savatchalar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.fio} - {self.product.name_uz} ({self.quantity} dona)"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Buyurtma"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Mahsulot"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Miqdori")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narxi")  # Mahsulotning o'sha paytdagi narxi
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Buyurtma elementi"
        verbose_name_plural = "Buyurtma elementlari"

    def __str__(self):
        return f"{self.product.name_uz} - {self.quantity} dona (Buyurtma ID: {self.order.id})"

    def total_price(self):
        return self.price * self.quantity