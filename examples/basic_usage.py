"""
Korean Investment & Securities API - Basic Usage Examples
========================================================

Basic examples for authentication, account info, and simple trading.
"""

import asyncio
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import KIS modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from korea_investment_trading import KISAuth, KISClient, KISWebSocket
from config.settings import settings


def example_authentication():
    """Example: Basic authentication"""
    print("=== Authentication Example ===")
    
    # Initialize authentication
    auth = KISAuth(
        app_key=settings.api.app_key,
        app_secret=settings.api.app_secret,
        is_mock=True  # Use mock environment for testing
    )
    
    # Authenticate
    success = auth.authenticate()
    if success:
        print("✅ Authentication successful")
        print(f"Token expires at: {auth.expires_at}")
    else:
        print("❌ Authentication failed")
        return None
    
    return auth


def example_account_info():
    """Example: Get account information"""
    print("\n=== Account Information Example ===")
    
    # Initialize client
    client = KISClient(
        app_key=settings.api.app_key,
        app_secret=settings.api.app_secret,
        account_number=settings.api.account_number,
        is_mock=True
    )
    
    # Authenticate
    if not client.authenticate():
        print("❌ Authentication failed")
        return
    
    try:
        # Get account balance
        balance = client.get_balance()
        
        print("✅ Account balance retrieved:")
        print(f"Total evaluation amount: {balance['output2'][0]['tot_evlu_amt']} KRW")
        print(f"Available cash: {balance['output2'][0]['dnca_tot_amt']} KRW")
        print(f"Total profit/loss: {balance['output2'][0]['evlu_pfls_smtl_amt']} KRW")
        
    except Exception as e:
        print(f"❌ Failed to get balance: {e}")


def example_market_data():
    """Example: Get current market data"""
    print("\n=== Market Data Example ===")
    
    # Initialize client
    client = KISClient(
        app_key=settings.api.app_key,
        app_secret=settings.api.app_secret,
        is_mock=True
    )
    
    # Authenticate
    if not client.authenticate():
        print("❌ Authentication failed")
        return
    
    try:
        # Get current price for Samsung Electronics (005930)
        symbol = "005930"  # Samsung Electronics
        price_data = client.get_current_price(symbol)
        
        print(f"✅ Current price for {symbol}:")
        output = price_data['output']
        print(f"Current price: {output['stck_prpr']} KRW")
        print(f"Change: {output['prdy_vrss']} KRW ({output['prdy_vrss_rate']}%)")
        print(f"Volume: {output['acml_vol']} shares")
        
    except Exception as e:
        print(f"❌ Failed to get market data: {e}")


def example_simple_trading():
    """Example: Simple buy/sell operations"""
    print("\n=== Simple Trading Example ===")
    
    # Initialize client
    client = KISClient(
        app_key=settings.api.app_key,
        app_secret=settings.api.app_secret,
        account_number=settings.api.account_number,
        is_mock=True
    )
    
    # Authenticate
    if not client.authenticate():
        print("❌ Authentication failed")
        return
    
    symbol = "005930"  # Samsung Electronics
    quantity = 1       # 1 share
    
    try:
        # Market buy order
        print(f"Placing market buy order for {quantity} shares of {symbol}")
        buy_result = client.buy_stock(
            symbol=symbol,
            quantity=quantity,
            order_type="01"  # Market order
        )
        
        print("✅ Buy order placed:")
        print(f"Order number: {buy_result['output']['ODNO']}")
        print(f"Order time: {buy_result['output']['ORD_TMD']}")
        
        # Note: In a real scenario, you'd wait for execution before selling
        # This is just for demonstration
        
    except Exception as e:
        print(f"❌ Trading failed: {e}")


async def example_websocket_data():
    """Example: Real-time WebSocket data"""
    print("\n=== WebSocket Real-time Data Example ===")
    
    # Initialize WebSocket client
    ws_client = KISWebSocket(
        app_key=settings.api.app_key,
        app_secret=settings.api.app_secret,
        is_mock=True
    )
    
    # Price update callback
    def on_price_update(data):
        print(f"📈 Price update: {data['symbol']} = {data['price']} KRW "
              f"({data['change']:+} / {data['change_rate']:+.2f}%)")
    
    # Orderbook update callback  
    def on_orderbook_update(data):
        print(f"📊 Orderbook update: {data['symbol']} "
              f"Best Bid: {data['buy_prices'][0]} "
              f"Best Ask: {data['sell_prices'][0]}")
    
    try:
        # Connect to WebSocket
        connected = await ws_client.connect()
        if not connected:
            print("❌ WebSocket connection failed")
            return
        
        print("✅ WebSocket connected")
        
        # Subscribe to real-time price data
        symbols = ["005930", "000660"]  # Samsung Electronics, SK Hynix
        await ws_client.subscribe_price(symbols, on_price_update)
        await ws_client.subscribe_orderbook(symbols, on_orderbook_update)
        
        print(f"📡 Subscribed to real-time data for: {', '.join(symbols)}")
        print("Listening for 30 seconds...")
        
        # Listen for 30 seconds
        await asyncio.sleep(30)
        
        # Disconnect
        await ws_client.disconnect()
        print("✅ WebSocket disconnected")
        
    except Exception as e:
        print(f"❌ WebSocket error: {e}")


def example_order_management():
    """Example: Order history and management"""
    print("\n=== Order Management Example ===")
    
    # Initialize client
    client = KISClient(
        app_key=settings.api.app_key,
        app_secret=settings.api.app_secret,
        account_number=settings.api.account_number,
        is_mock=True
    )
    
    # Authenticate
    if not client.authenticate():
        print("❌ Authentication failed")
        return
    
    try:
        # Get recent order history (last 30 days)
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        
        order_history = client.get_order_history(start_date, end_date)
        
        orders = order_history.get('output1', [])
        print(f"✅ Retrieved {len(orders)} recent orders:")
        
        for i, order in enumerate(orders[:5]):  # Show first 5 orders
            print(f"  {i+1}. {order['pdno']} | {order['ord_qty']} shares | "
                  f"{order['ord_unpr']} KRW | Status: {order['ord_dvsn_name']}")
    
    except Exception as e:
        print(f"❌ Failed to get order history: {e}")


def main():
    """Run all basic examples"""
    print("Korean Investment & Securities API - Basic Usage Examples")
    print("=" * 60)
    
    # Check configuration
    if not settings.api.app_key or not settings.api.app_secret:
        print("❌ Please configure your API credentials in .env file")
        print("Copy .env.example to .env and fill in your credentials")
        return
    
    # Run examples
    auth = example_authentication()
    if not auth:
        return
    
    example_account_info()
    example_market_data()
    example_simple_trading()
    example_order_management()
    
    # Run WebSocket example
    print("\nRunning WebSocket example...")
    asyncio.run(example_websocket_data())
    
    print("\n✅ All examples completed!")


if __name__ == "__main__":
    main()