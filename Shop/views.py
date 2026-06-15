from Shop.models import Product, SKU, Cart, CartItem, Order, OrderItem
from Users.models import Address
from Shop.serializers import (
    ProductSerializer, 
    SKUSerializer, 
    CartSerializer, 
    CartItemSerializer,
    OrderSerializer,
)
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from Shop.permissions import IsMerchant, IsProductOwner, IsCartOwner, IsOrderMerchant
from rest_framework.exceptions import PermissionDenied, NotFound, ValidationError
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from .filters import ProductFilter

class ProductViewSet(viewsets.ModelViewSet):
    """
    Descrição da ViewSet:
    - Endpoint para gerenciar o catálogo de produtos.
    - Permite a listagem pública e operações completas de CRUD para lojistas (criação, edição e exclusão).
    - Inclui validações para impedir a criação de produtos duplicados e restringe alterações apenas ao dono do produto.
    - Exibe apenas produtos ativos e com estoque para clientes, mas permite que o dono visualize seus inativos.

    Parâmetros:
    - pk (int): A chave primária do produto (utilizado em rotas de detalhe, como GET, PATCH e DELETE).

    Campos de ordenação:
    - price: Permite ordenar os produtos por preço (ascendente/descendente).
    - name: Permite ordenar os produtos por ordem alfabética do nome.

    Campos de pesquisa:
    - category: Pesquisar por correspondência de texto na categoria.
    - name: Pesquisar por correspondência de texto no nome do produto.

    Filtros disponíveis:
    - category / category__in: Filtrar por uma ou múltiplas categorias exatas (ex: ?category__in=SHIRTS,PANTS).

    Métodos HTTP permitidos:
    - GET, POST, PATCH, DELETE
    """
    
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = ProductFilter
    ordering_fields = ['price', 'name']
    search_fields = ['category', 'name']
    serializer_class = ProductSerializer
    http_method_names = ['post', 'get', 'patch', 'delete']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsMerchant]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        if Product.objects.filter(
            user=self.request.user,
            name=request.data.get('name'),
            price=request.data.get('price'),
            description=request.data.get('description')
        ).exists():
            raise ValidationError({"error": "Você já possui um produto com o mesmo nome, preço e descrição."})
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Product.objects.filter(
                Q(is_active=True, skus__stock__gt=0) | Q(user=user)
            ).distinct()
        return Product.objects.filter(is_active=True, skus__stock__gt=0).distinct()
        
    def update(self, request, *args, **kwargs):
        product_instance = self.get_object()
        if product_instance.user != self.request.user:
            raise PermissionDenied("Você não tem permissão para atualizar este produto.")
        return super().update(request, *args, **kwargs)
        
    def destroy(self, request, *args, **kwargs):
        product_instance = self.get_object()
        if product_instance.user != self.request.user:
            raise PermissionDenied("Você não tem permissão para deletar este produto.")
        return super().destroy(request, *args, **kwargs)


class SKUViewSet(viewsets.ModelViewSet):
    """
    Descrição da ViewSet:
    - Endpoint aninhado para gerenciar as variações (SKUs) de um produto específico.
    - Garante que SKUs não sejam duplicados (mesma cor e tamanho para o mesmo produto).
    - Assegura que apenas o lojista dono do produto pai possa adicionar, editar ou excluir suas variações.

    Parâmetros:
    - product_pk (int): O ID do produto pai ao qual os SKUs pertencem (herdado da URL aninhada).
    - pk (int): A chave primária da variação (SKU) para operações de detalhe.

    Campos de ordenação:
    - Não especificado nesta ViewSet.

    Campo de pesquisa:
    - Não especificado nesta ViewSet.

    Métodos HTTP permitidos:
    - GET, POST, PUT, PATCH, DELETE
    """
   
    queryset = SKU.objects.all()
    serializer_class = SKUSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    read_only_fields = ['product']

    def get_permissions(self):
        if self.action in ['update','partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsProductOwner, IsMerchant]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated, IsMerchant]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        product_id = kwargs.get('product_pk') 
        try:
            product_instance = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound("Produto não encontrado.")
        
        if product_instance.user != self.request.user:
            raise PermissionDenied("Você não tem permissão para adicionar SKUs a este produto.")
        
        if SKU.objects.filter(
            product_id=product_id, 
            color=request.data.get('color'),
            size=request.data.get('size')
        ).exists():
            raise ValidationError({"error": "Você já cadastrou uma variação com a mesma cor e tamanho para este produto."})
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_pk')
        serializer.save(product_id=product_id)

    def get_queryset(self):
        product_id = self.kwargs.get('product_pk')
        return SKU.objects.filter(product_id=product_id)


class CartViewSet(viewsets.ModelViewSet):
    """
    Descrição da ViewSet:
    - Endpoint para visualizar o carrinho do usuário autenticado.
    - O acesso é estritamente pessoal, não sendo possível visualizar carrinhos de terceiros.

    Parâmetros:
    - Não necessita de PK na requisição, pois a consulta é baseada no token do usuário logado.

    Campos de ordenação:
    - Não aplicável.

    Campo de pesquisa:
    - Não aplicável.

    Métodos HTTP permitidos:
    - GET
    """
    
    queryset = Cart.objects.none()
    serializer_class = CartSerializer
    http_method_names = ['get']
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        user = self.request.user
        if user.is_authenticated and self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsCartOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        cart_instance = Cart.objects.filter(user=user).first()

        if not user.is_authenticated:
            raise PermissionDenied("Você precisa estar autenticado para acessar o carrinho.")
        
        if cart_instance and cart_instance.user != self.request.user:
            raise PermissionDenied("Você não tem permissão para acessar este carrinho.")

        return Cart.objects.filter(user=user)


class CartItemViewSet(viewsets.ModelViewSet):
    """
    Descrição da ViewSet:
    - Endpoint para gerenciar a adição, edição (quantidade) e remoção de itens dentro do carrinho.
    - Valida o estoque disponível da variação escolhida (SKU).
    - Aplica regras de negócio essenciais: impede adicionar produtos de lojistas diferentes no mesmo carrinho e agrupa itens duplicados atualizando a quantidade.

    Parâmetros:
    - pk (int): A chave primária do item do carrinho para operações de edição ou exclusão.

    Campos de ordenação:
    - Não aplicável.

    Campo de pesquisa:
    - Não aplicável.

    Métodos HTTP permitidos:
    - POST, PUT, PATCH, DELETE
    """

    serializer_class = CartItemSerializer
    http_method_names = ['post', 'put', 'patch', 'delete']

    def get_permissions(self):
        user = self.request.user
        if user.is_authenticated and self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsCartOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def update(self, request, *args, **kwargs):
        if not request.data:
            raise ValidationError({"error": "Informe a quantity e o sku a ser atualizado"})

        cart_item_instance = self.get_object()
        quantity = request.data.get('quantity')
        instance_sku = cart_item_instance.sku
        
        new_sku = None
        if request.data.get('sku') is not None:
            new_sku = SKU.objects.filter(id=request.data.get('sku')).first()
            if not new_sku:
                raise ValidationError({"sku": "SKU não encontrado."})

        if cart_item_instance.cart.user != self.request.user:
            raise PermissionDenied("Você não tem permissão para atualizar este item do carrinho.")
        
        if quantity is not None:
            try:
                quantity = int(quantity)
                if quantity < 1:
                    raise ValueError
            except ValueError:
                raise ValidationError({"quantity": "A quantidade deve ser um número inteiro positivo e maior que zero."})

            if quantity > instance_sku.stock:
                raise ValidationError({"quantity": "Estoque indisponível."})
        
        if new_sku and new_sku.product.user != instance_sku.product.user:
            raise ValidationError({"error": "Este SKU pertence a outro lojista"})
            
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return CartItem.objects.filter(cart__user=user)
        return CartItem.objects.none()
    
    def create(self, request, *args, **kwargs):
        user = self.request.user

        try: 
            cart_instance = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            raise NotFound("Carrinho não encontrado para o usuário autenticado.")
        
        sku_id = request.data.get('sku')
        quantity = request.data.get('quantity', 1)
        cart_id = cart_instance.id

        if not sku_id or not quantity:
            raise ValidationError({"error": "Os campos 'sku' e 'quantity' são obrigatórios"})
        
        sku_add = SKU.objects.filter(id=sku_id).first()
        if not sku_add:
            raise ValidationError({"error": "SKU não encontrado"})
        
        product_add = sku_add.product

        try:
            quantity = int(quantity)
            if quantity < 1:
                raise ValueError
        except ValueError:
            raise ValidationError({"quantity": "A quantidade deve ser um número inteiro positivo e maior que zero."})
        
        existing_cart_item = CartItem.objects.filter(cart_id=cart_id, sku_id=sku_id).first()
        future_quantity = quantity + (existing_cart_item.quantity if existing_cart_item else 0)

        if future_quantity > sku_add.stock:
            raise ValidationError({"quantity": "Estoque indisponível."})                    
        
        if CartItem.objects.filter(cart_id=cart_id).exists():
            cart_item_instance = CartItem.objects.filter(cart_id=cart_id).first()
            if product_add.user != cart_item_instance.sku.product.user:
                raise ValidationError({"error": "Não é permitido adicionar produtos de lojistas diferentes no mesmo carrinho."})
        
        if existing_cart_item:
            existing_cart_item.quantity += quantity
            existing_cart_item.save()
            serializer = self.get_serializer(existing_cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(cart=self.request.user.cart)


class OrderViewSet(viewsets.ModelViewSet):

    """
    Descrição da ViewSet:
    - Endpoint para criação e gerenciamento de pedidos de compra.
    - Funciona como um snapshot do momento da compra, consolidando endereço, forma de pagamento e valor dos itens.
    - Atualizações genéricas (PATCH/PUT) são bloqueadas em favor da rota customizada `/orders/{id}/status/`.

    Parâmetros:
    - pk (int): A chave primária do pedido.

    Campos de ordenação:
    - status: Permite ordenar pelos status do pedido.

    Campo de pesquisa:
    - status: Pesquisar por correspondência de texto no status do pedido.

    Filtros da URL:
    - status: Filtra os pedidos por uma etapa específica de forma case-insensitive (ex: ?status=DELIVERED ou ?status=delivered).
    - status=ativos: Filtro "mágico" que exibe simultaneamente todos os pedidos em andamento ('PENDING', 'PROCESSING', 'SHIPPED').

    Métodos HTTP permitidos:
    - GET, POST, PATCH (Exclusivo via action de status)
    """

    queryset = Order.objects.none()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch']
    ordering_fields = ['status']
    search_fields = ['status']
    serializer_class = OrderSerializer
    
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT', detail='Não permitido. Use a rota /orders/{id}/status/ para atualizações.')

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH', detail='Não permitido. Use a rota /orders/{id}/status/ para atualizações.')

    """
        Retorna os pedidos atrelados ao usuário (seja ele o cliente ou o lojista).
        Intercepta os parâmetros da URL para aplicar o filtro mágico 'ativos' ou a 
        filtragem exata por status do banco de dados, protegendo contra erros de tipagem nula.
    """

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.filter(Q(customer=user) | Q(merchant=user))
        status_param = self.request.query_params.get('status', None)

        if status_param:
            if status_param.lower() == 'ativos':
                active_statuses = ['PENDING', 'PROCESSING', 'SHIPPED']
                queryset = queryset.filter(status__in=active_statuses)
            
            else:

                queryset = queryset.filter(status = status_param.upper())

        return queryset
    
    def create(self, request, *args, **kwargs):
        address_id = request.data.get('address_id')
        payment_method = request.data.get('payment_method')
        items_ids = request.data.get('selected_items', [])

        if not address_id or not payment_method or not items_ids:
            raise ValidationError({"error": "Os campos 'address_id', 'payment_method' e 'selected_items' são obrigatórios."})

        chosen_address = Address.objects.filter(id=address_id, users=request.user).first()
        if not chosen_address:
            raise ValidationError({"address_id": "O Endereço escolhido é inválido"})
        
        items_to_buy = CartItem.objects.filter(id__in=items_ids, cart__user=request.user)
        if items_to_buy.count() != len(items_ids):
            raise ValidationError({"items_id": "Um ou mais itens selecionados são inválidos ou não estão em seu carrinho"})
        
        for item in items_to_buy:
            if item.quantity > item.sku.stock:
                raise ValidationError({"error": f"Estoque insuficiente p/ {item.sku.product.name}."})
            
        try:
            with transaction.atomic():
                first_item = items_to_buy.first()
                order_merchant = first_item.sku.product.user

                order = Order.objects.create(
                    customer=request.user,
                    merchant=order_merchant,
                    delivery_address=str(chosen_address),
                    payment_method=payment_method,
                    status='PENDING',
                    total=0
                )

                total_order_value = 0

                for item in items_to_buy:
                    current_price = item.sku.product.price
                    item_subtotal = current_price * item.quantity

                    OrderItem.objects.create(
                        order=order,
                        sku=item.sku,
                        quantity=item.quantity,
                        unit_price=current_price,
                        subtotal=item_subtotal,
                        saved_product_name=item.sku.product.name,
                        saved_color=item.sku.color,
                        saved_size=item.sku.size
                    )

                    total_order_value += item_subtotal
                    item.sku.stock -= item.quantity
                    item.sku.save()

                order.total = total_order_value
                order.save()
                items_to_buy.delete()
        
        except Exception as e:
            raise ValidationError({"error": f"Falha no processamento do pedido: {str(e)}"})
        
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsOrderMerchant])
    def status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')

        if not new_status:
            return Response({'error': 'Nenhum status fornecido'}, status=status.HTTP_400_BAD_REQUEST)

        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]

        if new_status not in valid_statuses:
            return Response(
                {'error': f'Status inválido. Os status permitidos são: {valid_statuses}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()
        return Response({'status': f'Pedido Atualizado para: {new_status}'})