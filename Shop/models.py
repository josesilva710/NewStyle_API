from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings

class Product(models.Model):
    
    CATEGORY_CHOICES = (
        ('PANTS', 'Calças'),
        ('SHIRTS', 'Camisas'),
        ('BERMUDAS', 'Bermudas'),
        ('DRESSES', 'Vestidos'),
        ('SKIRTS', 'Saias'),
        ('SHORTS', 'Shorts'),
        ('BLOUSES', 'Blusas'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='products')

    is_active = models.BooleanField(default=True)

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

        constraints = [

            models.UniqueConstraint(fields=['user', 'name', 'price', 'description'], name='unique_product_per_merchant')
        ]

    def __str__(self):
        return f"{self.pk} - {self.user.fullname} - {self.name} - R${self.price:.2f} - Status: {'Active' if self.is_active else 'Inactive'}"


class SKU(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='skus')
    stock = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    color = models.CharField(max_length=50, null=False, blank=False)
    size = models.CharField(max_length=50, null=False, blank=False)

    class Meta:
        constraints = [

            models.UniqueConstraint(fields=['product', 'color', 'size'], name='unique_product_color_size')
        ]

    def __str__(self):
        return f"{self.product.name} - Color: {self.color} - Size: {self.size} - Stock: {self.stock}"


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='cart',
        null=False, blank=False)

    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    coupon = models.CharField(max_length=50, null=True, blank=True)
    delivery_address = models.CharField(max_length=255, null=True, blank=True)

    @property
    def total(self):
        total_products = 0

        for item in self.cart_items.all():
            total_products += item.sku.product.price * item.quantity

        # if self.coupon:
        #   if self.coupon == 'DESCONTO10':
        #       total_products *= 0.9  

        return total_products

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f"Cart of {self.user.fullname} - Total: {self.total:.2f}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'

    @property
    def subtotal(self):

        return self.sku.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.sku.product.name} in {self.cart.user.fullname}'s cart"


class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELED', 'Canceled'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('PIX', 'Pix'),
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('BOLETO', 'Boleto')
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='orders')
    
    merchant = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        related_name='sales')

    total = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.CharField(max_length=255, null=True, blank=True)
    payment_method = models.CharField(choices=PAYMENT_METHOD_CHOICES, blank=False, null=False)
    status = models.CharField(max_length=50, default='PENDING', choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order from Customer {self.customer.fullname} to Merchant {self.merchant.fullname} - Total: {self.total:.2f}"


# Apesar de parecer redundante alguns campos com o SKU, a classe OrderItem é necessária para armazenar as 
# informações específicas de cada item dentro de um pedido no momento que estão sendo realizados...
class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    sku = models.ForeignKey(SKU, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    saved_product_name = models.CharField(max_length=256, null=False, blank=False) 
    saved_size = models.CharField(max_length=50, null=False, blank=False)
    saved_color = models.CharField(max_length=50, null=False, blank=False)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.quantity}x {self.saved_product_name} in {self.order.customer.fullname}'s order"