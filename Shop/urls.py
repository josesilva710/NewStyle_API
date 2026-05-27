from django.urls import path, include
from rest_framework_nested import routers
from Shop.views import VitrineLojistaProdutoViewSet, PainelLojistaProdutoViewSet, SKUViewSet

router = routers.SimpleRouter()
router.register(r'products', VitrineLojistaProdutoViewSet, basename='vitrine-produtos')
router.register(r'my-products', PainelLojistaProdutoViewSet, basename='painel-produtos')

products_router = routers.NestedSimpleRouter(router, r'my-products', lookup='produto')
products_router.register(r'variations', SKUViewSet, basename='produto-variations')

variations_router = routers.SimpleRouter()
variations_router.register(r'variations', SKUViewSet, basename='variations')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(products_router.urls)),
    path('', include(variations_router.urls)),
]