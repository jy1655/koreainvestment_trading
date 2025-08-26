# Korean Investment & Securities Trading API Client

Python client for automated trading with Korean Investment & Securities OpenAPI. Supports both REST API and WebSocket for real-time data and algorithmic trading.

## Features

- 🔐 **OAuth2 Authentication** - Secure token-based authentication
- 📊 **REST API Client** - Complete trading and account management
- ⚡ **WebSocket Support** - Real-time market data streaming
- 🤖 **Algorithm Trading** - Built-in strategy framework
- ⚠️ **Risk Management** - Position sizing and stop-loss protection
- 📈 **Technical Analysis** - Moving averages and indicators
- 🛡️ **Mock Trading** - Safe testing environment

## Quick Start

### 1. Installation

```bash
git clone <repository-url>
cd korea_investment_trading
pip install -r requirements.txt
```

### 2. Configuration

Copy the environment template:
```bash
cp .env.example .env
```

Edit `.env` with your KIS API credentials:
```env
KIS_APP_KEY=your_app_key_here
KIS_APP_SECRET=your_app_secret_here
KIS_ACCOUNT_NUMBER=your_account_number_here
KIS_MOCK_MODE=true  # Set to false for production
```

### 3. Basic Usage

```python
import os
from korea_investment_trading import KISClient

# Initialize client with environment variables (SECURE)
client = KISClient(
    app_key=os.getenv("KIS_APP_KEY"),
    app_secret=os.getenv("KIS_APP_SECRET"), 
    account_number=os.getenv("KIS_ACCOUNT_NUMBER"),
    is_mock=True  # Safe testing mode
)

# Alternative: Use settings module
from config.settings import settings
client = KISClient(
    app_key=settings.api.app_key,
    app_secret=settings.api.app_secret,
    account_number=settings.api.account_number,
    is_mock=settings.api.is_mock
)

# Authenticate
client.authenticate()

# Get account balance
balance = client.get_balance()
print(f"Total value: {balance['output2'][0]['tot_evlu_amt']} KRW")

# Get current price
price = client.get_current_price("005930")  # Samsung Electronics
print(f"Samsung price: {price['output']['stck_prpr']} KRW")

# Buy stock (market order)
result = client.buy_stock(
    symbol="005930",
    quantity=1,
    order_type="01"  # Market order
)
```

### 4. WebSocket Real-time Data

```python
import asyncio
import os
from korea_investment_trading import KISWebSocket

async def price_callback(data):
    print(f"Price update: {data['symbol']} = {data['price']} KRW")

# Initialize WebSocket with environment variables (SECURE)
ws = KISWebSocket(
    app_key=os.getenv("KIS_APP_KEY"),
    app_secret=os.getenv("KIS_APP_SECRET"),
    is_mock=True
)

# Connect and subscribe
await ws.connect()
await ws.subscribe_price(["005930", "000660"], price_callback)

# Listen for updates
await asyncio.sleep(60)  # Listen for 1 minute
await ws.disconnect()
```

## Examples

Run the included examples to get started:

### Basic Usage
```bash
python examples/basic_usage.py
```

### Algorithmic Trading
```bash
python examples/algorithmic_trading.py
```

## Architecture

```
korea_investment_trading/
├── src/
│   ├── auth/           # Authentication module
│   ├── api/            # REST API client
│   ├── websocket/      # WebSocket client
│   ├── strategies/     # Trading strategies
│   └── utils/          # Utilities and exceptions
├── config/             # Configuration management
├── examples/           # Usage examples
├── tests/              # Unit tests
└── docs/               # Documentation
```

## API Coverage

### Authentication
- ✅ OAuth2 token management
- ✅ Automatic token refresh
- ✅ Environment switching (mock/production)

### Account Management
- ✅ Account balance inquiry
- ✅ Holdings inquiry
- ✅ Order history
- ✅ Transaction history

### Trading Operations
- ✅ Stock buy/sell orders
- ✅ Market/limit orders
- ✅ Order cancellation
- ✅ Order modification

### Market Data
- ✅ Real-time stock prices
- ✅ Real-time orderbook
- ✅ Current price inquiry
- ✅ Historical data

### WebSocket Streaming
- ✅ Real-time price updates
- ✅ Real-time orderbook
- ✅ Execution notifications
- ✅ Connection management

## Risk Management

The client includes comprehensive risk management features:

- **Position Sizing**: Automatic position sizing based on portfolio percentage
- **Stop Loss**: Configurable stop-loss percentage
- **Take Profit**: Configurable take-profit targets
- **Daily Loss Limit**: Maximum daily loss protection
- **Order Validation**: Minimum order amounts and validations

## Configuration Options

Key configuration parameters:

```python
# Risk Management
KIS_MAX_POSITION_SIZE=0.1    # 10% max per position
KIS_STOP_LOSS_PCT=-0.05      # 5% stop loss
KIS_TAKE_PROFIT_PCT=0.10     # 10% take profit
KIS_MAX_DAILY_LOSS=-0.02     # 2% daily loss limit

# Trading
KIS_DEFAULT_ORDER_TYPE=01    # Market orders
KIS_MIN_ORDER_AMOUNT=10000   # 10,000 KRW minimum

# Algorithm
KIS_LOOKBACK_PERIOD=20       # 20-day lookback
KIS_REBALANCE_FREQUENCY=1H   # Hourly rebalancing
```

## Strategy Framework

Built-in algorithmic trading strategies:

### Simple Moving Average
```python
from strategies import SimpleMovingAverageStrategy

strategy = SimpleMovingAverageStrategy(
    short_window=5,
    long_window=20,
    symbol="005930"
)

# Strategy automatically generates buy/sell signals
signal = strategy.calculate_signals()
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
flake8 src/
```

### Type Checking
```bash
mypy src/
```

## Important Notes

⚠️ **Security First**: Never hardcode API keys in your code. Always use environment variables.

⚠️ **Mock Mode**: Always test with `is_mock=True` before live trading

⚠️ **API Limits**: KIS API has rate limits (20 requests/second)

⚠️ **Risk**: Algorithmic trading involves financial risk. Test thoroughly.

⚠️ **Compliance**: Ensure compliance with Korean financial regulations

## Security

🔐 **READ FIRST**: [Security Guidelines](SECURITY.md) - Essential security practices for API key protection

**Quick Security Checklist:**
- ✅ Use environment variables for API keys
- ✅ Never commit `.env` files to Git  
- ✅ Use Mock mode for development/testing
- ✅ Regularly rotate API keys
- ✅ Monitor for unauthorized access

## Support

- 📖 [KIS OpenAPI Documentation](https://apiportal.koreainvestment.com)
- 🐙 [GitHub Repository](https://github.com/koreainvestment/open-trading-api)
- 📋 Official KIS API samples and documentation

## License

MIT License - see LICENSE file for details.

## Disclaimer

This software is for educational and research purposes. Trading involves financial risk. The authors are not responsible for any financial losses incurred through the use of this software. Always test thoroughly in mock mode before live trading.