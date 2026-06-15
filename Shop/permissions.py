from rest_framework.permissions import BasePermission
from rest_framework import permissions

class IsMerchant(BasePermission):
    """
    Permissão global que restringe o acesso exclusivamente a usuários autenticados 
    que possuam o perfil de Lojista ('MERCHANT') ou que sejam Administradores do sistema.
    
    Geralmente aplicada em rotas de criação de catálogo (Produtos e SKUs).
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.user_type == 'MERCHANT' or request.user.is_staff


class IsProductOwner(BasePermission):
    """
    Permissão a nível de objeto que garante que a ação só possa ser realizada 
    se o usuário logado for o criador original do produto associado.
    
    Muito útil em rotas aninhadas (como SKUs), onde a verificação de posse 
    é feita através da relação de chave estrangeira (obj.product.user).
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.product.user == request.user
    

class IsCartOwner(BasePermission):
    """
    Permissão a nível de objeto que bloqueia interações cruzadas entre clientes.
    
    Garante que modificações em um item específico (como alterar a quantidade 
    ou deletar o item) sejam feitas estritamente pelo dono daquele carrinho.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.cart.user == request.user
    

class IsOrderMerchant(BasePermission):
    """
    Permissão híbrida para gerenciamento de pedidos.
    
    - Métodos Seguros (GET): Permite a leitura para todos que passarem na validação 
      da ViewSet (clientes e lojistas).
    - Métodos de Escrita (PATCH/PUT): Restringe a ação estritamente ao Lojista ('merchant') 
      do pedido, garantindo que o cliente não consiga alterar o status da própria compra.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.merchant == request.user