"""
Slack alert system for laser equipment intelligence platform
"""

import json
import time
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class AlertType(Enum):
    """Alert type enumeration"""
    NEW_HIGH_MARGIN = "new_high_margin"
    AUCTION_ENDING = "auction_ending"
    SPIKE = "spike"
    BLOCK_WARNING = "block_warning"
    SYSTEM_ERROR = "system_error"
    SOURCE_DOWN = "source_down"
    CAPTCHA_SOLVED = "captcha_solved"
    DEMAND_MATCH = "demand_match"


@dataclass
class Alert:
    """Alert data structure"""
    alert_type: AlertType
    title: str
    message: str
    priority: str  # low, medium, high, critical
    data: Dict[str, Any]
    timestamp: float
    recipients: List[str] = None


class SlackAlertManager:
    """Manage Slack alerts and notifications"""
    
    def __init__(self, webhook_url: str, channel: str = "#laser-intelligence"):
        self.webhook_url = webhook_url
        self.channel = channel
        self.alert_history: List[Alert] = []
        self.rate_limits: Dict[str, float] = {}
        self.min_interval = 300  # 5 minutes between similar alerts
    
    def send_alert(self, alert: Alert) -> bool:
        """Send alert to Slack"""
        try:
            # Check rate limiting
            if self._is_rate_limited(alert):
                return False
            
            # Create Slack message
            slack_message = self._create_slack_message(alert)
            
            # Send to Slack
            response = requests.post(
                self.webhook_url,
                json=slack_message,
                timeout=10
            )
            
            if response.status_code == 200:
                self.alert_history.append(alert)
                self._update_rate_limit(alert)
                return True
            else:
                print(f'Slack alert failed: {response.status_code} - {response.text}')
                return False
                
        except Exception as e:
            print(f'Error sending Slack alert: {e}')
            return False
    
    def send_hot_listing_alert(self, listing: Dict[str, Any]) -> bool:
        """Send alert for HOT listing (score >= 70)"""
        alert = Alert(
            alert_type=AlertType.NEW_HIGH_MARGIN,
            title="🔥 HOT Listing Discovered",
            message=f"High-margin opportunity: {listing.get('brand')} {listing.get('model')}",
            priority="high",
            data=listing,
            timestamp=time.time(),
            recipients=["@procurement", "@sales"]
        )
        
        return self.send_alert(alert)
    
    def send_auction_ending_alert(self, listing: Dict[str, Any]) -> bool:
        """Send alert for auction ending soon"""
        hours_remaining = (listing.get('auction_end_ts', 0) - time.time()) / 3600
        
        alert = Alert(
            alert_type=AlertType.AUCTION_ENDING,
            title="⏰ Auction Ending Soon",
            message=f"Auction ending in {hours_remaining:.1f} hours: {listing.get('brand')} {listing.get('model')}",
            priority="high" if hours_remaining < 24 else "medium",
            data=listing,
            timestamp=time.time(),
            recipients=["@procurement"]
        )
        
        return self.send_alert(alert)
    
    def send_demand_match_alert(self, demand_item: Dict[str, Any], listing: Dict[str, Any]) -> bool:
        """Send alert for demand match"""
        alert = Alert(
            alert_type=AlertType.DEMAND_MATCH,
            title="🎯 Demand Match Found",
            message=f"Found {listing.get('brand')} {listing.get('model')} matching demand from {demand_item.get('buyer_contact')}",
            priority="high",
            data={
                'demand_item': demand_item,
                'listing': listing,
                'match_score': self._calculate_match_score(demand_item, listing)
            },
            timestamp=time.time(),
            recipients=[demand_item.get('buyer_contact', '@procurement')]
        )
        
        return self.send_alert(alert)
    
    def send_block_warning_alert(self, source: str, url: str, evasion_score: int) -> bool:
        """Send alert for potential blocking"""
        alert = Alert(
            alert_type=AlertType.BLOCK_WARNING,
            title="⚠️ Potential Blocking Detected",
            message=f"Low evasion score ({evasion_score}) on {source}: {url}",
            priority="medium",
            data={
                'source': source,
                'url': url,
                'evasion_score': evasion_score
            },
            timestamp=time.time(),
            recipients=["@devops"]
        )
        
        return self.send_alert(alert)
    
    def send_source_down_alert(self, source: str, error_count: int) -> bool:
        """Send alert for source failure"""
        alert = Alert(
            alert_type=AlertType.SOURCE_DOWN,
            title="🚨 Source Down",
            message=f"{source} has failed {error_count} times in a row",
            priority="critical",
            data={
                'source': source,
                'error_count': error_count
            },
            timestamp=time.time(),
            recipients=["@devops", "@procurement"]
        )
        
        return self.send_alert(alert)
    
    def send_system_error_alert(self, error: str, component: str) -> bool:
        """Send alert for system error"""
        alert = Alert(
            alert_type=AlertType.SYSTEM_ERROR,
            title="💥 System Error",
            message=f"Error in {component}: {error}",
            priority="critical",
            data={
                'error': error,
                'component': component
            },
            timestamp=time.time(),
            recipients=["@devops"]
        )
        
        return self.send_alert(alert)
    
    def send_daily_summary(self, stats: Dict[str, Any]) -> bool:
        """Send daily summary report"""
        alert = Alert(
            alert_type=AlertType.SPIKE,
            title="📊 Daily Summary",
            message=f"Processed {stats.get('total_listings', 0)} listings, {stats.get('hot_count', 0)} HOT items",
            priority="low",
            data=stats,
            timestamp=time.time(),
            recipients=["@procurement", "@management"]
        )
        
        return self.send_alert(alert)
    
    def _create_slack_message(self, alert: Alert) -> Dict[str, Any]:
        """Create Slack message format"""
        # Color coding based on priority
        color_map = {
            'low': '#36a64f',      # Green
            'medium': '#ff9500',   # Orange
            'high': '#ff0000',    # Red
            'critical': '#8b0000'  # Dark red
        }
        
        color = color_map.get(alert.priority, '#36a64f')
        
        # Create attachment with data
        attachment = {
            'color': color,
            'title': alert.title,
            'text': alert.message,
            'timestamp': alert.timestamp,
            'fields': []
        }
        
        # Add relevant data fields
        if alert.alert_type == AlertType.NEW_HIGH_MARGIN:
            attachment['fields'].extend([
                {
                    'title': 'Brand',
                    'value': alert.data.get('brand', 'N/A'),
                    'short': True
                },
                {
                    'title': 'Model',
                    'value': alert.data.get('model', 'N/A'),
                    'short': True
                },
                {
                    'title': 'Price',
                    'value': f"${alert.data.get('asking_price', 0):,.2f}",
                    'short': True
                },
                {
                    'title': 'Score',
                    'value': f"{alert.data.get('score_overall', 0):.1f}",
                    'short': True
                },
                {
                    'title': 'Source',
                    'value': alert.data.get('source_name', 'N/A'),
                    'short': True
                },
                {
                    'title': 'Location',
                    'value': f"{alert.data.get('location_city', 'N/A')}, {alert.data.get('location_state', 'N/A')}",
                    'short': True
                }
            ])
            
            # Add action buttons
            attachment['actions'] = [
                {
                    'type': 'button',
                    'text': 'View Listing',
                    'url': alert.data.get('source_url', '#'),
                    'style': 'primary'
                }
            ]
        
        elif alert.alert_type == AlertType.AUCTION_ENDING:
            hours_remaining = (alert.data.get('auction_end_ts', 0) - time.time()) / 3600
            attachment['fields'].extend([
                {
                    'title': 'Time Remaining',
                    'value': f"{hours_remaining:.1f} hours",
                    'short': True
                },
                {
                    'title': 'Current Bid',
                    'value': f"${alert.data.get('asking_price', 0):,.2f}",
                    'short': True
                }
            ])
        
        elif alert.alert_type == AlertType.DEMAND_MATCH:
            match_data = alert.data
            attachment['fields'].extend([
                {
                    'title': 'Demand Contact',
                    'value': match_data.get('demand_item', {}).get('buyer_contact', 'N/A'),
                    'short': True
                },
                {
                    'title': 'Match Score',
                    'value': f"{match_data.get('match_score', 0):.1f}%",
                    'short': True
                },
                {
                    'title': 'Urgency',
                    'value': match_data.get('demand_item', {}).get('urgency', 'N/A'),
                    'short': True
                }
            ])
        
        # Create the full message
        message = {
            'channel': self.channel,
            'username': 'Laser Intelligence Bot',
            'icon_emoji': ':robot_face:',
            'attachments': [attachment]
        }
        
        # Add mentions for recipients
        if alert.recipients:
            mentions = ' '.join(alert.recipients)
            message['text'] = f"{mentions}"
        
        return message
    
    def _is_rate_limited(self, alert: Alert) -> bool:
        """Check if alert is rate limited"""
        rate_key = f"{alert.alert_type.value}_{alert.data.get('source_url', '')}"
        
        if rate_key in self.rate_limits:
            time_since_last = time.time() - self.rate_limits[rate_key]
            if time_since_last < self.min_interval:
                return True
        
        return False
    
    def _update_rate_limit(self, alert: Alert):
        """Update rate limit timestamp"""
        rate_key = f"{alert.alert_type.value}_{alert.data.get('source_url', '')}"
        self.rate_limits[rate_key] = time.time()
    
    def _calculate_match_score(self, demand_item: Dict[str, Any], listing: Dict[str, Any]) -> float:
        """Calculate match score between demand and listing"""
        score = 0.0
        
        # Brand match
        if demand_item['brand'].lower() == listing['brand'].lower():
            score += 40
        elif demand_item['brand'].lower() in listing['brand'].lower():
            score += 30
        
        # Model match
        if demand_item['model'].lower() == listing['model'].lower():
            score += 30
        elif demand_item['model'].lower() in listing['model'].lower():
            score += 20
        
        # Condition match
        if demand_item['condition'] == 'any' or demand_item['condition'] == listing['condition']:
            score += 10
        
        # Price match
        if demand_item['max_price'] and listing['asking_price']:
            if listing['asking_price'] <= demand_item['max_price']:
                score += 20
        
        return min(100, score)
    
    def get_alert_history(self, limit: int = 50) -> List[Alert]:
        """Get recent alert history"""
        return self.alert_history[-limit:]
    
    def clear_alert_history(self):
        """Clear alert history"""
        self.alert_history.clear()
        self.rate_limits.clear()


class AlertScheduler:
    """Schedule and manage alert delivery"""
    
    def __init__(self, slack_manager: SlackAlertManager):
        self.slack_manager = slack_manager
        self.scheduled_alerts: List[Dict] = []
    
    def schedule_daily_summary(self, hour: int = 9):
        """Schedule daily summary alert"""
        # This would integrate with a scheduler like APScheduler
        pass
    
    def schedule_auction_reminders(self, listing: Dict[str, Any]):
        """Schedule auction ending reminders"""
        auction_end = listing.get('auction_end_ts', 0)
        current_time = time.time()
        
        if auction_end > current_time:
            # Schedule reminder 24 hours before
            reminder_time = auction_end - (24 * 3600)
            if reminder_time > current_time:
                self.scheduled_alerts.append({
                    'type': 'auction_reminder',
                    'time': reminder_time,
                    'data': listing
                })
            
            # Schedule final reminder 2 hours before
            final_reminder_time = auction_end - (2 * 3600)
            if final_reminder_time > current_time:
                self.scheduled_alerts.append({
                    'type': 'auction_final',
                    'time': final_reminder_time,
                    'data': listing
                })
    
    def process_scheduled_alerts(self):
        """Process scheduled alerts"""
        current_time = time.time()
        
        for alert in self.scheduled_alerts[:]:
            if alert['time'] <= current_time:
                if alert['type'] == 'auction_reminder':
                    self.slack_manager.send_auction_ending_alert(alert['data'])
                elif alert['type'] == 'auction_final':
                    self.slack_manager.send_auction_ending_alert(alert['data'])
                
                self.scheduled_alerts.remove(alert)
