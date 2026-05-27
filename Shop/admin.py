from django.contrib import admin
from .models import produto, SKU, Carrinho

admin.site.register(produto)
admin.site.register(SKU)
admin.site.register(Carrinho)

