import requests
from django.shortcuts import render

from .models import Thread

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Thread
from .serializers import ThreadSerializer
from rest_framework.exceptions import AuthenticationFailed


class ThreadListView(APIView):
    def get(self, request, *args, **kwargs):

        if request.auth is None:
            raise AuthenticationFailed('No valid token provided')

        user_role = request.auth.payload.get('role', None)

        if user_role not in ['client']:
            raise AuthenticationFailed('Unauthorized role')

        threads = Thread.objects.all()
        serializer = ThreadSerializer(threads, many=True)
        return Response(serializer.data)


class MessagesPage(APIView):
    def get(self, request, *args, **kwargs):
        if request.auth is None:
            raise AuthenticationFailed('No valid token provided')

        user_role = request.auth.payload.get('role', None)
        user_id = request.auth.payload.get('user_id', None)
        if user_id is None:
            raise AuthenticationFailed('User ID not found in token')

        if user_role not in ['client', 'admin']:
            raise AuthenticationFailed('Unauthorized role')

        users_url = 'http://rrc1:8000/users'
        try:
            response = requests.get(users_url)
            users = response.json() if response.status_code == 200 else []
        except requests.RequestException as e:
            print(f"Error fetching users: {e}")
            users = []

        user_dict = {str(user['id']): user['username'] for user in users}

        threads = Thread.objects.by_user(user=user_id).prefetch_related('chatmessage_thread').order_by('timestamp')

        for thread in threads:
            thread.first_person_username = user_dict.get(thread.first_person, 'Unknown')
            thread.second_person_username = user_dict.get(thread.second_person, 'Unknown')

        context = {'Threads': threads}
        return render(request, 'messages.html', context)
