from rest_framework import serializers
from .models import produto, SKU
from Users.models import Users

class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = produto
        fields = '__all__'

        # Define os campos que são somente leitura, ou seja, não podem ser modificados pelo cliente.
        reald_only_fields = ['users']

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
        fields = '__all__'
    def validate_produto(self, value):
        request = self.context.get('request')
        if request and request.user:
            if value.produto.users != request.user:
                raise serializers.ValidationError(
                    {"error": "O SKU deve estar associado a um produto criado pelo usuário autenticado."})
        return value