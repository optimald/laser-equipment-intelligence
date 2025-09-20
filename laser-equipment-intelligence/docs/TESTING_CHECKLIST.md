# 🧪 Laser Equipment Intelligence Platform - Local Testing Checklist

## 📋 **PRE-TESTING SETUP**

### **Environment Preparation**
- [ ] Virtual environment activated (`source venv/bin/activate`)
- [ ] PYTHONPATH set correctly (`export PYTHONPATH=$PYTHONPATH:src`)
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] PostgreSQL database running and accessible
- [ ] Redis server running and accessible
- [ ] Docker daemon running (if testing containers)
- [ ] Required API keys configured (GROQ_API_KEY, 2CAPTCHA_API_KEY, etc.)

### **Configuration Check**
- [ ] Environment variables set in `.env` file
- [ ] Database connection string configured
- [ ] Redis connection string configured
- [ ] Proxy credentials configured (if using)
- [ ] Slack webhook URL configured (if testing alerts)
- [ ] Tesseract OCR installed and accessible

---

## 🔧 **CORE SYSTEM TESTING**

### **1. Database & Infrastructure**
- [ ] **PostgreSQL Connection Test**
  ```bash
  python -c "from laser_intelligence.database.connection import test_connection; test_connection()"
  ```
- [ ] **Redis Connection Test**
  ```bash
  python -c "from laser_intelligence.cache.redis_client import test_connection; test_connection()"
  ```
- [ ] **Database Schema Creation**
  ```bash
  python -c "from laser_intelligence.database.schema import create_tables; create_tables()"
  ```
- [ ] **Sample Data Insertion**
  ```bash
  python -c "from laser_intelligence.database.seed import seed_sample_data; seed_sample_data()"
  ```

### **2. Scrapy Framework**
- [ ] **Scrapy Installation Check**
  ```bash
  scrapy version
  ```
- [ ] **Spider List Verification**
  ```bash
  PYTHONPATH=src scrapy list
  ```
- [ ] **Individual Spider Syntax Check**
  ```bash
  PYTHONPATH=src scrapy check dotmed_auctions
  PYTHONPATH=src scrapy check bidspotter
  PYTHONPATH=src scrapy check ebay_laser
  PYTHONPATH=src scrapy check facebook_marketplace
  PYTHONPATH=src scrapy check craigslist
  PYTHONPATH=src scrapy check labx
  PYTHONPATH=src scrapy check govdeals
  PYTHONPATH=src scrapy check proxibid
  PYTHONPATH=src scrapy check centurion
  PYTHONPATH=src scrapy check gsa_auctions
  PYTHONPATH=src scrapy check govplanet
  PYTHONPATH=src scrapy check heritage_global
  PYTHONPATH=src scrapy check iron_horse_auction
  PYTHONPATH=src scrapy check kurtz_auction
  PYTHONPATH=src scrapy check laser_agent
  PYTHONPATH=src scrapy check laser_service_solutions
  PYTHONPATH=src scrapy check thelaserwarehouse
  PYTHONPATH=src scrapy check asset_recovery_services
  PYTHONPATH=src scrapy check ajwillner_auctions
  PYTHONPATH=src scrapy check medwow
  PYTHONPATH=src scrapy check used_line
  ```

### **3. Playwright Integration**
- [ ] **Playwright Installation Check**
  ```bash
  playwright --version
  ```
- [ ] **Browser Installation**
  ```bash
  playwright install
  ```
- [ ] **Playwright Test Run**
  ```bash
  python -c "from playwright.sync_api import sync_playwright; print('Playwright working')"
  ```

---

## 🕷️ **SPIDER TESTING**

### **4. Individual Spider Tests**

#### **High-Priority Spiders (Test First)**
- [ ] **DOTmed Auctions Test**
  ```bash
  PYTHONPATH=src scrapy crawl dotmed_auctions -s CLOSESPIDER_PAGECOUNT=5 -L INFO
  ```
- [ ] **eBay Laser Test**
  ```bash
  PYTHONPATH=src scrapy crawl ebay_laser -s CLOSESPIDER_PAGECOUNT=3 -L INFO
  ```
- [ ] **GovDeals Test**
  ```bash
  PYTHONPATH=src scrapy crawl govdeals -s CLOSESPIDER_PAGECOUNT=5 -L INFO
  ```

#### **Auction Platform Spiders**
- [ ] **BidSpotter Test**
  ```bash
  PYTHONPATH=src scrapy crawl bidspotter -s CLOSESPIDER_PAGECOUNT=3 -L INFO
  ```
- [ ] **Proxibid Test**
  ```bash
  PYTHONPATH=src scrapy crawl proxibid -s CLOSESPIDER_PAGECOUNT=3 -L INFO
  ```
- [ ] **Centurion Test**
  ```bash
  PYTHONPATH=src scrapy crawl centurion -s CLOSESPIDER_PAGECOUNT=3 -L INFO
  ```
- [ ] **GSA Auctions Test**
  ```bash
  PYTHONPATH=src scrapy crawl gsa_auctions -s CLOSESPIDER_PAGECOUNT=3 -L INFO
  ```
- [ ] **GovPlanet Test**
  ```bash
  PYTHONPATH=src scrapy crawl govplanet -s CLOSESPIDER_PAGECOUNT=3 -L INFO
  ```
- [ ] **Heritage Global Test**
  ```bash
  PYTHONPATH=src scrapy crawl heritage_global -s CLOSESPIDER_PAGECOUNT=3 -L INFO
  ```
- [ ] **Iron Horse Auction Test**
  ```bash
  PYTHONPATH=src scrapy crawl iron_horse_auction -s CLOSESPIDER_PAGECOUNT=3 -L INFO
  ```
- [ ] **Kurtz Auction Test**
  ```bash
  PYTHONPATH=src scrapy crawl kurtz_auction -s CLOSESPIDER_PAGECOUNT=3 -L INFO
  ```

#### **Marketplace Spiders**
- [ ] **Facebook Marketplace Test** (Heavy Throttling)
  ```bash
  PYTHONPATH=src scrapy crawl facebook_marketplace -s CLOSESPIDER_PAGECOUNT=2 -L INFO
  ```
- [ ] **Craigslist Test** (Heavy Throttling)
  ```bash
  PYTHONPATH=src scrapy crawl craigslist -s CLOSESPIDER_PAGECOUNT=2 -L INFO
  ```
- [ ] **LabX Test**
  ```bash
  PYTHONPATH=src scrapy crawl labx -s CLOSESPIDER_PAGECOUNT=3 -L INFO
  ```

#### **Specialized Dealer Spiders**
- [ ] **TheLaserAgent Test**
  ```bash
  PYTHONPATH=src scrapy crawl laser_agent -s CLOSESPIDER_PAGECOUNT=3 -L INFO
  ```
- [ ] **Laser Service Solutions Test**
  ```bash
  PYTHONPATH=src scrapy crawl laser_service_solutions -s CLOSESPIDER_PAGECOUNT=3 -L INFO
  ```
- [ ] **TheLaserWarehouse Test**
  ```bash
  PYTHONPATH=src scrapy crawl thelaserwarehouse -s CLOSESPIDER_PAGECOUNT=3 -L INFO
  ```

#### **Asset Recovery Spiders**
- [ ] **Asset Recovery Services Test**
  ```bash
  PYTHONPATH=src scrapy crawl asset_recovery_services -s CLOSESPIDER_PAGECOUNT=3 -L INFO
  ```

#### **International Spiders**
- [ ] **AJ Willner Auctions Test**
  ```bash
  PYTHONPATH=src scrapy crawl ajwillner_auctions -s CLOSESPIDER_PAGECOUNT=3 -L INFO
  ```
- [ ] **Medwow Test**
  ```bash
  PYTHONPATH=src scrapy crawl medwow -s CLOSESPIDER_PAGECOUNT=3 -L INFO
  ```

#### **Equipment Marketplace Spiders**
- [ ] **Used-line Test**
  ```bash
  PYTHONPATH=src scrapy crawl used_line -s CLOSESPIDER_PAGECOUNT=3 -L INFO
  ```

### **5. Spider Performance Tests**
- [ ] **Concurrent Request Testing**
  ```bash
  PYTHONPATH=src scrapy crawl dotmed_auctions -s CONCURRENT_REQUESTS=8 -s CLOSESPIDER_PAGECOUNT=10 -L INFO
  ```
- [ ] **Download Delay Testing**
  ```bash
  PYTHONPATH=src scrapy crawl ebay_laser -s DOWNLOAD_DELAY=2 -s CLOSESPIDER_PAGECOUNT=5 -L INFO
  ```
- [ ] **Memory Usage Monitoring**
  ```bash
  PYTHONPATH=src scrapy crawl bidspotter -s CLOSESPIDER_PAGECOUNT=20 -L INFO
  ```

---

## 🛡️ **ANTI-DETECTION TESTING**

### **6. Evasion Middleware Tests**
- [ ] **Impersonate Middleware Test**
  ```bash
  python -c "from laser_intelligence.middleware.impersonate import ImpersonateMiddleware; print('Impersonate middleware loaded')"
  ```
- [ ] **Proxy Middleware Test**
  ```bash
  python -c "from laser_intelligence.middleware.proxy import ProxyMiddleware; print('Proxy middleware loaded')"
  ```
- [ ] **CAPTCHA Middleware Test**
  ```bash
  python -c "from laser_intelligence.middleware.captcha import CaptchaMiddleware; print('CAPTCHA middleware loaded')"
  ```
- [ ] **Evasion Middleware Test**
  ```bash
  python -c "from laser_intelligence.middleware.evasion import EvasionMiddleware; print('Evasion middleware loaded')"
  ```

### **7. Browser Fingerprinting Tests**
- [ ] **Chrome Fingerprint Test**
  ```bash
  python -c "from laser_intelligence.middleware.impersonate import ImpersonateMiddleware; m = ImpersonateMiddleware(); print(m._get_impersonate_headers('chrome120'))"
  ```
- [ ] **Firefox Fingerprint Test**
  ```bash
  python -c "from laser_intelligence.middleware.impersonate import ImpersonateMiddleware; m = ImpersonateMiddleware(); print(m._get_impersonate_headers('firefox120'))"
  ```
- [ ] **Safari Fingerprint Test**
  ```bash
  python -c "from laser_intelligence.middleware.impersonate import ImpersonateMiddleware; m = ImpersonateMiddleware(); print(m._get_impersonate_headers('safari17'))"
  ```

---

## 🤖 **AI/ML SYSTEM TESTING**

### **8. LLM Fallback Tests**
- [ ] **LLM Extractor Initialization**
  ```bash
  python -c "from laser_intelligence.utils.llm_fallback import LLMFallbackExtractor; extractor = LLMFallbackExtractor(); print('LLM extractor loaded')"
  ```
- [ ] **HTML Extraction Test**
  ```bash
  python -c "from laser_intelligence.utils.llm_fallback import LLMFallbackExtractor; extractor = LLMFallbackExtractor(); result = extractor.extract_from_html('<html><body><h1>Test Laser Equipment</h1></body></html>'); print(f'Extraction result: {result.success}')"
  ```
- [ ] **Error Recovery Test**
  ```bash
  python -c "from laser_intelligence.utils.llm_fallback import ErrorRecoveryManager; manager = ErrorRecoveryManager(None); print('Error recovery manager loaded')"
  ```

### **9. ML HTML Differ Tests**
- [ ] **HTML Differ Initialization**
  ```bash
  python -c "from laser_intelligence.ml.html_differ import MLHTMLDiffer; differ = MLHTMLDiffer(); print('HTML differ loaded')"
  ```
- [ ] **HTML Comparison Test**
  ```bash
  python -c "from laser_intelligence.ml.html_differ import MLHTMLDiffer; differ = MLHTMLDiffer(); result = differ.compare_html('<html><body><h1>Test</h1></body></html>', '<html><body><h1>Test Modified</h1></body></html>'); print(f'Similarity score: {result.similarity_score}')"
  ```

### **10. EfficientUICoder Tests**
- [ ] **UI Coder Initialization**
  ```bash
  python -c "from laser_intelligence.ml.efficient_ui_coder import EfficientUICoder; coder = EfficientUICoder(); print('UI coder loaded')"
  ```
- [ ] **Selector Generation Test**
  ```bash
  python -c "from laser_intelligence.ml.efficient_ui_coder import EfficientUICoder; coder = EfficientUICoder(); result = coder.generate_selectors('<html><body><div class=\"laser-equipment\">Test</div></body></html>'); print(f'Generated {len(result.best_selectors)} selectors')"
  ```

---

## 📚 **ASSET DICTIONARY TESTING**

### **11. Dictionary Management Tests**
- [ ] **Dictionary Initialization**
  ```bash
  python -c "from laser_intelligence.dictionary.asset_dictionary import AssetDictionaryManager; manager = AssetDictionaryManager(); print('Dictionary manager loaded')"
  ```
- [ ] **Brand Search Test**
  ```bash
  python -c "from laser_intelligence.dictionary.asset_dictionary import AssetDictionaryManager; manager = AssetDictionaryManager(); brands = manager.search_brand('sciton'); print(f'Found {len(brands)} Sciton brands')"
  ```
- [ ] **Model Search Test**
  ```bash
  python -c "from laser_intelligence.dictionary.asset_dictionary import AssetDictionaryManager; manager = AssetDictionaryManager(); models = manager.search_model('joule'); print(f'Found {len(models)} Joule models')"
  ```
- [ ] **Technology Search Test**
  ```bash
  python -c "from laser_intelligence.dictionary.asset_dictionary import AssetDictionaryManager; manager = AssetDictionaryManager(); techs = manager.search_technology('co2'); print(f'Found {len(techs)} CO2 technologies')"
  ```

### **12. Dictionary Statistics Test**
- [ ] **Dictionary Stats**
  ```bash
  python -c "from laser_intelligence.dictionary.asset_dictionary import AssetDictionaryManager; manager = AssetDictionaryManager(); stats = manager.get_dictionary_stats(); print(f'Dictionary stats: {stats}')"
  ```

---

## 🔄 **DATA PROCESSING TESTING**

### **13. Pipeline Tests**
- [ ] **Normalization Pipeline Test**
  ```bash
  python -c "from laser_intelligence.pipelines.normalization import NormalizationPipeline; pipeline = NormalizationPipeline(); print('Normalization pipeline loaded')"
  ```
- [ ] **Scoring Pipeline Test**
  ```bash
  python -c "from laser_intelligence.pipelines.scoring import ScoringPipeline; pipeline = ScoringPipeline(); print('Scoring pipeline loaded')"
  ```
- [ ] **Alerts Pipeline Test**
  ```bash
  python -c "from laser_intelligence.pipelines.alerts import AlertsPipeline; pipeline = AlertsPipeline(); print('Alerts pipeline loaded')"
  ```

### **14. Brand Mapping Tests**
- [ ] **Brand Mapper Test**
  ```bash
  python -c "from laser_intelligence.utils.brand_mapping import BrandMapper; mapper = BrandMapper(); result = mapper.map_brand('sciton joule'); print(f'Mapped brand: {result}')"
  ```

### **15. Price Analysis Tests**
- [ ] **Price Analyzer Test**
  ```bash
  python -c "from laser_intelligence.utils.price_analysis import PriceAnalyzer; analyzer = PriceAnalyzer(); print('Price analyzer loaded')"
  ```

---

## 📄 **PDF PROCESSING TESTING**

### **16. PDF Processor Tests**
- [ ] **PDF Processor Initialization**
  ```bash
  python -c "from laser_intelligence.utils.pdf_processor import PDFProcessor; processor = PDFProcessor(); print('PDF processor loaded')"
  ```
- [ ] **Tesseract OCR Test**
  ```bash
  python -c "from laser_intelligence.utils.pdf_processor import PDFProcessor; processor = PDFProcessor(); print('Tesseract OCR test completed')"
  ```

---

## 🔔 **ALERT SYSTEM TESTING**

### **17. Slack Integration Tests**
- [ ] **Slack Client Test**
  ```bash
  python -c "from laser_intelligence.alerts.slack_client import SlackClient; client = SlackClient(); print('Slack client loaded')"
  ```
- [ ] **Alert Manager Test**
  ```bash
  python -c "from laser_intelligence.alerts.alert_manager import AlertManager; manager = AlertManager(); print('Alert manager loaded')"
  ```

---

## 🧪 **INTEGRATION TESTING**

### **18. End-to-End Tests**
- [ ] **Complete Spider Run (Small Scale)**
  ```bash
  PYTHONPATH=src scrapy crawl dotmed_auctions -s CLOSESPIDER_PAGECOUNT=5 -s CLOSESPIDER_ITEMCOUNT=10 -L INFO
  ```
- [ ] **Multiple Spider Run**
  ```bash
  PYTHONPATH=src scrapy crawl govdeals -s CLOSESPIDER_PAGECOUNT=3 -s CLOSESPIDER_ITEMCOUNT=5 -L INFO
  PYTHONPATH=src scrapy crawl ebay_laser -s CLOSESPIDER_PAGECOUNT=3 -s CLOSESPIDER_ITEMCOUNT=5 -L INFO
  ```

### **19. Performance Tests**
- [ ] **Memory Usage Test**
  ```bash
  PYTHONPATH=src scrapy crawl dotmed_auctions -s CLOSESPIDER_PAGECOUNT=20 -L INFO
  ```
- [ ] **Concurrent Request Test**
  ```bash
  PYTHONPATH=src scrapy crawl bidspotter -s CONCURRENT_REQUESTS=16 -s CLOSESPIDER_PAGECOUNT=10 -L INFO
  ```

---

## 🐳 **DOCKER TESTING**

### **20. Container Tests**
- [ ] **Docker Build Test**
  ```bash
  docker build -t laser-intelligence .
  ```
- [ ] **Docker Run Test**
  ```bash
  docker run --rm laser-intelligence scrapy list
  ```
- [ ] **Docker Compose Test**
  ```bash
  docker-compose up -d
  docker-compose ps
  docker-compose down
  ```

---

## 📊 **MONITORING TESTING**

### **21. Prometheus Integration**
- [ ] **Prometheus Client Test**
  ```bash
  python -c "from laser_intelligence.monitoring.prometheus_client import PrometheusClient; client = PrometheusClient(); print('Prometheus client loaded')"
  ```

### **22. Grafana Dashboard**
- [ ] **Grafana Configuration Test**
  ```bash
  python -c "from laser_intelligence.monitoring.grafana_config import GrafanaConfig; config = GrafanaConfig(); print('Grafana config loaded')"
  ```

---

## 🔒 **SECURITY TESTING**

### **23. Compliance Tests**
- [ ] **ToS Auditor Test**
  ```bash
  python -c "from laser_intelligence.compliance.tos_auditor import ToSAuditor; auditor = ToSAuditor(); print('ToS auditor loaded')"
  ```
- [ ] **PII Auditor Test**
  ```bash
  python -c "from laser_intelligence.compliance.pii_auditor import PIIAuditor; auditor = PIIAuditor(); print('PII auditor loaded')"
  ```

---

## 📝 **TESTING RESULTS DOCUMENTATION**

### **24. Test Results Recording**
- [ ] **Create Test Results File**
  ```bash
  touch test_results_$(date +%Y%m%d_%H%M%S).md
  ```
- [ ] **Record Spider Test Results**
  - Document which spiders passed/failed
  - Record any errors encountered
  - Note performance metrics
- [ ] **Record System Test Results**
  - Document infrastructure status
  - Record AI/ML system performance
  - Note any configuration issues

---

## 🚨 **TROUBLESHOOTING CHECKLIST**

### **Common Issues & Solutions**
- [ ] **Import Errors**: Check PYTHONPATH and virtual environment
- [ ] **Database Connection**: Verify PostgreSQL is running and credentials are correct
- [ ] **Redis Connection**: Verify Redis is running and accessible
- [ ] **Playwright Issues**: Run `playwright install` to install browsers
- [ ] **Proxy Issues**: Check proxy credentials and connectivity
- [ ] **API Key Issues**: Verify all required API keys are set
- [ ] **Memory Issues**: Reduce CONCURRENT_REQUESTS and CLOSESPIDER_PAGECOUNT
- [ ] **Rate Limiting**: Increase DOWNLOAD_DELAY for problematic sites

---

## ✅ **TESTING COMPLETION CHECKLIST**

### **Final Verification**
- [ ] All spiders pass syntax check
- [ ] At least 5 spiders successfully crawl test data
- [ ] Database connections working
- [ ] Redis caching functional
- [ ] AI/ML systems operational
- [ ] Asset dictionary accessible
- [ ] Alert system configured
- [ ] Docker containers build successfully
- [ ] Monitoring systems active
- [ ] Security compliance verified

---

## 📋 **TESTING SIGN-OFF**

**Testing Completed By**: _________________  
**Date**: _________________  
**Environment**: _________________  
**Test Results**: _________________  
**Issues Found**: _________________  
**Resolution Status**: _________________  

**Ready for Production**: ☐ Yes ☐ No  
**Additional Notes**: _________________  

---

**🎯 This comprehensive testing checklist ensures all components of the Laser Equipment Intelligence Platform are thoroughly tested before deployment!**
