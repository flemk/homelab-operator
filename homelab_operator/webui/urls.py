from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='index'),
    path('dashboard/', views.dashboard, name='dashboard_default'),
    path('dashboard/<int:homelab_id>', views.dashboard, name='dashboard'),
    path('app_state/', views.app_state, name='app_state'),

    path('auto_discover_stream/<int:network_id>/<str:task_id>', views.auto_discover_stream, name='auto_discover_stream'),
    path('auto_discover_results/<int:network_id>/<str:task_id>/', views.auto_discover_results, name='auto_discover_results'),
    path('auto_discover_results/<int:network_id>/', views.auto_discover_results, name='auto_discover_results'),

    path('auto_discover/<int:network_id>/', views.auto_discover, name='auto_discover'),
    path('auto_discover/', views.auto_discover, name='auto_discover'),  # TODO Why extra? Is this even used?

    path('search/', views.search, name='search'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('cron/<str:api_key>/', views.cron, name='cron'),
    path('confirm', views.confirm, name='confirm'),  # No trailing slash: POST endpoint
    path('cron/<str:api_key>/', views.cron, name='cron'),

    path('wake/<int:server_id>/', views.wake, name='wake'),
    path('shutdown/<int:server_id>/', views.shutdown, name='shutdown'),
    path('is_online/<str:api_key>/<int:service_id>/<int:server_id>/', views.is_online,
         name='is_online'),

    path('edit/profile/', views.edit_profile, name='edit_profile'),
    path('notifications/', views.notifications, name='notifications'),

    path('create/homelab/', views.create_homelab, name='create_homelab'),
    path('edit/homelab/<int:homelab_id>/', views.edit_homelab, name='edit_homelab'),
    path('delete/homelab/<int:homelab_id>/', views.delete_homelab, name='delete_homelab'),

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

    path('pwiki/<int:wiki_id>/', views.public_wiki, name='public_wiki'),
    path('create/wiki/<int:homelab_id>/', views.create_wiki, name='create_wiki'),
    path('edit/wiki/<int:wiki_id>/', views.edit_wiki, name='edit_wiki'),
    path('delete/wiki/<int:wiki_id>/', views.delete_wiki, name='delete_wiki'),

    path('maintenance/<int:homelab_id>/', views.maintenance, name='maintenance'),
    path('create/maintenance/<int:homelab_id>/', views.create_maintenance, name='create_maintenance'),
    path('edit/maintenance/<int:maintenance_id>/', views.edit_maintenance, name='edit_maintenance'),

    path('create/report/<int:maintenance_id>/', views.create_report, name='create_report'),
    path('edit/report/<int:report_id>/', views.edit_report, name='edit_report'),

    path('ingress/<int:homelab_id>/', views.ingress, name='ingress_list'),
    path('create/ingress/<int:homelab_id>/', views.create_ingress, name='create_ingress'),
    path('edit/ingress/<int:ingress_id>/', views.edit_ingress, name='edit_ingress'),
    path('delete/ingress/<int:ingress_id>/', views.delete_ingress, name='delete_ingress'),

    path('create/shutdown_url/<int:server_id>/',
         views.create_shutdown_url, name='create_shutdown_url'),
    path('edit/shutdown_url/<int:shutdown_url_id>/',
         views.edit_shutdown_url, name='edit_shutdown_url'),
    path('delete/shutdown_url/<int:shutdown_url_id>/',
         views.delete_shutdown_url, name='delete_shutdown_url'),

     path('create/uptime_statistic/<int:server_id>/',
          views.create_uptime_statistic, name='create_uptime_statistic'),
     path('delete/uptime_statistic/<int:server_id>/',
          views.delete_uptime_statistic, name='delete_uptime_statistic'),
     path('reset/uptime_statistic/<int:server_id>/',
          views.reset_uptime_statistic, name='reset_uptime_statistic'),
]
