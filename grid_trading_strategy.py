"""
网格交易策略核心模块
实现网格交易的逻辑：在指定价格区间内设置多个买入和卖出订单
"""

import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN


@dataclass
class GridOrder:
    """网格订单数据结构"""
    price: Decimal
    quantity: Decimal
    side: str  # 'buy' or 'sell'
    grid_level: int  # 网格层级


class GridTradingStrategy:
    """网格交易策略类"""
    
    def __init__(self, symbol: str, lower_price: float, upper_price: float, 
                 grid_count: int, leverage: int, order_value: float):
        """
        初始化网格交易策略
        
        Args:
            symbol: 交易对符号，如 'BTC/USDT'
            lower_price: 网格下限价格
            upper_price: 网格上限价格
            grid_count: 网格数量
            leverage: 杠杆倍数
            order_value: 每个网格的开仓价值（USDT，名义价值，未乘以杠杆）
        """
        self.symbol = symbol
        self.lower_price = Decimal(str(lower_price))
        self.upper_price = Decimal(str(upper_price))
        self.grid_count = grid_count
        self.leverage = leverage
        self.order_value = Decimal(str(order_value))
        
        # 计算网格价格间隔
        self.price_step = (self.upper_price - self.lower_price) / Decimal(str(grid_count))
        
        # 存储网格订单
        self.grid_orders: List[GridOrder] = []
        
        # 设置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def calculate_grid_prices(self) -> List[Decimal]:
        """计算所有网格价格点"""
        prices = []
        for i in range(self.grid_count + 1):
            price = self.lower_price + self.price_step * Decimal(str(i))
            prices.append(price.quantize(Decimal('0.01'), rounding=ROUND_DOWN))
        return prices
    
    def generate_grid_orders(self, current_price: float) -> List[GridOrder]:
        """
        生成网格订单
        
        Args:
            current_price: 当前市场价格
            
        Returns:
            网格订单列表
        """
        current_price_decimal = Decimal(str(current_price))
        grid_prices = self.calculate_grid_prices()
        
        orders = []
        
        for i, price in enumerate(grid_prices):
            if price < current_price_decimal:
                # 当前价格下方，设置买入订单
                quantity = (self.order_value / price).quantize(
                    Decimal('0.000001'), rounding=ROUND_DOWN
                )
                orders.append(GridOrder(
                    price=price,
                    quantity=quantity,
                    side='buy',
                    grid_level=i
                ))
            elif price > current_price_decimal:
                # 当前价格上方，设置卖出订单
                quantity = (self.order_value / price).quantize(
                    Decimal('0.000001'), rounding=ROUND_DOWN
                )
                orders.append(GridOrder(
                    price=price,
                    quantity=quantity,
                    side='sell',
                    grid_level=i
                ))
        
        self.grid_orders = orders
        self.logger.info(f"生成了 {len(orders)} 个网格订单")
        return orders
    
    def get_order_summary(self) -> Dict:
        """获取订单摘要信息"""
        buy_orders = [o for o in self.grid_orders if o.side == 'buy']
        sell_orders = [o for o in self.grid_orders if o.side == 'sell']
        
        total_buy_value = sum(o.price * o.quantity for o in buy_orders)
        total_sell_value = sum(o.price * o.quantity for o in sell_orders)
        
        return {
            'symbol': self.symbol,
            'grid_range': f"{self.lower_price} - {self.upper_price}",
            'grid_count': self.grid_count,
            'leverage': self.leverage,
            'order_value': float(self.order_value),
            'buy_orders_count': len(buy_orders),
            'sell_orders_count': len(sell_orders),
            'total_buy_value': float(total_buy_value),
            'total_sell_value': float(total_sell_value),
            'total_capital_needed': float(total_buy_value / self.leverage)
        }
    
    def print_strategy_info(self):
        """打印策略信息"""
        summary = self.get_order_summary()
        print("\n" + "="*60)
        print("网格交易策略配置")
        print("="*60)
        print(f"交易对: {summary['symbol']}")
        print(f"网格区间: {summary['grid_range']}")
        print(f"网格数量: {summary['grid_count']}")
        print(f"杠杆倍数: {summary['leverage']}x")
        print(f"每网格开仓价值: {summary['order_value']} USDT (名义价值)")
        print(f"买入订单数: {summary['buy_orders_count']}")
        print(f"卖出订单数: {summary['sell_orders_count']}")
        print(f"总买入价值: {summary['total_buy_value']} USDT (名义价值)")
        print(f"总卖出价值: {summary['total_sell_value']} USDT (名义价值)")
        print(f"所需保证金: {summary['total_capital_needed']} USDT (实际需要)")
        print(f"\n说明: 开仓价值是名义价值，实际保证金 = 总买入价值 / 杠杆倍数")
        print("="*60 + "\n")

