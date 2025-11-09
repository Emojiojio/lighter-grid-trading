"""
网格交易策略图形界面
提供可视化的配置和运行界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
from grid_trading_strategy import GridTradingStrategy
from lighter_api import LighterAPI
from config import Config
import logging
from io import StringIO


class GridTradingGUI:
    """网格交易策略图形界面类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Lighter 交易所网格交易策略")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # 运行状态
        self.bot = None
        self.bot_thread = None
        self.is_running = False
        
        # 日志处理器
        self.log_stream = StringIO()
        self.setup_logging()
        
        # 创建界面
        self.create_widgets()
        
        # 加载已有配置
        self.load_config()
    
    def setup_logging(self):
        """设置日志"""
        handler = logging.StreamHandler(self.log_stream)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建 Notebook（标签页）
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # API 配置标签页
        self.api_frame = ttk.Frame(notebook)
        notebook.add(self.api_frame, text="API 配置")
        self.create_api_tab()
        
        # 交易配置标签页
        self.trading_frame = ttk.Frame(notebook)
        notebook.add(self.trading_frame, text="交易配置")
        self.create_trading_tab()
        
        # 策略运行标签页
        self.run_frame = ttk.Frame(notebook)
        notebook.add(self.run_frame, text="策略运行")
        self.create_run_tab()
        
        # 日志标签页
        self.log_frame = ttk.Frame(notebook)
        notebook.add(self.log_frame, text="运行日志")
        self.create_log_tab()
    
    def create_api_tab(self):
        """创建 API 配置标签页"""
        frame = self.api_frame
        
        # API Key
        ttk.Label(frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.api_key_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.api_key_var, width=50, show="*").grid(
            row=0, column=1, padx=10, pady=10, sticky=tk.W+tk.E
        )
        
        # API Secret
        ttk.Label(frame, text="API Secret:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        self.api_secret_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.api_secret_var, width=50, show="*").grid(
            row=1, column=1, padx=10, pady=10, sticky=tk.W+tk.E
        )
        
        # API Base URL
        ttk.Label(frame, text="API Base URL:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        self.api_url_var = tk.StringVar(value="https://api.lighter.xyz")
        ttk.Entry(frame, textvariable=self.api_url_var, width=50).grid(
            row=2, column=1, padx=10, pady=10, sticky=tk.W+tk.E
        )
        
        # 保存按钮
        ttk.Button(frame, text="保存 API 配置", command=self.save_api_config).grid(
            row=3, column=0, columnspan=2, pady=20
        )
        
        # 配置列权重
        frame.columnconfigure(1, weight=1)
    
    def create_trading_tab(self):
        """创建交易配置标签页"""
        frame = self.trading_frame
        
        # 交易对
        ttk.Label(frame, text="交易对:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
        self.symbol_var = tk.StringVar(value="BTC/USDT")
        ttk.Entry(frame, textvariable=self.symbol_var, width=30).grid(
            row=0, column=1, padx=10, pady=10, sticky=tk.W
        )
        ttk.Label(frame, text="示例: BTC/USDT, ETH/USDT").grid(
            row=0, column=2, sticky=tk.W, padx=5
        )
        
        # 网格下限价格
        ttk.Label(frame, text="网格下限价格:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)
        self.lower_price_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.lower_price_var, width=30).grid(
            row=1, column=1, padx=10, pady=10, sticky=tk.W
        )
        
        # 网格上限价格
        ttk.Label(frame, text="网格上限价格:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)
        self.upper_price_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.upper_price_var, width=30).grid(
            row=2, column=1, padx=10, pady=10, sticky=tk.W
        )
        
        # 网格数量
        ttk.Label(frame, text="网格数量:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
        self.grid_count_var = tk.StringVar(value="20")
        ttk.Entry(frame, textvariable=self.grid_count_var, width=30).grid(
            row=3, column=1, padx=10, pady=10, sticky=tk.W
        )
        ttk.Label(frame, text="建议: 5-50").grid(row=3, column=2, sticky=tk.W, padx=5)
        
        # 杠杆倍数
        ttk.Label(frame, text="杠杆倍数:").grid(row=4, column=0, sticky=tk.W, padx=10, pady=10)
        self.leverage_var = tk.StringVar(value="1")
        ttk.Entry(frame, textvariable=self.leverage_var, width=30).grid(
            row=4, column=1, padx=10, pady=10, sticky=tk.W
        )
        ttk.Label(frame, text="1表示不使用杠杆").grid(row=4, column=2, sticky=tk.W, padx=5)
        
        # 每网格开仓价值
        ttk.Label(frame, text="每网格开仓价值 (USDT):").grid(
            row=5, column=0, sticky=tk.W, padx=10, pady=10
        )
        self.order_value_var = tk.StringVar(value="100")
        ttk.Entry(frame, textvariable=self.order_value_var, width=30).grid(
            row=5, column=1, padx=10, pady=10, sticky=tk.W
        )
        
        # 策略预览按钮
        ttk.Button(frame, text="预览策略", command=self.preview_strategy).grid(
            row=6, column=0, columnspan=2, pady=10
        )
        
        # 保存按钮
        ttk.Button(frame, text="保存交易配置", command=self.save_trading_config).grid(
            row=7, column=0, columnspan=2, pady=20
        )
    
    def create_run_tab(self):
        """创建策略运行标签页"""
        frame = self.run_frame
        
        # 状态显示
        status_frame = ttk.LabelFrame(frame, text="运行状态", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.status_var = tk.StringVar(value="未运行")
        ttk.Label(status_frame, text="状态:").pack(side=tk.LEFT, padx=5)
        self.status_label = ttk.Label(
            status_frame, 
            textvariable=self.status_var, 
            foreground="red",
            font=("Arial", 12, "bold")
        )
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # 策略信息显示
        info_frame = ttk.LabelFrame(frame, text="策略信息", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=15, wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # 控制按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_button = ttk.Button(
            button_frame, 
            text="启动策略", 
            command=self.start_strategy,
            state=tk.NORMAL
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            button_frame, 
            text="停止策略", 
            command=self.stop_strategy,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
    
    def create_log_tab(self):
        """创建日志标签页"""
        frame = self.log_frame
        
        # 日志显示区域
        self.log_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=30)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 清空日志按钮
        ttk.Button(frame, text="清空日志", command=self.clear_log).pack(pady=5)
        
        # 定期更新日志
        self.update_log()
    
    def load_config(self):
        """加载已有配置"""
        try:
            # 加载 API 配置
            api_creds = Config.get_api_credentials()
            if api_creds.get('api_key'):
                self.api_key_var.set(api_creds['api_key'])
            if api_creds.get('api_secret'):
                self.api_secret_var.set(api_creds['api_secret'])
            if api_creds.get('base_url'):
                self.api_url_var.set(api_creds['base_url'])
            
            # 加载交易配置
            trading_config = Config.get_trading_config()
            if trading_config:
                self.symbol_var.set(trading_config.get('symbol', 'BTC/USDT'))
                self.lower_price_var.set(str(trading_config.get('lower_price', '')))
                self.upper_price_var.set(str(trading_config.get('upper_price', '')))
                self.grid_count_var.set(str(trading_config.get('grid_count', '20')))
                self.leverage_var.set(str(trading_config.get('leverage', '1')))
                self.order_value_var.set(str(trading_config.get('order_value', '100')))
        except Exception as e:
            self.log_message(f"加载配置时出错: {e}")
    
    def save_api_config(self):
        """保存 API 配置"""
        try:
            api_key = self.api_key_var.get().strip()
            api_secret = self.api_secret_var.get().strip()
            api_url = self.api_url_var.get().strip() or "https://api.lighter.xyz"
            
            if not api_key or not api_secret:
                messagebox.showwarning("警告", "请填写完整的 API 配置信息")
                return
            
            Config.save_api_credentials(api_key, api_secret, api_url)
            messagebox.showinfo("成功", "API 配置已保存")
            self.log_message("API 配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存 API 配置失败: {e}")
            self.log_message(f"保存 API 配置失败: {e}")
    
    def save_trading_config(self):
        """保存交易配置"""
        try:
            # 验证输入
            symbol = self.symbol_var.get().strip()
            lower_price = float(self.lower_price_var.get())
            upper_price = float(self.upper_price_var.get())
            grid_count = int(self.grid_count_var.get())
            leverage = int(self.leverage_var.get())
            order_value = float(self.order_value_var.get())
            
            if lower_price >= upper_price:
                messagebox.showwarning("警告", "下限价格必须小于上限价格")
                return
            
            if grid_count < 2:
                messagebox.showwarning("警告", "网格数量至少为2")
                return
            
            if leverage < 1:
                messagebox.showwarning("警告", "杠杆倍数至少为1")
                return
            
            if order_value <= 0:
                messagebox.showwarning("警告", "开仓价值必须大于0")
                return
            
            config = {
                'symbol': symbol,
                'lower_price': lower_price,
                'upper_price': upper_price,
                'grid_count': grid_count,
                'leverage': leverage,
                'order_value': order_value
            }
            
            Config.save_trading_config(config)
            messagebox.showinfo("成功", "交易配置已保存")
            self.log_message("交易配置已保存")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
        except Exception as e:
            messagebox.showerror("错误", f"保存交易配置失败: {e}")
            self.log_message(f"保存交易配置失败: {e}")
    
    def preview_strategy(self):
        """预览策略"""
        try:
            # 获取配置
            symbol = self.symbol_var.get().strip()
            lower_price = float(self.lower_price_var.get())
            upper_price = float(self.upper_price_var.get())
            grid_count = int(self.grid_count_var.get())
            leverage = int(self.leverage_var.get())
            order_value = float(self.order_value_var.get())
            
            # 创建策略实例（使用当前价格作为示例）
            current_price = (lower_price + upper_price) / 2
            strategy = GridTradingStrategy(
                symbol, lower_price, upper_price, 
                grid_count, leverage, order_value
            )
            
            # 生成订单
            strategy.generate_grid_orders(current_price)
            summary = strategy.get_order_summary()
            
            # 显示策略信息
            info = f"""
策略预览
{'='*50}
交易对: {summary['symbol']}
网格区间: {summary['grid_range']}
网格数量: {summary['grid_count']}
杠杆倍数: {summary['leverage']}x
每网格开仓价值: {summary['order_value']} USDT

订单统计:
  买入订单数: {summary['buy_orders_count']}
  卖出订单数: {summary['sell_orders_count']}
  总买入价值: {summary['total_buy_value']:.2f} USDT
  总卖出价值: {summary['total_sell_value']:.2f} USDT
  所需保证金: {summary['total_capital_needed']:.2f} USDT
{'='*50}
"""
            
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info)
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
        except Exception as e:
            messagebox.showerror("错误", f"预览策略失败: {e}")
    
    def start_strategy(self):
        """启动策略"""
        try:
            # 检查配置
            api_creds = Config.get_api_credentials()
            if not api_creds.get('api_key') or not api_creds.get('api_secret'):
                messagebox.showwarning("警告", "请先配置 API 凭证")
                return
            
            trading_config = Config.get_trading_config()
            if not trading_config:
                messagebox.showwarning("警告", "请先配置交易参数")
                return
            
            # 禁用启动按钮，启用停止按钮
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.is_running = True
            self.status_var.set("运行中")
            self.status_label.config(foreground="green")
            
            # 在新线程中启动策略
            self.bot_thread = threading.Thread(target=self.run_strategy, daemon=True)
            self.bot_thread.start()
            
            self.log_message("策略启动中...")
            
        except Exception as e:
            messagebox.showerror("错误", f"启动策略失败: {e}")
            self.log_message(f"启动策略失败: {e}")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.is_running = False
    
    def run_strategy(self):
        """运行策略（在后台线程中）"""
        try:
            from main import GridTradingBot
            
            self.bot = GridTradingBot()
            self.bot.running = True
            
            # 初始化
            self.bot.initialize()
            self.log_message("策略初始化完成")
            
            # 下单
            self.bot.place_grid_orders()
            
            # 监控循环
            import time
            while self.bot.running and self.is_running:
                time.sleep(60)
                if self.bot.running and self.is_running:
                    self.bot.monitor_orders()
                    
        except KeyboardInterrupt:
            self.log_message("收到停止信号")
        except Exception as e:
            self.log_message(f"策略运行出错: {e}")
        finally:
            if self.bot:
                self.bot.stop()
            self.is_running = False
            self.root.after(0, self.on_strategy_stopped)
    
    def on_strategy_stopped(self):
        """策略停止后的回调"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("已停止")
        self.status_label.config(foreground="red")
        self.log_message("策略已停止")
    
    def stop_strategy(self):
        """停止策略"""
        self.is_running = False
        if self.bot:
            self.bot.running = False
        self.log_message("正在停止策略...")
    
    def log_message(self, message):
        """添加日志消息"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
    
    def update_log(self):
        """更新日志显示"""
        # 读取日志流
        log_content = self.log_stream.getvalue()
        if log_content:
            current_content = self.log_text.get(1.0, tk.END)
            if log_content not in current_content:
                self.log_text.insert(tk.END, log_content)
                self.log_text.see(tk.END)
                self.log_stream.seek(0)
                self.log_stream.truncate(0)
        
        # 每500ms更新一次
        self.root.after(500, self.update_log)
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.log_stream.seek(0)
        self.log_stream.truncate(0)


def main():
    """主函数"""
    root = tk.Tk()
    app = GridTradingGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

