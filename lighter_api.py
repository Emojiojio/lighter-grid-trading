"""
Lighter 交易所 API 封装
注意：需要根据 Lighter 交易所的实际 API 文档进行调整
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import hmac
import hashlib
import logging
from typing import Dict, List, Optional
from decimal import Decimal


class LighterAPI:
    """Lighter 交易所 API 封装类"""
    
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.lighter.xyz",
                 timeout: int = 30, max_retries: int = 3, retry_backoff: float = 0.5):
        """
        初始化 API 客户端
        
        Args:
            api_key: API 密钥
            api_secret: API 密钥
            base_url: API 基础 URL（需要根据实际 API 地址调整）
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            retry_backoff: 重试退避系数（指数退避）
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        
        # 创建带重试机制的 Session
        self.session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=retry_backoff,
            status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的 HTTP 状态码
            allowed_methods=["GET", "POST"],  # 允许重试的 HTTP 方法
            raise_on_status=False
        )
        
        # 配置 HTTP 适配器
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,  # 连接池大小
            pool_maxsize=20
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _generate_signature(self, params: Dict) -> str:
        """
        生成签名（需要根据 Lighter 的实际签名算法调整）
        
        Args:
            params: 请求参数
            
        Returns:
            签名字符串
        """
        # 这里需要根据 Lighter 的实际签名算法实现
        # 示例：HMAC-SHA256
        query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                 signed: bool = False, retry_count: int = 0) -> Dict:
        """
        发送 API 请求（带重试机制）
        
        Args:
            method: HTTP 方法
            endpoint: API 端点
            params: 请求参数
            signed: 是否需要签名
            retry_count: 当前重试次数（内部使用）
            
        Returns:
            API 响应
            
        Raises:
            requests.exceptions.RequestException: 请求失败异常
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': self.api_key,
            'User-Agent': 'LighterGridTrading/1.0'
        }
        
        if params is None:
            params = {}
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        last_exception = None
        
        # 手动重试逻辑（配合 urllib3 的自动重试）
        for attempt in range(self.max_retries + 1):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(
                        url, 
                        params=params, 
                        headers=headers,
                        timeout=self.timeout
                    )
                elif method.upper() == 'POST':
                    response = self.session.post(
                        url, 
                        json=params, 
                        headers=headers,
                        timeout=self.timeout
                    )
                else:
                    raise ValueError(f"不支持的 HTTP 方法: {method}")
                
                # 检查响应状态
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout as e:
                last_exception = e
                wait_time = self.retry_backoff * (2 ** attempt)
                self.logger.warning(
                    f"请求超时 (尝试 {attempt + 1}/{self.max_retries + 1}): {e}. "
                    f"{wait_time:.1f}秒后重试..."
                )
                if attempt < self.max_retries:
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"请求超时，已达到最大重试次数")
                    raise
                    
            except requests.exceptions.ConnectionError as e:
                last_exception = e
                wait_time = self.retry_backoff * (2 ** attempt)
                self.logger.warning(
                    f"连接错误 (尝试 {attempt + 1}/{self.max_retries + 1}): {e}. "
                    f"{wait_time:.1f}秒后重试..."
                )
                if attempt < self.max_retries:
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"连接错误，已达到最大重试次数")
                    raise
                    
            except requests.exceptions.HTTPError as e:
                # 某些 HTTP 错误不应该重试（如 400, 401, 403）
                if e.response.status_code in [400, 401, 403, 404]:
                    self.logger.error(f"HTTP 错误（不重试）: {e.response.status_code} - {e}")
                    raise
                else:
                    last_exception = e
                    wait_time = self.retry_backoff * (2 ** attempt)
                    self.logger.warning(
                        f"HTTP 错误 (尝试 {attempt + 1}/{self.max_retries + 1}): "
                        f"{e.response.status_code} - {e}. {wait_time:.1f}秒后重试..."
                    )
                    if attempt < self.max_retries:
                        time.sleep(wait_time)
                    else:
                        self.logger.error(f"HTTP 错误，已达到最大重试次数")
                        raise
                        
            except requests.exceptions.RequestException as e:
                last_exception = e
                wait_time = self.retry_backoff * (2 ** attempt)
                self.logger.warning(
                    f"请求异常 (尝试 {attempt + 1}/{self.max_retries + 1}): {e}. "
                    f"{wait_time:.1f}秒后重试..."
                )
                if attempt < self.max_retries:
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"请求异常，已达到最大重试次数")
                    raise
        
        # 如果所有重试都失败
        if last_exception:
            raise last_exception
    
    def get_ticker(self, symbol: str) -> Dict:
        """
        获取交易对价格信息
        
        Args:
            symbol: 交易对符号
            
        Returns:
            价格信息
        """
        # 需要根据实际 API 调整
        endpoint = f"/api/v1/ticker"
        params = {'symbol': symbol}
        return self._request('GET', endpoint, params)
    
    def get_current_price(self, symbol: str) -> float:
        """
        获取当前价格
        
        Args:
            symbol: 交易对符号
            
        Returns:
            当前价格
        """
        ticker = self.get_ticker(symbol)
        # 需要根据实际 API 响应结构调整
        return float(ticker.get('price', 0))
    
    def place_order(self, symbol: str, side: str, price: float, 
                   quantity: float, leverage: int = 1) -> Dict:
        """
        下单
        
        Args:
            symbol: 交易对符号
            side: 买卖方向 ('buy' 或 'sell')
            price: 价格
            quantity: 数量
            leverage: 杠杆倍数
            
        Returns:
            订单信息
        """
        # 需要根据实际 API 调整
        endpoint = "/api/v1/order"
        params = {
            'symbol': symbol,
            'side': side,
            'price': str(price),
            'quantity': str(quantity),
            'leverage': leverage,
            'type': 'limit'  # 限价单
        }
        return self._request('POST', endpoint, params, signed=True)
    
    def cancel_order(self, order_id: str) -> Dict:
        """
        取消订单
        
        Args:
            order_id: 订单 ID
            
        Returns:
            取消结果
        """
        endpoint = f"/api/v1/order/{order_id}"
        return self._request('POST', endpoint, signed=True)
    
    def get_open_orders(self, symbol: str) -> List[Dict]:
        """
        获取未成交订单列表
        
        Args:
            symbol: 交易对符号
            
        Returns:
            订单列表
        """
        endpoint = "/api/v1/orders"
        params = {'symbol': symbol, 'status': 'open'}
        return self._request('GET', endpoint, params, signed=True)
    
    def cancel_all_orders(self, symbol: str) -> Dict:
        """
        取消所有订单
        
        Args:
            symbol: 交易对符号
            
        Returns:
            取消结果
        """
        endpoint = f"/api/v1/orders/cancel-all"
        params = {'symbol': symbol}
        return self._request('POST', endpoint, params, signed=True)
    
    def get_balance(self) -> Dict:
        """
        获取账户余额
        
        Returns:
            余额信息
        """
        endpoint = "/api/v1/account/balance"
        return self._request('GET', endpoint, signed=True)

