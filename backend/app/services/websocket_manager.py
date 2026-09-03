import json
import logging
import asyncio
from typing import Set
from fastapi import WebSocket
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages active WebSocket connections from dashboard clients
    and subscribes to Redis Pub/Sub events for real-time updates.
    """

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self._pubsub_task: asyncio.Task | None = None

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total active connections: {len(self.active_connections)}")

    async def broadcast_json(self, data: dict) -> None:
        """Broadcast JSON message to all connected WebSocket clients."""
        if not self.active_connections:
            return
        
        message_str = json.dumps(data)
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message: {str(e)}")
                disconnected.add(connection)

        for connection in disconnected:
            self.disconnect(connection)

    async def start_pubsub_listener(self, redis_client: aioredis.Redis) -> None:
        """
        Background task listening to Redis Pub/Sub channel and forwarding
        status change events to connected WebSockets.
        """
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(settings.PUBSUB_CHANNEL)
        logger.info(f"Subscribed to Redis Pub/Sub channel: {settings.PUBSUB_CHANNEL}")

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    raw_data = message["data"]
                    try:
                        data = json.loads(raw_data)
                        await self.broadcast_json(data)
                    except json.JSONDecodeError:
                        logger.error(f"Received malformed Pub/Sub JSON message: {raw_data}")
        except asyncio.CancelledError:
            logger.info("Pub/Sub listener task cancelled")
        except Exception as e:
            logger.error(f"Error in Pub/Sub listener: {str(e)}", exc_info=True)
        finally:
            await pubsub.unsubscribe(settings.PUBSUB_CHANNEL)


# Global WebSocketManager instance
ws_manager = WebSocketManager()
