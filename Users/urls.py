from django.urls import path, include
from rest_framework import routers
from Users.views import ( 
    UsersViewSet, 
    AddressViewSet, 
    LoginView, 
    RegisterView,
    ForgotPasswordView,
    ResetPasswordView,
    ContatoViewSet
)
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'addresses', AddressViewSet)

contact_router = routers.SimpleRouter()
contact_router.register(r'contato', ContatoViewSet, basename='contato')

suporte_router = routers.NestedSimpleRouter(contact_router, r'contato', lookup='contato')
suporte_router.register(r'messages', ContatoViewSet, basename='contato-messages')

atendimento_router = routers.NestedSimpleRouter(contact_router, r'contato', lookup='contato')
atendimento_router.register(r'atendimento', ContatoViewSet, basename='contato-atendimento')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', LoginView.as_view(), name='auth_login'),

    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='auth_forgot_password'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='auth_reset_password'),

    path('', include(contact_router.urls)),

    path('', include(router.urls)),
]