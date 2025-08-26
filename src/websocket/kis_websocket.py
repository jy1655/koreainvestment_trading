"""
Korean Investment & Securities WebSocket Client
==============================================

Real-time market data streaming client for KIS OpenAPI WebSocket services.
Supports real-time price, orderbook, and trading data.
"""

import asyncio
import websockets
import json
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import threading
import time
from enum import Enum

from ..auth.kis_auth import KISAuth
from ..utils.exceptions import KISWebSocketError

logger = logging.getLogger(__name__)


class SubscriptionType(Enum):
    """WebSocket subscription types"""
    REAL_TIME_PRICE = "H0STCNT0"     # Real-time price
    REAL_TIME_ORDERBOOK = "H0STASP0" # Real-time orderbook
    REAL_TIME_EXECUTION = "H0STCNI0" # Real-time execution
    

class KISWebSocket:
    """
    Korean Investment & Securities WebSocket Client
    
    Provides real-time market data streaming capabilities.
    """
    
    # WebSocket endpoints
    PROD_WS_URL = "ws://ops.koreainvestment.com:21000"
    MOCK_WS_URL = "ws://ops.koreainvestment.com:31000"
    
    def __init__(
        self,
        app_key: str,
        app_secret: str,
        is_mock: bool = True,
        ping_interval: int = 30,
        max_reconnect_attempts: int = 5
    ):
        """
        Initialize KIS WebSocket client
        
        Args:
            app_key: Application key from KIS
            app_secret: Application secret from KIS
            is_mock: Use mock environment (default: True)
            ping_interval: Ping interval in seconds (default: 30)
            max_reconnect_attempts: Maximum reconnection attempts (default: 5)
        """
        self.auth = KISAuth(app_key, app_secret, is_mock)
        self.app_key = app_key
        self.app_secret = app_secret
        self.is_mock = is_mock
        self.ping_interval = ping_interval
        self.max_reconnect_attempts = max_reconnect_attempts
        
        self.ws_url = self.MOCK_WS_URL if is_mock else self.PROD_WS_URL
        
        # Connection state
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.is_connected = False
        self.reconnect_count = 0
        
        # Subscription management
        self.subscriptions: Dict[str, Dict] = {}
        self.callbacks: Dict[str, Callable] = {}
        
        # Background tasks
        self.receive_task: Optional[asyncio.Task] = None
        self.ping_task: Optional[asyncio.Task] = None
        
        # Threading
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.thread: Optional[threading.Thread] = None
        
    async def connect(self) -> bool:
        """
        Connect to KIS WebSocket server
        
        Returns:
            bool: True if connection successful
        """
        try:
            # Ensure we have valid authentication
            if not self.auth.is_token_valid():
                logger.info("Authenticating for WebSocket connection")
                if not self.auth.authenticate():
                    raise KISWebSocketError("Authentication failed")
            
            logger.info(f"Connecting to WebSocket: {self.ws_url}")
            
            # Connect to WebSocket
            self.websocket = await websockets.connect(
                self.ws_url,
                ping_interval=None,  # We'll handle pings manually
                close_timeout=10
            )
            
            self.is_connected = True
            self.reconnect_count = 0
            
            logger.info("WebSocket connected successfully")
            
            # Start background tasks
            self.receive_task = asyncio.create_task(self._receive_messages())
            self.ping_task = asyncio.create_task(self._ping_loop())
            
            return True
            
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from WebSocket server"""
        logger.info("Disconnecting WebSocket")
        
        self.is_connected = False
        
        # Cancel background tasks
        if self.receive_task and not self.receive_task.done():
            self.receive_task.cancel()
        if self.ping_task and not self.ping_task.done():
            self.ping_task.cancel()
        
        # Close WebSocket connection
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        logger.info("WebSocket disconnected")
    
    async def subscribe_price(
        self,
        symbols: List[str],
        callback: Optional[Callable] = None
    ) -> bool:
        """
        Subscribe to real-time price data
        
        Args:
            symbols: List of stock symbols (6-digit codes)
            callback: Callback function for price updates
            
        Returns:
            bool: True if subscription successful
        """
        return await self._subscribe(
            SubscriptionType.REAL_TIME_PRICE,
            symbols,
            callback
        )
    
    async def subscribe_orderbook(
        self,
        symbols: List[str],
        callback: Optional[Callable] = None
    ) -> bool:
        """
        Subscribe to real-time orderbook data
        
        Args:
            symbols: List of stock symbols (6-digit codes)  
            callback: Callback function for orderbook updates
            
        Returns:
            bool: True if subscription successful
        """
        return await self._subscribe(
            SubscriptionType.REAL_TIME_ORDERBOOK,
            symbols,
            callback
        )
    
    async def _subscribe(
        self,
        sub_type: SubscriptionType,
        symbols: List[str],
        callback: Optional[Callable] = None
    ) -> bool:
        """
        Internal method to handle subscriptions
        """
        if not self.is_connected or not self.websocket:
            raise KISWebSocketError("WebSocket not connected")
        
        try:
            for symbol in symbols:
                # Create subscription message
                sub_data = {
                    "header": {
                        "approval_key": self.auth.access_token,
                        "custtype": "P",
                        "tr_type": "1",  # Subscribe
                        "content-type": "utf-8"
                    },
                    "body": {
                        "input": {
                            "tr_id": sub_type.value,
                            "tr_key": symbol
                        }
                    }
                }
                
                # Send subscription request
                await self.websocket.send(json.dumps(sub_data))
                
                # Store subscription info
                sub_key = f"{sub_type.value}_{symbol}"
                self.subscriptions[sub_key] = {
                    "type": sub_type,
                    "symbol": symbol,
                    "callback": callback
                }
                
                if callback:
                    self.callbacks[sub_key] = callback
                
                logger.info(f"Subscribed to {sub_type.value} for {symbol}")
        
            return True
            
        except Exception as e:
            logger.error(f"Subscription failed: {e}")
            return False
    
    async def unsubscribe(self, sub_type: SubscriptionType, symbols: List[str]) -> bool:
        """
        Unsubscribe from real-time data
        
        Args:
            sub_type: Subscription type to unsubscribe from
            symbols: List of symbols to unsubscribe
            
        Returns:
            bool: True if unsubscription successful
        """
        if not self.is_connected or not self.websocket:
            raise KISWebSocketError("WebSocket not connected")
        
        try:
            for symbol in symbols:
                # Create unsubscription message
                unsub_data = {
                    "header": {
                        "approval_key": self.auth.access_token,
                        "custtype": "P", 
                        "tr_type": "2",  # Unsubscribe
                        "content-type": "utf-8"
                    },
                    "body": {
                        "input": {
                            "tr_id": sub_type.value,
                            "tr_key": symbol
                        }
                    }
                }
                
                # Send unsubscription request
                await self.websocket.send(json.dumps(unsub_data))
                
                # Remove from subscriptions
                sub_key = f"{sub_type.value}_{symbol}"
                self.subscriptions.pop(sub_key, None)
                self.callbacks.pop(sub_key, None)
                
                logger.info(f"Unsubscribed from {sub_type.value} for {symbol}")
            
            return True
            
        except Exception as e:
            logger.error(f"Unsubscription failed: {e}")
            return False
    
    async def _receive_messages(self):
        """Background task to receive and process WebSocket messages"""
        try:
            while self.is_connected and self.websocket:
                try:
                    # Receive message with timeout
                    message = await asyncio.wait_for(
                        self.websocket.recv(), 
                        timeout=60  # 60 second timeout
                    )
                    
                    # Process message
                    await self._process_message(message)
                    
                except asyncio.TimeoutError:
                    logger.warning("WebSocket receive timeout")
                    continue
                except websockets.exceptions.ConnectionClosed:
                    logger.warning("WebSocket connection closed")
                    break
                
        except Exception as e:
            logger.error(f"Message receiving error: {e}")
        finally:
            if self.is_connected:
                # Connection lost, attempt reconnect
                await self._reconnect()
    
    async def _process_message(self, message: str):
        """Process received WebSocket message"""
        try:
            data = json.loads(message)
            
            # Extract header and body
            header = data.get("header", {})
            body = data.get("body", {})
            
            tr_id = header.get("tr_id", "")
            tr_key = body.get("tr_key", "")
            
            # Find matching subscription and callback
            sub_key = f"{tr_id}_{tr_key}"
            
            if sub_key in self.callbacks:
                callback = self.callbacks[sub_key]
                
                # Call callback with processed data
                if callback:
                    try:
                        # Parse market data based on type
                        parsed_data = self._parse_market_data(tr_id, body)
                        callback(parsed_data)
                    except Exception as e:
                        logger.error(f"Callback execution failed: {e}")
            else:
                logger.debug(f"No callback for {sub_key}")
                
        except Exception as e:
            logger.error(f"Message processing error: {e}")
    
    def _parse_market_data(self, tr_id: str, body: Dict) -> Dict[str, Any]:
        """Parse market data based on TR ID"""
        
        if tr_id == "H0STCNT0":  # Real-time price
            return {
                "type": "price",
                "symbol": body.get("mksc_shrn_iscd", ""),
                "price": int(body.get("stck_prpr", 0)),
                "change": int(body.get("prdy_vrss", 0)),
                "change_rate": float(body.get("prdy_vrss_rate", 0)),
                "volume": int(body.get("acml_vol", 0)),
                "timestamp": datetime.now()
            }
        elif tr_id == "H0STASP0":  # Real-time orderbook
            return {
                "type": "orderbook", 
                "symbol": body.get("mksc_shrn_iscd", ""),
                "buy_prices": [int(body.get(f"bidp{i}", 0)) for i in range(1, 11)],
                "buy_volumes": [int(body.get(f"bidp_rsqn{i}", 0)) for i in range(1, 11)],
                "sell_prices": [int(body.get(f"askp{i}", 0)) for i in range(1, 11)],
                "sell_volumes": [int(body.get(f"askp_rsqn{i}", 0)) for i in range(1, 11)],
                "timestamp": datetime.now()
            }
        else:
            return {
                "type": "unknown",
                "raw_data": body,
                "timestamp": datetime.now()
            }
    
    async def _ping_loop(self):
        """Background task to send periodic ping messages"""
        try:
            while self.is_connected and self.websocket:
                await asyncio.sleep(self.ping_interval)
                
                if self.websocket:
                    try:
                        await self.websocket.ping()
                        logger.debug("WebSocket ping sent")
                    except Exception as e:
                        logger.warning(f"WebSocket ping failed: {e}")
                        break
                        
        except Exception as e:
            logger.error(f"Ping loop error: {e}")
    
    async def _reconnect(self):
        """Attempt to reconnect to WebSocket"""
        if self.reconnect_count >= self.max_reconnect_attempts:
            logger.error("Maximum reconnection attempts exceeded")
            return
        
        self.reconnect_count += 1
        logger.info(f"Attempting reconnection {self.reconnect_count}/{self.max_reconnect_attempts}")
        
        # Wait before reconnecting
        await asyncio.sleep(min(5 * self.reconnect_count, 60))
        
        # Attempt reconnection
        if await self.connect():
            # Restore subscriptions
            for sub_key, sub_info in self.subscriptions.items():
                await self._subscribe(
                    sub_info["type"],
                    [sub_info["symbol"]],
                    sub_info.get("callback")
                )
    
    def start_background_thread(self):
        """Start WebSocket in background thread"""
        if self.thread and self.thread.is_alive():
            logger.warning("Background thread already running")
            return
        
        def run_websocket():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.connect())
            self.loop.run_forever()
        
        self.thread = threading.Thread(target=run_websocket, daemon=True)
        self.thread.start()
        
        # Wait for connection
        time.sleep(2)
        
        logger.info("WebSocket started in background thread")
    
    def stop_background_thread(self):
        """Stop background WebSocket thread"""
        if self.loop and self.loop.is_running():
            # Schedule disconnect in the loop
            asyncio.run_coroutine_threadsafe(self.disconnect(), self.loop)
            
            # Stop the loop
            self.loop.call_soon_threadsafe(self.loop.stop)
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=10)
        
        logger.info("WebSocket background thread stopped")