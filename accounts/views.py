from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


def user_signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")

        User.objects.create_user(username=username, password=password)
        return redirect("login")

    return render(request, "accounts/signup.html")


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid credentials")

    return render(request, "accounts/login.html")


def user_logout(request):
    logout(request)
    return redirect("login")
