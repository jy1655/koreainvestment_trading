"""
Korean Investment & Securities API Exceptions
=============================================

Custom exception classes for KIS API client.
"""


class KISError(Exception):
    """Base exception class for KIS API"""
    pass


class KISAuthError(KISError):
    """Authentication related errors"""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class KISAPIError(KISError):
    """API request related errors"""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)


class KISWebSocketError(KISError):
    """WebSocket related errors"""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class KISConfigError(KISError):
    """Configuration related errors"""
    
    def __init__(self, message: str, config_key: str = None):
        self.message = message
        self.config_key = config_key
        super().__init__(self.message)


class KISStrategyError(KISError):
    """Trading strategy related errors"""
    
    def __init__(self, message: str, strategy_name: str = None):
        self.message = message
        self.strategy_name = strategy_name
        super().__init__(self.message)