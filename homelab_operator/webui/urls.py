from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('wake/<int:server_id>/', views.wake, name='wake'),
    path('edit/server/<int:server_id>/', views.edit_server, name='edit_server'),    
    path('create/server/', views.create_server, name='create_server'),
]