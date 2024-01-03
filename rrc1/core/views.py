from datetime import datetime

from django.conf import settings
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
import logging

from .tokens import CustomToken

from .decorators import admin_required, client_required
from .forms import UserForm, UserForm2, DeviceForm
from .models import User, Thread, ChatMessage
from .serializers import UserSerializer, ChatMessageSerializer


class UserAPIView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


def login_page(request):
    return render(request, "login/login.html")


def register(request):
    return render(request, "login/register.html")


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)

                refresh = CustomToken.for_user(user)
                access_token = str(refresh.access_token)

                request.session['access_token'] = access_token
                request.session['refresh_token'] = str(refresh)

                # print(request.session['access_token'])
                # print(request.session['refresh_token'])

                if user.role == 'admin':
                    return redirect('/administration/')
                elif user.role == 'client':
                    return redirect('/client/')

    return render(request, 'login/login.html')


def register_view(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            firstname = form.cleaned_data.get('firstname')
            lastname = form.cleaned_data.get('lastname')
            role = form.cleaned_data.get('role')
            user = authenticate(username=username, password=password)
            if user is None:
                user = User.objects.create_user(username=username, password=password, first_name=firstname,
                                                last_name=lastname, role=role)
                user.is_staff = True
                if user.role == "admin":
                    user.is_superuser = True
                user.save()
                return render(request, 'login/login.html')
    else:
        form = UserForm()
    return render(request, 'login/login.html', {'form': form})


@admin_required
def admin_page_view(request):
    users = User.objects.all()
    devices = []
    access_token = request.session.get('access_token')

    if access_token:
        devices_url = f'http://rrc2:8001/api/smartdevices'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(devices_url, headers=headers, verify=False)

        if response.status_code == 200:
            devices = response.json()
    return render(request, 'admin.html', {'users': users, 'devices': devices})


@client_required
def client_page_view(request):
    mappings = []
    access_token = request.session.get('access_token')

    if access_token:
        devices_url = 'http://rrc2:8001/api/smartdevices'
        headers = {'Authorization': f'Bearer {access_token}'}

        try:
            response = requests.get(devices_url, headers=headers)
            if response.status_code == 200:
                mappings = response.json()
            else:
                logging.error(f"Error fetching data: {response.status_code}")
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")

    return render(request, 'client.html', {'mappings': mappings})


@client_required
def clientdevices(request):
    user_id = request.user.id

    mappings = []
    access_token = request.session.get('access_token')
    if access_token:
        devices_url = f'http://rrc2:8001/api/userdevices/' + str(user_id)
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(devices_url, headers=headers)

        if response.status_code == 200:
            mappings = response.json()

    return render(request, 'clientdevices.html', {'mappings': mappings})


def logout_view(request):
    logout(request)
    return render(request, 'login/login.html')


@admin_required
def add_admin_view(request):
    return render(request, "add_admin.html")


@admin_required
def add_admin_event(request):
    if request.method == 'POST':
        form = UserForm2(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            firstname = form.cleaned_data.get('firstname')
            lastname = form.cleaned_data.get('lastname')
            user = User.objects.create_user(username=username, password=password, first_name=firstname,
                                            last_name=lastname, role='admin')
            user.is_staff = True
            user.is_superuser = True
            user.save()
            return render(request, 'add_admin.html')
    return render(request, 'add_admin.html')


@admin_required
def add_client_event(request):
    if request.method == 'POST':
        form = UserForm2(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            firstname = form.cleaned_data.get('firstname')
            lastname = form.cleaned_data.get('lastname')
            user = User.objects.create_user(username=username, password=password, first_name=firstname,
                                            last_name=lastname, role='client')
            user.save()
            return render(request, 'add_client.html')
    return render(request, 'add_client.html')


@admin_required
def add_device_event(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST)
        if form.is_valid():
            description = form.cleaned_data.get('description')
            address = form.cleaned_data.get('address')
            maximum_hourly_energy_consumption = form.cleaned_data.get('maximum_hourly_energy_consumption')

            device_data = {
                'description': description,
                'address': address,
                'maximum_hourly_energy_consumption': maximum_hourly_energy_consumption,
            }

            access_token = request.session.get('access_token')
            if access_token:
                devices_url = f"http://rrc2:8001/api/smartdevices"
                headers = {'Authorization': f'Bearer {access_token}'}
                response = requests.post(devices_url, data=device_data, headers=headers, verify=False)

                if response.status_code == 201:
                    return render(request, 'add_device.html')
                else:
                    error_message = f'Failed to create the device. Response: {response.status_code} - {response.text}'
                    return HttpResponse(error_message)
    return render(request, "add_device.html")


@admin_required
def add_client_view(request):
    return render(request, "add_client.html")


@admin_required
def add_device_view(request):
    return render(request, "add_device.html")


@admin_required
def delete_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        user.delete()
    users = User.objects.all()
    devices = []

    access_token = request.session.get('access_token')
    if access_token:
        devices_url = f"http://rrc2:8001/api/smartdevices"
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(devices_url, headers=headers, verify=False)

        if response.status_code == 200:
            devices = response.json()
        else:
            devices = []
    return render(request, 'admin.html', {'users': users, 'devices': devices})


@admin_required
def delete_device(request):
    error_message = ""
    if request.method == 'POST':
        device_id = request.POST.get('device_id')

        access_token = request.session.get('access_token')
        if access_token:

            devices_url = f"http://rrc2:8001/api/smartdevices/delete/" + str(device_id)
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.delete(devices_url, headers=headers, verify=False)

            if response.status_code == 204:
                return admin_page_view(request)
            else:
                error_message = f'Failed to delete the device. Response: {response.status_code} - {response.text}'
    return HttpResponse(error_message)


@admin_required
def edit_user_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        return render(request, 'edit_user.html', {'user': user})
    else:
        return HttpResponse("error")


@admin_required
def update(request):
    user = []
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        user.username = request.POST.get('username')
        user.first_name = request.POST.get('firstname')
        user.last_name = request.POST.get('lastname')
        user.role = request.POST.get('role')
        if user.role == 'admin':
            user.is_staff = True
        else:
            user.is_staff = True
        user.save()
    return render(request, 'edit_user.html', {'user': user})


@admin_required
def edit_device_view(request):
    device = []
    if request.method == 'POST':
        device_id = request.POST.get('device_id')

        access_token = request.session.get('access_token')
        if access_token:
            devices_url = f"http://rrc2:8001/api/smartdevices/" + str(device_id)
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(devices_url, headers=headers, verify=False)

            if response.status_code == 200:
                device = response.json()
    return render(request, 'edit_device.html', {'device': device})


@admin_required
def update_device(request):
    if request.method == 'POST':
        device_id = request.POST.get('device_id')
        description = request.POST.get('description')
        address = request.POST.get('address')
        maximum_hourly_energy_consumption = request.POST.get('maximum_hourly_energy_consumption')

        access_token = request.session.get('access_token')
        if access_token:
            device_update_url = f"http://rrc2:8001/api/smartdevices/update/{device_id}/"
            headers = {'Authorization': f'Bearer {access_token}'}

            device_data = {
                'device_id': device_id,
                'description': description,
                'address': address,
                'maximum_hourly_energy_consumption': maximum_hourly_energy_consumption,
            }

            response = requests.put(device_update_url, headers=headers, json=device_data, verify=False)

            if response.status_code == 200:
                return edit_device_view(request)
            else:
                return HttpResponse(f"Failed to update the device: {response.status_code}")
    return HttpResponse("Invalid request method")


@client_required
def charts_view(request):
    user_id = request.user.id
    devices_url = f'http://rrc2:8001/api/userdevices/' + str(user_id)
    response = requests.get(devices_url)

    if response.status_code == 200:
        devices = response.json()
    else:
        devices = []

    selected_date_str = request.GET.get('selectedDate')
    selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date() if selected_date_str else None
    measurement_url = f'http://acrn:8002/measurements'
    response = requests.get(measurement_url)
    if response.status_code == 200:
        measurements = response.json()
        if selected_date:
            measurements = [m for m in measurements if m.get('measurement_date') == str(selected_date)]
    else:
        measurements = []
    return render(request, 'clientcharts.html',
                  {'devices': devices, 'measurements': measurements, 'selected_date': selected_date_str})


@client_required
def calendar(request):
    return render(request, "calendar.html")


def chatv2(request):
    image_url = settings.STATIC_URL + 'images/rolly.jpg'

    if request.user.role == 'client':
        users_to_display = User.objects.filter(role='admin')
    else:
        users_to_display = User.objects.filter(role='client')

    threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
    access_token = request.session.get('access_token')

    context = {
        'Threads': threads,
        'users_to_display': users_to_display,
        'image_url': image_url,
        'access_token': access_token,
    }

    return render(request, "chat/messages.html", context)


class CreateChatMessageView(APIView):
    def post(self, request, *args, **kwargs):

        thread_id = request.data.get('thread_id')
        user_id = request.data.get('user_id')
        message = request.data.get('message')

        try:
            thread = Thread.objects.get(id=thread_id)
            user = User.objects.get(id=user_id)

        except (Thread.DoesNotExist, User.DoesNotExist):
            return Response({"error": "Thread or user not found."}, status=status.HTTP_404_NOT_FOUND)

        chat_message = ChatMessage.objects.create(
            thread=thread,
            user=user,
            message=message
        )

        serializer = ChatMessageSerializer(chat_message)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
