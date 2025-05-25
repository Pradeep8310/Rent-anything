from django import forms
from .models import Rental
from datetime import date

class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = ['start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'min': date.today().strftime('%Y-%m-%d')}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'min': date.today().strftime('%Y-%m-%d')}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date > end_date:
                raise forms.ValidationError("End date should be after start date")
            
            if start_date < date.today():
                raise forms.ValidationError("Start date cannot be in the past")
        
        return cleaned_data