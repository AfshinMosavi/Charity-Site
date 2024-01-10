from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import UserRegistration, LogoutAPIView

urlpatterns = [
    path('login/', obtain_auth_token, name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('register/', UserRegistration.as_view(), name='register'),
]




