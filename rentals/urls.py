from django.urls import path
from . import views

urlpatterns = [
    path('create/<int:product_id>/<slug:product_slug>/', views.create_rental, name='create_rental'),
    path('my-rentals/', views.my_rentals, name='my_rentals'),
    path('bill/<uuid:rental_id>/', views.generate_bill, name='generate_bill'),
    path('cancel/<uuid:rental_id>/', views.cancel_rental, name='cancel_rental'),
]