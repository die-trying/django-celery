from django.contrib.auth import authenticate, login
from django.shortcuts import redirect


def hi(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user:
        if user.is_active:
            login(request, user)
            redirect('secret.html')

    redirect('hello')
