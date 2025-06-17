from django.contrib import admin
from django.urls import path , include


# Main URL configuration

urlpatterns = [
    path('account/', include('account.urls')),
    path('home/', include('home.urls'))
    
]
