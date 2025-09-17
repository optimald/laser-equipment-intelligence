# Laser Equipment Intelligence Platform

A comprehensive web scraping and intelligence platform for discovering, normalizing, and scoring aesthetic/medical laser equipment supply opportunities from public and partner sources.

## 🎯 Objective

Continuously discover, normalize, and score **aesthetic/medical laser equipment** supply opportunities from public and partner sources, feeding Procurement with **actionable, margin-qualified leads** before Sales creates backorders.

## 🏗️ Architecture

### Core Framework
- **Scrapy**: Primary crawling framework with Twisted async support
- **Playwright**: JavaScript rendering and stealth browser automation
- **BeautifulSoup/Parsel**: HTML parsing and extraction
- **undetected-playwright**: Advanced fingerprint evasion

### Anti-Detection & Evasion
- **Proxy Rotation**: Bright Data/Oxylabs residential proxies
- **CAPTCHA Solving**: 2Captcha integration with 95% success rate
- **Behavioral Simulation**: Human-like browsing patterns
- **Fingerprint Evasion**: Canvas, WebGL, and hardware spoofing

### Data Sources
- **Auction Platforms**: DOTmed, BidSpotter, Proxibid, GovDeals
- **Marketplaces**: eBay, Facebook Marketplace, Craigslist
- **Specialized Dealers**: Laser-focused equipment dealers
- **International Sources**: EU/UK liquidation specialists

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd laser-equipment-intelligence
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Deploy spiders**
   ```bash
   docker exec laser-scrapyd scrapyd-deploy
   ```

5. **Start scraping**
   ```bash
   docker exec laser-scrapyd curl http://localhost:6800/schedule.json -d project=laser-intelligence -d spider=dotmed_auctions
   ```

### Manual Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **Set up database**
   ```bash
   createdb laser_intelligence
   psql laser_intelligence < docker/init.sql
   ```

4. **Run spiders**
   ```bash
   scrapy crawl dotmed_auctions
   ```

## 📊 Monitoring

- **Scrapyd Web UI**: http://localhost:6800
- **Grafana Dashboards**: http://localhost:3000 (admin/admin)
- **Prometheus Metrics**: http://localhost:9090

## 🎯 Target Equipment

### Core Brands
- Sciton (Joule, Profile, Contour)
- Cynosure (PicoSure, PicoWay, GentleMax Pro)
- Cutera (Excel V, TruSculpt, Genesis)
- Candela (GentleMax Pro, Gentle YAG)
- Lumenis (M22, Elite+, LightSheer)
- Alma (Harmony XL, Soprano, OPUS)
- InMode (Secret RF, Morpheus8, Emsculpt)

### Technology Categories
- CO2 Lasers
- Er:YAG Lasers
- Nd:YAG Lasers
- Alexandrite Lasers
- Diode Lasers
- IPL Systems
- RF Microneedling
- HIFU Body Contouring
- Cryolipolysis

## 🔧 Configuration

### Evasion Settings
Edit `src/laser_intelligence/config/evasion_config.yaml`:

```yaml
sources:
  dotmed:
    evasion_level: "high"
    proxy_tier: "residential_us"
    delay_min: 5
    delay_max: 15
    stealth_mode: true
```

### Source Configuration
Edit `src/laser_intelligence/config/sources_config.yaml`:

```yaml
sources:
  dotmed:
    name: "DOTmed Auctions"
    type: "auction"
    base_url: "https://www.dotmed.com/auction"
    evasion_level: "high"
    priority: 1
    crawl_frequency: 3600
```

## 📈 Scoring System

Items are scored on multiple criteria:

- **Margin Score (0-60)**: Based on estimated resale vs. asking price
- **Urgency Score (0-25)**: Auction timing, scarcity, demand
- **Condition Score (0-10)**: Equipment condition assessment
- **Reputation Score (0-5)**: Seller reputation and history

**Qualification Levels:**
- `score_overall ≥ 70` → **HOT** (immediate notification)
- `50–69` → **REVIEW** (daily digest)
- `<50` → **ARCHIVE**

## 🛡️ Legal & Compliance

- **Public Data Only**: Scrape only publicly accessible listings
- **No PII Collection**: Automatic redaction of personal information
- **Fair Use Defense**: Market intelligence gathering for business purposes
- **ToS Monitoring**: Automated compliance tracking and alerts

## 🔍 Data Sources

### High-Priority Sources
1. **DOTmed Auctions** - High-value medical equipment auctions
2. **BidSpotter** - Infinite scroll, JS-heavy auction platform
3. **eBay** - High volume marketplace with CAPTCHA risk
4. **GovDeals** - Government surplus equipment (low risk)

### Specialized Dealers
- The Laser Agent
- Laser Service Solutions
- The Laser Warehouse
- MedPro Lasers
- New and Used Lasers

### International Sources
- Hilditch Group (EU/UK liquidations)
- British Medical Auctions
- Medwow (global marketplace)

## 📝 API Usage

### Demand Integration
```python
# CSV demand input
demand_data = {
    "brand": "Sciton",
    "model": "Joule",
    "condition": "any",
    "urgency": "high",
    "quantity_needed": 1,
    "max_price": 150000,
    "buyer_contact": "procurement@company.com"
}
```

### Real-time API
```bash
curl -X POST http://localhost:6800/api/v1/demand/update \
  -H "Content-Type: application/json" \
  -d '{"demand_items": [{"brand": "Sciton", "model": "Joule", "urgency": "high"}]}'
```

## 🚨 Alerts & Notifications

- **Slack Integration**: Real-time alerts for HOT items
- **Email Digests**: Daily summaries of REVIEW items
- **SMS Notifications**: Critical auction endings
- **Dashboard Alerts**: Grafana-based monitoring

## 🔧 Development

### Adding New Spiders
1. Create spider in `src/laser_intelligence/spiders/`
2. Add source configuration in `sources_config.yaml`
3. Test with `scrapy crawl <spider_name>`
4. Deploy with `scrapyd-deploy`

### Custom Middleware
- **EvasionMiddleware**: Anti-detection and behavioral simulation
- **ProxyMiddleware**: Proxy rotation and health monitoring
- **CaptchaMiddleware**: CAPTCHA solving integration

### Data Pipelines
- **NormalizationPipeline**: Brand/model normalization
- **ScoringPipeline**: Opportunity scoring and qualification
- **AlertsPipeline**: Notification generation

## 📊 Performance Targets

- **Uptime**: 99.9%
- **Block Rate**: <5%
- **Extraction Accuracy**: 85%+
- **Evasion Score**: 70+ (out of 100)
- **Processing Speed**: 100+ items/minute

## 🛠️ Troubleshooting

### Common Issues

1. **Proxy Failures**
   ```bash
   # Check proxy health
   docker exec laser-scrapyd python -c "from laser_intelligence.utils.proxy_manager import ProxyManager; pm = ProxyManager(); print(pm.get_proxy_health_score('proxy_ip'))"
   ```

2. **CAPTCHA Solving**
   ```bash
   # Check 2Captcha balance
   docker exec laser-scrapyd python -c "from laser_intelligence.utils.captcha_solver import CaptchaSolver; cs = CaptchaSolver(); print(cs.get_balance())"
   ```

3. **Database Connection**
   ```bash
   # Test database connection
   docker exec laser-postgres psql -U laser_user -d laser_intelligence -c "SELECT COUNT(*) FROM listings;"
   ```

## 📚 Documentation

- [Technical Specification](docs/SPEC.md)
- [Implementation Checklist](docs/CHECKLIST.md)
- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For support and questions:
- Email: support@company.com
- Slack: #laser-intelligence
- Documentation: [docs/](docs/)

---

**Built with ❤️ for laser equipment procurement intelligence**
