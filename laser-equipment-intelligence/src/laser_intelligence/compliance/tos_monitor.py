"""
Terms of Service monitoring and compliance system
"""

import re
import time
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from bs4 import BeautifulSoup
import psycopg2
from laser_intelligence.alerts.slack_alerts import SlackAlertManager, AlertType


class ComplianceLevel(Enum):
    """Compliance level enumeration"""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"


@dataclass
class ToSPolicy:
    """Terms of Service policy data structure"""
    source_id: str
    source_name: str
    robots_txt_url: str
    tos_url: str
    robots_policy: str
    tos_content: str
    last_checked: float
    compliance_level: ComplianceLevel
    violations: List[str]
    warnings: List[str]


@dataclass
class ComplianceViolation:
    """Compliance violation data structure"""
    violation_type: str
    severity: str
    description: str
    source: str
    url: str
    timestamp: float
    resolved: bool = False


class ToSMonitor:
    """Monitor Terms of Service and robots.txt compliance"""
    
    def __init__(self, database_url: str, slack_manager: Optional[SlackAlertManager] = None):
        self.database_url = database_url
        self.slack_manager = slack_manager
        self.policies: Dict[str, ToSPolicy] = {}
        self.violations: List[ComplianceViolation] = []
        self.check_interval = 604800  # 1 week in seconds
        self.last_check = 0
        
        # Compliance patterns
        self.blocking_patterns = [
            r'disallow:\s*/\s*$',  # Disallow all
            r'disallow:\s*/auction',  # Disallow auction pages
            r'disallow:\s*/search',  # Disallow search pages
            r'disallow:\s*/api',  # Disallow API endpoints
        ]
        
        self.tos_violation_patterns = [
            r'no\s+scraping',
            r'no\s+automated\s+access',
            r'prohibited.*scraping',
            r'violates.*terms',
            r'robots\.txt.*violation',
        ]
        
        # PII detection patterns
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b',
        }
    
    def initialize_sources(self):
        """Initialize ToS policies for all sources"""
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, name, base_url FROM sources")
            sources = cursor.fetchall()
            
            for source_id, source_name, base_url in sources:
                robots_url = f"{base_url.rstrip('/')}/robots.txt"
                tos_url = f"{base_url.rstrip('/')}/terms"
                
                policy = ToSPolicy(
                    source_id=source_id,
                    source_name=source_name,
                    robots_txt_url=robots_url,
                    tos_url=tos_url,
                    robots_policy="unknown",
                    tos_content="",
                    last_checked=0,
                    compliance_level=ComplianceLevel.COMPLIANT,
                    violations=[],
                    warnings=[]
                )
                
                self.policies[source_id] = policy
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f'Error initializing sources: {e}')
    
    def check_all_sources(self) -> Dict[str, ComplianceLevel]:
        """Check compliance for all sources"""
        if time.time() - self.last_check < self.check_interval:
            return {source_id: policy.compliance_level for source_id, policy in self.policies.items()}
        
        compliance_results = {}
        
        for source_id, policy in self.policies.items():
            try:
                compliance_level = self._check_source_compliance(policy)
                compliance_results[source_id] = compliance_level
                
                # Update policy
                policy.compliance_level = compliance_level
                policy.last_checked = time.time()
                
                # Send alerts for violations
                if compliance_level in [ComplianceLevel.WARNING, ComplianceLevel.VIOLATION, ComplianceLevel.CRITICAL]:
                    self._send_compliance_alert(policy)
                
            except Exception as e:
                print(f'Error checking compliance for {policy.source_name}: {e}')
                compliance_results[source_id] = ComplianceLevel.WARNING
        
        self.last_check = time.time()
        return compliance_results
    
    def _check_source_compliance(self, policy: ToSPolicy) -> ComplianceLevel:
        """Check compliance for a single source"""
        violations = []
        warnings = []
        
        # Check robots.txt
        robots_compliance = self._check_robots_txt(policy)
        if robots_compliance['level'] == ComplianceLevel.VIOLATION:
            violations.extend(robots_compliance['issues'])
        elif robots_compliance['level'] == ComplianceLevel.WARNING:
            warnings.extend(robots_compliance['issues'])
        
        # Check Terms of Service
        tos_compliance = self._check_terms_of_service(policy)
        if tos_compliance['level'] == ComplianceLevel.VIOLATION:
            violations.extend(tos_compliance['issues'])
        elif tos_compliance['level'] == ComplianceLevel.WARNING:
            warnings.extend(tos_compliance['issues'])
        
        # Update policy
        policy.violations = violations
        policy.warnings = warnings
        
        # Determine overall compliance level
        if violations:
            return ComplianceLevel.VIOLATION
        elif warnings:
            return ComplianceLevel.WARNING
        else:
            return ComplianceLevel.COMPLIANT
    
    def _check_robots_txt(self, policy: ToSPolicy) -> Dict[str, Any]:
        """Check robots.txt compliance"""
        try:
            response = requests.get(policy.robots_txt_url, timeout=10)
            
            if response.status_code == 404:
                # No robots.txt - generally compliant
                policy.robots_policy = "none"
                return {'level': ComplianceLevel.COMPLIANT, 'issues': []}
            
            if response.status_code != 200:
                return {'level': ComplianceLevel.WARNING, 'issues': [f'robots.txt not accessible: {response.status_code}']}
            
            robots_content = response.text
            policy.robots_policy = robots_content
            
            # Check for blocking patterns
            violations = []
            warnings = []
            
            for pattern in self.blocking_patterns:
                if re.search(pattern, robots_content, re.IGNORECASE):
                    violations.append(f'Blocking pattern detected: {pattern}')
            
            # Check for user-agent specific blocks
            if 'User-agent: *' in robots_content:
                user_agent_section = self._extract_user_agent_section(robots_content)
                if 'Disallow: /' in user_agent_section:
                    violations.append('Complete site blocking detected')
            
            if violations:
                return {'level': ComplianceLevel.VIOLATION, 'issues': violations}
            elif warnings:
                return {'level': ComplianceLevel.WARNING, 'issues': warnings}
            else:
                return {'level': ComplianceLevel.COMPLIANT, 'issues': []}
                
        except Exception as e:
            return {'level': ComplianceLevel.WARNING, 'issues': [f'Error checking robots.txt: {e}']}
    
    def _check_terms_of_service(self, policy: ToSPolicy) -> Dict[str, Any]:
        """Check Terms of Service compliance"""
        try:
            # Try multiple common ToS URLs
            tos_urls = [
                policy.tos_url,
                f"{policy.tos_url}/terms-of-service",
                f"{policy.tos_url}/terms-of-use",
                f"{policy.tos_url}/legal",
                f"{policy.tos_url}/privacy-policy"
            ]
            
            tos_content = ""
            tos_url = None
            
            for url in tos_urls:
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        tos_content = response.text
                        tos_url = url
                        break
                except:
                    continue
            
            if not tos_content:
                return {'level': ComplianceLevel.WARNING, 'issues': ['Terms of Service not accessible']}
            
            policy.tos_content = tos_content
            
            # Check for scraping violations
            violations = []
            warnings = []
            
            for pattern in self.tos_violation_patterns:
                if re.search(pattern, tos_content, re.IGNORECASE):
                    violations.append(f'ToS violation pattern detected: {pattern}')
            
            # Check for data usage restrictions
            if re.search(r'personal.*data|private.*information', tos_content, re.IGNORECASE):
                warnings.append('Personal data restrictions detected')
            
            if violations:
                return {'level': ComplianceLevel.VIOLATION, 'issues': violations}
            elif warnings:
                return {'level': ComplianceLevel.WARNING, 'issues': warnings}
            else:
                return {'level': ComplianceLevel.COMPLIANT, 'issues': []}
                
        except Exception as e:
            return {'level': ComplianceLevel.WARNING, 'issues': [f'Error checking Terms of Service: {e}']}
    
    def _extract_user_agent_section(self, robots_content: str) -> str:
        """Extract user-agent section from robots.txt"""
        lines = robots_content.split('\n')
        user_agent_section = []
        in_user_agent_section = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('User-agent:'):
                if line == 'User-agent: *':
                    in_user_agent_section = True
                    user_agent_section = []
                else:
                    in_user_agent_section = False
            elif in_user_agent_section and line:
                user_agent_section.append(line)
            elif in_user_agent_section and not line:
                break
        
        return '\n'.join(user_agent_section)
    
    def scan_for_pii(self, text: str, source: str) -> List[ComplianceViolation]:
        """Scan text for Personally Identifiable Information"""
        violations = []
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text)
            
            if matches:
                violation = ComplianceViolation(
                    violation_type=f'pii_{pii_type}',
                    severity='high',
                    description=f'PII detected: {pii_type}',
                    source=source,
                    url='',
                    timestamp=time.time()
                )
                violations.append(violation)
        
        return violations
    
    def check_fda_recalls(self) -> List[Dict[str, Any]]:
        """Check FDA device recall database"""
        try:
            # FDA API endpoint for device recalls
            fda_url = "https://api.fda.gov/device/recall.json"
            params = {
                'limit': 100,
                'search': 'date_received:[2024-01-01+TO+2025-12-31]'
            }
            
            response = requests.get(fda_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                recalls = data.get('results', [])
                
                # Filter for laser equipment recalls
                laser_recalls = []
                for recall in recalls:
                    if self._is_laser_equipment_recall(recall):
                        laser_recalls.append(recall)
                
                return laser_recalls
            else:
                print(f'FDA API error: {response.status_code}')
                return []
                
        except Exception as e:
            print(f'Error checking FDA recalls: {e}')
            return []
    
    def _is_laser_equipment_recall(self, recall: Dict[str, Any]) -> bool:
        """Check if recall is for laser equipment"""
        laser_keywords = [
            'laser', 'ipl', 'rf', 'hifu', 'cryolipolysis',
            'sciton', 'cynosure', 'cutera', 'candela', 'lumenis',
            'alma', 'inmode', 'btl', 'lutronic', 'bison',
            'aesthetic', 'cosmetic', 'dermatology', 'hair removal'
        ]
        
        # Check device name and description
        device_name = recall.get('device_name', '').lower()
        device_description = recall.get('device_description', '').lower()
        
        text_to_check = f"{device_name} {device_description}"
        
        return any(keyword in text_to_check for keyword in laser_keywords)
    
    def _send_compliance_alert(self, policy: ToSPolicy):
        """Send compliance alert via Slack"""
        if not self.slack_manager:
            return
        
        alert_data = {
            'source': policy.source_name,
            'compliance_level': policy.compliance_level.value,
            'violations': policy.violations,
            'warnings': policy.warnings,
            'robots_url': policy.robots_txt_url,
            'tos_url': policy.tos_url
        }
        
        if policy.compliance_level == ComplianceLevel.VIOLATION:
            alert = {
                'alert_type': AlertType.SYSTEM_ERROR,
                'title': '🚨 Compliance Violation',
                'message': f'Compliance violation detected on {policy.source_name}',
                'priority': 'critical',
                'data': alert_data,
                'timestamp': time.time(),
                'recipients': ['@legal', '@devops']
            }
        else:
            alert = {
                'alert_type': AlertType.BLOCK_WARNING,
                'title': '⚠️ Compliance Warning',
                'message': f'Compliance warning on {policy.source_name}',
                'priority': 'medium',
                'data': alert_data,
                'timestamp': time.time(),
                'recipients': ['@legal']
            }
        
        # Create alert object and send
        from laser_intelligence.alerts.slack_alerts import Alert
        alert_obj = Alert(**alert)
        self.slack_manager.send_alert(alert_obj)
    
    def get_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report"""
        total_sources = len(self.policies)
        compliant_sources = sum(1 for policy in self.policies.values() 
                               if policy.compliance_level == ComplianceLevel.COMPLIANT)
        warning_sources = sum(1 for policy in self.policies.values() 
                             if policy.compliance_level == ComplianceLevel.WARNING)
        violation_sources = sum(1 for policy in self.policies.values() 
                               if policy.compliance_level == ComplianceLevel.VIOLATION)
        
        return {
            'total_sources': total_sources,
            'compliant_sources': compliant_sources,
            'warning_sources': warning_sources,
            'violation_sources': violation_sources,
            'compliance_rate': (compliant_sources / total_sources * 100) if total_sources > 0 else 0,
            'last_check': self.last_check,
            'next_check': self.last_check + self.check_interval,
            'policies': {source_id: {
                'name': policy.source_name,
                'compliance_level': policy.compliance_level.value,
                'violations': policy.violations,
                'warnings': policy.warnings,
                'last_checked': policy.last_checked
            } for source_id, policy in self.policies.items()}
        }
    
    def update_source_compliance(self, source_id: str, compliance_level: ComplianceLevel):
        """Update source compliance level in database"""
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE sources 
                SET compliance_level = %s, last_compliance_check = %s
                WHERE id = %s
            """, (compliance_level.value, time.time(), source_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f'Error updating source compliance: {e}')


class ComplianceAuditor:
    """Audit compliance and generate reports"""
    
    def __init__(self, tos_monitor: ToSMonitor):
        self.tos_monitor = tos_monitor
    
    def audit_data_collection(self, listings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Audit data collection for compliance"""
        audit_results = {
            'total_listings': len(listings),
            'pii_violations': [],
            'compliance_issues': [],
            'recommendations': []
        }
        
        for listing in listings:
            # Check for PII in listing data
            text_fields = [
                listing.get('title_raw', ''),
                listing.get('description_raw', ''),
                listing.get('seller_contact', ''),
                listing.get('seller_name', '')
            ]
            
            combined_text = ' '.join(text_fields)
            pii_violations = self.tos_monitor.scan_for_pii(combined_text, listing.get('source_url', ''))
            
            if pii_violations:
                audit_results['pii_violations'].extend(pii_violations)
        
        # Generate recommendations
        if audit_results['pii_violations']:
            audit_results['recommendations'].append('Implement PII redaction before data storage')
        
        return audit_results
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        compliance_report = self.tos_monitor.get_compliance_report()
        
        # Add audit recommendations
        recommendations = []
        
        if compliance_report['violation_sources'] > 0:
            recommendations.append('Review and update scraping strategies for violating sources')
        
        if compliance_report['warning_sources'] > 0:
            recommendations.append('Monitor warning sources closely for policy changes')
        
        compliance_report['recommendations'] = recommendations
        
        return compliance_report
