# Facebook Groups Integration Setup

This guide explains how to set up Facebook Groups access for laser equipment discovery.

## Overview

We have three methods for accessing Facebook Groups:

1. **Facebook Graph API** (Recommended) - Most reliable and compliant
2. **Selenium/Playwright with User Session** - For groups that don't allow API access
3. **Reddit Integration** - Alternative social platform

## Method 1: Facebook Graph API (Recommended)

### Prerequisites

1. **Facebook Developer Account**: Create at [developers.facebook.com](https://developers.facebook.com)
2. **Facebook App**: Create a new app with appropriate permissions
3. **User Access Token**: Generate a long-lived access token

### Setup Steps

#### 1. Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com)
2. Click "Create App" → "Consumer" → "Next"
3. Fill in app details:
   - **App Name**: "Laser Equipment Intelligence"
   - **App Contact Email**: Your email
   - **App Purpose**: "Educational Research"

#### 2. Configure App Permissions

1. Go to App Dashboard → "App Review" → "Permissions and Features"
2. Request these permissions:
   - `groups_access_member_info` - Access group member information
   - `groups_show_list` - Show groups the user belongs to
   - `groups_read_member_content` - Read group content
   - `pages_read_engagement` - Read page content

#### 3. Generate Access Token

**Option A: Using Graph API Explorer**
1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Add permissions: `groups_access_member_info`, `groups_show_list`, `groups_read_member_content`
4. Generate User Access Token
5. Exchange for Long-lived Token (60 days)

**Option B: Using Facebook Login SDK**
```python
# Generate access token programmatically
import requests

def get_long_lived_token(short_token, app_id, app_secret):
    url = f"https://graph.facebook.com/oauth/access_token"
    params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': short_token
    }
    response = requests.get(url, params=params)
    return response.json()['access_token']
```

#### 4. Environment Configuration

Create `.env` file:
```bash
# Facebook API Configuration
FACEBOOK_ACCESS_TOKEN=your_long_lived_access_token_here
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here

# Optional: For session-based access
FACEBOOK_EMAIL=your_facebook_email@example.com
FACEBOOK_PASSWORD=your_facebook_password
```

#### 5. Test API Access

```bash
# Test the API spider
cd laser-equipment-intelligence
source venv/bin/activate
PYTHONPATH=src scrapy crawl facebook_groups_api -L INFO
```

## Method 2: Selenium/Playwright with User Session

### Prerequisites

1. **Facebook Account**: Must be member of target groups
2. **Two-Factor Authentication**: Disabled (or use app passwords)
3. **Browser Profile**: Persistent session storage

### Setup Steps

#### 1. Join Target Groups

Manually join these Facebook groups:
- MedicalEquipmentForSale
- UsedMedicalEquipment
- AestheticEquipment
- LaserEquipmentSales
- MedicalDeviceTrading
- CosmeticEquipment
- DermatologyEquipment
- MedicalAuction
- EquipmentLiquidation
- MedicalSurplus

#### 2. Configure Credentials

Set environment variables:
```bash
export FACEBOOK_EMAIL="your_facebook_email@example.com"
export FACEBOOK_PASSWORD="your_facebook_password"
```

#### 3. Test Session Access

```bash
# Test the session spider
cd laser-equipment-intelligence
source venv/bin/activate
PYTHONPATH=src scrapy crawl facebook_groups_session -L INFO
```

## Method 3: Reddit Integration

### Setup Steps

#### 1. No Authentication Required

Reddit allows public access to most subreddits.

#### 2. Test Reddit Spider

```bash
# Test the Reddit spider
cd laser-equipment-intelligence
source venv/bin/activate
PYTHONPATH=src scrapy crawl reddit -L INFO
```

## Target Groups and Subreddits

### Facebook Groups
- **MedicalEquipmentForSale** - Medical equipment marketplace
- **UsedMedicalEquipment** - Used medical equipment sales
- **AestheticEquipment** - Aesthetic and cosmetic equipment
- **LaserEquipmentSales** - Laser equipment specific
- **MedicalDeviceTrading** - Medical device trading
- **CosmeticEquipment** - Cosmetic equipment sales
- **DermatologyEquipment** - Dermatology equipment
- **MedicalAuction** - Medical equipment auctions
- **EquipmentLiquidation** - Equipment liquidation sales
- **MedicalSurplus** - Medical surplus equipment

### Reddit Subreddits
- **r/medicaldevices** - Medical device discussions
- **r/UsedGear** - Used equipment sales
- **r/Flipping** - Equipment flipping and resale
- **r/laser** - Laser equipment discussions
- **r/aesthetic** - Aesthetic equipment
- **r/dermatology** - Dermatology equipment
- **r/cosmeticsurgery** - Cosmetic surgery equipment
- **r/medicalequipment** - Medical equipment general
- **r/usedmedical** - Used medical equipment
- **r/equipmentforsale** - Equipment for sale

## Data Extraction

### Facebook Groups Data
- Post content and title
- Author information
- Post timestamp
- Images and attachments
- Comments and engagement
- Contact information (emails, phones)
- Price information
- Location data

### Reddit Data
- Post content and title
- Author information
- Post score and comments
- Subreddit information
- Contact information
- Price information
- Location data

## Rate Limiting and Compliance

### Facebook API Limits
- **User Access Token**: 200 calls per hour per user
- **App Access Token**: 200 calls per hour per app
- **Long-lived Token**: 60 days validity

### Facebook Session Limits
- **Heavy Throttling**: 2-3 minutes between requests
- **Session Limits**: 10 requests per session
- **Group Access**: Must be member of target groups

### Reddit Limits
- **Moderate Throttling**: 3-8 seconds between requests
- **No Authentication**: Public access only
- **Rate Limits**: 200 requests per hour

## Monitoring and Alerts

### Success Metrics
- Posts discovered per session
- Laser equipment matches
- Contact information extracted
- Price information found
- Location data captured

### Error Handling
- API rate limit exceeded
- Authentication failures
- Group access denied
- Network timeouts
- Parsing errors

## Security Considerations

### API Access
- Store tokens securely
- Rotate tokens regularly
- Monitor usage patterns
- Implement rate limiting

### Session Access
- Use dedicated Facebook account
- Enable 2FA for security
- Monitor account activity
- Use residential proxies

### Data Privacy
- No PII collection
- Contact info redaction
- Secure data storage
- Compliance logging

## Troubleshooting

### Common Issues

1. **"Invalid Access Token"**
   - Check token expiration
   - Regenerate long-lived token
   - Verify app permissions

2. **"Group Access Denied"**
   - Ensure user is member of group
   - Check group privacy settings
   - Verify API permissions

3. **"Rate Limit Exceeded"**
   - Implement exponential backoff
   - Reduce request frequency
   - Use multiple tokens

4. **"Login Failed"**
   - Check credentials
   - Disable 2FA temporarily
   - Use app passwords

### Debug Mode

Enable debug logging:
```bash
PYTHONPATH=src scrapy crawl facebook_groups_api -L DEBUG
```

## Production Deployment

### Environment Variables
```bash
# Production environment
export FACEBOOK_ACCESS_TOKEN="production_token"
export FACEBOOK_APP_ID="production_app_id"
export FACEBOOK_APP_SECRET="production_app_secret"
export FACEBOOK_EMAIL="production_email"
export FACEBOOK_PASSWORD="production_password"
```

### Monitoring
- Set up Prometheus metrics
- Configure Grafana dashboards
- Implement Slack alerts
- Monitor API usage

### Scaling
- Use multiple access tokens
- Implement request queuing
- Add proxy rotation
- Monitor rate limits

## Legal Compliance

### Facebook Terms of Service
- Respect rate limits
- Use official APIs when possible
- Follow data usage policies
- Implement proper attribution

### Data Protection
- No personal information collection
- Secure data transmission
- Regular security audits
- Compliance documentation

### Best Practices
- Human-like behavior simulation
- Respectful data collection
- Transparent data usage
- Regular compliance reviews
