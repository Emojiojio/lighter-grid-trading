"""
配置文件管理模块
"""

import json
import os
from typing import Dict, Optional


class Config:
    """配置管理类"""
    
    CONFIG_FILE = "config.json"
    
    @staticmethod
    def load_config() -> Dict:
        """加载配置文件"""
        if os.path.exists(Config.CONFIG_FILE):
            with open(Config.CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    @staticmethod
    def save_config(config: Dict):
        """保存配置文件"""
        with open(Config.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    
    @staticmethod
    def get_api_credentials() -> Dict[str, str]:
        """获取 API 凭证"""
        config = Config.load_config()
        return {
            'api_key': config.get('api_key', ''),
            'api_secret': config.get('api_secret', ''),
            'base_url': config.get('base_url', 'https://api.lighter.xyz')
        }
    
    @staticmethod
    def save_api_credentials(api_key: str, api_secret: str, base_url: str = "https://api.lighter.xyz"):
        """保存 API 凭证"""
        config = Config.load_config()
        config['api_key'] = api_key
        config['api_secret'] = api_secret
        config['base_url'] = base_url
        Config.save_config(config)
    
    @staticmethod
    def get_trading_config() -> Dict:
        """获取交易配置"""
        config = Config.load_config()
        return config.get('trading', {})
    
    @staticmethod
    def save_trading_config(trading_config: Dict):
        """保存交易配置"""
        config = Config.load_config()
        config['trading'] = trading_config
        Config.save_config(config)

