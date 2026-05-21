from django.db import models
from django.contrib.auth.models import AbstractUser


#Classe AbstractUser para criar um modelo de usuário personalizado, 
# com campos adicionais para diferenciar entre clientes e lojistas, 
# além de informações pessoais como nome completo, data de nascimento, CPF e telefone.
#AbstractUser já inclui campos básicos como username, password, email, etc., 
#então não precisamos redefinir esses campos, apenas adicionamos os novos campos 
#específicos para a nossa classe.
class Users(AbstractUser):
    USER_TYPE_CHOICES = (
        ('cliente', 'Cliente'),
        ('lojista', 'Lojista'),
    )
    #cliente_lojista é um campo de escolha que indica se o usuário é um cliente ou um lojista.
    cliente_lojista = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES, 
        default='cliente')
    #dados que faltavam para o cadastro.
    fullname = models.CharField(max_length=255)
    birthday = models.DateField(null=True, blank=True)
    cpf = models.CharField(max_length=14, unique=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'fullname', 'cpf']

    #classe para definir o nome singular e plural do modelo no admin do Django,
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    #método __str__ para retornar uma representação legível do objeto,
    def __str__(self):
        return f"{self.fullname} - {self.cliente_lojista}"

#Classe Address para armazenar os endereços dos usuários, 
# com um relacionamento de chave estrangeira para o modelo Users.
class Address(models.Model):
    user = models.ForeignKey(
        Users, 
        on_delete=models.CASCADE, 
        related_name='addresses')
    
    rua = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    cep = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    def __str__(self):
        return f"{self.rua}, {self.cidade} / {self.estado}, {self.cep}"