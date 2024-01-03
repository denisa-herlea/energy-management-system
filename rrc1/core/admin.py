from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Thread, ChatMessage


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'password', 'first_name', 'last_name', 'role']


class ThreadAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_person', 'second_person', 'updated', 'timestamp']


admin.site.register(Thread, ThreadAdmin)


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'thread', 'user', 'message', 'timestamp']


admin.site.register(ChatMessage, ChatMessageAdmin)
