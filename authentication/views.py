from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
# Create your views here.
def home(request):
    return render(request, "Webpages/Home.html")

def signup(request):

    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        myuser = User.objects.create_user(username, email, password)
        myuser.user_name = username

        myuser.save()

        messages.success(request, "Your Account has been successfuly Created")

        print("I told you so")

        return redirect('login')

        

    return render(request, 'Webpages/Signup.html')

def login(request):

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return render(request, "Webpages/Home.html",{'username':username} )

        else:
            messages.error(request,"Bad Credential!")
            return redirect('home')

    return render(request, 'Webpages/Login.html')