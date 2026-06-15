from rest_framework import serializers
from .models import Users, Address, Contact, PaymentMethodUser
import django.contrib.auth.password_validation as validators
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class AddressSerializer(serializers.ModelSerializer):
    """
    Descrição do Serializer:
    - Gerencia a entrada e saída de dados dos endereços dos usuários.

    Validações Adicionais:
    - validate: Impede que um usuário cadastre um endereço exatamente igual (mesma rua, cidade e cep) 
      mais de uma vez, evitando poluição no banco de dados e na interface de checkout.
    """
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
    """
    Descrição do Serializer:
    - Gerencia o registro e a exibição do perfil dos usuários (Clientes e Lojistas).

    Campos Customizados:
    - password: Configurado como 'write_only=True' por segurança, garantindo que a senha 
      nunca seja retornada nas respostas da API.
    - addresses: Traz os endereços aninhados em modo somente leitura.

    Sobrescritas de Método:
    - create: Intercepta a criação padrão do DRF para utilizar o 'create_user' do UsersManager. 
      Isso é crucial para garantir que a senha passe por hash (criptografia) antes de ser salva no banco.
    """
    
    password = serializers.CharField(write_only=True)
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = Users
        fields = ['id', 'fullname', 'email', 'user_type', 'birthday', 'national_id', 'telephone', 'password', 'addresses']

    def create(self, validated_data):
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
    """
    Descrição do Serializer:
    - Valida o payload de entrada (e-mail) para iniciar o fluxo de recuperação de senha.
    - Como não está atrelado a um Model, herda de serializers.Serializer.
    """
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Descrição do Serializer:
    - Valida o token recebido e a nova senha durante a redefinição de credenciais.

    Validações Adicionais:
    - validate_new_password: Passa a nova senha pelos validadores de força de senha 
      nativos do Django (ex: tamanho mínimo, não ser muito comum) antes de aceitá-la.
    """
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        try:
            validators.validate_password(value)
        except ValidationError as erro:
            raise serializers.ValidationError(list(erro.messages))
        return value
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Descrição do Serializer:
    - Customiza a geração do token JWT padrão do SimpleJWT utilizado no Login.
    
    Mensagens Customizadas:
    - Substitui o erro padrão por uma mensagem unificada. Isso melhora a segurança 
      ao evitar ataques de enumeração (onde um invasor descobre se um e-mail existe 
      na base pela diferença das mensagens de erro).
    """
    default_error_messages = {
        'no_active_account': 'Email ou Senha inválidos. Por favor, tente novamente.'
    }

class ContactSerializer(serializers.ModelSerializer):
    """
    Descrição do Serializer:
    - Gerencia a criação e leitura dos tickets de contato ou suporte (Fale Conosco).
    """
    class Meta:
        model = Contact
        fields = ['name', 'phone', 'request_type', 'email', 'subject', 'message', 'created_at']

class PaymentMethodUserSerializer(serializers.ModelSerializer):
    """
    Descrição do Serializer:
    - Gerencia a associação de métodos de pagamento permitidos/favoritos do usuário.
    """

    customer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = PaymentMethodUser
        fields = '__all__'