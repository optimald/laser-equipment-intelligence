# 🤖 LLM-Driven Hunting System

**Clay.com-Style Intelligent Equipment Discovery**

This document describes our advanced LLM-driven hunting system that automatically discovers and extracts laser equipment listings from any website, similar to Clay.com's approach.

## 🎯 Overview

Unlike traditional scrapers that require pre-built parsers for each website, our LLM hunting system uses artificial intelligence to:

1. **Discover new sources** automatically by searching the web
2. **Analyze website structure** and determine the best extraction approach
3. **Extract data** from any website without pre-built scrapers
4. **Adapt to changes** in website structure automatically
5. **Find alternative sources** when primary sources fail

## 🏗️ Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Hunting Orchestrator                     │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │   LLM Hunter    │ │ Source Discovery│ │Adaptive Extractor│ │
│  │                 │ │                 │ │                 │ │
│  │ • Brand hunting │ │ • Auto discovery│ │ • Universal     │ │
│  │ • Price analysis│ │ • Validation    │ │   extraction    │ │
│  │ • Scoring       │ │ • Categorization│ │ • Site analysis │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

- **🔍 Intelligent Source Discovery**: Automatically finds new auction sites, marketplaces, and dealers
- **🧠 Adaptive Extraction**: Handles any website structure without pre-built scrapers
- **🎯 Targeted Hunting**: Focus on specific brands, price ranges, or equipment types
- **🌍 Geographic Scope**: Search specific regions or globally
- **📊 Smart Scoring**: AI-powered ranking and qualification of listings
- **🔄 Self-Improving**: Learns from successful extractions to improve future performance

## 🚀 Quick Start

### Prerequisites

```bash
# Set your Groq API key
export GROQ_API_KEY="your_groq_api_key_here"

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from laser_intelligence.ai.hunting_orchestrator import HuntingOrchestrator

# Initialize the hunting system
orchestrator = HuntingOrchestrator()

# Run a comprehensive hunt
session = orchestrator.hunt_laser_equipment(
    strategy='comprehensive',
    search_terms=['sciton', 'cynosure', 'cutera'],
    geographic_scope=['United States'],
    max_sources=50,
    min_confidence=0.7
)

# View results
print(f"Discovered {len(session.discovered_sources)} sources")
print(f"Extracted {len(session.extracted_listings)} listings")
print(f"Success rate: {session.success_rate:.1%}")
```

### Demo Script

```bash
# Run the interactive demo
python scripts/llm_hunting_demo.py --interactive

# Or run all strategies automatically
python scripts/llm_hunting_demo.py
```

## 🎯 Hunting Strategies

### 1. Comprehensive Hunt
**Best for**: General equipment discovery
- Discovers all types of sources (auctions, marketplaces, dealers, classifieds)
- Searches multiple geographic regions
- Extracts maximum number of listings
- **Use case**: Regular monitoring and broad discovery

### 2. Targeted Hunt
**Best for**: Specific brand/model searches
- Focuses on specific search terms
- Higher confidence requirements
- More precise results
- **Use case**: Looking for specific equipment like "Sciton Joule" or "Cynosure PicoSure"

### 3. Discovery Hunt
**Best for**: Finding new sources
- Emphasizes source discovery over extraction
- Tests a sample of discovered sources
- Builds a database of potential sources
- **Use case**: Expanding your source network

### 4. High-Value Hunt
**Best for**: Expensive equipment
- Focuses on high-value brands and models
- Higher price thresholds
- Premium equipment only
- **Use case**: Finding expensive, profitable equipment

### 5. Auction-Focused Hunt
**Best for**: Auction sites specifically
- Discovers auction websites and government surplus
- Extracts auction-specific data (bids, end times, lot numbers)
- **Use case**: Auction-based equipment sourcing

## 🔧 Advanced Configuration

### Custom Search Parameters

```python
# Brand-specific hunting
session = orchestrator.hunt_laser_equipment(
    strategy='targeted',
    search_terms=['sciton joule', 'cynosure picosure', 'cutera excel v'],
    geographic_scope=['United States', 'Canada'],
    max_sources=30,
    max_listings_per_source=50,
    min_confidence=0.8
)

# High-value equipment only
session = orchestrator.hunt_laser_equipment(
    strategy='high_value',
    geographic_scope=['United States'],
    max_sources=20,
    min_confidence=0.9
)
```

### Source Discovery Options

```python
from laser_intelligence.ai.source_discovery import LLMSourceDiscovery

discovery = LLMSourceDiscovery()

# Discover specific source types
auction_sources = discovery.discover_auction_sites('United States')
dealer_sources = discovery.discover_dealer_sites('United States')
gov_sources = discovery.discover_government_sources()

# International discovery
intl_sources = discovery.discover_international_sources()
```

### Adaptive Extraction

```python
from laser_intelligence.ai.adaptive_extractor import AdaptiveExtractor

extractor = AdaptiveExtractor()

# Extract from any URL
result = extractor.extract_from_url(
    url='https://example-auction-site.com',
    max_pages=10
)

if result.success:
    print(f"Extracted {len(result.extracted_listings)} listings")
    print(f"Confidence: {result.confidence_score:.2f}")
    print(f"Method: {result.extraction_method}")
```

## 📊 Results Analysis

### Session Summary

```python
# Get detailed session summary
summary = orchestrator.get_session_summary(session)
print(summary)
```

### Key Metrics

- **Sources Discovered**: Number of new sources found
- **Listings Extracted**: Total equipment listings found
- **Success Rate**: Percentage of successful extractions
- **Confidence Score**: Average confidence in results
- **Processing Time**: Total time for the hunt
- **Brand Distribution**: Breakdown by equipment brand
- **Price Analysis**: Price ranges and average values
- **Qualification Levels**: HOT/REVIEW/ARCHIVE classifications

### Data Structure

Each extracted listing includes:

```python
{
    'title_raw': 'Sciton Joule Laser System - Excellent Condition',
    'description_raw': 'Complete system with handpieces...',
    'brand': 'Sciton',
    'model': 'Joule',
    'asking_price': 75000.0,
    'condition': 'excellent',
    'location_city': 'Los Angeles',
    'location_state': 'CA',
    'location_country': 'USA',
    'serial_number': 'SN12345',
    'year': 2022,
    'hours': 500,
    'accessories': ['handpieces', 'cart', 'chiller'],
    'auction_end_ts': 1640995200,
    'seller_name': 'Medical Equipment Liquidators',
    'source_url': 'https://example.com/auction/123',
    'source_type': 'auction',
    'extraction_method': 'llm_adaptive',
    'discovery_confidence': 0.85,
    'overall_score': 78.5,
    'qualification_level': 'HOT'
}
```

## 🎛️ Configuration Options

### API Configuration

```python
# Use different LLM provider
orchestrator = HuntingOrchestrator(api_key='your_key', api_url='https://api.openai.com/v1/chat/completions')

# Configure retry logic
orchestrator.hunter.max_retries = 5
orchestrator.hunter.retry_delay = 2
```

### Search Configuration

```python
# Custom search terms
search_terms = [
    'sciton', 'cynosure', 'cutera', 'candela', 'lumenis', 'alma',
    'inmode', 'btl', 'lutronic', 'bison', 'deka', 'quanta',
    'laser', 'ipl', 'rf', 'hifu', 'aesthetic equipment'
]

# Geographic scope
geographic_scope = [
    'United States', 'Canada', 'United Kingdom', 
    'Australia', 'Germany', 'France'
]

# Price ranges
price_range = (10000, 500000)  # $10k to $500k

# Equipment types
equipment_types = ['laser', 'ipl', 'rf', 'hifu', 'aesthetic equipment']
```

## 🔍 Monitoring and Debugging

### Logging

```python
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('laser_intelligence.ai')

# Monitor hunting progress
logger.info(f"Starting {strategy} hunt...")
logger.info(f"Discovered {len(sources)} sources")
logger.info(f"Extracted {len(listings)} listings")
```

### Error Handling

```python
try:
    session = orchestrator.hunt_laser_equipment(strategy='comprehensive')
except Exception as e:
    print(f"Hunting failed: {e}")
    # Check API key, network connection, etc.
```

### Performance Monitoring

```python
# Monitor processing time
start_time = time.time()
session = orchestrator.hunt_laser_equipment(strategy='targeted')
processing_time = time.time() - start_time

print(f"Processing time: {processing_time:.2f} seconds")
print(f"Listings per second: {len(session.extracted_listings) / processing_time:.2f}")
```

## 🚀 Production Deployment

### Environment Setup

```bash
# Production environment variables
export GROQ_API_KEY="your_production_api_key"
export HUNTING_LOG_LEVEL="INFO"
export MAX_CONCURRENT_HUNTS="5"
export HUNTING_CACHE_TTL="3600"
```

### Scheduled Hunting

```python
# Schedule regular hunts
import schedule
import time

def run_daily_hunt():
    orchestrator = HuntingOrchestrator()
    session = orchestrator.hunt_laser_equipment(
        strategy='comprehensive',
        max_sources=100,
        min_confidence=0.7
    )
    # Process and store results
    process_hunting_results(session)

# Schedule daily at 6 AM
schedule.every().day.at("06:00").do(run_daily_hunt)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Integration with Existing System

```python
# Integrate with existing spider system
from laser_intelligence.spiders.base_spider import BaseSpider

class LLMEnhancedSpider(BaseSpider):
    def __init__(self):
        super().__init__()
        self.hunter = LLMHunter()
        self.adaptive_extractor = AdaptiveExtractor()
    
    def discover_new_sources(self):
        """Use LLM to discover new sources for this spider"""
        return self.hunter.discover_sources()
    
    def extract_from_unknown_site(self, url):
        """Use adaptive extraction for unknown sites"""
        return self.adaptive_extractor.extract_from_url(url)
```

## 📈 Performance Optimization

### Caching

```python
# Cache discovered sources
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_sources(region, source_type):
    cache_key = f"sources:{region}:{source_type}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    return None

def cache_sources(region, source_type, sources):
    cache_key = f"sources:{region}:{source_type}"
    redis_client.setex(cache_key, 3600, json.dumps(sources))
```

### Parallel Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def parallel_hunting():
    strategies = ['comprehensive', 'targeted', 'high_value', 'auction_focused']
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        tasks = [
            executor.submit(orchestrator.hunt_laser_equipment, strategy=s)
            for s in strategies
        ]
        
        results = await asyncio.gather(*[asyncio.wrap_future(task) for task in tasks])
    
    return results
```

## 🔒 Security Considerations

### API Key Management

```python
# Use environment variables for API keys
import os
from cryptography.fernet import Fernet

def encrypt_api_key(key):
    f = Fernet(os.getenv('ENCRYPTION_KEY'))
    return f.encrypt(key.encode())

def decrypt_api_key(encrypted_key):
    f = Fernet(os.getenv('ENCRYPTION_KEY'))
    return f.decrypt(encrypted_key).decode()
```

### Rate Limiting

```python
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = 60.0 / calls_per_minute - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

@rate_limit(calls_per_minute=30)
def call_llm_api(prompt, content):
    # LLM API call with rate limiting
    pass
```

## 🎯 Best Practices

### 1. Start Small
Begin with targeted hunts for specific brands before running comprehensive searches.

### 2. Monitor Performance
Track success rates, processing times, and confidence scores to optimize your hunting strategy.

### 3. Use Appropriate Strategies
- Use `discovery` for finding new sources
- Use `targeted` for specific equipment searches
- Use `comprehensive` for regular monitoring

### 4. Set Realistic Expectations
- Higher confidence thresholds = fewer but higher quality results
- More sources = longer processing times
- International searches = more diverse but potentially lower quality results

### 5. Cache Results
Store discovered sources and successful extraction patterns to avoid redundant work.

### 6. Monitor Costs
LLM API calls have costs - monitor usage and optimize prompts for efficiency.

## 🚀 Future Enhancements

### Planned Features

1. **Multi-LLM Support**: Support for OpenAI, Anthropic, and other LLM providers
2. **Learning System**: Learn from successful extractions to improve future performance
3. **Real-time Monitoring**: Live dashboard for hunting progress and results
4. **Advanced Filtering**: More sophisticated filtering and ranking algorithms
5. **Integration APIs**: REST APIs for external system integration
6. **Mobile App**: Mobile interface for monitoring and control

### Contributing

We welcome contributions to improve the LLM hunting system:

1. **New Extraction Strategies**: Add support for new website types
2. **Improved Prompts**: Better LLM prompts for more accurate extraction
3. **Performance Optimizations**: Faster processing and lower resource usage
4. **New Hunting Strategies**: Additional hunting approaches for specific use cases

## 📞 Support

For questions, issues, or feature requests related to the LLM hunting system:

1. Check the documentation and examples
2. Review the test cases for usage patterns
3. Open an issue on GitHub
4. Contact the development team

---

**The LLM hunting system represents a significant advancement in automated equipment discovery, providing Clay.com-style intelligence for laser equipment sourcing.**
