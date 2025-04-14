from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('wake/<int:server_id>/', views.wake, name='wake'),
    path('shutdown/<int:server_id>/', views.shutdown, name='shutdown'),
    path('create/server/', views.create_server, name='create_server'),
    path('create/service/', views.create_service, name='create_service'),
    path('create/network/', views.create_network, name='create_network'),
    path('edit/server/<int:server_id>/', views.edit_server, name='edit_server'),
    #path('edit/service/<int:service_id>/', views.edit_service, name='edit_service'),
    path('edit/network/<int:network_id>/', views.edit_network, name='edit_network'),
]