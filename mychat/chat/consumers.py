import json
import httpx
from channels.consumer import AsyncConsumer
from urllib.parse import parse_qs
import jwt
from jwt.exceptions import DecodeError, ExpiredSignatureError


def decode_token(token):
    try:
        decoded_data = jwt.decode(jwt=token, key='5ahp8kseKOVB_w', algorithms=["HS256"])
        return decoded_data
    except (DecodeError, ExpiredSignatureError):
        return 0


class ChatConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print('connected', event)

        query_string = parse_qs(self.scope['query_string'].decode())
        token = query_string.get('token', [None])[0]

        user_info = decode_token(token)
        user_id = user_info['user_id']

        user = user_id
        chat_room = f'user_chatroom_{user}'

        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        print('receive', event)
        received_data = json.loads(event['text'])

        msg = received_data.get('message')
        sent_by_id = received_data.get('sent_by')
        send_to_id = received_data.get('send_to')
        thread_id = received_data.get('thread_id')

        if not msg:
            print('Error:: empty message')
            return False

        await self.create_chat_message(thread_id, sent_by_id, msg)

        query_string = parse_qs(self.scope['query_string'].decode())
        token = query_string.get('token', [None])[0]
        user_info = decode_token(token)
        user_id = user_info['user_id']

        user = user_id

        other_user_chat_room = f'user_chatroom_{send_to_id}'

        response = {
            'message': msg,
            'sent_by': user,
            'thread_id': thread_id
        }

        await self.channel_layer.group_send(
            other_user_chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

    async def websocket_disconnect(self, event):
        print('disconnect', event)

    async def chat_message(self, event):
        print('chat_message', event)
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    async def create_chat_message(self, thread_id, user_id, msg):
        async with httpx.AsyncClient() as client:
            data = {'thread_id': thread_id, 'user_id': user_id, 'message': msg}
            response = await client.post('http://rrc1:8000/create_chat_message/', json=data)
            return response.json()
        return None
