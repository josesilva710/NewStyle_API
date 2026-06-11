from django.contrib import admin
from .models import Product, SKU, Cart, CartItem, Order, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'price', 'category', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'merchant', 'total', 'status', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('customer__email', 'merchant__email')

admin.site.register(SKU)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)