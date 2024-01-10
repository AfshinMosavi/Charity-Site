from django.shortcuts import render
from django.contrib.auth import get_user_model
from accounts.models import User
# Create your views here.

def about_us(request):
    context = {
        'members': get_user_model().objects.all()
    }
    return render(request, 'about_us.html', context)



