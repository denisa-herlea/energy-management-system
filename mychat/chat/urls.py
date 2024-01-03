from django.urls import path
from . import views
from .views import ThreadListView

urlpatterns = [
    path('', views.MessagesPage.as_view()),

    path('api/threads/', ThreadListView.as_view(), name='thread-list'),
]
