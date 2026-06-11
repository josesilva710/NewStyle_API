from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Cart

# Este arquivo define um sinal que é acionado sempre que um novo usuário é criado.

# Este sinal é acionado sempre que um novo usuário é criado. 
# Ele verifica se o usuário foi criado (created=True) e, em caso afirmativo, 
# cria automaticamente um carrinho associado a esse usuário.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_cart_automatically(sender, instance, created, **kwargs):

    if created:
        Cart.objects.create(user=instance)