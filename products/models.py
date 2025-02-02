from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Default (e.g., in English)
    name_ru = models.CharField(max_length=100, blank=True, null=True)  # Russian name
    name_uz = models.CharField(max_length=100, blank=True, null=True)  # Uzbek name
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name


class Company(models.Model):
    COUNTRY_CHOICES = [
        ('Germany', 'Germany'),
        ('France', 'France'),
        ('Italy', 'Italy'),
    ]

    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='products/', blank=True, null=True)
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    COUNTRY_CHOICES = [
        ('Germany', 'Germany'),
        ('France', 'France'),
        ('Italy', 'Italy'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()  # Default description in English
    productdescription_ru = models.TextField(null=True, blank=True)  # Russian translation
    productdescription_uz = models.TextField(null=True, blank=True)  # Uzbek translation
    categories = models.ManyToManyField('Category', related_name="products")
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES)
    brand = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='products')  # Foreign key to Company (brand)
    original_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    image1 = models.ImageField(upload_to='products/', blank=True, null=True)
    image2 = models.ImageField(upload_to='products/', blank=True, null=True)
    image3 = models.ImageField(upload_to='products/', blank=True, null=True)
    image4 = models.ImageField(upload_to='products/', blank=True, null=True)
    image5 = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_hot_deal1 = models.BooleanField(default=False)
    is_hot_deal2 = models.BooleanField(default=False)
    is_hot_deal3 = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user} - {self.product.name}"

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.product.name}"
    
class Order(models.Model):
    PENDING = 'Pending'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=255)
    email = models.EmailField()
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    specifications = models.CharField(max_length=1000)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    # For displaying order items
    items = models.ManyToManyField('Product', through='OrderItem')

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username}"
    
# Example: In your models.py
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)  # This ensures OrderItems are deleted when an Order is deleted
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Ensure this field is set correctly

    def __str__(self):
        return f"{self.product.name} - {self.quantity} x {self.price}"

class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5)  # Rating out of 5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s review of {self.product.name}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email}) on {self.date_created}"
