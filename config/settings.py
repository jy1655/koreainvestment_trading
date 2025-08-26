"""
Korean Investment & Securities Trading Configuration
===================================================

Configuration settings and environment management.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class APIConfig:
    """API configuration settings"""
    app_key: str
    app_secret: str
    account_number: str = ""
    is_mock: bool = True
    timeout: int = 30
    max_retries: int = 3
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.app_key or not self.app_secret:
            raise ValueError("app_key and app_secret are required")


@dataclass  
class WebSocketConfig:
    """WebSocket configuration settings"""
    ping_interval: int = 30
    max_reconnect_attempts: int = 5
    reconnect_delay: int = 5
    message_timeout: int = 60


@dataclass
class TradingConfig:
    """Trading strategy configuration"""
    max_position_size: float = 0.1  # 10% of portfolio per position
    stop_loss_pct: float = -0.05    # 5% stop loss
    take_profit_pct: float = 0.10   # 10% take profit
    max_daily_loss: float = -0.02   # 2% daily loss limit
    risk_free_rate: float = 0.03    # 3% annual risk-free rate
    
    # Order settings
    default_order_type: str = "01"  # 01: Market, 00: Limit
    min_order_amount: int = 10000   # Minimum order amount in KRW
    
    # Algorithm settings
    lookback_period: int = 20       # Days for technical indicators
    rebalance_frequency: str = "1H" # Rebalancing frequency
    
    def validate(self):
        """Validate trading configuration"""
        if self.max_position_size <= 0 or self.max_position_size > 1:
            raise ValueError("max_position_size must be between 0 and 1")
        if self.stop_loss_pct >= 0:
            raise ValueError("stop_loss_pct must be negative")
        if self.take_profit_pct <= 0:
            raise ValueError("take_profit_pct must be positive")


class Settings:
    """Main settings manager"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize settings
        
        Args:
            config_file: Path to configuration file (optional)
        """
        self.config_file = config_file
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment or config file"""
        # API Configuration
        self.api = APIConfig(
            app_key=os.getenv("KIS_APP_KEY", ""),
            app_secret=os.getenv("KIS_APP_SECRET", ""), 
            account_number=os.getenv("KIS_ACCOUNT_NUMBER", ""),
            is_mock=os.getenv("KIS_MOCK_MODE", "true").lower() == "true",
            timeout=int(os.getenv("KIS_TIMEOUT", "30")),
            max_retries=int(os.getenv("KIS_MAX_RETRIES", "3"))
        )
        
        # WebSocket Configuration
        self.websocket = WebSocketConfig(
            ping_interval=int(os.getenv("KIS_WS_PING_INTERVAL", "30")),
            max_reconnect_attempts=int(os.getenv("KIS_WS_MAX_RECONNECTS", "5")),
            reconnect_delay=int(os.getenv("KIS_WS_RECONNECT_DELAY", "5")),
            message_timeout=int(os.getenv("KIS_WS_MESSAGE_TIMEOUT", "60"))
        )
        
        # Trading Configuration
        self.trading = TradingConfig(
            max_position_size=float(os.getenv("KIS_MAX_POSITION_SIZE", "0.1")),
            stop_loss_pct=float(os.getenv("KIS_STOP_LOSS_PCT", "-0.05")),
            take_profit_pct=float(os.getenv("KIS_TAKE_PROFIT_PCT", "0.10")),
            max_daily_loss=float(os.getenv("KIS_MAX_DAILY_LOSS", "-0.02")),
            risk_free_rate=float(os.getenv("KIS_RISK_FREE_RATE", "0.03")),
            default_order_type=os.getenv("KIS_DEFAULT_ORDER_TYPE", "01"),
            min_order_amount=int(os.getenv("KIS_MIN_ORDER_AMOUNT", "10000")),
            lookback_period=int(os.getenv("KIS_LOOKBACK_PERIOD", "20")),
            rebalance_frequency=os.getenv("KIS_REBALANCE_FREQUENCY", "1H")
        )
        
        # Validate configurations
        self.trading.validate()
        
        # Logging Configuration
        self.logging = {
            "level": os.getenv("KIS_LOG_LEVEL", "INFO"),
            "format": os.getenv("KIS_LOG_FORMAT", 
                              "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            "file": os.getenv("KIS_LOG_FILE", "kis_trading.log"),
            "max_size": int(os.getenv("KIS_LOG_MAX_SIZE", "10485760")),  # 10MB
            "backup_count": int(os.getenv("KIS_LOG_BACKUP_COUNT", "5"))
        }
        
        # Database Configuration (for future use)
        self.database = {
            "url": os.getenv("DATABASE_URL", "sqlite:///kis_trading.db"),
            "echo": os.getenv("DB_ECHO", "false").lower() == "true"
        }
    
    def update_config(self, section: str, **kwargs):
        """
        Update configuration section
        
        Args:
            section: Configuration section name
            **kwargs: Configuration values to update
        """
        if hasattr(self, section):
            config_obj = getattr(self, section)
            for key, value in kwargs.items():
                if hasattr(config_obj, key):
                    setattr(config_obj, key, value)
                    
            # Re-validate if it's trading config
            if section == "trading":
                config_obj.validate()
        else:
            raise ValueError(f"Unknown configuration section: {section}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return {
            "api": self.api.__dict__,
            "websocket": self.websocket.__dict__,
            "trading": self.trading.__dict__,
            "logging": self.logging,
            "database": self.database
        }
    
    @classmethod
    def from_env_file(cls, env_file: str = ".env"):
        """
        Load settings from environment file
        
        Args:
            env_file: Path to environment file
            
        Returns:
            Settings: Configured settings instance
        """
        env_path = Path(env_file)
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
        
        return cls()


# Global settings instance
settings = Settings()