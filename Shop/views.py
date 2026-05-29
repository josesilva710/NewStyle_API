from Shop.models import produto, SKU
from Shop.serializers import ProdutoSerializer, SKUSerializer
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from Shop.permissions import IsLojista, IsDonoDoProduto
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.exceptions import ValidationError
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

class ProdutoViewSet(viewsets.ModelViewSet):

    queryset = produto.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['preco', 'nome']
    search_fields = ['categoria', 'nome']
    serializer_class = ProdutoSerializer

    # Permissões: qualquer pessoa pode listar e visualizar produtos, 
    # mas apenas lojistas autenticados podem criar, atualizar ou deletar produtos.
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsLojista]

        return [permission() for permission in permission_classes]

    # Validação para garantir que um lojista não crie produtos duplicados com o mesmo nome, preço e descrição.
    def create(self, request, *args, **kwargs):

        if produto.objects.filter(

        user=self.request.user,
        nome=request.data.get('nome'), 
        preco=request.data.get('preco'), 
        descricao=request.data.get('descricao')).exists():

            raise ValidationError({"error": "Você já possui um produto com o mesmo nome, preço e descrição já existe."})
        
        return super().create(request, *args, **kwargs)
    # Validação para garantir que apenas o dono do produto possa atualizá-lo ou deletá-lo.
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # Garantindo que apenas produtos ativos sejam listados e visualizados.
    def get_queryset(self):

        user = self.request.user

        if user.is_authenticated:

            return produto.objects.filter(
                Q(ativo=True) | Q(user=user)
            )

        return produto.objects.filter(ativo=True)
    
    def update(self, request, *args, **kwargs):
        
        produto_instance = self.get_object()
        
        if produto_instance.user != self.request.user:
            raise PermissionDenied("Você não tem permissão para atualizar este produto.")
        
        return super().update(request, *args, **kwargs)
        
    def destroy(self, request, *args, **kwargs):
        
        produto_instance = self.get_object()
        
        if produto_instance.user != self.request.user:
            raise PermissionDenied("Você não tem permissão para deletar este produto.")
        
        return super().destroy(request, *args, **kwargs)

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
        
        if produto_instance.user != self.request.user:
            raise PermissionDenied("Você não tem permissão para adicionar SKUs a este produto.")
        
        if SKU.objects.filter(produto_id=produto_id, 
                              cor=request.data.get('cor'), 
                              tamanho=request.data.get('tamanho')).exists():
            
            raise ValidationError({"error": "Você já cadastrou uma variação com a mesma cor e tamanho para este produto."})

        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        produto_id = self.kwargs.get('produto_pk')
        serializer.save(produto_id=produto_id)