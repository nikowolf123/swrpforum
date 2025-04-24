from django.urls import path
from . import views

urlpatterns = [
    path('', views.topic_list, name='topic_list'),
    path('filter/', views.filter_topics, name='filter_topics'),
    path('topic/<int:pk>/', views.topic_detail, name='topic_detail'),
    path('create/', views.create_topic, name='create_topic'),
    path('edit_topic/<int:topic_id>/', views.edit_topic, name='edit_topic'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-account/', views.manage_account, name='manage_account'),
    path('admin_dashboard/tags/', views.manage_tags, name='manage_tags'),
    path('admin_dashboard/user_lookup/', views.user_lookup, name='user_lookup'),
    path('admin_dashboard/user/<int:user_id>/', views.user_detail, name='user_detail'),
    path('admin_dashboard/user/<int:user_id>/<str:action>/', views.user_action, name='user_action'),
    path('admin_dashboard/user/<int:user_id>/set_timeout/', views.set_timeout, name='set_timeout'),
    path('admin_dashboard/topic/<int:topic_id>/<str:action>/', views.toggle_pin_topic, name='toggle_pin_topic'),
]
