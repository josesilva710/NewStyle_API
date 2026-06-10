from django.contrib import admin
from .models import Produto, SKU, Carrinho, ItemCarrinho, Pedido, ItemPedido

admin.site.register(Produto)
admin.site.register(SKU)
admin.site.register(Carrinho)
admin.site.register(ItemCarrinho)
admin.site.register(Pedido)
admin.site.register(ItemPedido)
