from rest_framework.permissions import BasePermission
from rest_framework import permissions

# BasePermission é a classe base para criar permissões personalizadas no Django REST Framework.

# A classe IsMerchant verifica se o usuário é autenticado e tem a permissão de lojista, 
# com o objetivo de permitir que apenas lojistas autenticados possam criar, 
# atualizar ou deletar produtos e SKUs.
class IsMerchant(BasePermission): 
    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False
        # Verifica se o usuário é autenticado e tem a permissão de lojista
        return request.user.user_type == 'MERCHANT' or request.user.is_staff


class IsProductOwner(BasePermission): 
    def has_object_permission(self, request, view, obj):

        if request.user.is_staff:
            return True

        # Verifica se o usuário é o dono do produto
        return obj.product.user == request.user
    

class IsCartOwner(BasePermission): 

    def has_object_permission(self, request, view, obj):

        if request.user.is_staff:
            return True

        # Verifica se o usuário é o dono do carrinho
        return obj.cart.user == request.user
    

class IsOrderMerchant(BasePermission): 

    def has_object_permission(self, request, view, obj):

        # Se for apenas um método de listagem
        if request.method in permissions.SAFE_METHODS:
            return True

        # se for um método de PATCH/PUT
        return obj.merchant == request.user