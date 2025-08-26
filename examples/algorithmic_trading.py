"""
Korean Investment & Securities API - Algorithmic Trading Example
===============================================================

Advanced example showing algorithmic trading strategies with risk management.
"""

import asyncio
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Import KIS modules
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from korea_investment_trading import KISClient, KISWebSocket
from config.settings import settings


class SimpleMovingAverageStrategy:
    """
    Simple Moving Average Crossover Strategy
    
    Buy when short MA crosses above long MA
    Sell when short MA crosses below long MA
    """
    
    def __init__(
        self,
        short_window: int = 5,
        long_window: int = 20,
        symbol: str = "005930"
    ):
        self.short_window = short_window
        self.long_window = long_window
        self.symbol = symbol
        
        # Price history storage
        self.price_history: List[float] = []
        self.max_history = max(short_window, long_window) + 10
        
        # Strategy state
        self.position = 0  # 0: No position, 1: Long, -1: Short
        self.last_signal = None
        
    def add_price(self, price: float):
        """Add new price to history"""
        self.price_history.append(price)
        
        # Keep only required history
        if len(self.price_history) > self.max_history:
            self.price_history = self.price_history[-self.max_history:]
    
    def calculate_signals(self) -> Optional[str]:
        """
        Calculate trading signals based on moving averages
        
        Returns:
            str: 'buy', 'sell', or None
        """
        if len(self.price_history) < self.long_window:
            return None
        
        # Calculate moving averages
        short_ma = np.mean(self.price_history[-self.short_window:])
        long_ma = np.mean(self.price_history[-self.long_window:])
        
        # Previous moving averages for crossover detection
        if len(self.price_history) < self.long_window + 1:
            return None
            
        prev_short_ma = np.mean(self.price_history[-(self.short_window + 1):-1])
        prev_long_ma = np.mean(self.price_history[-(self.long_window + 1):-1])
        
        # Detect crossovers
        current_signal = None
        
        # Bullish crossover: short MA crosses above long MA
        if prev_short_ma <= prev_long_ma and short_ma > long_ma:
            current_signal = 'buy'
            
        # Bearish crossover: short MA crosses below long MA  
        elif prev_short_ma >= prev_long_ma and short_ma < long_ma:
            current_signal = 'sell'
        
        # Avoid duplicate signals
        if current_signal == self.last_signal:
            current_signal = None
        else:
            self.last_signal = current_signal
            
        logger.info(f"MA Signal - Short: {short_ma:.2f}, Long: {long_ma:.2f}, Signal: {current_signal}")
        
        return current_signal


class RiskManager:
    """Risk management system"""
    
    def __init__(
        self,
        max_position_size: float = 0.1,
        stop_loss_pct: float = -0.05,
        take_profit_pct: float = 0.10,
        max_daily_loss: float = -0.02
    ):
        self.max_position_size = max_position_size
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_daily_loss = max_daily_loss
        
        # Track daily performance
        self.daily_pnl = 0.0
        self.daily_start_value = None
        
        # Track positions
        self.positions: Dict[str, Dict] = {}
        
    def check_daily_loss_limit(self, current_portfolio_value: float) -> bool:
        """Check if daily loss limit is exceeded"""
        if self.daily_start_value is None:
            self.daily_start_value = current_portfolio_value
            return False
        
        daily_return = (current_portfolio_value - self.daily_start_value) / self.daily_start_value
        
        if daily_return <= self.max_daily_loss:
            logger.warning(f"Daily loss limit exceeded: {daily_return:.2%}")
            return True
            
        return False
    
    def calculate_position_size(
        self,
        portfolio_value: float,
        price: float
    ) -> int:
        """Calculate position size based on risk management rules"""
        max_value = portfolio_value * self.max_position_size
        shares = int(max_value / price)
        
        # Ensure minimum order amount
        min_shares = int(settings.trading.min_order_amount / price)
        
        return max(shares, min_shares) if shares >= min_shares else 0
    
    def should_stop_loss(self, symbol: str, current_price: float) -> bool:
        """Check if position should be closed due to stop loss"""
        if symbol not in self.positions:
            return False
            
        position = self.positions[symbol]
        entry_price = position['price']
        quantity = position['quantity']
        
        if quantity > 0:  # Long position
            return_pct = (current_price - entry_price) / entry_price
            return return_pct <= self.stop_loss_pct
        elif quantity < 0:  # Short position
            return_pct = (entry_price - current_price) / entry_price  
            return return_pct <= self.stop_loss_pct
            
        return False
    
    def should_take_profit(self, symbol: str, current_price: float) -> bool:
        """Check if position should be closed due to take profit"""
        if symbol not in self.positions:
            return False
            
        position = self.positions[symbol]
        entry_price = position['price']
        quantity = position['quantity']
        
        if quantity > 0:  # Long position
            return_pct = (current_price - entry_price) / entry_price
            return return_pct >= self.take_profit_pct
        elif quantity < 0:  # Short position (not supported in this example)
            return_pct = (entry_price - current_price) / entry_price
            return return_pct >= self.take_profit_pct
            
        return False


class AlgorithmicTrader:
    """Main algorithmic trading system"""
    
    def __init__(self):
        # Initialize components
        self.client = KISClient(
            app_key=settings.api.app_key,
            app_secret=settings.api.app_secret,
            account_number=settings.api.account_number,
            is_mock=True
        )
        
        self.ws_client = KISWebSocket(
            app_key=settings.api.app_key,
            app_secret=settings.api.app_secret,
            is_mock=True
        )
        
        self.strategy = SimpleMovingAverageStrategy()
        self.risk_manager = RiskManager()
        
        # Trading state
        self.is_running = False
        self.portfolio_value = 0.0
        
    async def initialize(self) -> bool:
        """Initialize trading system"""
        logger.info("Initializing algorithmic trading system...")
        
        # Authenticate REST client
        if not self.client.authenticate():
            logger.error("REST client authentication failed")
            return False
        
        # Get initial portfolio value
        try:
            balance = self.client.get_balance()
            self.portfolio_value = float(balance['output2'][0]['tot_evlu_amt'])
            logger.info(f"Initial portfolio value: {self.portfolio_value:,.0f} KRW")
        except Exception as e:
            logger.error(f"Failed to get initial balance: {e}")
            return False
        
        # Connect WebSocket
        if not await self.ws_client.connect():
            logger.error("WebSocket connection failed")
            return False
        
        # Subscribe to price updates
        await self.ws_client.subscribe_price(
            [self.strategy.symbol],
            self.on_price_update
        )
        
        logger.info("✅ Trading system initialized successfully")
        return True
    
    def on_price_update(self, data: Dict):
        """Handle real-time price updates"""
        if data['symbol'] != self.strategy.symbol:
            return
            
        current_price = float(data['price'])
        logger.info(f"Price update: {self.strategy.symbol} = {current_price:,.0f} KRW")
        
        # Add price to strategy
        self.strategy.add_price(current_price)
        
        # Check risk management conditions
        if self.risk_manager.should_stop_loss(self.strategy.symbol, current_price):
            logger.warning("Stop loss triggered!")
            asyncio.create_task(self.close_position("stop_loss"))
            return
            
        if self.risk_manager.should_take_profit(self.strategy.symbol, current_price):
            logger.info("Take profit triggered!")
            asyncio.create_task(self.close_position("take_profit"))
            return
        
        # Check for trading signals
        signal = self.strategy.calculate_signals()
        if signal:
            asyncio.create_task(self.execute_signal(signal, current_price))
    
    async def execute_signal(self, signal: str, current_price: float):
        """Execute trading signal"""
        logger.info(f"Executing signal: {signal} at price {current_price:,.0f}")
        
        try:
            if signal == 'buy':
                await self.execute_buy(current_price)
            elif signal == 'sell':
                await self.execute_sell(current_price)
                
        except Exception as e:
            logger.error(f"Signal execution failed: {e}")
    
    async def execute_buy(self, price: float):
        """Execute buy order"""
        # Check daily loss limit
        if self.risk_manager.check_daily_loss_limit(self.portfolio_value):
            logger.warning("Daily loss limit reached, skipping buy signal")
            return
        
        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            self.portfolio_value, price
        )
        
        if position_size <= 0:
            logger.warning("Calculated position size is 0, skipping buy")
            return
        
        try:
            # Place market buy order
            result = self.client.buy_stock(
                symbol=self.strategy.symbol,
                quantity=position_size,
                order_type="01"  # Market order
            )
            
            # Update position tracking
            self.risk_manager.positions[self.strategy.symbol] = {
                'quantity': position_size,
                'price': price,
                'timestamp': datetime.now(),
                'order_id': result['output']['ODNO']
            }
            
            self.strategy.position = 1
            
            logger.info(f"✅ Buy order placed: {position_size} shares at ~{price:,.0f} KRW")
            
        except Exception as e:
            logger.error(f"Buy order failed: {e}")
    
    async def execute_sell(self, price: float):
        """Execute sell order"""
        if self.strategy.symbol not in self.risk_manager.positions:
            logger.warning("No position to sell")
            return
        
        position = self.risk_manager.positions[self.strategy.symbol]
        quantity = position['quantity']
        
        try:
            # Place market sell order
            result = self.client.sell_stock(
                symbol=self.strategy.symbol,
                quantity=quantity,
                order_type="01"  # Market order
            )
            
            # Calculate P&L
            entry_price = position['price']
            pnl = (price - entry_price) * quantity
            pnl_pct = (price - entry_price) / entry_price * 100
            
            # Remove position
            del self.risk_manager.positions[self.strategy.symbol]
            self.strategy.position = 0
            
            logger.info(f"✅ Sell order placed: {quantity} shares at ~{price:,.0f} KRW")
            logger.info(f"P&L: {pnl:+,.0f} KRW ({pnl_pct:+.2f}%)")
            
        except Exception as e:
            logger.error(f"Sell order failed: {e}")
    
    async def close_position(self, reason: str):
        """Close current position"""
        if self.strategy.symbol not in self.risk_manager.positions:
            return
        
        # Get current price
        try:
            price_data = self.client.get_current_price(self.strategy.symbol)
            current_price = float(price_data['output']['stck_prpr'])
            
            logger.info(f"Closing position due to {reason}")
            await self.execute_sell(current_price)
            
        except Exception as e:
            logger.error(f"Failed to close position: {e}")
    
    async def run_strategy(self, duration_minutes: int = 60):
        """Run the algorithmic trading strategy"""
        logger.info(f"Starting algorithmic trading for {duration_minutes} minutes...")
        
        self.is_running = True
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        try:
            while self.is_running and datetime.now() < end_time:
                # Update portfolio value periodically
                if datetime.now().minute % 10 == 0:  # Every 10 minutes
                    try:
                        balance = self.client.get_balance()
                        self.portfolio_value = float(balance['output2'][0]['tot_evlu_amt'])
                        logger.info(f"Portfolio value: {self.portfolio_value:,.0f} KRW")
                    except:
                        pass
                
                await asyncio.sleep(1)  # Small delay
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Cleanup trading system"""
        logger.info("Cleaning up trading system...")
        
        self.is_running = False
        
        # Close any open positions
        if self.strategy.symbol in self.risk_manager.positions:
            await self.close_position("system_shutdown")
        
        # Disconnect WebSocket
        await self.ws_client.disconnect()
        
        logger.info("✅ Cleanup completed")


async def main():
    """Main function to run algorithmic trading example"""
    logger.info("Korean Investment & Securities - Algorithmic Trading Example")
    logger.info("=" * 70)
    
    # Check configuration
    if not settings.api.app_key or not settings.api.app_secret:
        logger.error("Please configure your API credentials in .env file")
        return
    
    # Initialize trader
    trader = AlgorithmicTrader()
    
    # Initialize system
    if not await trader.initialize():
        logger.error("Failed to initialize trading system")
        return
    
    try:
        # Run strategy for 60 minutes (or until interrupted)
        await trader.run_strategy(duration_minutes=60)
        
    except Exception as e:
        logger.error(f"Trading error: {e}")
    
    logger.info("✅ Algorithmic trading example completed")


if __name__ == "__main__":
    asyncio.run(main())