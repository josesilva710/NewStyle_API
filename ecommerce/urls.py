from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from Users.views import( 
    UsersViewSet, 
    AddressViewSet, 
    LoginView, 
    RegisterView,
    ForgotPasswordView,
    ResetPasswordView
)

router = routers.DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'addresses', AddressViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('auth/register', RegisterView.as_view(), name='auth_register'),
    path('auth/login', LoginView.as_view(), name='auth_login'),

    path('auth/forgot-password', ForgotPasswordView.as_view(), name='auth_forgot_password'),
    path('auth/reset-password', ResetPasswordView.as_view(), name='auth_reset_password'),

    path('', include(router.urls)),
]
