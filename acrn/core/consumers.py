import json
from datetime import datetime

import requests
from asgiref.sync import sync_to_async
from django.db import transaction
from .models import Measurement
import pika
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("notifications_group", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications_group", self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.send(text_data=json.dumps({"message": message}))

    async def send_notification(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))


async def create_notification_sync(message):
    channel_layer = get_channel_layer()

    channel_layer.group_send(
        "notifications_group",
        {
            "type": "send_notification",
            "message": message,
        },
    )

device_data = {}


def calculate_hourly_average(device_key, hour):
    if device_key in device_data and device_data[device_key]['count'] > 0:
        hourly_average = device_data[device_key]['cumulative_value'] / device_data[device_key]['count']

        devices_url = f"http://rrc2:8001/api/smartdevices/" + str(device_key)
        response = requests.get(devices_url, verify=False)

        device = response.json()
        consumption = device.get('maximum_hourly_energy_consumption')

        device_data[device_key]['cumulative_value'] = 0
        device_data[device_key]['count'] = 0

        start_hour = hour
        end_hour = start_hour + 1

        Measurement.objects.create(
            device_id=device_key,
            hourly_average=hourly_average,
            start_hour=hour,
            end_hour=hour + 1
        )

        if consumption is not None and hourly_average > float(consumption):
            # await create_notification_sync("WARNING!")
            print(f"WARNING! Device {device_key} above limit!")

        print(f"Device {device_key}, Hourly Average: {hourly_average}, Start Hour: {start_hour}, End Hour: {end_hour}")


def process_measurement(ch, method, properties, body):
    try:
        measurement_data = json.loads(body)
        print("Received measurement data:")
        print(measurement_data)

        timestamp_str = measurement_data['timestamp']
        device_key = measurement_data['device_id']

        timestamp_datetime = datetime.utcfromtimestamp(int(timestamp_str) / 1000)
        hour = timestamp_datetime.hour

        if device_key not in device_data:
            device_data[device_key] = {
                'cumulative_value': 0,
                'count': 0,
            }

        device_data[device_key]['cumulative_value'] += measurement_data['measurement_value']
        device_data[device_key]['count'] += 1

        current_hour = str(hour)
        if device_data[device_key].get('last_hour') is None:
            device_data[device_key]['last_hour'] = current_hour

        if current_hour != device_data[device_key]['last_hour']:
            calculate_hourly_average(device_key, hour)
            device_data[device_key]['last_hour'] = current_hour

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing measurement: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)


def start_message_consumer():
    rabbitmq_params = pika.ConnectionParameters(
        host='shrimp-01.rmq.cloudamqp.com',
        port=5672,
        virtual_host='zouvoihi',
        credentials=pika.PlainCredentials(
            username='zouvoihi',
            password='4pmASno_GCBW2BSQ2OYOhOnD315zNNnW',
        ),
    )

    connection = pika.BlockingConnection(rabbitmq_params)
    channel = connection.channel()
    channel.queue_declare(queue='energy_consumption', durable=True)
    channel.basic_consume(queue='energy_consumption', on_message_callback=process_measurement)
    print('Waiting for messages.')
    channel.start_consuming()
