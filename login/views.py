from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.contrib.auth import login as login_user
from django.contrib.auth import logout as logout_user


def auth(request):
    return redirect('auth/login')


def login(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login_user(request, user)
                return redirect('/')
        return render(request, 'auth/login.html', {"login_failed": True})
    return render(request, 'auth/login.html', {"login_failed": False})


def logout(request):
    if not request.user.is_authenticated:
        return redirect('/')

    return render(request, "auth/logout.html")


def instant_logout(request):
    if request.user.is_authenticated:
        logout_user(request)

    return redirect('/')
