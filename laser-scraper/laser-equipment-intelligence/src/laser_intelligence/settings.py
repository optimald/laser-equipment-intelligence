"""
Scrapy settings for laser_intelligence project
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_NAME = 'laser_intelligence'

SPIDER_MODULES = ['laser_intelligence.spiders']
NEWSPIDER_MODULE = 'laser_intelligence.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = int(os.getenv('CONCURRENT_REQUESTS', 16))

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = int(os.getenv('DOWNLOAD_DELAY_MIN', 2))
RANDOMIZE_DOWNLOAD_DELAY = os.getenv('RANDOMIZE_DOWNLOAD_DELAY', 'true').lower() == 'true'

# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = int(os.getenv('CONCURRENT_REQUESTS_PER_DOMAIN', 4))
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Enable or disable spider middlewares
SPIDER_MIDDLEWARES = {
    'laser_intelligence.middleware.evasion.EvasionMiddleware': 543,
    'laser_intelligence.middleware.proxy.ProxyMiddleware': 544,
    'laser_intelligence.middleware.captcha.CaptchaMiddleware': 545,
}

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'laser_intelligence.middleware.evasion.EvasionMiddleware': 543,
    'laser_intelligence.middleware.proxy.ProxyMiddleware': 544,
    'laser_intelligence.middleware.captcha.CaptchaMiddleware': 545,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
}

# Enable or disable extensions
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
    'scrapy.extensions.logstats.LogStats': 0,
    'scrapy.extensions.corestats.CoreStats': 0,
}

# Configure item pipelines
ITEM_PIPELINES = {
    'laser_intelligence.pipelines.normalization.NormalizationPipeline': 300,
    'laser_intelligence.pipelines.scoring.ScoringPipeline': 400,
    'laser_intelligence.pipelines.alerts.AlertsPipeline': 500,
}

# Enable and configure the AutoThrottle extension (disabled by default)
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = [503, 504, 505, 500, 403, 404, 408, 429]

# Playwright settings
PLAYWRIGHT_BROWSER_TYPE = 'chromium'
PLAYWRIGHT_LAUNCH_OPTIONS = {
    'headless': True,
    'args': [
        '--disable-blink-features=AutomationControlled',
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--no-first-run',
        '--no-zygote',
        '--disable-gpu'
    ]
}
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 60000
PLAYWRIGHT_PROCESS_REQUEST_HEADERS = None

# Database settings
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/laser_intelligence')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Proxy settings
PROXY_ENABLED = os.getenv('PROXY_ROTATION', 'true').lower() == 'true'
BRIGHT_DATA_USERNAME = os.getenv('BRIGHT_DATA_USERNAME')
BRIGHT_DATA_PASSWORD = os.getenv('BRIGHT_DATA_PASSWORD')
OXYLABS_API_KEY = os.getenv('OXYLABS_API_KEY')

# CAPTCHA settings
TWOCAPTCHA_API_KEY = os.getenv('TWOCAPTCHA_API_KEY')
ANTICAPTCHA_API_KEY = os.getenv('ANTICAPTCHA_API_KEY')

# Monitoring settings
PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT', 9090))
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')

# Logging settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_ENABLED = True
LOG_FILE = 'scrapy.log'

# Retry settings
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]

# Custom settings
STEALTH_MODE = os.getenv('STEALTH_MODE', 'true').lower() == 'true'
FINGERPRINT_EVASION = os.getenv('FINGERPRINT_EVASION', 'true').lower() == 'true'
USER_AGENT_ROTATION = os.getenv('USER_AGENT_ROTATION', 'true').lower() == 'true'

# Environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
