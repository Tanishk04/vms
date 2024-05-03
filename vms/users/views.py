from django.contrib import messages, auth
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import NoReverseMatch
from types import NoneType
from .forms import LoginForm, RegisterForm


from rest_framework_simplejwt.tokens import RefreshToken

def sign_in(request):
    if request.method == "GET":
        next_url = request.GET.get("next")
        if request.user.is_authenticated:
            return redirect("account")
        form = LoginForm()
        return render(request, "users/login.html", {"form": form, "next": next_url})
    elif request.method == "POST":
        form = LoginForm(request.POST)
        next_url = request.POST.get("next")
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(username=username, password=password)
            if user:
                login(request, user)

                #  Generate JWT token
                refresh = RefreshToken.for_user(user)
                token = str(refresh.access_token)

                # Store token in session
                request.session['jwt_token'] = token

                try:
                    return redirect(next_url)
                except NoReverseMatch:
                    return redirect("home")
            else:
                messages.error(request, "Invalid username or password")
                return redirect("login")

def register(request):
    if request.method == "GET":
        form = RegisterForm()
        return render(request, "users/register.html", {"form": form})
    elif request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            email = form.cleaned_data["email"]

            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
                return redirect("register")

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists")
                return redirect("register")

            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()
            login(request, user)
            messages.success(request, "Account created successfully")
            return redirect("home")


@login_required(login_url="login")
def account(request):
    return render(request, "users/profile.html", {"user": request.user})


def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
        return redirect("home")


def home(request):
    return render(request, "users/home.html", {"user": request.user})
