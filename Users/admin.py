from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Users, Address

# 1. Faz o endereço aparecer dentro da página do usuário
class AddressInline(admin.StackedInline):
    model = Address
    extra = 1  # Quantidade de espaços em branco para novos endereços
    classes = ['collapse'] # Deixa recolhido para não poluir visualmente

@admin.register(Users)
class MyUserAdmin(UserAdmin):
    #Inlines: mostra os endereços do usuário na mesma tela
    inlines = [AddressInline]

    #O que aparece na LISTA principal (na tabela de usuários)
    list_display = ('username', 'fullname', 'email', 'cliente_lojista', 'is_staff')
    
    #Adiciona filtros na lateral direita (muito útil!)
    list_filter = ('cliente_lojista', 'is_staff', 'is_superuser', 'is_active')

    #Define quais campos podem ser pesquisados na barra de busca
    search_fields = ('username', 'fullname', 'email', 'cpf')

    # 5. Organiza os campos dentro da página de EDIÇÃO
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('fullname', 'email', 'cpf', 'birthday', 'telephone')}),
        ('Tipo de Conta', {'fields': ('cliente_lojista',)}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    #Ordenação padrão na lista
    ordering = ('username',)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('rua', 'cidade', 'estado', 'cep', 'user')
    search_fields = ('rua', 'cep', 'user__username', 'user__fullname')