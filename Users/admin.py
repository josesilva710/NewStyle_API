from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Users, Address, Contact, PaymentMethodUser
from django.db import models

@admin.register(Users)
class MyUserAdmin(admin.ModelAdmin):

    filter_horizontal = ['addresses']

    list_display = ('fullname', 'email', 'user_type', 'is_staff', 'is_active')
    
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')

    search_fields = ('fullname', 'email', 'national_id')

    # Organiza os campos dentro da página de edição
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('fullname', 'national_id', 'birthday', 'telephone')}),
        ('Endereços', {'fields': ('addresses',)}),
        ('Tipo de Conta', {'fields': ('user_type',)}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login',)}),
    )

    # Ordenação padrão na lista
    ordering = ('fullname',)

# Registra o modelo Address para que ele apareça no admin
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'street', 'city', 'state', 'cep', 'get_users')
    search_fields = ('street', 'cep', 'users__email', 'users__fullname')

    def get_users(self, obj):

        return ", ".join([user.fullname for user in obj.users.all()])
    
    get_users.short_description = 'Usuários Vinculados'

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('subject', 'email', 'name', 'created_at')
    search_fields = ('subject', 'email', 'name')

admin.site.register(PaymentMethodUser)