import json
import time
import pandas as pd
import pika
import requests


def send_measurement(channel, measurement):
    channel.basic_publish(
        exchange='',
        routing_key='energy_consumption',
        body=json.dumps(measurement),
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )
    print(f"Sent: {measurement}")


def get_existing_device_ids():
    response = requests.get('http://rrc2:8001/api/smartdevices/get_device_ids/')
    existing_device_ids = response.json()
    return existing_device_ids


def publish_device_change(channel, action, device_config):
    change_message = {
        "action": action,
        "device": device_config
    }
    channel.basic_publish(
        exchange='',
        routing_key='device_changes',
        body=json.dumps(change_message),
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )


def simulate_smart_meter():
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
    channel.queue_declare(queue='device_changes', durable=True)

    data = pd.read_csv('sensor.csv', header=None)

    devices = get_existing_device_ids()

    for index, row in data.iterrows():
        timestamp = int((time.time() + int(index) * 600 - 5) * 1000)
        device_id = devices[int(index) % len(devices)]
        measurement_value = row[0]

        measurement = {
            "timestamp": str(timestamp),
            "device_id": device_id,
            "measurement_value": measurement_value
        }

        send_measurement(channel, measurement)
        time.sleep(5)

        updated_devices = get_existing_device_ids()

        for new_device_id in set(updated_devices) - set(devices):
            device_config = {
                "device_id": new_device_id,
            }
            publish_device_change(channel, "add", device_config)

        for removed_device_id in set(devices) - set(updated_devices):
            device_config = {
                "device_id": removed_device_id
            }
            publish_device_change(channel, "remove", device_config)

        devices = updated_devices

    connection.close()


if __name__ == '__main__':
    simulate_smart_meter()

