from rest_framework import serializers
from .models import Product, SKU, Cart, CartItem, Order, OrderItem

class ProductSerializer(serializers.ModelSerializer):
    """
    Descrição do Serializer:
    - Transforma os dados do modelo Product em JSON e vice-versa.
    - Otimiza a leitura adicionando dados contextuais úteis para o front-end.

    Campos Customizados (Apenas Leitura):
    - merchant_name: Retorna o nome completo do lojista dono do produto.
    - variations_count: Calcula em tempo real a quantidade de SKUs atrelados ao produto.

    Validações Adicionais:
    - validate: Bloqueia a criação de produtos por usuários que não possuam o perfil de 'MERCHANT'.
    """
    
    merchant_name = serializers.ReadOnlyField(source='user.fullname')
    variations_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'merchant_name',
            'name',
            'price',
            'description',
            'category',
            'is_active',
            'variations_count'
        ]

        read_only_fields = ['user']

    def validate(self, data):
        request = self.context.get('request')
        if request and request.user:
            if request.user.user_type != 'MERCHANT':
                raise serializers.ValidationError({
                    "error": "Apenas usuários com perfil de lojista podem criar produtos."})
        return data
    
    def get_variations_count(self, obj):
        return obj.skus.count()
            
class SKUSerializer(serializers.ModelSerializer):
    """
    Descrição do Serializer:
    - Gerencia a serialização das variações de estoque de um produto (SKU).

    Validações Adicionais:
    - validate_product: Garante de forma extra de segurança que a variação está sendo atrelada
      a um produto que realmente pertence ao usuário autenticado.
    """

    class Meta:
        model = SKU
        fields = ['id', 'stock', 'color', 'size']
        
    def validate_product(self, value):
        request = self.context.get('request')
        if request and request.user:
            if value.user != request.user:
                raise serializers.ValidationError(
                    {"error": "O SKU deve estar associado a um produto criado pelo usuário autenticado."})
        return value

class CartItemSerializer(serializers.ModelSerializer):
    """
    Descrição do Serializer:
    - Gerencia a entrada (criação/edição) e saída (leitura) dos itens individuais no carrinho.

    Representação Customizada:
    - to_representation: Sobrescreve o comportamento padrão do DRF para retornar um payload
      rico em detalhes (aninhando nome do produto, lojista, detalhes do SKU e subtotal),
      dispensando múltiplas chamadas do front-end à API.
    """

    sku = serializers.PrimaryKeyRelatedField(queryset=SKU.objects.all())

    class Meta:
        model = CartItem
        fields = ['id', 'sku', 'quantity']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        unit_price = instance.sku.product.price

        return {
            'item_id': data['id'],
            'product_id': instance.sku.product.id, 
            'merchant': instance.sku.product.user.fullname,
            'product': instance.sku.product.name,
            'unit_price': unit_price,
            'sku': {
                'sku_id': instance.sku.id,
                'color': instance.sku.color,
                'size': instance.sku.size
            },
            'quantity': data['quantity'],
            'subtotal': instance.subtotal,
        }

class CartSerializer(serializers.ModelSerializer):
    """
    Descrição do Serializer:
    - Representa o carrinho de compras completo do cliente.
    - Funciona apenas para consolidar os dados de leitura, trazendo os itens aninhados e o valor total calculado.
    """

    cart_items = CartItemSerializer(many=True, read_only=True)
    total = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['cart_items', 'total']
    
class OrderItemSerializer(serializers.ModelSerializer):
    """
    Descrição do Serializer:
    - Serializa os itens individuais após a concretização de um pedido.
    - Serve como um registro imutável (snapshot) das características do produto no momento exato da compra.
    - Oculta propositalmente as chaves estrangeiras (sku, order) para simplificar a visualização do JSON.
    """

    class Meta:
        model = OrderItem
        exclude = ['sku', 'order']

class OrderSerializer(serializers.ModelSerializer):
    """
    Descrição do Serializer:
    - Consolida todas as informações de um pedido finalizado (status, pagamento, endereço).
    - Traz os itens do pedido aninhados automaticamente (order_items) para visualização do extrato da compra.
    """

    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'status', 'payment_method', 'delivery_address', 'order_items', 'total']