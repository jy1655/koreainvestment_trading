"""
Korean Investment & Securities Trading API Client
================================================

A Python client for automated trading with Korean Investment & Securities OpenAPI.
Supports both REST API and WebSocket for real-time data and algorithmic trading.

Features:
- OAuth2 authentication
- REST API for trading operations
- WebSocket for real-time market data
- Algorithm trading strategies
- Risk management
- Portfolio management

Example:
    >>> from korea_investment_trading import KISClient
    >>> client = KISClient(app_key='your_key', app_secret='your_secret')
    >>> client.authenticate()
    >>> balance = client.get_balance()
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .auth.kis_auth import KISAuth
from .api.kis_client import KISClient
from .websocket.kis_websocket import KISWebSocket

__all__ = [
    'KISAuth',
    'KISClient', 
    'KISWebSocket'
]