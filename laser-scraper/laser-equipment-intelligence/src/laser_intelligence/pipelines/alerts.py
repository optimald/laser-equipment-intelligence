"""
Alert generation pipeline for laser equipment intelligence platform
"""

import time
from typing import Dict, Any, Optional
from scrapy import Item
from laser_intelligence.pipelines.normalization import LaserListingItem
from laser_intelligence.alerts.slack_alerts import SlackAlertManager, AlertType


class AlertsPipeline:
    """Generate alerts for high-value opportunities and system events"""
    
    def __init__(self):
        self.slack_manager = None
        self.alert_count = 0
        self.hot_alerts = 0
        self.auction_alerts = 0
        self.demand_alerts = 0
        
        # Initialize Slack manager if webhook URL is available
        slack_webhook = self._get_slack_webhook()
        if slack_webhook:
            self.slack_manager = SlackAlertManager(slack_webhook)
    
    def process_item(self, item: LaserListingItem, spider) -> LaserListingItem:
        """Process item and generate alerts"""
        try:
            # Check for HOT listing (score >= 70)
            if item.get('score_overall', 0) >= 70:
                self._send_hot_listing_alert(item, spider)
                self.hot_alerts += 1
            
            # Check for auction ending soon
            if self._is_auction_ending_soon(item):
                self._send_auction_ending_alert(item, spider)
                self.auction_alerts += 1
            
            # Check for demand matches
            demand_matches = self._check_demand_matches(item)
            if demand_matches:
                for match in demand_matches:
                    self._send_demand_match_alert(match, item, spider)
                    self.demand_alerts += 1
            
            self.alert_count += 1
            spider.logger.info(f'Processed alerts for item: {item.get("brand")} {item.get("model")}')
            
            return item
            
        except Exception as e:
            spider.logger.error(f'Error processing alerts: {e}')
            return item
    
    def _send_hot_listing_alert(self, item: LaserListingItem, spider):
        """Send alert for HOT listing"""
        if not self.slack_manager:
            spider.logger.warning('Slack manager not available, skipping hot listing alert')
            return
        
        try:
            alert_data = {
                'brand': item.get('brand'),
                'model': item.get('model'),
                'asking_price': item.get('asking_price'),
                'score_overall': item.get('score_overall'),
                'margin_pct': item.get('margin_pct'),
                'source_url': item.get('source_url'),
                'source_name': self._get_source_name(item.get('source_id')),
                'location_city': item.get('location_city'),
                'location_state': item.get('location_state'),
                'condition': item.get('condition'),
                'auction_end_ts': item.get('auction_end_ts')
            }
            
            self.slack_manager.send_hot_listing_alert(alert_data)
            spider.logger.info(f'Sent HOT listing alert for {item.get("brand")} {item.get("model")}')
            
        except Exception as e:
            spider.logger.error(f'Error sending HOT listing alert: {e}')
    
    def _send_auction_ending_alert(self, item: LaserListingItem, spider):
        """Send alert for auction ending soon"""
        if not self.slack_manager:
            return
        
        try:
            alert_data = {
                'brand': item.get('brand'),
                'model': item.get('model'),
                'asking_price': item.get('asking_price'),
                'auction_end_ts': item.get('auction_end_ts'),
                'source_url': item.get('source_url'),
                'source_name': self._get_source_name(item.get('source_id')),
                'score_overall': item.get('score_overall')
            }
            
            self.slack_manager.send_auction_ending_alert(alert_data)
            spider.logger.info(f'Sent auction ending alert for {item.get("brand")} {item.get("model")}')
            
        except Exception as e:
            spider.logger.error(f'Error sending auction ending alert: {e}')
    
    def _send_demand_match_alert(self, demand_match: Dict[str, Any], item: LaserListingItem, spider):
        """Send alert for demand match"""
        if not self.slack_manager:
            return
        
        try:
            alert_data = {
                'demand_item': demand_match,
                'listing': {
                    'brand': item.get('brand'),
                    'model': item.get('model'),
                    'asking_price': item.get('asking_price'),
                    'source_url': item.get('source_url'),
                    'score_overall': item.get('score_overall'),
                    'condition': item.get('condition')
                },
                'match_score': self._calculate_match_score(demand_match, item)
            }
            
            self.slack_manager.send_demand_match_alert(demand_match, alert_data['listing'])
            spider.logger.info(f'Sent demand match alert for {item.get("brand")} {item.get("model")}')
            
        except Exception as e:
            spider.logger.error(f'Error sending demand match alert: {e}')
    
    def _is_auction_ending_soon(self, item: LaserListingItem) -> bool:
        """Check if auction is ending soon"""
        auction_end = item.get('auction_end_ts')
        if not auction_end:
            return False
        
        current_time = time.time()
        time_remaining = auction_end - current_time
        
        # Alert if auction ends within 4 hours
        return 0 < time_remaining <= (4 * 3600)
    
    def _check_demand_matches(self, item: LaserListingItem) -> list:
        """Check if item matches current demand"""
        try:
            # This would query the demand_items table
            # For now, return empty list
            return []
            
        except Exception as e:
            print(f'Error checking demand matches: {e}')
            return []
    
    def _calculate_match_score(self, demand_item: Dict[str, Any], listing: LaserListingItem) -> float:
        """Calculate match score between demand and listing"""
        score = 0.0
        
        # Brand match
        if demand_item.get('brand', '').lower() == listing.get('brand', '').lower():
            score += 40
        elif demand_item.get('brand', '').lower() in listing.get('brand', '').lower():
            score += 30
        
        # Model match
        if demand_item.get('model', '').lower() == listing.get('model', '').lower():
            score += 30
        elif demand_item.get('model', '').lower() in listing.get('model', '').lower():
            score += 20
        
        # Condition match
        if (demand_item.get('condition') == 'any' or 
            demand_item.get('condition') == listing.get('condition')):
            score += 10
        
        # Price match
        if (demand_item.get('max_price') and listing.get('asking_price') and
            listing.get('asking_price') <= demand_item.get('max_price')):
            score += 20
        
        return min(100, score)
    
    def _get_source_name(self, source_id: str) -> str:
        """Get source name by ID"""
        # This would query the sources table
        # For now, return placeholder
        return "Unknown Source"
    
    def _get_slack_webhook(self) -> Optional[str]:
        """Get Slack webhook URL from environment"""
        import os
        return os.getenv('SLACK_WEBHOOK_URL')
    
    def close_spider(self, spider):
        """Called when spider closes"""
        spider.logger.info(f'AlertsPipeline statistics:')
        spider.logger.info(f'  Total alerts processed: {self.alert_count}')
        spider.logger.info(f'  HOT listing alerts: {self.hot_alerts}')
        spider.logger.info(f'  Auction ending alerts: {self.auction_alerts}')
        spider.logger.info(f'  Demand match alerts: {self.demand_alerts}')


class SystemAlertsPipeline:
    """Generate system-level alerts"""
    
    def __init__(self):
        self.slack_manager = None
        self.error_count = 0
        self.block_count = 0
        self.captcha_count = 0
        
        # Initialize Slack manager if webhook URL is available
        slack_webhook = self._get_slack_webhook()
        if slack_webhook:
            self.slack_manager = SlackAlertManager(slack_webhook)
    
    def process_response(self, request, response, spider):
        """Process response and check for system issues"""
        try:
            # Check for blocking
            if response.status in [403, 429, 503]:
                self._send_block_warning_alert(request, response, spider)
                self.block_count += 1
            
            # Check for CAPTCHA
            if 'captcha' in response.text.lower():
                self._send_captcha_alert(request, response, spider)
                self.captcha_count += 1
            
            # Check evasion score
            evasion_score = response.meta.get('evasion_score', 100)
            if evasion_score < 50:
                self._send_low_evasion_alert(request, response, spider, evasion_score)
            
            return response
            
        except Exception as e:
            spider.logger.error(f'Error processing system alerts: {e}')
            return response
    
    def _send_block_warning_alert(self, request, response, spider):
        """Send alert for potential blocking"""
        if not self.slack_manager:
            return
        
        try:
            alert_data = {
                'url': request.url,
                'status_code': response.status,
                'source': spider.name,
                'timestamp': time.time()
            }
            
            # Create alert
            from laser_intelligence.alerts.slack_alerts import Alert
            alert = Alert(
                alert_type=AlertType.BLOCK_WARNING,
                title="⚠️ Potential Blocking Detected",
                message=f"Status {response.status} on {spider.name}: {request.url}",
                priority="medium",
                data=alert_data,
                timestamp=time.time(),
                recipients=["@devops"]
            )
            
            self.slack_manager.send_alert(alert)
            spider.logger.warning(f'Sent block warning alert for {request.url}')
            
        except Exception as e:
            spider.logger.error(f'Error sending block warning alert: {e}')
    
    def _send_captcha_alert(self, request, response, spider):
        """Send alert for CAPTCHA detection"""
        if not self.slack_manager:
            return
        
        try:
            alert_data = {
                'url': request.url,
                'source': spider.name,
                'timestamp': time.time()
            }
            
            # Create alert
            from laser_intelligence.alerts.slack_alerts import Alert
            alert = Alert(
                alert_type=AlertType.CAPTCHA_SOLVED,
                title="🤖 CAPTCHA Detected",
                message=f"CAPTCHA detected on {spider.name}: {request.url}",
                priority="medium",
                data=alert_data,
                timestamp=time.time(),
                recipients=["@devops"]
            )
            
            self.slack_manager.send_alert(alert)
            spider.logger.info(f'Sent CAPTCHA alert for {request.url}')
            
        except Exception as e:
            spider.logger.error(f'Error sending CAPTCHA alert: {e}')
    
    def _send_low_evasion_alert(self, request, response, spider, evasion_score: int):
        """Send alert for low evasion score"""
        if not self.slack_manager:
            return
        
        try:
            alert_data = {
                'url': request.url,
                'source': spider.name,
                'evasion_score': evasion_score,
                'timestamp': time.time()
            }
            
            # Create alert
            from laser_intelligence.alerts.slack_alerts import Alert
            alert = Alert(
                alert_type=AlertType.BLOCK_WARNING,
                title="📉 Low Evasion Score",
                message=f"Low evasion score ({evasion_score}) on {spider.name}: {request.url}",
                priority="medium",
                data=alert_data,
                timestamp=time.time(),
                recipients=["@devops"]
            )
            
            self.slack_manager.send_alert(alert)
            spider.logger.warning(f'Sent low evasion alert for {request.url}')
            
        except Exception as e:
            spider.logger.error(f'Error sending low evasion alert: {e}')
    
    def _get_slack_webhook(self) -> Optional[str]:
        """Get Slack webhook URL from environment"""
        import os
        return os.getenv('SLACK_WEBHOOK_URL')
    
    def send_daily_summary(self, spider, stats: Dict[str, Any]):
        """Send daily summary report"""
        if not self.slack_manager:
            return
        
        try:
            self.slack_manager.send_daily_summary(stats)
            spider.logger.info('Sent daily summary report')
            
        except Exception as e:
            spider.logger.error(f'Error sending daily summary: {e}')
    
    def close_spider(self, spider):
        """Called when spider closes"""
        spider.logger.info(f'SystemAlertsPipeline statistics:')
        spider.logger.info(f'  Block warnings: {self.block_count}')
        spider.logger.info(f'  CAPTCHA alerts: {self.captcha_count}')
        spider.logger.info(f'  Total errors: {self.error_count}')
