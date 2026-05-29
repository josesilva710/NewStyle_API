from Shop.models import produto, SKU
from Shop.serializers import ProdutoSerializer, SKUSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from Shop.permissions import IsLojista, IsDonoDoProduto
from rest_framework.exceptions import PermissionDenied, NotFound

class ProdutoViewSet(viewsets.ModelViewSet):

  queryset = produto.objects.all()
  serializer_class = ProdutoSerializer

    # Permissões: qualquer pessoa pode listar e visualizar produtos, 
    # mas apenas lojistas autenticados podem criar, atualizar ou deletar produtos.
  def get_permissions(self):
    if self.action in ['list', 'retrieve']:
        permission_classes = [AllowAny]
    else:
        permission_classes = [IsAuthenticated, IsLojista]
    return [permission() for permission in permission_classes]
  
  def perform_create(self, serializer):
    serializer.save(users=self.request.user)

class SKUViewSet(viewsets.ModelViewSet):
   
    queryset = SKU.objects.all()
    serializer_class = SKUSerializer
    http_method_names = ['post', 'put', 'patch', 'delete']

    read_only_fields = ['produto']

    def get_permissions(self):
        if self.action in ['update','partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsDonoDoProduto, IsLojista]
        else:
            permission_classes = [IsAuthenticated, IsLojista]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):

        produto_id = kwargs.get('produto_pk')
        produto_instance = produto.objects.filter(id=produto_id)

        try:
            produto_instance = produto_instance.get()
        except produto.DoesNotExist:
            raise NotFound("Produto não encontrado.")
        
        if produto_instance.users != self.request.user:
            raise PermissionDenied("Você não tem permissão para adicionar SKUs a este produto.")

        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        produto_id = self.kwargs.get('produto_pk')
        serializer.save(produto=produto_id)