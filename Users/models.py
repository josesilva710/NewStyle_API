from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import uuid
from django.utils import timezone
from datetime import timedelta
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.contrib.auth.base_user import BaseUserManager

class UsersManager(BaseUserManager):
    """
    Gerenciador customizado para o modelo de Usuário.
    Substitui o comportamento padrão do Django para exigir e utilizar o e-mail 
    como identificador principal para login, em vez do 'username' padrão.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class Users(AbstractBaseUser, PermissionsMixin):
    """
    Modelo base de Usuário customizado da aplicação.
    
    Desacopla o sistema do modelo padrão do Django para usar o e-mail como credencial (USERNAME_FIELD).
    Divide os usuários da plataforma em dois perfis de acesso: Cliente ('CUSTOMER') e Lojista ('MERCHANT').
    """

    objects = UsersManager()

    USER_TYPE_CHOICES = (
        ('CUSTOMER', 'Customer'),
        ('MERCHANT', 'Merchant'),
    )
    
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES, 
    )
    
    addresses = models.ManyToManyField('Address', related_name='users', blank=True, default=0)

    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    birthday = models.DateField(null=True, blank=True)
    national_id = models.CharField(max_length=14, unique=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname', 'national_id', 'telephone']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.fullname} - {self.user_type}"

class Address(models.Model):
    """
    Representa um endereço físico no sistema.
    
    Projetado para ser reutilizável (através da relação ManyToMany no modelo Users).
    O campo 'number' é tipado como String de propósito para acomodar endereços 
    que contenham letras ou blocos (ex: '123-A', 'S/N').
    """
    
    street = models.CharField(max_length=255)
    number = models.CharField(max_length=20, null=False, blank=False)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    cep = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        constraints = [
            models.UniqueConstraint(fields=['street', 'number', 'city', 'state', 'cep'], name='unique_address')
        ]

    def __str__(self):
        return f"{self.street}, {self.city} / {self.state}, {self.cep}"

class Contact(models.Model):
    """
    Registro de chamados ou mensagens de contato do usuário com a plataforma.
    
    Aplica validações de tamanho de string para garantir que a mensagem 
    contenha conteúdo útil. Possui uma restrição que evita a criação de chamados 
    exatamente idênticos (prevenção de envios duplicados/spam).
    """

    TYPES_CHOICES = [
        ('SUPPORT', 'Support'),
        ('SERVICE', 'Service'),
    ]

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    request_type = models.CharField(max_length=20, choices=TYPES_CHOICES, blank=False, null=False)
    subject = models.CharField(max_length=255)
    message = models.TextField(
        validators=[
            MinLengthValidator(10, message="The message must be at least 10 characters long."),
            MaxLengthValidator(2000, message="The message cannot exceed 2000 characters.")
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        constraints = [
            models.UniqueConstraint(fields=['name', 'email', 'subject', 'message'], name='unique_request_user')
        ]

    def __str__(self):
        return f"Contact Ticket - {self.subject} ({self.name}) - {self.created_at.strftime('%d/%m/%Y - %H:%M:%S')}"

class PaymentMethodUser(models.Model):
    """
    Gerencia as opções de métodos de pagamento vinculados aos clientes.
    """

    customer = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name='payments_methods')
    
    PAYMENT_METHOD_CHOICES = (
        ('PIX', 'Pix'),
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('BOLETO', 'Boleto')
    )

    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHOD_CHOICES, blank=False, null=False)

    def __str__(self):

        return f"Method: {self.payment_method} from {self.customer.fullname}" 

class PasswordResetToken(models.Model):
    """
    Gerencia a criação e validação de tokens seguros para redefinição de senha.
    
    Utiliza UUID4 para garantir tokens longos, únicos e impossíveis de prever.
    Fornece um método utilitário (is_valid) para checar simultaneamente 
    se o token não foi gasto e se ainda está na janela de 15 minutos de validade.
    """

    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        """Verifica se o token é válido (não utilizado e dentro do prazo de 15 minutos)."""
        expiration_time = self.created_at + timedelta(minutes=15)
        return not self.is_used and timezone.now() < expiration_time