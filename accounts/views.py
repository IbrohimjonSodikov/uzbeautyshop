from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
    


def login_view(request):
    next_url = request.GET.get('next', '/')  # Default to home page if no 'next' param
    if request.method == 'POST':
        # Login logic here
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url)  # Redirect to the original page after login
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html', {'next': next_url})
