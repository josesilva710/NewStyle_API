from Shop.models import produto, SKU, Carrinho, ItemCarrinho
from Shop.serializers import(
    ProdutoSerializer, 
    SKUSerializer, 
    CarrinhoSerializer, 
    ItemCarrinhoSerializer
)
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from Shop.permissions import IsLojista, IsDonoDoProduto, IsDonoDoCarrinho
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from rest_framework.response import Response

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
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    read_only_fields = ['produto']

    def get_permissions(self):
        if self.action in ['update','partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsDonoDoProduto, IsLojista]
        
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsLojista]

        if self.action in ['list', 'retrieve']:
                permission_classes = [AllowAny]

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
    
    # Garante que o SKU esteja associado ao produto correto, 
    # que deve ser criado pelo usuário autenticado.
    def perform_create(self, serializer):
        produto_id = self.kwargs.get('produto_pk')
        serializer.save(produto_id=produto_id)

    # Garante que apenas SKUs associados a um produto criado pelo 
    # usuário autenticado sejam listados e visualizados.
    def get_queryset(self):
        produto_id = self.kwargs.get('produto_pk')
        return SKU.objects.filter(produto_id=produto_id)

class CarrinhoViewSet(viewsets.ModelViewSet):
    
    serializer_class = CarrinhoSerializer
    http_method_names = ['get']

    #   Como somente há o método get para o carrinho e o mesmo já verifica se 
    # o usuário autenticado é o dono do carrinho, 
    # não é necessário adicionar a permissão IsDonoDoCarrinho aqui, 
    # pois o próprio método get_queryset já garante que apenas o
    # carrinho do usuário autenticado seja acessível.
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        
        user = self.request.user

        if user.is_authenticated and self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsDonoDoCarrinho]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]
    
    def get_queryset(self):

        user = self.request.user
        carrinho_instance = Carrinho.objects.filter(user=user).first()

        if not user.is_authenticated:
            raise PermissionDenied("Você precisa estar autenticado para acessar o carrinho.")
        
        if carrinho_instance.user != self.request.user:
            raise PermissionDenied("Você não tem permissão para acessar este carrinho.")

        return Carrinho.objects.filter(user=user)

class ItemCarrinhoViewSet(viewsets.ModelViewSet):

    serializer_class = ItemCarrinhoSerializer
    http_method_names = ['post', 'put', 'patch', 'delete']

    def get_permissions(self):
        
        user = self.request.user

        if user.is_authenticated and self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsDonoDoCarrinho]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    def update(self, request, *args, **kwargs):

        #Se o JSON For enviado vazio:
        if not request.data:
            raise ValidationError({
                "error": "Informe a quantidade_add e o sku a ser atualizado"
            })

        #captando os dados inseridos
        item_carrinho_instance = self.get_object()
        quantidade = request.data.get('quantidade_add')
        sku_da_instancia = SKU.objects.filter(id=item_carrinho_instance.sku.id).first()
        
        #Verificand o SKU inserido
        novo_sku = None
        if request.data.get('sku') is not None:
            novo_sku = SKU.objects.filter(id=request.data.get('sku')).first()
            if not novo_sku:
                raise ValidationError({"sku": "SKU não encontrado."})

        #Verificando o proprietario do carrinho
        if item_carrinho_instance.carrinho.user != self.request.user:
            raise PermissionDenied("Você não tem permissão para atualizar este item do carrinho.")
        
        #Verificando a quantidade inserida
        if quantidade is not None:
            try:
                quantidade = int(quantidade)
                if quantidade < 1:
                    raise ValueError
            except ValueError:
                raise ValidationError({"quantidade": "A quantidade deve ser um número inteiro positivo e maior que zero."})

            if quantidade > sku_da_instancia.estoque:
                raise ValidationError({"quantidade": "Estoque indisponível."})
        
        #Verificando se o SKU é de um lojista diferente ao da instância.
        if novo_sku and novo_sku.produto.user != sku_da_instancia.produto.user:
            raise ValidationError({"error": "Este SKU pertence a outro lojista"})
            
        return super().update(request, *args, **kwargs)

    def get_queryset(self):

        user = self.request.user

        if user.is_authenticated:

            return ItemCarrinho.objects.filter(carrinho__user=user)
        
        return ItemCarrinho.objects.none()
    
    def create(self, request, *args, **kwargs):

        user = self.request.user

        #   Mesmo sabendo que o model de carrinho tem uma relação OneToOne com o usuário, 
        # é importante validar a existência do carrinho para o usuário autenticado 
        # no momento da criação do item do carrinho para garantir que o item seja associado 
        # a um carrinho válido e evitar erros de referência ou inconsistências nos dados.
        try: 
            carrinho_instance = Carrinho.objects.get(user=user)
        except Carrinho.DoesNotExist:
            raise NotFound("Carrinho não encontrado para o usuário autenticado.")
        
        sku_id = request.data.get('sku')
        produto_id = request.data.get('produto')
        quantidade_add = request.data.get('quantidade_add', 1)
        carrinho_id = carrinho_instance.id

        produto_add = produto.objects.filter(id = produto_id).first()
        sku_add = SKU.objects.filter(id = sku_id).first()

        if produto.objects.filter(id = produto_id).exists() == False:
            raise NotFound("O ID inserido em 'produto' não pertence à um produto existente")

        if produto_add.user != sku_add.produto.user:

            raise ValidationError({"error": "Adicione um sku pertencente ao produto"})
        

        #   Embora o model possua um campo de quantidade PositiveIntegerField, 
        # é importante validar a quantidade no momento da criação do item do carrinho 
        # para garantir que o valor seja um número inteiro positivo e evitar erros de 
        # validação posteriores ou injeções maliciosas.
        try:
            quantidade_add = int(quantidade_add)
            if quantidade_add < 1:
                raise ValueError
        except ValueError:
            raise ValidationError({"quantidade": "A quantidade deve ser um número inteiro positivo e maior que zero."})
        
        sku_disponivel = SKU.objects.filter(id=sku_id).first()

        if not sku_disponivel or not produto_id:
            raise ValidationError({

                "produto": ["Este campo é obrigatório."],
                "sku": ["Este campo é obrigatório."]})

        # Verificando se o item do carrinho já existe para o mesmo SKU e carrinho
        item_carrinho_existente = ItemCarrinho.objects.filter(
            carrinho_id=carrinho_id,
            sku_id=sku_id
        ).first()
        
        quantidade_futura = quantidade_add

        if item_carrinho_existente:
            quantidade_futura += item_carrinho_existente.quantidade_add

        if quantidade_futura > sku_disponivel.estoque:
            raise ValidationError({"quantidade": "Estoque indisponível."})                    
        
        #verificando se há produtos de lojistas diferentes:
        if ItemCarrinho.objects.filter(carrinho_id=carrinho_id).exists():
            item_carrinho_instance = ItemCarrinho.objects.filter(carrinho_id=carrinho_id).first()
            produto_loja = item_carrinho_instance.sku.produto.user
            produto_novo = produto.objects.filter(id=produto_id).first()

            #   Caso o produto novo seja de um lojista diferente do produto já presente no carrinho, a adição do item é negada 
            if produto_novo and produto_novo.user != produto_loja:
                
                raise ValidationError({"error": "Não é permitido adicionar produtos de lojistas diferentes no mesmo carrinho."})
        
        # Se o item do carrinho já existir, 
        # atualiza a quantidade adicionada em vez de criar um novo item.
        if item_carrinho_existente:

            item_carrinho_existente.quantidade_add += quantidade_add
            item_carrinho_existente.save()

            serializer = self.get_serializer(item_carrinho_existente)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return super().create(request, *args, **kwargs)
    
    # Garante que o item do carrinho seja associado ao carrinho do usuário autenticado.
    def perform_create(self, serializer):

        serializer.save(carrinho = self.request.user.carrinho)
        
