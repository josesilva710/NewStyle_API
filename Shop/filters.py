from django_filters import rest_framework as filters
from .models import Product

class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    """
    Filtro customizado para aceitar múltiplos valores separados por vírgula em requisições de API.
    
    Herda de `BaseInFilter` (que transforma a string separada por vírgula em uma lista do Python) 
    e de `CharFilter` (que aplica essa lista em um campo de texto no banco de dados).
    """
    pass

class ProductFilter(filters.FilterSet):
    """
    Conjunto de filtros avançados para o modelo Product.

    Esta classe substitui a declaração simples de `filterset_fields` na ViewSet,
    permitindo buscas mais complexas, como combinações usando o operador 'IN'.

    Filtros Disponíveis:
        - `category__in`: Busca produtos que pertençam a qualquer uma das categorias listadas.
          Uso na URL: ?category__in=SHIRTS,PANTS
        
        - `category`: Mantém o comportamento original de busca por correspondência exata.
          Uso na URL: ?category=SHIRTS
    """
    
    category__in = CharInFilter(field_name='category', lookup_expr='in')
    category = filters.CharFilter(field_name='category', lookup_expr='exact')

    class Meta:
        model = Product
        fields = ['category']