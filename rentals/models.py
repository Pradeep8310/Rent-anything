from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.utils import timezone
from datetime import timedelta
import uuid


class Rental(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),


    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
            return f"{self.user.username} - {self.product.name}"
    
    def save(self, *args, **kwargs):
            if not self.total_price:
                days = (self.end_date - self.start_date).days + 1
                self.total_price = self.product.price_per_day * days
            super().save(*args, **kwargs)
    
    def get_rental_days(self):
            return (self.end_date - self.start_date).days + 1
    
    def generate_bill_id(self):
            return f"BILL-{self.id.hex[:8]}"
    
    
