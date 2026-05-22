from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from Users.views import UsersViewSet, AddressViewSet, LoginView, RegisterView

routers = routers.DefaultRouter()
routers.register(r'users', UsersViewSet)
routers.register(r'addresses', AddressViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/register', RegisterView.as_view(), name='auth_register'),
    path('auth/login', LoginView.as_view(), name='auth_login'),
    path('', include(routers.urls)),
]
