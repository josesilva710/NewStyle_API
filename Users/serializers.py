from rest_framework import serializers
from .models import Users, Address, Contact, PaymentMethodUser
import django.contrib.auth.password_validation as validators
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street', 'city', 'state', 'cep', 'number']

    def validate(self, data):
        user = self.context.get('request').user
        
        if Address.objects.filter(
            users=user,
            street=data['street'],
            city=data['city'],
            cep=data['cep']
        ).exists():
            raise serializers.ValidationError("Este endereço já está cadastrado para este usuário.")
        return data

class UsersSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True)
    
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = Users
        fields = ['id', 'fullname', 'email', 'user_type', 'birthday', 'national_id', 'telephone', 'password', 'addresses']

    #Reescrevendo o método que salva o objeto no banco de dados
    def create(self, validated_data):
        #metodo create_user para garantir a criptografia.
        user = Users.objects.create_user(
            email=validated_data['email'],
            fullname=validated_data['fullname'],
            user_type=validated_data['user_type'],
            birthday=validated_data.get('birthday'),
            national_id=validated_data.get('national_id'),
            telephone=validated_data.get('telephone'),
            password=validated_data['password']
        )
        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        try:
            validators.validate_password(value)
        except ValidationError as erro:
            raise serializers.ValidationError(list(erro.messages))
        return value
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': 'Email ou Senha inválidos. Por favor, tente novamente.'
    }

class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact
        fields = ['name', 'phone', 'request_type', 'email', 'subject', 'message', 'created_at']


class PaymentMethodUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentMethodUser
        fields = '__all__'