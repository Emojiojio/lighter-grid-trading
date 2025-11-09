"""
网格交易策略主程序
"""

import time
import sys
from grid_trading_strategy import GridTradingStrategy, GridOrder
from lighter_api import LighterAPI
from config import Config
import logging


class GridTradingBot:
    """网格交易机器人"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api = None
        self.strategy = None
        self.running = False
        self.placed_orders = []  # 已下单的订单ID列表
    
    def initialize(self):
        """初始化"""
        # 加载配置
        trading_config = Config.get_trading_config()
        if not trading_config:
            print("❌ 未找到交易配置，请先运行交互式配置脚本:")
            print("   python interactive_setup.py")
            sys.exit(1)
        
        # 初始化 API
        api_creds = Config.get_api_credentials()
        if not api_creds.get('api_key') or not api_creds.get('api_secret'):
            print("❌ 未找到 API 凭证，请先运行交互式配置脚本:")
            print("   python interactive_setup.py")
            sys.exit(1)
        
        # 获取网络配置（可选）
        network_config = Config.load_config().get('network', {})
        
        self.api = LighterAPI(
            api_key=api_creds['api_key'],
            api_secret=api_creds['api_secret'],
            base_url=api_creds.get('base_url', 'https://api.lighter.xyz'),
            timeout=network_config.get('timeout', 30),
            max_retries=network_config.get('max_retries', 3),
            retry_backoff=network_config.get('retry_backoff', 0.5)
        )
        
        # 初始化策略
        self.strategy = GridTradingStrategy(**trading_config)
        self.strategy.print_strategy_info()
    
    def place_grid_orders(self):
        """下单网格订单"""
        try:
            # 获取当前价格
            current_price = self.api.get_current_price(self.strategy.symbol)
            self.logger.info(f"当前价格: {current_price}")
            
            # 生成网格订单
            grid_orders = self.strategy.generate_grid_orders(current_price)
            
            # 取消之前的订单
            self.cancel_all_orders()
            
            # 下单
            placed_count = 0
            for order in grid_orders:
                try:
                    result = self.api.place_order(
                        symbol=self.strategy.symbol,
                        side=order.side,
                        price=float(order.price),
                        quantity=float(order.quantity),
                        leverage=self.strategy.leverage
                    )
                    
                    if result.get('order_id'):
                        self.placed_orders.append(result['order_id'])
                        placed_count += 1
                        self.logger.info(
                            f"✅ 下单成功: {order.side} {order.quantity} @ {order.price} "
                            f"(订单ID: {result['order_id']})"
                        )
                    else:
                        self.logger.warning(f"⚠️  下单失败: {order.side} @ {order.price}")
                    
                    # 避免请求过快
                    time.sleep(0.1)
                    
                except Exception as e:
                    self.logger.error(f"❌ 下单异常: {e}")
                    # 网络错误时等待更长时间
                    if "timeout" in str(e).lower() or "connection" in str(e).lower():
                        self.logger.info("网络不稳定，等待5秒后继续...")
                        time.sleep(5)
                    continue
            
            self.logger.info(f"✅ 共下单 {placed_count}/{len(grid_orders)} 个订单")
            
        except Exception as e:
            self.logger.error(f"❌ 下单过程出错: {e}")
            raise
    
    def cancel_all_orders(self):
        """取消所有订单"""
        try:
            self.api.cancel_all_orders(self.strategy.symbol)
            self.placed_orders = []
            self.logger.info("✅ 已取消所有订单")
        except Exception as e:
            self.logger.warning(f"⚠️  取消订单时出错: {e}")
    
    def monitor_orders(self):
        """监控订单状态"""
        try:
            open_orders = self.api.get_open_orders(self.strategy.symbol)
            self.logger.info(f"当前未成交订单数: {len(open_orders)}")
            
            # 检查是否需要重新下单
            if len(open_orders) < len(self.strategy.grid_orders) * 0.5:
                self.logger.info("订单数量不足，重新下单...")
                self.place_grid_orders()
                
        except Exception as e:
            self.logger.error(f"❌ 监控订单时出错: {e}")
            # 网络错误时不立即退出，等待下次循环
            if "timeout" in str(e).lower() or "connection" in str(e).lower():
                self.logger.warning("网络不稳定，将在下次循环时重试")
    
    def run(self):
        """运行策略"""
        self.initialize()
        
        print("\n" + "="*60)
        print("网格交易策略启动")
        print("="*60)
        print("按 Ctrl+C 停止策略\n")
        
        self.running = True
        
        try:
            # 初始下单
            self.place_grid_orders()
            
            # 循环监控
            while self.running:
                time.sleep(60)  # 每60秒检查一次
                self.monitor_orders()
                
        except KeyboardInterrupt:
            print("\n\n⚠️  收到停止信号...")
            self.stop()
        except Exception as e:
            self.logger.error(f"❌ 运行出错: {e}")
            self.stop()
    
    def stop(self):
        """停止策略"""
        self.running = False
        print("\n正在取消所有订单...")
        self.cancel_all_orders()
        print("✅ 策略已停止")


if __name__ == "__main__":
    bot = GridTradingBot()
    bot.run()

