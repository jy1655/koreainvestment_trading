"""
Korean Investment & Securities Authentication Module
==================================================

Handles OAuth2 authentication for KIS OpenAPI.
Manages access tokens, refresh tokens, and authentication state.
"""

import requests
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class KISAuth:
    """
    Korean Investment & Securities Authentication Client
    
    Handles OAuth2 token management for KIS OpenAPI access.
    """
    
    # API Endpoints
    PROD_BASE_URL = "https://openapi.koreainvestment.com:9443"
    MOCK_BASE_URL = "https://openapimock.koreainvestment.com:9443"
    
    TOKEN_ENDPOINT = "/oauth2/tokenP"
    REVOKE_ENDPOINT = "/oauth2/revokeP"
    
    def __init__(
        self,
        app_key: str,
        app_secret: str,
        is_mock: bool = True,
        auto_refresh: bool = True
    ):
        """
        Initialize KIS Authentication client
        
        Args:
            app_key: Application key from KIS
            app_secret: Application secret from KIS  
            is_mock: Use mock environment (default: True)
            auto_refresh: Automatically refresh expired tokens (default: True)
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.is_mock = is_mock
        self.auto_refresh = auto_refresh
        
        self.base_url = self.MOCK_BASE_URL if is_mock else self.PROD_BASE_URL
        
        # Token storage
        self.access_token: Optional[str] = None
        self.token_type: Optional[str] = None
        self.expires_at: Optional[datetime] = None
        
        # Session for connection pooling
        self.session = requests.Session()
        
    def authenticate(self) -> bool:
        """
        Authenticate with KIS OpenAPI and obtain access token
        
        Returns:
            bool: True if authentication successful, False otherwise
            
        Raises:
            requests.RequestException: If API request fails
            ValueError: If invalid credentials or response
        """
        try:
            url = f"{self.base_url}{self.TOKEN_ENDPOINT}"
            
            headers = {
                "Content-Type": "application/json; charset=utf-8"
            }
            
            data = {
                "grant_type": "client_credentials",
                "appkey": self.app_key,
                "appsecret": self.app_secret
            }
            
            logger.info(f"Attempting authentication with KIS API at {url}")
            
            response = self.session.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Validate response
            if not token_data.get("access_token"):
                logger.error(f"No access token in response: {token_data}")
                return False
                
            # Store token information
            self.access_token = token_data["access_token"]
            self.token_type = token_data.get("token_type", "Bearer")
            
            # Calculate expiry time (default 24 hours if not provided)
            expires_in = token_data.get("expires_in", 86400)  # 24 hours
            self.expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            logger.info("Authentication successful")
            logger.debug(f"Token expires at: {self.expires_at}")
            
            return True
            
        except requests.RequestException as e:
            logger.error(f"Authentication request failed: {e}")
            return False
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid authentication response: {e}")
            return False
    
    def is_token_valid(self) -> bool:
        """
        Check if current access token is valid and not expired
        
        Returns:
            bool: True if token is valid, False otherwise
        """
        if not self.access_token or not self.expires_at:
            return False
            
        # Check if token expires within next 5 minutes
        buffer_time = timedelta(minutes=5)
        return datetime.now() < (self.expires_at - buffer_time)
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authorization headers for API requests
        
        Returns:
            dict: Headers with authorization token
            
        Raises:
            ValueError: If no valid token available
        """
        if self.auto_refresh and not self.is_token_valid():
            logger.info("Token expired or invalid, attempting refresh")
            if not self.authenticate():
                raise ValueError("Failed to refresh authentication token")
        
        if not self.access_token:
            raise ValueError("No valid access token available")
            
        return {
            "Authorization": f"{self.token_type} {self.access_token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
    
    def revoke_token(self) -> bool:
        """
        Revoke current access token
        
        Returns:
            bool: True if revocation successful, False otherwise
        """
        if not self.access_token:
            logger.warning("No token to revoke")
            return True
            
        try:
            url = f"{self.base_url}{self.REVOKE_ENDPOINT}"
            
            headers = {
                "Content-Type": "application/json; charset=utf-8"
            }
            
            data = {
                "appkey": self.app_key,
                "appsecret": self.app_secret,
                "token": self.access_token
            }
            
            response = self.session.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Clear stored token data
            self.access_token = None
            self.token_type = None
            self.expires_at = None
            
            logger.info("Token revoked successfully")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Token revocation failed: {e}")
            return False
    
    def __del__(self):
        """Clean up resources"""
        if hasattr(self, 'session'):
            self.session.close()