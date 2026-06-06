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

router = routers.DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'addresses', AddressViewSet)
router.register(r'contact', ContatoViewSet, basename='contato')
router.registe(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', LoginView.as_view(), name='auth_login'),

    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='auth_forgot_password'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='auth_reset_password'),

    path('', include(router.urls)),
]