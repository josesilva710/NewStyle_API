from Shop.models import produto, SKU
from Shop.serializers import ProdutoSerializer, SKUSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

class VitrineLojistaProdutoViewSet(viewsets.ReadOnlyModelViewSet):

  queryset = produto.objects.all()
  serializer_class = ProdutoSerializer
  permission_classes = [AllowAny]

class PainelLojistaProdutoViewSet(viewsets.ModelViewSet):

  queryset = produto.objects.all()
  serializer_class = ProdutoSerializer
  permission_classes = [IsAuthenticated]

  # Sobrescreve o método perform_create para associar o usuário autenticado ao produto criado
  def perform_create(self, serializer):
    serializer.save(users=self.request.user)

  def get_queryset(self):
    # Retorna apenas os produtos do usuário autenticado
     return produto.objects.filter(users=self.request.user)

class SKUViewSet(viewsets.ModelViewSet):

  queryset = SKU.objects.all()
  serializer_class = SKUSerializer
  permission_classes = [IsAuthenticated]

  def get_queryset(self):
    if 'produto_pk' in self.kwargs:
        return SKU.objects.filter(produto_id=self.kwargs['produto_pk'], produto__users=self.request.user)
    
    return SKU.objects.filter(produto__users=self.request.user)