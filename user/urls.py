from django.urls import path
from .views import LoginView, RegisterView, UserCredentialView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('user/', UserCredentialView.as_view()),  # <- Add this line
]