"""
Pilot validation script for laser equipment intelligence platform
Tests 3 sources for 48 hours to validate evasion effectiveness
"""

import os
import time
import json
import psycopg2
from datetime import datetime, timedelta
from typing import Dict, List, Any
import subprocess
import requests
from laser_intelligence.alerts.slack_alerts import SlackAlertManager


class PilotValidator:
    """Validate system performance with 3-source pilot test"""
    
    def __init__(self, database_url: str, slack_webhook: str = None):
        self.database_url = database_url
        self.slack_manager = SlackAlertManager(slack_webhook) if slack_webhook else None
        self.start_time = time.time()
        self.test_duration = 48 * 3600  # 48 hours
        self.test_sources = ['dotmed_auctions', 'govdeals', 'ebay']
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'blocked_requests': 0,
            'captcha_encounters': 0,
            'total_listings': 0,
            'hot_listings': 0,
            'evasion_scores': [],
            'source_performance': {}
        }
    
    def run_pilot_test(self):
        """Run the 48-hour pilot test"""
        self.log("Starting 48-hour pilot validation test")
        
        # Initialize test environment
        self.setup_test_environment()
        
        # Start spiders
        self.start_test_spiders()
        
        # Monitor performance
        self.monitor_performance()
        
        # Generate final report
        self.generate_final_report()
    
    def setup_test_environment(self):
        """Set up test environment"""
        self.log("Setting up test environment")
        
        # Create test database tables if needed
        self.create_test_tables()
        
        # Clear existing data for clean test
        self.clear_test_data()
        
        # Initialize metrics
        for source in self.test_sources:
            self.metrics['source_performance'][source] = {
                'requests': 0,
                'successful': 0,
                'blocked': 0,
                'captcha': 0,
                'listings': 0,
                'hot_listings': 0,
                'avg_evasion_score': 0
            }
    
    def create_test_tables(self):
        """Create test-specific tables"""
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            # Create pilot test metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pilot_test_metrics (
                    id SERIAL PRIMARY KEY,
                    source_name VARCHAR(100),
                    metric_name VARCHAR(100),
                    metric_value FLOAT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.log(f"Error creating test tables: {e}")
    
    def clear_test_data(self):
        """Clear existing test data"""
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            # Clear pilot test metrics
            cursor.execute("DELETE FROM pilot_test_metrics")
            
            # Clear test listings
            cursor.execute("DELETE FROM listings WHERE source_name IN %s", (tuple(self.test_sources),))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.log(f"Error clearing test data: {e}")
    
    def start_test_spiders(self):
        """Start test spiders"""
        self.log("Starting test spiders")
        
        for source in self.test_sources:
            try:
                # Start spider using Scrapy command
                cmd = f"scrapy crawl {source} -s LOG_LEVEL=INFO"
                subprocess.Popen(cmd, shell=True)
                self.log(f"Started spider: {source}")
                
            except Exception as e:
                self.log(f"Error starting spider {source}: {e}")
    
    def monitor_performance(self):
        """Monitor performance during test"""
        self.log("Starting performance monitoring")
        
        while time.time() - self.start_time < self.test_duration:
            try:
                # Collect metrics
                self.collect_metrics()
                
                # Check for issues
                self.check_for_issues()
                
                # Send periodic updates
                self.send_periodic_update()
                
                # Wait before next check
                time.sleep(300)  # 5 minutes
                
            except Exception as e:
                self.log(f"Error during monitoring: {e}")
                time.sleep(60)  # Wait 1 minute before retry
    
    def collect_metrics(self):
        """Collect current metrics"""
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            # Get total listings
            cursor.execute("SELECT COUNT(*) FROM listings WHERE source_name IN %s", (tuple(self.test_sources),))
            total_listings = cursor.fetchone()[0]
            
            # Get hot listings
            cursor.execute("SELECT COUNT(*) FROM listings WHERE source_name IN %s AND score_overall >= 70", (tuple(self.test_sources),))
            hot_listings = cursor.fetchone()[0]
            
            # Get source-specific metrics
            for source in self.test_sources:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        AVG(evasion_score) as avg_evasion,
                        COUNT(CASE WHEN score_overall >= 70 THEN 1 END) as hot_count
                    FROM listings 
                    WHERE source_name = %s
                """, (source,))
                
                result = cursor.fetchone()
                if result:
                    self.metrics['source_performance'][source]['listings'] = result[0]
                    self.metrics['source_performance'][source]['avg_evasion_score'] = result[1] or 0
                    self.metrics['source_performance'][source]['hot_listings'] = result[2]
            
            # Update global metrics
            self.metrics['total_listings'] = total_listings
            self.metrics['hot_listings'] = hot_listings
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.log(f"Error collecting metrics: {e}")
    
    def check_for_issues(self):
        """Check for issues during test"""
        try:
            # Check for high block rates
            for source, perf in self.metrics['source_performance'].items():
                if perf['blocked'] > 0 and perf['requests'] > 0:
                    block_rate = perf['blocked'] / perf['requests']
                    if block_rate > 0.05:  # 5% block rate threshold
                        self.send_alert(f"High block rate detected for {source}: {block_rate:.2%}")
                
                # Check for low evasion scores
                if perf['avg_evasion_score'] < 70:
                    self.send_alert(f"Low evasion score for {source}: {perf['avg_evasion_score']:.1f}")
            
            # Check for no new listings
            if self.metrics['total_listings'] == 0:
                self.send_alert("No listings discovered - possible system issue")
            
        except Exception as e:
            self.log(f"Error checking for issues: {e}")
    
    def send_periodic_update(self):
        """Send periodic update"""
        elapsed_hours = (time.time() - self.start_time) / 3600
        
        if elapsed_hours % 6 == 0:  # Every 6 hours
            self.log(f"Pilot test progress: {elapsed_hours:.1f} hours elapsed")
            self.log(f"Total listings: {self.metrics['total_listings']}")
            self.log(f"Hot listings: {self.metrics['hot_listings']}")
            
            # Send Slack update
            if self.slack_manager:
                self.slack_manager.send_daily_summary({
                    'total_listings': self.metrics['total_listings'],
                    'hot_count': self.metrics['hot_listings'],
                    'elapsed_hours': elapsed_hours,
                    'test_status': 'running'
                })
    
    def generate_final_report(self):
        """Generate final pilot test report"""
        self.log("Generating final pilot test report")
        
        # Calculate final metrics
        total_time = time.time() - self.start_time
        success_rate = self.calculate_success_rate()
        block_rate = self.calculate_block_rate()
        evasion_effectiveness = self.calculate_evasion_effectiveness()
        
        # Create report
        report = {
            'test_duration_hours': total_time / 3600,
            'sources_tested': self.test_sources,
            'total_listings_discovered': self.metrics['total_listings'],
            'hot_listings_discovered': self.metrics['hot_listings'],
            'success_rate': success_rate,
            'block_rate': block_rate,
            'evasion_effectiveness': evasion_effectiveness,
            'source_performance': self.metrics['source_performance'],
            'recommendations': self.generate_recommendations(),
            'test_status': 'completed',
            'timestamp': datetime.now().isoformat()
        }
        
        # Save report
        self.save_report(report)
        
        # Send final alert
        self.send_final_alert(report)
        
        return report
    
    def calculate_success_rate(self):
        """Calculate overall success rate"""
        total_requests = sum(perf['requests'] for perf in self.metrics['source_performance'].values())
        successful_requests = sum(perf['successful'] for perf in self.metrics['source_performance'].values())
        
        if total_requests > 0:
            return successful_requests / total_requests
        return 0
    
    def calculate_block_rate(self):
        """Calculate overall block rate"""
        total_requests = sum(perf['requests'] for perf in self.metrics['source_performance'].values())
        blocked_requests = sum(perf['blocked'] for perf in self.metrics['source_performance'].values())
        
        if total_requests > 0:
            return blocked_requests / total_requests
        return 0
    
    def calculate_evasion_effectiveness(self):
        """Calculate evasion effectiveness"""
        total_evasion_scores = []
        for perf in self.metrics['source_performance'].values():
            if perf['avg_evasion_score'] > 0:
                total_evasion_scores.append(perf['avg_evasion_score'])
        
        if total_evasion_scores:
            return sum(total_evasion_scores) / len(total_evasion_scores)
        return 0
    
    def generate_recommendations(self):
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check success rate
        success_rate = self.calculate_success_rate()
        if success_rate < 0.95:
            recommendations.append(f"Success rate {success_rate:.2%} below 95% target - review evasion strategies")
        
        # Check block rate
        block_rate = self.calculate_block_rate()
        if block_rate > 0.05:
            recommendations.append(f"Block rate {block_rate:.2%} above 5% target - improve proxy rotation")
        
        # Check evasion effectiveness
        evasion_effectiveness = self.calculate_evasion_effectiveness()
        if evasion_effectiveness < 70:
            recommendations.append(f"Evasion effectiveness {evasion_effectiveness:.1f} below 70 target - enhance stealth measures")
        
        # Check listing discovery
        if self.metrics['total_listings'] < 100:
            recommendations.append("Low listing discovery - review spider selectors and source coverage")
        
        # Check hot listing ratio
        if self.metrics['total_listings'] > 0:
            hot_ratio = self.metrics['hot_listings'] / self.metrics['total_listings']
            if hot_ratio < 0.1:
                recommendations.append(f"Low hot listing ratio {hot_ratio:.2%} - review scoring algorithm")
        
        return recommendations
    
    def save_report(self, report):
        """Save report to file and database"""
        try:
            # Save to JSON file
            report_file = f"pilot_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.log(f"Report saved to {report_file}")
            
            # Save metrics to database
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO pilot_test_metrics (source_name, metric_name, metric_value)
                VALUES (%s, %s, %s)
            """, ('system', 'success_rate', report['success_rate']))
            
            cursor.execute("""
                INSERT INTO pilot_test_metrics (source_name, metric_name, metric_value)
                VALUES (%s, %s, %s)
            """, ('system', 'block_rate', report['block_rate']))
            
            cursor.execute("""
                INSERT INTO pilot_test_metrics (source_name, metric_name, metric_value)
                VALUES (%s, %s, %s)
            """, ('system', 'evasion_effectiveness', report['evasion_effectiveness']))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.log(f"Error saving report: {e}")
    
    def send_final_alert(self, report):
        """Send final alert with test results"""
        if self.slack_manager:
            alert_data = {
                'test_duration': f"{report['test_duration_hours']:.1f} hours",
                'total_listings': report['total_listings_discovered'],
                'hot_listings': report['hot_listings_discovered'],
                'success_rate': f"{report['success_rate']:.2%}",
                'block_rate': f"{report['block_rate']:.2%}",
                'evasion_effectiveness': f"{report['evasion_effectiveness']:.1f}",
                'recommendations': report['recommendations']
            }
            
            self.slack_manager.send_daily_summary(alert_data)
    
    def send_alert(self, message):
        """Send alert message"""
        self.log(f"ALERT: {message}")
        
        if self.slack_manager:
            from laser_intelligence.alerts.slack_alerts import Alert, AlertType
            alert = Alert(
                alert_type=AlertType.SYSTEM_ERROR,
                title="Pilot Test Alert",
                message=message,
                priority="medium",
                data={'test_phase': 'pilot_validation'},
                timestamp=time.time(),
                recipients=["@devops"]
            )
            self.slack_manager.send_alert(alert)
    
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")


def main():
    """Main function to run pilot validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run pilot validation test')
    parser.add_argument('--database-url', required=True, help='Database URL')
    parser.add_argument('--slack-webhook', help='Slack webhook URL')
    parser.add_argument('--duration', type=int, default=48, help='Test duration in hours')
    
    args = parser.parse_args()
    
    # Create validator
    validator = PilotValidator(args.database_url, args.slack_webhook)
    
    # Override test duration if specified
    if args.duration != 48:
        validator.test_duration = args.duration * 3600
    
    # Run pilot test
    validator.run_pilot_test()


if __name__ == '__main__':
    main()
