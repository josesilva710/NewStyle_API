from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

class Users(AbstractUser):
    USER_TYPE_CHOICES = (
        ('cliente', 'Cliente'),
        ('lojista', 'Lojista'),
    )
    
    cliente_lojista = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES, 
        default='cliente')
    
    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    birthday = models.DateField(null=True, blank=True)
    cpf = models.CharField(max_length=14, unique=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname', 'cpf']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return f"{self.fullname} - {self.cliente_lojista}"

class Address(models.Model):
    user = models.ForeignKey(
        Users, 
        on_delete=models.CASCADE, 
        related_name='addresses')
    
    rua = models.CharField(max_length=255)
    numero = models.IntegerField(null=True, blank=True)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    cep = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    def __str__(self):
        return f"{self.rua}, {self.cidade} / {self.estado}, {self.cep}"

class Suporte(models.Model):
    user = models.ForeignKey(
        Users, 
        on_delete=models.CASCADE, 
        related_name='suporte_tickets')
    email = models.EmailField()
    assunto = models.CharField(max_length=255)
    descricao = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Suporte'
        verbose_name_plural = 'Suportes'

    def __str__(self):
        return f"Ticket de Suporte - {self.assunto} ({self.user.fullname}) - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

#Classe Para gerenciamento de tokens de redefinição de senha
class PasswordResetToken(models.Model):

    #Relacionamento com o usuário para quem o token foi gerado
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    #Gerar um token UUID único para cada solicitação
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    #Data de criação do token para controle de expiração
    created_at = models.DateTimeField(auto_now_add=True)
    #Campo para marcar se o token já foi utilizado
    is_used = models.BooleanField(default=False)

#Método para verificar se o token é válido (não utilizado e dentro do prazo de expiração)
    def is_valid(self):
        expiration_time = self.created_at + timedelta(minutes=15)
        return not self.is_used and timezone.now() < expiration_time