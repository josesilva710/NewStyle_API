from rest_framework import serializers
from .models import Produto, SKU, Carrinho, ItemCarrinho, Pedido, ItemPedido

class ProdutoSerializer(serializers.ModelSerializer):
    
    nome_lojista = serializers.ReadOnlyField(source='user.fullname')

    class Meta:
        model = Produto
        fields = [
            'id',
            'nome_lojista',
            'nome',
            'preco',
            'descricao',
            'categoria',
            'ativo'
        ]

        # Define os campos que são somente leitura, ou seja, não podem ser modificados pelo cliente.
        read_only_fields = ['users']

        #Garante que apenas usuários com perfil de lojista possam criar produtos.
        def validate(self, data):
            request = self.context.get('request')
            if request and request.user:
                if request.user.cliente.lojista != 'lojista':
                    raise serializers.ValidationError({
                        "error": "Apenas usuários com perfil de lojista podem criar produtos."})
                return data
            
class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ['id', 'estoque', 'cor', 'tamanho']
        
    # Garante que o SKU esteja associado a um produto criado pelo usuário autenticado.
    def validate_produto(self, value):
        request = self.context.get('request')
        if request and request.user:
            if value.produto.users != request.user:
                raise serializers.ValidationError(
                    {"error": "O SKU deve estar associado a um produto criado pelo usuário autenticado."})
        return value

class ItemCarrinhoSerializer(serializers.ModelSerializer):

    sku = serializers.PrimaryKeyRelatedField(queryset=SKU.objects.all())

    class Meta:
        model = ItemCarrinho
        fields = ['id', 'sku', 'quantidade_add']

    def to_representation(self, instance):

        data = super().to_representation(instance)
        preço_unit = instance.sku.produto.preco

        return {
            'id_do_item': data['id'],
            'id_do_produto': instance.sku.produto.id, 
            'Lojista': instance.sku.produto.user.fullname,
            'produto': instance.sku.produto.nome,
            'preço_unit': preço_unit,
            'sku': {
                'id_sku': instance.sku.id,
                'cor': instance.sku.cor,
                'tamanho': instance.sku.tamanho
            },
            'quantidade_add': data['quantidade_add'],
            'subtotal': instance.subtotal,
        }

class CarrinhoSerializer(serializers.ModelSerializer):

    itens_do_carrinho = ItemCarrinhoSerializer(many=True, read_only=True, source='itens_carrinho')
    total = serializers.FloatField(read_only=True)
    class Meta:
        model = Carrinho

        fields = ['itens_do_carrinho', 'total']
    
class ItemPedidoSerializer(serializers.ModelSerializer):

    class Meta:

        model = ItemPedido

        exclude = ['sku', 'pedido']

class PedidoSerializer(serializers.ModelSerializer):

    itens_do_pedido = ItemPedidoSerializer(many = True, read_only = True, source='itens_pedido')

    class Meta:

        model = Pedido

        fields = ['id', 'data', 'status', 'forma_pagamento', 'entrega', 'itens_do_pedido', 'total']