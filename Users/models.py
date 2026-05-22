from django.db import models
from django.contrib.auth.models import AbstractUser

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