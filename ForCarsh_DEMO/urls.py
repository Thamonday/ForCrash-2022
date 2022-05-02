from django.urls import path,include
from ForCarsh_DEMO import views

urlpatterns = [
    path('',include('ForCarsh_DEMO.urls')),
    path('index/',views.hello),
    path('LogIn/',views.login),
    path('register/',views.register),
]
