from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, ProfileUpdateForm

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}. You can now log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    rentals = request.user.rental_set.all().order_by('-created_at')
    return render(request, 'accounts/profile.html', {'rentals': rentals})

@login_required
def update_profile(request):
    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    return render(request, 'accounts/update_profile.html', {'form': profile_form})