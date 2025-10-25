from backend.services.websocket_service import WebSocketService
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer
import json
import logging

"""
WebSocket Router for Real-Time Data Streaming
Handles WebSocket connections and real-time data broadcasting
"""

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws", tags=["websocket"])
security = HTTPBearer()

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket, user_id: str | None = None):
    """
    WebSocket endpoint for real-time data streaming
    """
    try:
        # Accept the WebSocket connection
        await websocket.accept()

        # If no user_id provided, try to get from query params
        if not user_id:
            # In a real implementation, you'd validate the user_id
            # For now, we'll use a default or extract from token
            user_id = "anonymous"

        logger.info(f"WebSocket connection attempt for user: {user_id}")

        # Connect user to WebSocket service
        await WebSocketService.connect_user(websocket, user_id)

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle the message
                await WebSocketService.handle_user_message(user_id, message)

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user: {user_id}")
        except Exception as e:
            logger.error(f"WebSocket error for user {user_id}: {e}")
        finally:
            # Disconnect user from WebSocket service
            await WebSocketService.disconnect_user(user_id)

    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass

@router.websocket("/portfolio/{user_id}")
async def portfolio_websocket(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint specifically for portfolio updates
    """
    try:
        await websocket.accept()
        logger.info(f"Portfolio WebSocket connection for user: {user_id}")

        # Connect user to WebSocket service
        await WebSocketService.connect_user(websocket, user_id)

        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle portfolio-specific messages
                await WebSocketService.handle_user_message(user_id, message)

        except WebSocketDisconnect:
            logger.info(f"Portfolio WebSocket disconnected for user: {user_id}")
        except Exception as e:
            logger.error(f"Portfolio WebSocket error for user {user_id}: {e}")
        finally:
            await WebSocketService.disconnect_user(user_id)

    except Exception as e:
        logger.error(f"Portfolio WebSocket connection error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass

@router.websocket("/market-data")
async def market_data_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for market data streaming
    """
    try:
        await websocket.accept()
        logger.info("Market data WebSocket connection")

        # For market data, we might not need user authentication
        # but we'll use a generic user_id
        user_id = "market_data_subscriber"

        await WebSocketService.connect_user(websocket, user_id)

        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle market data messages
                await WebSocketService.handle_user_message(user_id, message)

        except WebSocketDisconnect:
            logger.info("Market data WebSocket disconnected")
        except Exception as e:
            logger.error(f"Market data WebSocket error: {e}")
        finally:
            await WebSocketService.disconnect_user(user_id)

    except Exception as e:
        logger.error(f"Market data WebSocket connection error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass
