# from django.contrib import admin
# from .models import BotUser, Product, Order
#
# @admin.register(BotUser)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('fio', 'phone_number', 'created_at')
#     search_fields = ('fio', 'phone_number')
#
# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('name', 'price', 'is_active')
#     list_filter = ('is_active',)
#     search_fields = ('name',)
#
# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('user', 'product', 'quantity', 'status', 'created_at')
#     list_filter = ('status',)
#     search_fields = ('user__fio', 'product__name')

from django.contrib import admin
from .models import BotUser, Product, Order, Cart

@admin.register(BotUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'created_at', 'language')
    search_fields = ('full_name', 'phone_number')
    list_filter = ('language',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name_uz', 'price', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name_uz', 'name_ru')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__full_name', 'product__name_uz', 'product__name_ru')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'created_at')
    search_fields = ('user__full_name', 'product__name_uz', 'product__name_ru')