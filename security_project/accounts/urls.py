from django.urls import path
from .views import CustomLoginAPIView

urlpatterns = [
    path('login/', CustomLoginAPIView.as_view(), name='api-login'),  # Ensure this matches the API endpoint
]
