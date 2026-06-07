from django.urls import path, include
from rest_framework_nested import routers
from Shop.views import ProdutoViewSet, SKUViewSet, ItemCarrinhoViewSet, CarrinhoViewSet, PedidoViewSet

router = routers.SimpleRouter()
router.register(r'products', ProdutoViewSet, basename='produtos')

# Rota aninhada para detalhes de produtos (produtos/{produto_id}/)
products_router = routers.NestedSimpleRouter(router, r'products', lookup='produto')

# Rota para variações de produtos (produtos/{produto_id}/variations/)
products_router.register(r'variations', SKUViewSet, basename='products-variations')

# Rota para manipular itens do carrinho (cart/items/)
router.register(r'cart/items', ItemCarrinhoViewSet, basename='cart-items')

# Rota para carrinho de compras (/cart/)
router.register(r'cart', CarrinhoViewSet, basename='cart')

# Rota p/ realizar pedidos (/orders/)
router.register(r'orders', PedidoViewSet, basename = 'orders')

# Rota p/ visualizar o pedido por id (/orders/:id)
orders_router = routers.NestedSimpleRouter(router, r'orders', lookup = 'orders')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(products_router.urls)),
]