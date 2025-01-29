from django.urls import path
from .views import (
    register_user, login_user, logout_user,
    CarListCreateView, CarDetailView, CarSearchView
)

urlpatterns = [
    # Authentication
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    
    # Car Management
    path('cars/', CarListCreateView.as_view(), name='car-list-create'),
    path('cars/<int:id>/', CarDetailView.as_view(), name='car-detail'),
    
    # Global Search
    path('cars/search/', CarSearchView.as_view(), name='car-search'),
]
