from django.contrib import admin
from .models import produto, SKU, Carrinho, ItemCarrinho

admin.site.register(produto)
admin.site.register(SKU)
admin.site.register(Carrinho)
admin.site.register(ItemCarrinho)
