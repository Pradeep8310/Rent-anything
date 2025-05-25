from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Category, Product

def product_list(request, category_slug=None):
    category = None
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    return render(request, 'products/list.html', {
        'category': category,
        'products': products
    })

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    
    return render(request, 'products/detail.html', {
        'product': product
    })

def search_products(request):
    query = request.GET.get('q')
    products = Product.objects.filter(available=True)
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    
    return render(request, 'products/search_results.html', {
        'products': products,
        'query': query
    })