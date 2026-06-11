from django.urls import path, include
from rest_framework_nested import routers
from Shop.views import ProductViewSet, SKUViewSet, CartItemViewSet, CartViewSet, OrderViewSet

router = routers.SimpleRouter()

# Rota para listar produtos (/products/)
router.register(r'products', ProductViewSet, basename='products')

# Rota aninhada para detalhes de produtos (products/:id/)
products_router = routers.NestedSimpleRouter(router, r'products', lookup='product')

# Rota para variações de produtos (products/:id/variations/)
products_router.register(r'variations', SKUViewSet, basename='product-variations')

# Rota para manipular itens do carrinho (cart/items/)
router.register(r'cart/items', CartItemViewSet, basename='cart-items')

# Rota para carrinho de compras (/cart/)
router.register(r'cart', CartViewSet, basename='cart')

# Rota p/ realizar pedidos (/orders/)
router.register(r'orders', OrderViewSet, basename='orders')

# Rota p/ visualizar o pedido por id (/orders/:id)
orders_router = routers.NestedSimpleRouter(router, r'orders', lookup='order')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(products_router.urls)),
    path('', include(orders_router.urls)),
]