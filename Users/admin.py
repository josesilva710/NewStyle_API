from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Users, Address, Contact, PaymentMethodUser
from django.db import models

# Faz o endereço aparecer dentro da página do usuário
class AddressInline(admin.StackedInline):
    model = Address
    extra = 1  # Quantidade de espaços em branco para novos endereços
    classes = ['collapse'] # Deixa recolhido para não poluir visualmente

@admin.register(Users)
class MyUserAdmin(admin.ModelAdmin):
    # Inlines: mostra os endereços do usuário na mesma tela
    inlines = [AddressInline]

    # O que aparece na LISTA principal (na tabela de usuários)
    list_display = ('fullname', 'email', 'user_type', 'is_staff', 'is_active')
    
    # Adiciona filtros na lateral direita (muito útil!)
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')

    # Define quais campos podem ser pesquisados na barra de busca
    search_fields = ('fullname', 'email', 'national_id')

    # Organiza os campos dentro da página de edição
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('fullname', 'national_id', 'birthday', 'telephone')}),
        ('Tipo de Conta', {'fields': ('user_type',)}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login',)}),
    )

    # Ordenação padrão na lista
    ordering = ('fullname',)

# Registra o modelo Address para que ele apareça no admin
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'street', 'city', 'state', 'cep', 'user')
    search_fields = ('street', 'cep', 'user__email', 'user__fullname')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('subject', 'email', 'name', 'created_at')
    search_fields = ('subject', 'email', 'name')

admin.site.register(PaymentMethodUser)