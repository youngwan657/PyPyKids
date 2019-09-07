from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import redirect, render

from list.models import *


def signup(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            custom_user = CustomUser.objects.create(name=user.username)
            custom_user.badges.add(Badge.objects.get(order=0))
            custom_user.save()
            login(request, user)
            return redirect("/")

    context = {
        'form': form,
    }
    return render(request, 'list/signup.html', context)


def signout(request):
    logout(request)
    return redirect("/")


def signin(request):
    context = {}
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                context['login_error'] = 1
        else:
            context['login_error'] = 1

    form = AuthenticationForm()
    context['form'] = form
    return render(request, "list/signin.html", context)

