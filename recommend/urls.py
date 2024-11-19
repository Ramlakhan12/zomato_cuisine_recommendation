from django.urls import path

from . import views

app_name = "recommends"

urlpatterns = [
    path('home/',views.top_restaurants_view, name="top_restaurants"),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
]