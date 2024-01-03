from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


class User(AbstractUser):
    role = models.CharField(max_length=20, choices=[('admin', 'Admin'), ('client', 'Client')])


class ThreadManager(models.Manager):
    def by_user(self, **kwargs):
        user = kwargs.get('user')
        if not user:
            return self.none()
        lookup = Q(first_person=user) | Q(second_person=user)
        return self.get_queryset().filter(lookup).distinct()


class Thread(models.Model):
    first_person = models.ForeignKey(User, on_delete=models.CASCADE, related_name='threads_as_first_person', null=True,
                                     blank=True)
    second_person = models.ForeignKey(User, on_delete=models.CASCADE, related_name='threads_as_second_person',
                                      null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ThreadManager()

    class Meta:
        unique_together = ['first_person', 'second_person']


class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.CASCADE,
                               related_name='chatmessage_thread')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)