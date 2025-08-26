"""
Korean Investment & Securities REST API Client
==============================================

Main client for interacting with KIS OpenAPI REST endpoints.
Provides methods for trading, account management, and market data.
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import hashlib

from ..auth.kis_auth import KISAuth
from ..utils.exceptions import KISAPIError, KISAuthError

logger = logging.getLogger(__name__)


class KISClient:
    """
    Korean Investment & Securities REST API Client
    
    Provides comprehensive access to KIS trading and market data APIs.
    """
    
    def __init__(
        self,
        app_key: str,
        app_secret: str,
        account_number: str = "",
        is_mock: bool = True,
        timeout: int = 30
    ):
        """
        Initialize KIS API Client
        
        Args:
            app_key: Application key from KIS
            app_secret: Application secret from KIS
            account_number: Trading account number
            is_mock: Use mock environment (default: True)
            timeout: Request timeout in seconds (default: 30)
        """
        self.auth = KISAuth(app_key, app_secret, is_mock)
        self.account_number = account_number
        self.timeout = timeout
        
        # Session for connection pooling
        self.session = requests.Session()
        
        # API endpoints
        self.base_url = self.auth.base_url
        
    def authenticate(self) -> bool:
        """
        Authenticate with KIS API
        
        Returns:
            bool: True if successful
        """
        return self.auth.authenticate()
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        tr_id: str = "",
        custtype: str = "P"  # P: Personal, B: Business
    ) -> Dict[str, Any]:
        """
        Make authenticated request to KIS API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            tr_id: Transaction ID for the request
            custtype: Customer type (P: Personal, B: Business)
            
        Returns:
            dict: API response data
            
        Raises:
            KISAuthError: If authentication fails
            KISAPIError: If API request fails
        """
        try:
            # Ensure we have valid authentication
            headers = self.auth.get_auth_headers()
            
            # Add common headers
            headers.update({
                "Content-Type": "application/json; charset=utf-8",
                "custtype": custtype
            })
            
            # Add transaction ID if provided
            if tr_id:
                headers["tr_id"] = tr_id
            
            url = f"{self.base_url}{endpoint}"
            
            logger.debug(f"Making {method} request to {url}")
            
            # Make request
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data if data else None,
                params=params,
                timeout=self.timeout
            )
            
            # Handle HTTP errors
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('msg1', f'HTTP {response.status_code}')
                logger.error(f"API request failed: {error_msg}")
                raise KISAPIError(error_msg, response.status_code, error_data)
            
            result = response.json()
            
            # Check for API-level errors
            if result.get('rt_cd') != '0':
                error_msg = result.get('msg1', 'Unknown API error')
                logger.error(f"API returned error: {error_msg}")
                raise KISAPIError(error_msg, response.status_code, result)
            
            return result
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise KISAPIError(f"Request failed: {e}")
        except ValueError as e:
            if "authentication" in str(e).lower():
                raise KISAuthError(str(e))
            raise KISAPIError(f"Response parsing failed: {e}")
    
    def get_balance(self, account_number: Optional[str] = None) -> Dict[str, Any]:
        """
        Get account balance and holdings
        
        Args:
            account_number: Account number (uses default if not provided)
            
        Returns:
            dict: Account balance information
        """
        acct_no = account_number or self.account_number
        if not acct_no:
            raise ValueError("Account number is required")
        
        params = {
            "CANO": acct_no[:8],
            "ACNT_PRDT_CD": acct_no[8:],
            "AFHR_FLPR_YN": "N",  # After hours flag
            "OFL_YN": "",         # Offline flag  
            "INQR_DVSN": "02",    # Inquiry division
            "UNPR_DVSN": "01",    # Unit price division
            "FUND_STTL_ICLD_YN": "N",  # Fund settlement included
            "FNCG_AMT_AUTO_RDPT_YN": "N",  # Financing amount auto redemption
            "PRCS_DVSN": "01",    # Process division
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        
        return self._make_request(
            "GET",
            "/uapi/domestic-stock/v1/trading/inquire-balance",
            params=params,
            tr_id="TTTC8434R"
        )
    
    def buy_stock(
        self,
        symbol: str,
        quantity: int,
        price: Optional[int] = None,
        order_type: str = "01",  # 01: Market, 00: Limit
        account_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Buy stock order
        
        Args:
            symbol: Stock symbol (6-digit code)
            quantity: Number of shares to buy
            price: Limit price (required for limit orders)
            order_type: Order type (01: Market, 00: Limit)
            account_number: Account number (uses default if not provided)
            
        Returns:
            dict: Order result
        """
        return self._place_order(
            symbol=symbol,
            quantity=quantity,
            price=price,
            order_type=order_type,
            side="buy",
            account_number=account_number
        )
    
    def sell_stock(
        self,
        symbol: str,
        quantity: int,
        price: Optional[int] = None,
        order_type: str = "01",  # 01: Market, 00: Limit
        account_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sell stock order
        
        Args:
            symbol: Stock symbol (6-digit code)
            quantity: Number of shares to sell
            price: Limit price (required for limit orders)
            order_type: Order type (01: Market, 00: Limit)  
            account_number: Account number (uses default if not provided)
            
        Returns:
            dict: Order result
        """
        return self._place_order(
            symbol=symbol,
            quantity=quantity,
            price=price,
            order_type=order_type,
            side="sell",
            account_number=account_number
        )
    
    def _place_order(
        self,
        symbol: str,
        quantity: int,
        price: Optional[int],
        order_type: str,
        side: str,
        account_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Internal method to place buy/sell orders
        """
        acct_no = account_number or self.account_number
        if not acct_no:
            raise ValueError("Account number is required")
        
        # Validate order type and price
        if order_type == "00" and price is None:
            raise ValueError("Price is required for limit orders")
        
        data = {
            "CANO": acct_no[:8],
            "ACNT_PRDT_CD": acct_no[8:],
            "PDNO": symbol,
            "ORD_DVSN": order_type,
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price) if price else "0",
        }
        
        if side == "buy":
            endpoint = "/uapi/domestic-stock/v1/trading/order-cash"
            tr_id = "TTTC0802U"
        else:  # sell
            endpoint = "/uapi/domestic-stock/v1/trading/order-cash"  
            tr_id = "TTTC0801U"
        
        return self._make_request(
            "POST",
            endpoint,
            data=data,
            tr_id=tr_id
        )
    
    def get_current_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current stock price
        
        Args:
            symbol: Stock symbol (6-digit code)
            
        Returns:
            dict: Current price information
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",  # Market division
            "FID_INPUT_ISCD": symbol,
        }
        
        return self._make_request(
            "GET",
            "/uapi/domestic-stock/v1/quotations/inquire-price",
            params=params,
            tr_id="FHKST01010100"
        )
    
    def get_order_history(
        self,
        start_date: str,
        end_date: str,
        account_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get order history
        
        Args:
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            account_number: Account number (uses default if not provided)
            
        Returns:
            dict: Order history
        """
        acct_no = account_number or self.account_number
        if not acct_no:
            raise ValueError("Account number is required")
        
        params = {
            "CANO": acct_no[:8],
            "ACNT_PRDT_CD": acct_no[8:],
            "INQR_STRT_DT": start_date,
            "INQR_END_DT": end_date,
            "SLL_BUY_DVSN_CD": "00",  # All orders
            "INQR_DVSN": "00",
            "PDNO": "",
            "CCLD_DVSN": "00",
            "ORD_GNO_BRNO": "",
            "ODNO": "",
            "INQR_DVSN_3": "00",
            "INQR_DVSN_1": "",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        
        return self._make_request(
            "GET", 
            "/uapi/domestic-stock/v1/trading/inquire-daily-ccld",
            params=params,
            tr_id="TTTC8001R"
        )
    
    def cancel_order(self, order_number: str, account_number: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel order
        
        Args:
            order_number: Order number to cancel
            account_number: Account number (uses default if not provided)
            
        Returns:
            dict: Cancellation result
        """
        acct_no = account_number or self.account_number
        if not acct_no:
            raise ValueError("Account number is required")
        
        data = {
            "CANO": acct_no[:8],
            "ACNT_PRDT_CD": acct_no[8:],
            "KRX_FWDG_ORD_ORGNO": "",
            "ORGN_ODNO": order_number,
            "ORD_DVSN": "00",
            "RVSE_CNCL_DVSN_CD": "02",  # Cancel
            "ORD_QTY": "0",
            "ORD_UNPR": "0",
            "QTY_ALL_ORD_YN": "Y"  # Cancel all quantity
        }
        
        return self._make_request(
            "POST",
            "/uapi/domestic-stock/v1/trading/order-rvsecncl",
            data=data,
            tr_id="TTTC0803U"
        )
    
    def __del__(self):
        """Clean up resources"""
        if hasattr(self, 'session'):
            self.session.close()