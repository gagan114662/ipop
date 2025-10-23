# 🚀 How to Use Your Autonomous Marketing Agency

## Quick Start

Your marketing agency is now running! Here's how to transform any brand:

### 1. Start a Brand Analysis

Send a POST request to ingest a brand's website:

```bash
curl -X POST http://localhost:5000/api/ingest-brand \
  -H "Content-Type: application/json" \
  -d '{
    "websiteUrl": "https://example-brand.com",
    "brandName": "Example Brand"
  }'
```

**Response:**
```json
{
  "campaignId": "campaign_1729717200_abc123xyz",
  "message": "Brand ingestion started. Your autonomous marketing agency is now analyzing the brand and generating creatives.",
  "status": "processing"
}
```

### 2. Check Campaign Status

Use the `campaignId` to retrieve results:

```bash
curl http://localhost:5000/api/campaign/campaign_1729717200_abc123xyz
```

**Response includes:**
```json
{
  "campaign": {
    "id": "campaign_1729717200_abc123xyz",
    "websiteUrl": "https://example-brand.com",
    "brandName": "Example Brand",
    "status": "completed",
    
    "products": [
      {
        "sku": "PROD-001",
        "name": "Wireless Headphones",
        "price": "$199",
        "imageUrl": "https://...",
        "description": "..."
      }
    ],
    
    "brandAnalysis": {
      "qualityScore": 45,
      "needsOverhaul": true,
      "strengths": ["Clear product catalog", "Fast shipping"],
      "weaknesses": ["Outdated design", "Inconsistent branding"],
      "industry": "Consumer Electronics",
      "targetAudience": "Tech-savvy millennials"
    },
    
    "competitorAnalysis": {
      "competitors": [
        {
          "name": "Competitor A",
          "strengths": ["Modern design", "Strong social presence"],
          "visualStyle": "Minimalist, monochrome"
        }
      ],
      "marketGaps": ["Sustainability messaging", "Lifestyle focus"],
      "differentiationOpportunities": ["Focus on design quality"]
    },
    
    "creativeStrategy": {
      "elevatedBrandIdentity": {
        "colorPalette": ["#2C3E50", "#ECF0F1", "#E74C3C"],
        "typography": {
          "primary": "Inter",
          "secondary": "Playfair Display"
        },
        "visualStyle": "Clean, modern, premium",
        "mood": ["sophisticated", "trustworthy", "innovative"]
      },
      "campaignConcepts": [
        {
          "name": "Sound Elevated",
          "description": "Premium audio for modern life",
          "visualDirection": "Minimalist product shots with premium lifestyle contexts"
        }
      ]
    },
    
    "generatedCreatives": [
      {
        "skuId": "PROD-001",
        "productName": "Wireless Headphones",
        "format": "social-post",
        "concept": "Sound Elevated",
        "imagePath": "generated-creatives/PROD_001_social-post_v0_1729717456789.png",
        "prompt": "Create a stunning social media post for Wireless Headphones..."
      },
      {
        "skuId": "PROD-001",
        "productName": "Wireless Headphones",
        "format": "product-ad",
        "concept": "Sound Elevated",
        "imagePath": "generated-creatives/PROD_001_product-ad_v0_1729717459012.png",
        "prompt": "Create a premium product advertisement..."
      }
    ]
  }
}
```

## 🎯 What Happens Automatically

When you submit a brand website, the system:

1. **Scrapes the website** to find all products and SKUs
2. **Analyzes the brand** using AI to score design quality (1-100)
3. **Identifies the industry** and target audience
4. **Researches 5-7 competitors** and market trends
5. **Develops a creative strategy** with:
   - Elevated color palette
   - Modern typography recommendations
   - New visual style direction
   - Campaign concepts
6. **Generates professional creatives** for each product:
   - Social media posts
   - Product ads
   - 2 variations of each format
7. **Saves all images** to the `generated-creatives/` folder

## 📊 Understanding Brand Quality Scores

- **80-100**: Excellent branding - Minor refinements suggested
- **60-79**: Good branding - Targeted improvements needed
- **40-59**: Needs overhaul - Significant transformation required
- **0-39**: Poor branding - Complete redesign necessary

Brands scoring **below 60** automatically get "transformation" strategies focused on complete elevation.

## 🎨 Creative Formats

Each SKU gets these creative variations:

### Social Post
- Instagram/Pinterest-ready
- Product-focused with lifestyle elements
- Modern, clean styling

### Product Ad
- High-end advertising creative
- Magazine-quality product shots
- Premium positioning

### Variations
- Each format gets 2 different concepts
- Based on different campaign themes
- Ready for A/B testing

## 🔍 Example Brands to Try

Good test cases:
- E-commerce stores with product catalogs
- Fashion/apparel brands
- Consumer electronics sites
- Home goods retailers
- Beauty/cosmetics brands

## 💡 Tips

1. **Wait time**: Processing takes 2-5 minutes depending on:
   - Number of products found
   - Complexity of competitor research
   - Image generation time

2. **Best results**: Brands with:
   - Clear product listings
   - Multiple SKUs to feature
   - Existing brand identity to elevate

3. **Check status**: Poll the `/api/campaign/:id` endpoint every 30 seconds

## 🛠️ API Reference

### Health Check
```bash
GET /api/health
```
Verifies system is running and API keys are configured.

### Ingest Brand
```bash
POST /api/ingest-brand
Body: { "websiteUrl": "https://...", "brandName": "..." }
```
Starts the autonomous workflow.

### Get Campaign
```bash
GET /api/campaign/:campaignId
```
Retrieves complete campaign results.

## 📁 Generated Assets

All creative images are saved to:
```
generated-creatives/
├── SKU001_social-post_v0_timestamp.png
├── SKU001_social-post_v1_timestamp.png
├── SKU001_product-ad_v0_timestamp.png
├── SKU001_product-ad_v1_timestamp.png
└── ...
```

Each filename contains:
- SKU identifier
- Creative format
- Variation number
- Timestamp

---

**Ready to transform brands? Start by hitting the `/api/ingest-brand` endpoint!** 🚀
