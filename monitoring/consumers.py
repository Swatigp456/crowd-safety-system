import json
from channels.generic.websocket import AsyncWebsocketConsumer

class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'alerts'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', '')
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'alert_message',
                'message': message
            }
        )
    
    # Receive message from room group
    async def alert_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'title': 'New Alert',
            'message': message
        }))

class CrowdConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'crowd_data'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        # Broadcast to all connected clients
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'crowd_update',
                'data': text_data_json
            }
        )
    
    async def crowd_update(self, event):
        data = event['data']
        
        await self.send(text_data=json.dumps({
            'data': data
        }))