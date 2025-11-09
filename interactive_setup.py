"""
交互式配置脚本
允许用户通过命令行交互式地配置网格交易参数
"""

import sys
from typing import Dict, Optional
from grid_trading_strategy import GridTradingStrategy
from lighter_api import LighterAPI
from config import Config


class InteractiveSetup:
    """交互式配置类"""
    
    def __init__(self):
        self.config = {}
    
    def print_header(self):
        """打印标题"""
        print("\n" + "="*60)
        print("Lighter 交易所网格交易策略配置")
        print("="*60 + "\n")
    
    def get_symbol(self) -> str:
        """获取交易对"""
        print("请选择交易标的（交易对）:")
        print("示例: BTC/USDT, ETH/USDT, SOL/USDT")
        symbol = input("请输入交易对: ").strip().upper()
        
        if not symbol:
            print("❌ 交易对不能为空，请重新输入")
            return self.get_symbol()
        
        # 确保格式正确
        if '/' not in symbol:
            print("❌ 交易对格式错误，请使用格式如 BTC/USDT")
            return self.get_symbol()
        
        return symbol
    
    def get_grid_range(self) -> tuple:
        """获取网格区间"""
        print("\n请设置网格区间（价格范围）:")
        
        while True:
            try:
                lower = input("请输入网格下限价格: ").strip()
                upper = input("请输入网格上限价格: ").strip()
                
                lower_price = float(lower)
                upper_price = float(upper)
                
                if lower_price >= upper_price:
                    print("❌ 下限价格必须小于上限价格，请重新输入")
                    continue
                
                if lower_price <= 0 or upper_price <= 0:
                    print("❌ 价格必须大于0，请重新输入")
                    continue
                
                return (lower_price, upper_price)
            except ValueError:
                print("❌ 请输入有效的数字")
    
    def get_grid_count(self) -> int:
        """获取网格数量"""
        print("\n请设置网格数量:")
        print("提示: 网格数量越多，订单越密集，但需要更多资金")
        
        while True:
            try:
                count = input("请输入网格数量 (建议 5-50): ").strip()
                grid_count = int(count)
                
                if grid_count < 2:
                    print("❌ 网格数量至少为2，请重新输入")
                    continue
                
                if grid_count > 100:
                    print("⚠️  网格数量较大，可能导致订单过多，是否继续？(y/n): ", end='')
                    confirm = input().strip().lower()
                    if confirm != 'y':
                        continue
                
                return grid_count
            except ValueError:
                print("❌ 请输入有效的整数")
    
    def get_leverage(self) -> int:
        """获取杠杆倍数"""
        print("\n请设置杠杆倍数:")
        print("提示: 杠杆越高风险越大，请谨慎设置")
        
        while True:
            try:
                lev = input("请输入杠杆倍数 (1-10，输入1表示不使用杠杆): ").strip()
                leverage = int(lev)
                
                if leverage < 1:
                    print("❌ 杠杆倍数至少为1，请重新输入")
                    continue
                
                if leverage > 10:
                    print("⚠️  杠杆倍数较高，风险较大，是否继续？(y/n): ", end='')
                    confirm = input().strip().lower()
                    if confirm != 'y':
                        continue
                
                return leverage
            except ValueError:
                print("❌ 请输入有效的整数")
    
    def get_order_value(self) -> float:
        """获取开仓价值"""
        print("\n请设置每个网格的开仓价值:")
        print("提示: 这是每个网格订单的价值（USDT）")
        
        while True:
            try:
                value = input("请输入每个网格的开仓价值 (USDT): ").strip()
                order_value = float(value)
                
                if order_value <= 0:
                    print("❌ 开仓价值必须大于0，请重新输入")
                    continue
                
                if order_value < 10:
                    print("⚠️  开仓价值较小，可能影响策略效果，是否继续？(y/n): ", end='')
                    confirm = input().strip().lower()
                    if confirm != 'y':
                        continue
                
                return order_value
            except ValueError:
                print("❌ 请输入有效的数字")
    
    def confirm_config(self, config: Dict) -> bool:
        """确认配置"""
        print("\n" + "="*60)
        print("配置确认")
        print("="*60)
        print(f"交易对: {config['symbol']}")
        print(f"网格区间: {config['lower_price']} - {config['upper_price']}")
        print(f"网格数量: {config['grid_count']}")
        print(f"杠杆倍数: {config['leverage']}x")
        print(f"每网格开仓价值: {config['order_value']} USDT")
        print("="*60)
        
        confirm = input("\n确认以上配置？(y/n): ").strip().lower()
        return confirm == 'y'
    
    def setup(self) -> Dict:
        """执行完整配置流程"""
        self.print_header()
        
        # 检查 API 配置
        api_creds = Config.get_api_credentials()
        if not api_creds.get('api_key') or not api_creds.get('api_secret'):
            print("⚠️  检测到未配置 API 凭证")
            setup_api = input("是否现在配置？(y/n): ").strip().lower()
            if setup_api == 'y':
                api_key = input("请输入 API Key: ").strip()
                api_secret = input("请输入 API Secret: ").strip()
                base_url = input("请输入 API Base URL (直接回车使用默认): ").strip()
                if not base_url:
                    base_url = "https://api.lighter.xyz"
                Config.save_api_credentials(api_key, api_secret, base_url)
                print("✅ API 凭证已保存\n")
        
        # 获取交易参数
        symbol = self.get_symbol()
        lower_price, upper_price = self.get_grid_range()
        grid_count = self.get_grid_count()
        leverage = self.get_leverage()
        order_value = self.get_order_value()
        
        config = {
            'symbol': symbol,
            'lower_price': lower_price,
            'upper_price': upper_price,
            'grid_count': grid_count,
            'leverage': leverage,
            'order_value': order_value
        }
        
        # 显示策略预览
        strategy = GridTradingStrategy(**config)
        strategy.print_strategy_info()
        
        # 确认配置
        if not self.confirm_config(config):
            print("❌ 配置已取消")
            sys.exit(0)
        
        # 保存配置
        Config.save_trading_config(config)
        print("✅ 配置已保存")
        
        return config


if __name__ == "__main__":
    setup = InteractiveSetup()
    config = setup.setup()
    print(f"\n✅ 配置完成！可以使用以下命令启动策略:")
    print(f"   python main.py")

