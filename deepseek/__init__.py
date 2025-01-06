import os
import requests
import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@dataclass
class ApiResponse:
    text: str
    status: int 
    error: Optional[str] = None

class DeepseekClient:
    API_URL = 'https://api.deepseek.com/v1/chat/completions'
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    
    def __init__(self, api_key: str = None):
        if not api_key:
            raise ValueError("API key is required")
            
        # Clean and format key
        api_key = str(api_key).strip()
        if api_key.startswith('Bearer '):
            api_key = api_key[7:]
        if api_key.startswith('sk-'):
            api_key = api_key[3:]
        
        # Format for authentication
        self.api_key = f"Bearer sk-{api_key}"
        
        # Update session headers
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        logger.debug(f"Initialized with API key: {self.api_key[:7]}...")

    def generate(self, prompt: str, model: str = "deepseek-chat", max_tokens: int = 3000) -> ApiResponse:
        for attempt in range(self.MAX_RETRIES):
            try:
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens
                }
                logger.debug(f"Attempt {attempt + 1}: {payload}")
                
                response = self.session.post(self.API_URL, json=payload)
                logger.debug(f"Status: {response.status_code}")
                
                if response.status_code == 401:
                    logger.error("Authentication failed")
                    if attempt < self.MAX_RETRIES - 1:
                        time.sleep(self.RETRY_DELAY)
                        continue
                    return ApiResponse(text="", status=401, error="Authentication failed")
                    
                response.raise_for_status()
                data = response.json()
                return ApiResponse(
                    text=data['choices'][0]['message']['content'],
                    status=response.status_code
                )
                
            except Exception as e:
                logger.error(f"Request failed: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY)
                    continue
                return ApiResponse(text="", status=500, error=str(e))