from django.urls import path, include
from rest_framework import routers
from Users.views import ( 
    UsersViewSet, 
    AddressViewSet, 
    LoginView, 
    RegisterView,
    ForgotPasswordView,
    ResetPasswordView,
    ContactViewSet,
    PaymentMethodViewSet
)

router = routers.DefaultRouter()

# Rotas de gerenciamento do perfil, endereço e configurações do usuário
router.register(r'users', UsersViewSet)
router.register(r'addresses', AddressViewSet)
router.register(r'contacts', ContactViewSet, basename='contacts')
router.register(r'payments', PaymentMethodViewSet, basename='payments')

urlpatterns = [
    # Rotas customizadas para o fluxo de Autenticação e Registro de novos usuários
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', LoginView.as_view(), name='auth_login'),

    # Rotas customizadas para o fluxo de Recuperação de Senha (geração de token e redefinição)
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='auth_forgot_password'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='auth_reset_password'),

    # Incluindo todas as rotas dinâmicas geradas pelo router na lista principal
    path('', include(router.urls))
]