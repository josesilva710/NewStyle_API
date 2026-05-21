from rest_framework import serializers
from .models import Users, Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:

        model = Address

        fields = ['id', 'user', 'rua', 'cidade', 'estado', 'cep']

class UsersSerializer(serializers.ModelSerializer):
    class Meta:

        addresses = AddressSerializer(many = True, read_only = True)

        model = Users
        fields = ['id', 'fullname', 'email', 'cliente_lojista', 'birthday', 'cpf', 'telephone', 'addresses']