from rest_framework import serializers
from .models import Product, SKU, Cart, CartItem, Order, OrderItem

class ProductSerializer(serializers.ModelSerializer):
    
    merchant_name = serializers.ReadOnlyField(source='user.fullname')

    class Meta:
        model = Product
        fields = [
            'id',
            'merchant_name',
            'name',
            'price',
            'description',
            'category',
            'is_active'
        ]

        read_only_fields = ['user']

    def validate(self, data):
        request = self.context.get('request')
        if request and request.user:
            if request.user.user_type != 'MERCHANT':
                raise serializers.ValidationError({
                    "error": "Apenas usuários com perfil de lojista podem criar produtos."})
        return data
            
class SKUSerializer(serializers.ModelSerializer):

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

    cart_items = CartItemSerializer(many=True, read_only=True)
    total = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['cart_items', 'total']
    
class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:

        model = OrderItem

        exclude = ['sku', 'order']

class OrderSerializer(serializers.ModelSerializer):

    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:

        model = Order

        fields = ['id', 'created_at', 'status', 'payment_method', 'delivery_address', 'order_items', 'total']