from django.shortcuts import render, redirect


def index(request):
    return render(request, 'public/index.html', {"pagename": "status"})


def status(request):
    return redirect('/')