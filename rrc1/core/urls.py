from django.urls import path, include
from . import views
from .views import UserAPIView, CreateChatMessageView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [

    path('users', UserAPIView.as_view()),
    path('', views.login_page, name="login_page"),
    path('login', views.login_page, name="login_page"),
    path('register', views.register, name="register"),
    path('login_view', views.login_view, name="login_view"),
    path('register_view', views.register_view, name="register_view"),
    path('logout', views.logout_view, name='logout_view'),

    path('administration/', views.admin_page_view, name='administration'),
    path('client/', views.client_page_view, name='client'),
    path('client_devices', views.clientdevices, name='client_devices'),

    path('add_admin', views.add_admin_view, name='add_admin'),
    path('add_admin_event', views.add_admin_event, name='add_admin_event'),
    path('add_client', views.add_client_view, name='add_client'),
    path('add_client_event', views.add_client_event, name='add_client_event'),
    path('add_device', views.add_device_view, name='add_device'),
    path('add_device_event', views.add_device_event, name='add_device_event'),

    path('delete_user', views.delete_user, name='delete_user'),
    path('delete_device', views.delete_device, name='delete_device'),

    path('edit_user_view', views.edit_user_view, name='edit_user_view'),
    path('edit_device_view', views.edit_device_view, name='edit_device_view'),
    path('update', views.update, name='update'),
    path('update_device', views.update_device, name='update_device'),

    path('view_charts', views.charts_view, name='charts_view'),
    path('calendar', views.calendar, name='calendar'),

    path('chatv2', views.chatv2, name='chatv2'),
    path('create_chat_message/', CreateChatMessageView.as_view(), name='create_chat_message'),

    path("token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),

]
