from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings

#classe produto para representar os produtos disponíveis na loja, 
# contendo informações como nome, descrição, preço e imagem, 
# e um relacionamento de chave estrangeira.
class produto(models.Model):
    #Relacionamento de chave estrangeira para o modelo de usuário personalizado.
    #cada produto está associado a um usuário (lojista) que o criou, 
    # e se o usuário for deletado, os produtos associados a ele também serão deletados.
    users = models.ForeignKey(
    settings.AUTH_USER_MODEL, 
    on_delete=models.CASCADE, 
    related_name='produtos')

    nome = models.CharField(max_length=255)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def __str__(self):
        return f"{self.nome} - R${self.preco:.2f}"


#Classe SKU para representar as variações de um produto, como cor e tamanho,
# e para controlar o estoque de cada variação.
class SKU(models.Model):
    produto = models.ForeignKey(produto, on_delete=models.CASCADE, related_name='skus')
    estoque = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    cor = models.CharField(max_length=50, null=True, blank=True)
    tamanho = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.produto.nome} - Cor: {self.cor} - Tamanho: {self.tamanho} - Estoque: {self.estoque}"

#classe Carrinho para representar o carrinho de compras de um usuário,
# contendo informações sobre os itens adicionados, o total do carrinho, 
# o valor do frete, a quantidade total de itens, o cupom aplicado e o endereço de entrega.
class Carrinho(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='carrinho')

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_frete = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    cupom = models.CharField(max_length=50, null=True, blank=True)
    entrega = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Carrinho'
        verbose_name_plural = 'Carrinhos'

    def __str__(self):
        return f"Carrinho de {self.user.fullname} - Total: {self.total:.2f}"

#Classe ItemCarrinho para representar os itens individuais dentro do carrinho de compras,
# contendo informações sobre o SKU do produto, a quantidade adicionada e o subtotal para aquele item
# (que é calculado multiplicando a quantidade pelo preço do produto).
class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens')
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE)
    quantidade_add = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = 'Item do Carrinho'
        verbose_name_plural = 'Itens do Carrinho'

    def __str__(self):
        return f"{self.quantidade_add}x {self.sku.produto.nome} no carrinho de {self.carrinho.user.fullname}"

#Classe Pedido para representar um pedido realizado por um usuário, 
# contendo informações sobre o usuário que fez o pedido, 
# o total do pedido, o endereço de entrega, a forma de pagamento, 
# o status do pedido e a data em que o pedido foi criado.
class Pedido(models.Model):
    status_choices = (
        ('pendente', 'Pendente'),
        ('em processamento', 'Em Processamento'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='pedidos')

    total = models.DecimalField(max_digits=10, decimal_places=2)
    entrega = models.CharField(max_length=255, null=True, blank=True)
    forma_pagamento = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, default='pendente', choices=status_choices)
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f"Pedido de {self.user.fullname} - Total: {self.total:.2f}"

#Apesar de parecer redudante alguns campos com o SKU, a classe itempedido é necessária para armazenar as 
# informações específicas de cada item dentro de um pedido no momento que estão sendo realizados, pois o 
# estoque do SKU pode mudar depois que o pedido é feito, e precisamos garantir que as informações do pedido 
# permaneçam consistentes mesmo que o estoque do SKU seja atualizado posteriormente.
class itemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    sku = models.ForeignKey(SKU, on_delete=models.SET_NULL, null=True)
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tamanho_save = models.CharField(max_length=50, null=True, blank=True)
    cor_save = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def __str__(self):
        nome_produto = self.sku.produto.nome if self.sku else "Produto removido"
        return f"{self.quantidade}x {nome_produto} no pedido de {self.pedido.user.fullname}"