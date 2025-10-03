# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LaserIntelligenceItem(scrapy.Item):
    # Core identification
    id = scrapy.Field()
    title = scrapy.Field()
    brand = scrapy.Field()
    model = scrapy.Field()
    
    # Equipment details
    condition = scrapy.Field()
    price = scrapy.Field()
    location = scrapy.Field()
    description = scrapy.Field()
    
    # Source information
    url = scrapy.Field()
    source = scrapy.Field()
    images = scrapy.Field()
    
    # Metadata
    discovered_at = scrapy.Field()
    score_overall = scrapy.Field()
    
    # Additional fields
    margin_estimate = scrapy.Field()
    status = scrapy.Field()
