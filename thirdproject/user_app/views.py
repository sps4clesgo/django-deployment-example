from django.shortcuts import render
from user_app.forms import UserForm, UserProfileInfoForm

# Imports for login functionality
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    return render(request, 'user_app/index.html')

@login_required
def special(request):
    return render(request, 'user_app/special.html')

# Decorator to avoid that a user can see the logout without being logged in
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def register(request):
    registered = False
    if request.method == "POST":
        user_form = UserForm(data = request.POST)
        profile_form = UserProfileInfoForm(data = request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            # Hashing the password
            user.set_password(user.password)
            user.save()

            # Not commit to avoid overwriting
            profile = profile_form.save(commit = False)
            # For the OneToOne relationship with user
            profile.user = user

            if 'profile_pic' in request.FILES:
                # request.FILES is acting as a dictionary
                profile.profile_pic = request.FILES['profile_pic']

            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()

    return render(request,
                  'user_app/registration.html',
                  {'user_form' : user_form,
                  'profile_form' : profile_form,
                  'registered' : registered})

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # This authenticates the user automatically
        user = authenticate(username = username, password = password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("ACCOUNT NOT ACTIVE")
        else:
            print("Someone tried to login and failed!")
            print("Username {} and password {}".format(username, password))
            return HttpResponse("Invalid login details supplied!")
    else:
        return render(request, 'user_app/login.html', {})
