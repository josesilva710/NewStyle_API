from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings

class Produto(models.Model):
    
    categorias_choices = (
        ('calcas', 'Calças'),
        ('camisas', 'Camisas'),
        ('bermudas', 'Bermudas'),
        ('vestidos', 'Vestidos'),
        ('saias', 'Saias'),
        ('shorts', 'Shorts'),
        ('blusas', 'Blusas'),
    )
    
    user = models.ForeignKey(
    settings.AUTH_USER_MODEL, 
    on_delete=models.CASCADE, 
    related_name='produtos')

    ativo = models.BooleanField(default=True)

    nome = models.CharField(max_length=255)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)
    categoria = models.CharField(max_length=50, choices=categorias_choices)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

        constraints = [
            models.UniqueConstraint(fields=['user', 'nome', 'preco', 'descricao'], name='unique_produto_por_lojista')
        ]

    def __str__(self):
        return f"{self.pk} - {self.user.fullname} - {self.nome} - R${self.preco:.2f} - Status: {'Ativo' if self.ativo else 'Inativo'}"

class SKU(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='skus')
    estoque = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    cor = models.CharField(max_length=50, null=False, blank=False)
    tamanho = models.CharField(max_length=50, null=False, blank=False)

    class Meta:

        constraints = [
            models.UniqueConstraint(fields=['produto', 'cor', 'tamanho'], name='unique_produto_cor_tamanho')
        ]

    def __str__(self):
        return f"{self.produto.nome} - Cor: {self.cor} - Tamanho: {self.tamanho} - Estoque: {self.estoque}"

class Carrinho(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='carrinho',
        null=False, blank=False)

    valor_frete = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quantidade = models.PositiveIntegerField(default=0)
    cupom = models.CharField(max_length=50, null=True, blank=True)
    entrega = models.CharField(max_length=255, null=True, blank=True)

    # A propriedade total calcula o valor total do carrinho somando o valor dos produtos 
    # sendo um campo dinâmico.
    @property
    def total(self):

        total_produtos = 0

        for item in self.itens.all():
            total_produtos += item.sku.produto.preco * item.quantidade_add

        #Exemplo de onde entraria a lógica para aplicar um desconto baseado em um cupom, 
        # caso seja necessário implementar essa funcionalidade no futuro.
        #uma alternativa seria o cadastro de cupoms(models) associados a cada lojista ou a plataforma.

        
        #if self.cupom:
            # Exemplo de desconto de 10% para um cupom específico
        #   if self.cupom == 'DESCONTO10':
        #       total_produtos *= 0.9  # Aplica um desconto de 10%

        return total_produtos

    class Meta:
        verbose_name = 'Carrinho'
        verbose_name_plural = 'Carrinhos'

    def __str__(self):
        return f"Carrinho de {self.user.fullname} - Total: {self.total:.2f}"

class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens_carrinho')
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE)
    quantidade_add = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Item do Carrinho'
        verbose_name_plural = 'Itens do Carrinho'

    # A propriedade subtotal calcula o valor total do item no carrinho com base no 
    # preço do produto e na quantidade adicionada, sendo um campo dinâmico.
    @property
    def subtotal(self):
        return self.sku.produto.preco * self.quantidade_add

    def __str__(self):
        return f"{self.quantidade_add}x {self.sku.produto.nome} no carrinho de {self.carrinho.user.fullname}"

class Pedido(models.Model):
    status_choices = (
        ('pendente', 'Pendente'),
        ('em processamento', 'Em Processamento'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    )

    formas_de_pagamento = (
        ('pix', 'Pix'),
        ('crédito', 'Crédito'),
        ('débito', 'Débito'),
        ('boleto', 'Boleto')
    )

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='pedidos')
    
    total = models.DecimalField(max_digits=10, decimal_places=2)
    entrega = models.CharField(max_length=255, null=True, blank=True)
    forma_pagamento = models.CharField(choices = formas_de_pagamento, blank = False, null = False)
    status = models.CharField(max_length=50, default='pendente', choices=status_choices)
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"Pedido de {self.user.fullname} - Total: {self.total:.2f}"

#   Apesar de parecer redudante alguns campos com o SKU, a classe itempedido é necessária para armazenar as 
# informações específicas de cada item dentro de um pedido no momento que estão sendo realizados, pois o 
# estoque do SKU pode mudar depois que o pedido é feito, e precisamos garantir que as informações do pedido 
# permaneçam consistentes mesmo que o estoque do SKU seja atualizado posteriormente.
class ItemPedido(models.Model):

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens_pedido')
    sku = models.ForeignKey(SKU, on_delete=models.SET_NULL, null=True)
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    produto_nome_save = models.CharField(max_length=256, null = False, blank = False)
    tamanho_save = models.CharField(max_length=50, null=False, blank=False)
    cor_save = models.CharField(max_length=50, null= False, blank=False)

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def __str__(self):
        nome_produto = self.sku.produto.nome if self.sku else "Produto removido"
        return f"{self.quantidade}x {self.produto_nome_save} no pedido de {self.pedido.user.fullname}"