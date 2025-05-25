from django.contrib import admin
from .models import Rental

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'start_date', 'end_date', 'status', 'created_at')
    list_filter = ('status', 'start_date')
    search_fields = ('user__username', 'product__name')