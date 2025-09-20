"""
CAPTCHA solving utility for laser equipment intelligence platform
"""

import time
import requests
import base64
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class CaptchaTask:
    """CAPTCHA task information"""
    task_id: str
    captcha_type: str
    site_key: str
    page_url: str
    image_data: Optional[bytes] = None
    created_at: float = 0.0
    solved_at: Optional[float] = None
    solution: Optional[str] = None
    status: str = "pending"  # pending, processing, solved, failed


class CaptchaSolver:
    """CAPTCHA solving service integration"""
    
    def __init__(self, api_key: str = None, service: str = "2captcha"):
        self.api_key = api_key or "your_2captcha_api_key"
        self.service = service
        self.api_url = "http://2captcha.com"
        self.timeout = 120  # 2 minutes timeout
        self.cost_per_solve = 0.003  # $0.003 per solve
        self.monthly_budget = 100  # $100 monthly budget
        self.solved_count = 0
        self.failed_count = 0
        self.total_cost = 0.0
        
    def solve_captcha(self, captcha_data: Dict[str, Any]) -> Optional[str]:
        """Solve CAPTCHA using 2Captcha service"""
        try:
            # Create captcha task
            task = self._create_captcha_task(captcha_data)
            if not task:
                return None
            
            # Submit task to 2Captcha
            task_id = self._submit_captcha_task(task)
            if not task_id:
                return None
            
            task.task_id = task_id
            task.status = "processing"
            
            # Wait for solution
            solution = self._get_captcha_solution(task)
            if solution:
                task.solution = solution
                task.solved_at = time.time()
                task.status = "solved"
                self.solved_count += 1
                self.total_cost += self.cost_per_solve
                return solution
            else:
                task.status = "failed"
                self.failed_count += 1
                return None
                
        except Exception as e:
            print(f'Error solving CAPTCHA: {e}')
            self.failed_count += 1
            return None
    
    def _create_captcha_task(self, captcha_data: Dict[str, Any]) -> Optional[CaptchaTask]:
        """Create captcha task from data"""
        try:
            captcha_type = captcha_data.get('type', 'image')
            site_key = captcha_data.get('site_key', '')
            page_url = captcha_data.get('page_url', '')
            image_url = captcha_data.get('image_url', '')
            
            # Download image if URL provided
            image_data = None
            if image_url:
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    image_data = response.content
            
            task = CaptchaTask(
                task_id="",
                captcha_type=captcha_type,
                site_key=site_key,
                page_url=page_url,
                image_data=image_data,
                created_at=time.time()
            )
            
            return task
            
        except Exception as e:
            print(f'Error creating captcha task: {e}')
            return None
    
    def _submit_captcha_task(self, task: CaptchaTask) -> Optional[str]:
        """Submit captcha task to 2Captcha service"""
        try:
            if task.captcha_type == 'image' and task.image_data:
                # Submit image CAPTCHA
                return self._submit_image_captcha(task)
            elif task.captcha_type == 'recaptcha' and task.site_key:
                # Submit reCAPTCHA
                return self._submit_recaptcha(task)
            else:
                print(f'Unsupported captcha type: {task.captcha_type}')
                return None
                
        except Exception as e:
            print(f'Error submitting captcha task: {e}')
            return None
    
    def _submit_image_captcha(self, task: CaptchaTask) -> Optional[str]:
        """Submit image CAPTCHA to 2Captcha"""
        try:
            # Encode image to base64
            image_b64 = base64.b64encode(task.image_data).decode('utf-8')
            
            # Submit to 2Captcha
            submit_url = f"{self.api_url}/in.php"
            data = {
                'key': self.api_key,
                'method': 'base64',
                'body': image_b64,
                'json': 1
            }
            
            response = requests.post(submit_url, data=data, timeout=30)
            result = response.json()
            
            if result.get('status') == 1:
                return result.get('request')
            else:
                print(f'2Captcha submission failed: {result.get("error_text")}')
                return None
                
        except Exception as e:
            print(f'Error submitting image captcha: {e}')
            return None
    
    def _submit_recaptcha(self, task: CaptchaTask) -> Optional[str]:
        """Submit reCAPTCHA to 2Captcha"""
        try:
            submit_url = f"{self.api_url}/in.php"
            data = {
                'key': self.api_key,
                'method': 'userrecaptcha',
                'googlekey': task.site_key,
                'pageurl': task.page_url,
                'json': 1
            }
            
            response = requests.post(submit_url, data=data, timeout=30)
            result = response.json()
            
            if result.get('status') == 1:
                return result.get('request')
            else:
                print(f'2Captcha reCAPTCHA submission failed: {result.get("error_text")}')
                return None
                
        except Exception as e:
            print(f'Error submitting recaptcha: {e}')
            return None
    
    def _get_captcha_solution(self, task: CaptchaTask) -> Optional[str]:
        """Get captcha solution from 2Captcha"""
        try:
            get_url = f"{self.api_url}/res.php"
            params = {
                'key': self.api_key,
                'action': 'get',
                'id': task.task_id,
                'json': 1
            }
            
            start_time = time.time()
            
            while time.time() - start_time < self.timeout:
                response = requests.get(get_url, params=params, timeout=10)
                result = response.json()
                
                if result.get('status') == 1:
                    return result.get('request')
                elif result.get('error_text') == 'CAPCHA_NOT_READY':
                    time.sleep(5)  # Wait 5 seconds before retry
                    continue
                else:
                    print(f'2Captcha solution failed: {result.get("error_text")}')
                    return None
            
            print('2Captcha solution timeout')
            return None
            
        except Exception as e:
            print(f'Error getting captcha solution: {e}')
            return None
    
    def get_balance(self) -> float:
        """Get account balance from 2Captcha service"""
        try:
            balance_url = f"{self.api_url}/res.php"
            params = {
                'key': self.api_key,
                'action': 'getbalance',
                'json': 1
            }
            
            response = requests.get(balance_url, params=params, timeout=10)
            result = response.json()
            
            if result.get('status') == 1:
                return float(result.get('request', 0))
            else:
                print(f'Failed to get balance: {result.get("error_text")}')
                return 0.0
                
        except Exception as e:
            print(f'Error getting balance: {e}')
            return 0.0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get CAPTCHA solving statistics"""
        success_rate = 0.0
        if self.solved_count + self.failed_count > 0:
            success_rate = self.solved_count / (self.solved_count + self.failed_count)
        
        return {
            'solved_count': self.solved_count,
            'failed_count': self.failed_count,
            'success_rate': success_rate,
            'total_cost': self.total_cost,
            'monthly_budget': self.monthly_budget,
            'budget_remaining': self.monthly_budget - self.total_cost,
            'balance': self.get_balance()
        }
    
    def is_budget_exceeded(self) -> bool:
        """Check if monthly budget is exceeded"""
        return self.total_cost >= self.monthly_budget
    
    def reset_monthly_stats(self):
        """Reset monthly statistics"""
        self.solved_count = 0
        self.failed_count = 0
        self.total_cost = 0.0
