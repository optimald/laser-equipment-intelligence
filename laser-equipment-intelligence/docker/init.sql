-- Laser Equipment Intelligence Platform Database Schema

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS laser_intelligence;

-- Use the database
\c laser_intelligence;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- Sources table
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('auction', 'dealer', 'marketplace', 'social', 'manual')),
    crawl_method VARCHAR(20) DEFAULT 'html',
    base_url VARCHAR(500) NOT NULL,
    robots_policy VARCHAR(20) DEFAULT 'disallow',
    tos_notes TEXT,
    rate_limit_policy INTEGER DEFAULT 100,
    evasion_level VARCHAR(20) DEFAULT 'medium' CHECK (evasion_level IN ('low', 'medium', 'high')),
    block_history TIMESTAMP,
    success_rate_7d DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Listings table (core table)
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES sources(id),
    source_url VARCHAR(1000) NOT NULL,
    source_listing_id VARCHAR(255),
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Item fields
    brand VARCHAR(100),
    model VARCHAR(200),
    modality VARCHAR(100),
    title_raw TEXT,
    description_raw TEXT,
    images JSONB,
    condition VARCHAR(20) CHECK (condition IN ('new', 'excellent', 'good', 'fair', 'poor', 'used', 'refurbished', 'as-is', 'unknown')),
    serial_number VARCHAR(100),
    year INTEGER CHECK (year >= 1990 AND year <= 2025),
    hours INTEGER CHECK (hours >= 0),
    accessories JSONB,
    
    -- Location
    location_city VARCHAR(100),
    location_state VARCHAR(50),
    location_country VARCHAR(50),
    lat DECIMAL(10, 8),
    lng DECIMAL(11, 8),
    
    -- Commercial details
    asking_price DECIMAL(12, 2),
    reserve_price DECIMAL(12, 2),
    buy_now_price DECIMAL(12, 2),
    auction_start_ts TIMESTAMP,
    auction_end_ts TIMESTAMP,
    seller_name VARCHAR(255),
    seller_contact VARCHAR(255),
    
    -- Enrichment
    est_wholesale DECIMAL(12, 2),
    est_resale DECIMAL(12, 2),
    refurb_cost_estimate DECIMAL(12, 2),
    freight_estimate DECIMAL(12, 2),
    margin_estimate DECIMAL(12, 2),
    margin_pct DECIMAL(5, 2),
    
    -- Scoring
    score_margin DECIMAL(5, 2) DEFAULT 0.0,
    score_urgency DECIMAL(5, 2) DEFAULT 0.0,
    score_condition DECIMAL(5, 2) DEFAULT 0.0,
    score_reputation DECIMAL(5, 2) DEFAULT 0.0,
    score_overall DECIMAL(5, 2) DEFAULT 0.0,
    
    -- Status
    ingest_status VARCHAR(20) DEFAULT 'new' CHECK (ingest_status IN ('new', 'updated', 'dropped')),
    dedupe_key VARCHAR(255),
    pipeline_status VARCHAR(20) DEFAULT 'new' CHECK (pipeline_status IN ('new', 'contacted', 'negotiating', 'po_issued', 'won', 'lost', 'archived')),
    notes TEXT,
    
    -- Scraping metadata
    scraped_with_proxy VARCHAR(255),
    evasion_score INTEGER DEFAULT 100 CHECK (evasion_score >= 0 AND evasion_score <= 100),
    scraped_legally BOOLEAN DEFAULT true,
    block_warnings INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Price comparisons table
CREATE TABLE price_comps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(200) NOT NULL,
    modality VARCHAR(100),
    condition VARCHAR(20) NOT NULL,
    sold_price DECIMAL(12, 2) NOT NULL,
    sold_date DATE NOT NULL,
    source VARCHAR(255) NOT NULL,
    url VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alerts table
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    listing_id UUID REFERENCES listings(id),
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('new_high_margin', 'auction_ending', 'spike', 'block_warning')),
    sent_to JSONB,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message TEXT,
    status VARCHAR(20) DEFAULT 'sent' CHECK (status IN ('sent', 'delivered', 'failed'))
);

-- Demand items table
CREATE TABLE demand_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(200) NOT NULL,
    condition VARCHAR(20) DEFAULT 'any',
    urgency VARCHAR(20) DEFAULT 'medium' CHECK (urgency IN ('low', 'medium', 'high')),
    quantity_needed INTEGER DEFAULT 1,
    max_price DECIMAL(12, 2),
    buyer_contact VARCHAR(255),
    notes TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Proxy performance table
CREATE TABLE proxy_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proxy_ip VARCHAR(45) NOT NULL,
    proxy_tier VARCHAR(50) NOT NULL,
    requests INTEGER DEFAULT 0,
    successes INTEGER DEFAULT 0,
    failures INTEGER DEFAULT 0,
    avg_response_time DECIMAL(8, 3),
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Evasion logs table
CREATE TABLE evasion_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES sources(id),
    url VARCHAR(1000) NOT NULL,
    evasion_score INTEGER NOT NULL,
    status_code INTEGER,
    response_length INTEGER,
    proxy_used VARCHAR(255),
    user_agent TEXT,
    block_warnings INTEGER DEFAULT 0,
    captcha_solved BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_listings_source_id ON listings(source_id);
CREATE INDEX idx_listings_brand_model ON listings(brand, model);
CREATE INDEX idx_listings_score_overall ON listings(score_overall DESC);
CREATE INDEX idx_listings_discovered_at ON listings(discovered_at DESC);
CREATE INDEX idx_listings_condition ON listings(condition);
CREATE INDEX idx_listings_asking_price ON listings(asking_price);
CREATE INDEX idx_listings_auction_end_ts ON listings(auction_end_ts);
CREATE INDEX idx_listings_dedupe_key ON listings(dedupe_key);
CREATE INDEX idx_listings_pipeline_status ON listings(pipeline_status);

CREATE INDEX idx_price_comps_brand_model ON price_comps(brand, model);
CREATE INDEX idx_price_comps_sold_date ON price_comps(sold_date DESC);
CREATE INDEX idx_price_comps_sold_price ON price_comps(sold_price);

CREATE INDEX idx_alerts_listing_id ON alerts(listing_id);
CREATE INDEX idx_alerts_alert_type ON alerts(alert_type);
CREATE INDEX idx_alerts_sent_at ON alerts(sent_at DESC);

CREATE INDEX idx_demand_items_brand_model ON demand_items(brand, model);
CREATE INDEX idx_demand_items_urgency ON demand_items(urgency);
CREATE INDEX idx_demand_items_expires_at ON demand_items(expires_at);

CREATE INDEX idx_proxy_performance_proxy_ip ON proxy_performance(proxy_ip);
CREATE INDEX idx_proxy_performance_proxy_tier ON proxy_performance(proxy_tier);
CREATE INDEX idx_proxy_performance_last_used ON proxy_performance(last_used DESC);

CREATE INDEX idx_evasion_logs_source_id ON evasion_logs(source_id);
CREATE INDEX idx_evasion_logs_evasion_score ON evasion_logs(evasion_score);
CREATE INDEX idx_evasion_logs_created_at ON evasion_logs(created_at DESC);

-- Create triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_sources_updated_at BEFORE UPDATE ON sources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_listings_updated_at BEFORE UPDATE ON listings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_demand_items_updated_at BEFORE UPDATE ON demand_items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_proxy_performance_updated_at BEFORE UPDATE ON proxy_performance FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial sources data
INSERT INTO sources (name, type, base_url, evasion_level, priority) VALUES
('DOTmed Auctions', 'auction', 'https://www.dotmed.com/auction', 'high', 1),
('BidSpotter', 'auction', 'https://www.bidspotter.com', 'medium', 2),
('Proxibid', 'auction', 'https://www.proxibid.com', 'medium', 3),
('GovDeals', 'auction', 'https://www.govdeals.com', 'low', 4),
('GSA Auctions', 'auction', 'https://gsaauctions.gov', 'low', 5),
('eBay', 'marketplace', 'https://www.ebay.com', 'high', 6),
('Facebook Marketplace', 'marketplace', 'https://www.facebook.com/marketplace', 'high', 7),
('Craigslist', 'marketplace', 'https://craigslist.org', 'medium', 8),
('The Laser Agent', 'dealer', 'https://www.thelaseragent.com', 'medium', 9),
('Laser Service Solutions', 'dealer', 'https://www.laserservicesolutions.com', 'medium', 10),
('The Laser Warehouse', 'dealer', 'https://www.thelaserwarehouse.com', 'medium', 11),
('Hilditch Group', 'auction', 'https://www.hilditchgroup.com', 'medium', 12),
('British Medical Auctions', 'auction', 'https://www.britishmedicalauctions.co.uk', 'medium', 13);

-- Create views for common queries
CREATE VIEW hot_listings AS
SELECT l.*, s.name as source_name
FROM listings l
JOIN sources s ON l.source_id = s.id
WHERE l.score_overall >= 70
ORDER BY l.score_overall DESC, l.discovered_at DESC;

CREATE VIEW review_listings AS
SELECT l.*, s.name as source_name
FROM listings l
JOIN sources s ON l.source_id = s.id
WHERE l.score_overall >= 50 AND l.score_overall < 70
ORDER BY l.score_overall DESC, l.discovered_at DESC;

CREATE VIEW source_performance AS
SELECT 
    s.name,
    s.type,
    COUNT(l.id) as total_listings,
    AVG(l.score_overall) as avg_score,
    COUNT(CASE WHEN l.score_overall >= 70 THEN 1 END) as hot_count,
    COUNT(CASE WHEN l.score_overall >= 50 AND l.score_overall < 70 THEN 1 END) as review_count,
    s.success_rate_7d
FROM sources s
LEFT JOIN listings l ON s.id = l.source_id
GROUP BY s.id, s.name, s.type, s.success_rate_7d
ORDER BY avg_score DESC;
