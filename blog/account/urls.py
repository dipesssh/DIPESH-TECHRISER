from django.urls import path
# Importing the views that handle registration and login logic
from account.views import RegisterView, LoginView



# Defining the URL patterns for the API
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),  # ✅ add name here
    path('login/', LoginView.as_view(), name='login'),           # ✅ add name here
]