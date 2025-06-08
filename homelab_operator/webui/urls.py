from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='index'),
    path('dashboard/', views.dashboard, name='dashboard_default'),
    path('dashboard/<int:homelab_id>', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('confirm', views.confirm, name='confirm'),
    path('cron/<str:api_key>/', views.cron, name='cron'),

    path('wake/<int:server_id>/', views.wake, name='wake'),
    path('shutdown/<int:server_id>/', views.shutdown, name='shutdown'),

    path('create/server/', views.create_server, name='create_server'),
    path('edit/server/<int:server_id>/', views.edit_server, name='edit_server'),
    path('delete/server/<int:server_id>/', views.delete_server, name='delete_server'),

    path('create/service/', views.create_service, name='create_service'),
    path('edit/service/<int:service_id>/', views.edit_service, name='edit_service'),
    path('delete/service/<int:service_id>/', views.delete_service, name='delete_service'),

    path('create/network/', views.create_network, name='create_network'),
    path('edit/network/<int:network_id>/', views.edit_network, name='edit_network'),
    path('delete/network/<int:network_id>/', views.delete_network, name='delete_network'),

    path('create/schedule/', views.create_schedule, name='create_schedule'),
    path('edit/schedule/<int:schedule_id>/', views.edit_schedule, name='edit_schedule'),
    path('delete/schedule/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),

    path('create/shutdown_url/<int:server_id>',
         views.create_shutdown_url, name='create_shutdown_url'),
    path('edit/shutdown_url/<int:shutdown_url_id>/',
         views.edit_shutdown_url, name='edit_shutdown_url'),
    path('delete/shutdown_url/<int:shutdown_url_id>/',
         views.delete_shutdown_url, name='delete_shutdown_url'),
]
