from rest_framework import serializers
from .models import Users, Address, PasswordResetToken, Contato
import django.contrib.auth.password_validation as validators
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class AddressSerializer(serializers.ModelSerializer):
    class Meta:

        model = Address

        fields = ['id', 'user', 'rua', 'cidade', 'estado', 'cep', 'numero']

    def validate(self, data):
        #Verifica se já existe um endereço igual para o mesmo usuário
        if Address.objects.filter(
            user=data['user'],
            rua=data['rua'],
            cidade=data['cidade'],
            cep=data['cep']
        ).exists():
            raise serializers.ValidationError("Este endereço já está cadastrado para este usuário.")
        return data

class UsersSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True)
    
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = Users

        fields = ['id', 'fullname', 'email', 'cliente_lojista', 'birthday', 'cpf', 'telephone', 'password', 'addresses']

    #Reescrevendo o método que salva o objeto no banco de dados
    def create(self, validated_data):
        #metodo create_user para garantir a criptografia.
        user = Users.objects.create_user(
            email=validated_data['email'],
            fullname=validated_data['fullname'],
            cliente_lojista=validated_data['cliente_lojista'],
            birthday=validated_data.get('birthday'),
            cpf=validated_data.get('cpf'),
            telephone=validated_data.get('telephone'),
            password=validated_data['password']
        )
        return user
    
class passwordResetTokenSerializer(serializers.Serializer):
    
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        try:
            validators.validate_password(value)
        except ValidationError as erro:
            raise serializers.ValidationError(list(erro.messages))
        return value
    
class MeuTokenPersonalizadoSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': 'Email ou Senha inválidos. Por favor, tente novamente.'
    }

class ContatoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contato
        fields = ['nome', 'telefone', 'solicitacao', 'email', 'assunto', 'mensagem', 'created_at']