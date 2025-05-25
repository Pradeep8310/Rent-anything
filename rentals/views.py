from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Rental
from products.models import Product
from .forms import RentalForm
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from io import BytesIO


@login_required
def create_rental(request, product_id, product_slug):
    product = get_object_or_404(Product, id=product_id, slug=product_slug, available=True)
    
    if request.method == 'POST':
        form = RentalForm(request.POST)
        if form.is_valid():
            rental = form.save(commit=False)
            rental.user = request.user
            rental.product = product
            
            # Calculate total price
            days = (rental.end_date - rental.start_date).days + 1
            rental.total_price = product.price_per_day * days
            
            rental.save()
            
            messages.success(request, 'Rental created successfully!')
            return redirect('my_rentals')
    else:
        form = RentalForm()
    
    return render(request, 'rentals/create.html', {
        'form': form,
        'product': product
    })

@login_required
def my_rentals(request):
    rentals = Rental.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'rentals/my_rentals.html', {'rentals': rentals})

@login_required
def cancel_rental(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    
    if rental.status in ['pending', 'active']:
        rental.status = 'cancelled'
        rental.save()
        messages.success(request, 'Rental cancelled successfully!')
    else:
        messages.error(request, 'Cannot cancel this rental!')
    
    return redirect('my_rentals')

@login_required
def generate_bill(request, rental_id):
    rental = get_object_or_404(Rental, id=rental_id, user=request.user)
    
    # Create a BytesIO buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object, using the BytesIO buffer as its "file"
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Set up the document
    p.setTitle(f"Rental Bill - {rental.generate_bill_id()}")
    
    # Add company logo and information
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, 750, "RentAll Products")
    
    p.setFont("Helvetica", 10)
    p.drawString(50, 735, "123 Rental Street, City, Country")
    p.drawString(50, 720, "Phone: (123) 456-7890")
    p.drawString(50, 705, "Email: info@rentalproducts.com")
    
    # Add bill information
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, 670, f"BILL #{rental.generate_bill_id()}")
    p.drawString(400, 670, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    
    # Add customer information
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 630, "Customer Information")
    p.setFont("Helvetica", 10)
    p.drawString(50, 615, f"Name: {rental.user.get_full_name() or rental.user.username}")
    p.drawString(50, 600, f"Email: {rental.user.email}")
    
    # Add rental information
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 570, "Rental Information")
    p.setFont("Helvetica", 10)
    p.drawString(50, 555, f"Product: {rental.product.name}")
    p.drawString(50, 540, f"Category: {rental.product.category.name}")
    p.drawString(50, 525, f"Rental Period: {rental.start_date} to {rental.end_date}")
    p.drawString(50, 510, f"Duration: {rental.get_rental_days()} days")
    
    # Create table for bill details
    data = [
    ["Item", "Rate (per day)", "Duration", "Amount"],
    [rental.product.name, f"INR{rental.product.price_per_day}", f"{rental.get_rental_days()} days", f"INR{rental.total_price}"],
    ["", "", "Total", f"INR{rental.total_price}"]
]
    
    
    table = Table(data, colWidths=[200, 100, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (3, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (3, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (3, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (3, 0), 10),
        ('BOTTOMPADDING', (0, 0), (3, 0), 12),
        ('BACKGROUND', (0, 1), (3, 1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('SPAN', (0, 2), (1, 2)),
        ('ALIGN', (2, 0), (3, 2), 'RIGHT'),
    ]))
    
    table.wrapOn(p, 400, 200)
    table.drawOn(p, 50, 450)
    
    # Add terms and conditions
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 400, "Terms and Conditions")
    p.setFont("Helvetica", 8)
    p.drawString(50, 385, "1. The rented product must be returned in the same condition as received.")
    p.drawString(50, 375, "2. Late returns will incur additional charges.")
    p.drawString(50, 365, "3. Damage to the product will result in repair/replacement costs.")
    
    # Add footer
    p.setFont("Helvetica-Oblique", 8)
    p.drawString(250, 50, "Thank you for your business!")
    
    # Close the PDF object cleanly
    p.showPage()
    p.save()
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bill_{rental.generate_bill_id()}.pdf"'
    
    return response