from Shop.models import produto, SKU
from Shop.serializers import ProdutoSerializer, SKUSerializer
from rest_framework import viewsets

class ProdutoViewSet(viewsets.ModelViewSet):

    queryset = produto.objects.all()
    serializer_class = ProdutoSerializer

class SKUViewSet(viewsets.ModelViewSet):

    queryset = SKU.objects.all()
    serializer_class = SKUSerializer