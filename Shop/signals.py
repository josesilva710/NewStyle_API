from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Cart

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_cart_automatically(sender, instance, created, **kwargs):
    """
    Cria automaticamente um carrinho de compras vazio sempre que um novo usuário é registrado.
    
    Este sinal (signal) intercepta o evento 'post_save' do modelo de Usuário. 
    A validação 'if created' garante que o carrinho seja gerado exclusivamente na 
    criação da conta, sendo ignorada em atualizações futuras de perfil.
    """
    if created:
        Cart.objects.create(user=instance)