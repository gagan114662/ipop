# API Keys & Credentials Setup Guide

## 🔑 Required API Keys for Full Functionality

### Priority 1: Core Platform APIs (Required for Real Campaign Management)

#### 1. **Google Ads API** 
**Status:** 🔴 Required for Google Ads campaigns

**What you need:**
```bash
GOOGLE_ADS_DEVELOPER_TOKEN=xxxxx
GOOGLE_ADS_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=xxxxx
GOOGLE_ADS_REFRESH_TOKEN=xxxxx
GOOGLE_ADS_CUSTOMER_ID=xxx-xxx-xxxx  # Your Google Ads account
```

**How to get:**
1. Go to [Google Ads API Center](https://developers.google.com/google-ads/api/docs/first-call/overview)
2. Apply for API access (requires existing Google Ads account)
3. Create OAuth 2.0 credentials in Google Cloud Console
4. Generate refresh token using OAuth flow
5. Get your Customer ID from Google Ads account

**Documentation:** https://developers.google.com/google-ads/api/docs/start

**Approval Time:** 24-48 hours for developer token

---

#### 2. **Meta Marketing API (Facebook/Instagram)**
**Status:** 🔴 Required for Meta campaigns

**What you need:**
```bash
META_APP_ID=xxxxx
META_APP_SECRET=xxxxx
META_ACCESS_TOKEN=xxxxx  # Long-lived token (60 days)
META_AD_ACCOUNT_ID=act_xxxxx
```

**How to get:**
1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new app
3. Add "Marketing API" product
4. Get App ID and Secret from app dashboard
5. Use [Access Token Tool](https://developers.facebook.com/tools/accesstoken/) to generate token
6. Exchange short-lived token for long-lived token
7. Get Ad Account ID from Facebook Ads Manager

**Documentation:** https://developers.facebook.com/docs/marketing-apis

**Approval Time:** Instant for testing, requires Business Verification for production

---

#### 3. **TikTok Marketing API**
**Status:** 🟡 Optional (unless managing TikTok campaigns)

**What you need:**
```bash
TIKTOK_APP_ID=xxxxx
TIKTOK_SECRET=xxxxx
TIKTOK_ACCESS_TOKEN=xxxxx
TIKTOK_ADVERTISER_ID=xxxxx
```

**How to get:**
1. Go to [TikTok for Business](https://ads.tiktok.com/marketing_api/homepage)
2. Apply for Marketing API access
3. Create app in TikTok Ads Manager
4. Generate access token through OAuth
5. Get Advertiser ID from TikTok Ads Manager

**Documentation:** https://ads.tiktok.com/marketing_api/docs

**Approval Time:** 3-5 business days

---

#### 4. **LinkedIn Marketing API**
**Status:** 🟡 Optional (unless managing LinkedIn campaigns)

**What you need:**
```bash
LINKEDIN_CLIENT_ID=xxxxx
LINKEDIN_CLIENT_SECRET=xxxxx
LINKEDIN_ACCESS_TOKEN=xxxxx
LINKEDIN_AD_ACCOUNT_ID=xxxxx
```

**How to get:**
1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Create new app
3. Request Marketing Developer Platform access
4. Get Client ID and Secret
5. Complete OAuth 2.0 flow for access token
6. Get Ad Account ID from Campaign Manager

**Documentation:** https://docs.microsoft.com/en-us/linkedin/marketing/

**Approval Time:** 5-7 business days for Marketing Developer Platform

---

### Priority 2: Media Buying Integrators (Optional Enhancements)

#### 5. **Revealbot**
**Status:** 🟢 Optional enhancement

```bash
REVEALBOT_API_KEY=xxxxx
```

**How to get:**
1. Sign up at [Revealbot](https://revealbot.com/)
2. Go to Settings → API Keys
3. Generate new API key

**Use case:** Advanced automation rules and bulk operations

---

#### 6. **AdRoll**
**Status:** 🟢 Optional enhancement

```bash
ADROLL_API_KEY=xxxxx
ADROLL_API_SECRET=xxxxx
```

**How to get:**
1. Sign up at [AdRoll](https://www.adroll.com/)
2. Go to Account Settings → API Access
3. Generate API credentials

**Use case:** Retargeting and cross-platform campaigns

---

#### 7. **StackAdapt**
**Status:** 🟢 Optional enhancement

```bash
STACKADAPT_API_KEY=xxxxx
```

**How to get:**
1. Contact [StackAdapt](https://www.stackadapt.com/) sales
2. Request API access
3. Receive API key from account manager

**Use case:** Programmatic advertising

---

#### 8. **AdEspresso**
**Status:** 🟢 Optional enhancement

```bash
ADESPRESSO_API_KEY=xxxxx
```

**How to get:**
1. Sign up at [AdEspresso](https://adespresso.com/)
2. Go to Settings → Integrations → API
3. Generate API key

**Use case:** Facebook/Instagram campaign optimization

---

#### 9. **Madgicx**
**Status:** 🟢 Optional enhancement

```bash
MADGICX_API_KEY=xxxxx
```

**How to get:**
1. Sign up at [Madgicx](https://madgicx.com/)
2. Go to Settings → API Access
3. Generate API key

**Use case:** AI-powered Facebook ads optimization

---

### Priority 3: Infrastructure Services (Optional)

#### 10. **Google Cloud Platform (GCP)**
**Status:** 🟢 Optional (for Secret Manager, Cloud Run deployment)

```bash
GCP_PROJECT_ID=your-project-id
GCP_SECRET_MANAGER_ENABLED=true
```

**How to get:**
1. Create project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Secret Manager API
3. Create service account with Secret Manager permissions
4. Download service account key JSON

**Use case:** Secure credential storage

---

#### 11. **Sentry (Error Monitoring)**
**Status:** 🟢 Optional (recommended for production)

```bash
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
SENTRY_ENVIRONMENT=production
```

**How to get:**
1. Sign up at [Sentry.io](https://sentry.io/)
2. Create new project (Python/FastAPI)
3. Copy DSN from project settings

**Use case:** Error tracking and performance monitoring

---

## 🎯 Minimum Setup for Testing

### Option A: Full Testing (Recommended)
```bash
# Core (Required)
SECRET_KEY=your-random-32-char-secret-key-here
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379/0

# At least one platform (pick Google Ads OR Meta)
GOOGLE_ADS_DEVELOPER_TOKEN=xxxxx
GOOGLE_ADS_CLIENT_ID=xxxxx
# ... rest of Google Ads credentials
```

### Option B: Quick Demo (No External APIs)
```bash
# Just these three - uses test data
SECRET_KEY=any-random-string-at-least-32-characters-long
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379/0
```

Then run:
```bash
docker-compose up -d
docker-compose exec api python -m app.db.seed_test_data
```

---

## 📋 Setup Checklist

- [ ] Generate SECRET_KEY (32+ characters)
- [ ] Start MongoDB and Redis
- [ ] Apply for Google Ads API access (24-48h wait)
- [ ] Create Meta app and get credentials
- [ ] (Optional) Apply for TikTok API access
- [ ] (Optional) Apply for LinkedIn Marketing API
- [ ] (Optional) Sign up for integrators
- [ ] Update .env file with all credentials
- [ ] Test authentication
- [ ] Test platform connections
- [ ] Run first optimization

---

## 🚨 Security Notes

1. **Never commit credentials to Git**
   - All keys in .env file
   - .env is in .gitignore
   
2. **Use GCP Secret Manager in production**
   - Don't store credentials in .env on servers
   - Use GCP_SECRET_MANAGER_ENABLED=true
   
3. **Rotate tokens regularly**
   - Meta tokens expire every 60 days
   - Google Ads refresh tokens should be rotated
   - Set up token refresh automation

4. **Use least-privilege access**
   - Only grant API permissions needed
   - Separate dev and production credentials
   - Use service accounts where possible

---

## 💰 Cost Estimates

**Free Tier / Development:**
- Google Ads API: Free (requires active Ads account)
- Meta Marketing API: Free
- TikTok Marketing API: Free
- LinkedIn Marketing API: Free
- MongoDB: Free (Community Edition)
- Redis: Free (Open Source)

**Paid Services (Optional):**
- Revealbot: $49-499/month
- AdRoll: Custom pricing
- StackAdapt: Enterprise only
- AdEspresso: $49-259/month  
- Madgicx: $29-999/month
- Sentry: Free up to 5K events/month
- GCP Secret Manager: $0.06 per 10K operations

**Recommendation:** Start with free platform APIs only, add integrators later if needed.
