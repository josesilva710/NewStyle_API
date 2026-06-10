from rest_framework.permissions import BasePermission
from rest_framework import permissions

#BasePermission é a classe base para criar permissões personalizadas no Django REST Framework.

#A classe IsLojista verifica se o usuário é autenticado e tem a permissão de lojista, 
# com o objetivo de permitir que apenas lojistas autenticados possam criar, 
# atualizar ou deletar produtos e SKUs.
class IsLojista (BasePermission):
    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False
        # Verifica se o usuário é autenticado e tem a permissão de lojista
        return request.user.cliente_lojista == 'lojista' or request.user.is_staff

class IsDonoDoProduto(BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.user.is_staff:
            return True

        # Verifica se o usuário é o dono do produto
        return obj.produto.user == request.user
    
class IsDonoDoCarrinho(BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.user.is_staff:
            return True

        # Verifica se o usuário é o dono do carrinho
        return obj.carrinho.user == request.user
    
class IsLojistaDoPedido(BasePermission):

    def has_object_permission(self, request, view, obj):


        #Se for apenas um método de listagem
        if request.method in permissions.SAFE_METHODS:

            return True

        #se for um método de PATCH/PUT
        return obj.lojista == request.user