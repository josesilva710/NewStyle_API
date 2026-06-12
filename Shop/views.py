from Shop.models import Product, SKU, Cart, CartItem, Order, OrderItem
from Users.models import Address
from Shop.serializers import(
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

class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['price', 'name']
    search_fields = ['category', 'name']
    serializer_class = ProductSerializer
    http_method_names = ['post', 'get', 'patch', 'delete']

    # Permissões: qualquer pessoa pode listar e visualizar produtos, 
    # mas apenas lojistas autenticados podem criar, atualizar ou deletar produtos.
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsMerchant]

        return [permission() for permission in permission_classes]

    # Validação para garantir que um lojista não crie produtos duplicados com o mesmo nome, preço e descrição.
    def create(self, request, *args, **kwargs):

        if Product.objects.filter(
            user=self.request.user,
            name=request.data.get('name'),
            price=request.data.get('price'),
            description=request.data.get('description')
        ).exists():

            raise ValidationError({"error": "Você já possui um produto com o mesmo nome, preço e descrição já existe."})
        
        return super().create(request, *args, **kwargs)
    
    # Validação para garantir que apenas o dono do produto possa atualizá-lo ou deletá-lo.
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # Garantindo que apenas produtos ativos sejam listados e visualizados.
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
   
    queryset = SKU.objects.all()
    serializer_class = SKUSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    read_only_fields = ['product']

    def get_permissions(self):
        if self.action in ['update','partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsProductOwner, IsMerchant]
        
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsMerchant]

        if self.action in ['list', 'retrieve']:
                permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):

        product_id = kwargs.get('product_pk') 
        product_instance = Product.objects.filter(id=product_id)

        try:
            product_instance = product_instance.get()
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
    
    # Garante que o SKU esteja associado ao produto correto, 
    # que deve ser criado pelo usuário autenticado.
    def perform_create(self, serializer):
        product_id = self.kwargs.get('product_pk')
        serializer.save(product_id=product_id)

    # Garante que apenas SKUs associados a um produto criado pelo 
    # usuário autenticado sejam listados e visualizados.
    def get_queryset(self):
        product_id = self.kwargs.get('product_pk')
        return SKU.objects.filter(product_id=product_id)

class CartViewSet(viewsets.ModelViewSet):
    
    # Apenas para o swagger conseguir ler o formato
    queryset = Cart.objects.none()

    serializer_class = CartSerializer
    http_method_names = ['get']

    # Como somente há o método get para o carrinho e o mesmo já verifica se 
    # o usuário autenticado é o dono do carrinho, 
    # não é necessário adicionar a permissão IsDonoDoCarrinho aqui, 
    # pois o próprio método get_queryset já garante que apenas o
    # carrinho do usuário autenticado seja acessível.
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
        
        if cart_instance.user != self.request.user:
            raise PermissionDenied("Você não tem permissão para acessar este carrinho.")

        return Cart.objects.filter(user=user)

class CartItemViewSet(viewsets.ModelViewSet):

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

        # Se o JSON For enviado vazio:
        if not request.data:
            raise ValidationError({
                "error": "Informe a quantity e o sku a ser atualizado"
            })

        # captando os dados inseridos
        cart_item_instance = self.get_object()
        quantity = request.data.get('quantity')
        instance_sku = SKU.objects.filter(id=cart_item_instance.sku.id).first()
        
        # Verificando o SKU inserido
        new_sku = None
        if request.data.get('sku') is not None:
            new_sku = SKU.objects.filter(id=request.data.get('sku')).first()
            if not new_sku:
                raise ValidationError({"sku": "SKU não encontrado."})

        # Verificando o proprietario do carrinho
        if cart_item_instance.cart.user != self.request.user:
            raise PermissionDenied("Você não tem permissão para atualizar este item do carrinho.")
        
        # Verificando a quantidade inserida
        if quantity is not None:
            try:
                quantity = int(quantity)
                if quantity < 1:
                    raise ValueError
            except ValueError:
                raise ValidationError({"quantity": "A quantidade deve ser um número inteiro positivo e maior que zero."})

            if quantity > instance_sku.stock:
                raise ValidationError({"quantity": "Estoque indisponível."})
        
        # Verificando se o SKU é de um lojista diferente ao da instância.
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

        # Mesmo sabendo que o model de carrinho tem uma relação OneToOne com o usuário, 
        # é importante validar a existência do carrinho para o usuário autenticado 
        # no momento da criação do item do carrinho para garantir que o item seja associado 
        # a um carrinho válido e evitar erros de referência ou inconsistências nos dados.
        try: 
            cart_instance = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            raise NotFound("Carrinho não encontrado para o usuário autenticado.")
        
        sku_id = request.data.get('sku')
        quantity = request.data.get('quantity', 1)
        cart_id = cart_instance.id

        if not sku_id or not quantity:
            raise ValidationError({"error": "Os campos 'sku' e 'quantity' são obrigatórios"})
        
        sku_add = SKU.objects.filter(id = sku_id).first()
        
        if not sku_add:
            raise ValidationError({"error": "SKU não encontrado"})
        
        product_add = sku_add.product

        if product_add.user != sku_add.product.user:
            raise ValidationError({"error": "Adicione um sku pertencente ao produto"})
        

        # Embora o model possua um campo de quantidade PositiveIntegerField, 
        # é importante validar a quantidade no momento da criação do item do carrinho 
        # para garantir que o valor seja um número inteiro positivo e evitar erros de 
        # validação posteriores ou injeções maliciosas.
        try:
            quantity = int(quantity)
            if quantity < 1:
                raise ValueError
        except ValueError:
            raise ValidationError({"quantity": "A quantidade deve ser um número inteiro positivo e maior que zero."})
        
        available_sku = SKU.objects.filter(id=sku_id).first()

        # Verificando se o item do carrinho já existe para o mesmo SKU e carrinho
        existing_cart_item = CartItem.objects.filter(
            cart_id=cart_id,
            sku_id=sku_id
        ).first()
        
        future_quantity = quantity

        if existing_cart_item:
            future_quantity += existing_cart_item.quantity

        if future_quantity > available_sku.stock:
            raise ValidationError({"quantity": "Estoque indisponível."})                    
        
        # verificando se há produtos de lojistas diferentes:
        if CartItem.objects.filter(cart_id=cart_id).exists():
            cart_item_instance = CartItem.objects.filter(cart_id=cart_id).first()
            store_product_user = cart_item_instance.sku.product.user

            if product_add.user != store_product_user:
                raise ValidationError({"error": "Não é permitido adicionar produtos de lojistas diferentes no mesmo carrinho."})
        
        # Se o item do carrinho já existir, 
        # atualiza a quantidade adicionada em vez de criar um novo item.
        if existing_cart_item:

            existing_cart_item.quantity += quantity
            existing_cart_item.save()

            serializer = self.get_serializer(existing_cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return super().create(request, *args, **kwargs)
    
    # Garante que o item do carrinho seja associado ao carrinho do usuário autenticado.
    def perform_create(self, serializer):
        serializer.save(cart = self.request.user.cart)

class OrderViewSet(viewsets.ModelViewSet):

    # Apenas para o Swagger conseguir ler o formato
    queryset = Order.objects.none()

    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch']
    ordering_fields = ['status']
    search_fields = ['status']
    serializer_class = OrderSerializer

    def get_queryset(self):
        
        user = self.request.user
        queryset = Order.objects.filter(Q(customer=user) | Q(merchant=user))

        status_param = self.request.query_params.get('status', None)

        if status_param == 'ativos':
            active_statuses = ['PENDING', 'PROCESSING', 'SHIPPED']
            queryset = queryset.filter(status__in=active_statuses)
        
        return queryset
    
    def create(self, request, *args, **kwargs):

        address_id = request.data.get('address_id')
        payment_method = request.data.get('payment_method')
        items_ids = request.data.get('selected_items', [])

        if not address_id or not payment_method or not items_ids:
            raise ValidationError({"error": "Os campos 'address_id', 'payment_method' e 'selected_items' são obrigatórios."})

        # Validando o endereço.
        chosen_address = Address.objects.filter(id = address_id, users=request.user).first()
        if not chosen_address:
            raise ValidationError({"address_id": "O Endereço escolhido é inválido"})
        
        # Validando os itens selecionados.
        items_to_buy = CartItem.objects.filter(id__in = items_ids, cart__user = request.user)

        if items_to_buy.count() != len(items_ids):
            raise ValidationError({"items_id": "Um ou mais itens selecionados, são inválidos ou não estão em seu carrinho"})
        
        # Verificando o estoque de cada item.
        for item in items_to_buy:

            if item.quantity > item.sku.stock:
                raise ValidationError({"error": f"Estoque insuficiente p/ {item.sku.product.name}."})
            
        try:
            
            # Inicição uma transação atômica garantindo que só conclua se cada etapa ocorrer com sucesso,
            # caso contrário será encerrado e desfeito todo o passo.
            with transaction.atomic():
                
                first_item = items_to_buy.first()
                order_merchant = first_item.sku.product.user

                # Criando o pedido
                order = Order.objects.create(
                    customer = request.user,
                    merchant = order_merchant,
                    delivery_address = str(chosen_address),
                    payment_method = payment_method,
                    status = 'PENDING',
                    total = 0
                )

                total_order_value = 0

                # Calculando e obtendo criando os itens do pedido
                for item in items_to_buy:
                    
                    current_price = item.sku.product.price
                    item_subtotal = current_price * item.quantity

                    OrderItem.objects.create(
                        order = order,
                        sku = item.sku,
                        quantity = item.quantity,
                        unit_price = item.sku.product.price,
                        subtotal = item_subtotal,
                        saved_product_name = item.sku.product.name,
                        saved_color = item.sku.color,
                        saved_size = item.sku.size
                    )

                    total_order_value += item_subtotal

                    # Atualizando o estoque após o pedido
                    item.sku.stock -= item.quantity
                    item.sku.save()

                # Salvando o pedido
                order.total = total_order_value
                order.save()

                # Removendo os itens pedidos do carrinho do usuário.
                items_to_buy.delete()
        
        # Tratamento de erro 
        except Exception as e:
            raise ValidationError({"error": f"Falha no processamento do pedido: {str(e)}"})
        
        serializer = self.get_serializer(order)

        return Response(serializer.data, status = status.HTTP_201_CREATED)
    
    @action(detail = True, methods = ['patch'], permission_classes=[IsAuthenticated, IsOrderMerchant])
    def status(self, request, pk=None):

        order = self.get_object()

        new_status = request.data.get('status')

        if new_status:
            order.status = new_status
            order.save()
            return Response({'status': f'Pedido Atualizado para: {new_status}'})
        
        return Response({'error': 'Nenhum status fornecido'}, status = status.HTTP_400_BAD_REQUEST)