# AI Creative Generation - Award-Winning Creatives

## Overview

The AI Creative Generation system uses OpenAI's GPT-4 Vision and DALL-E 3 to generate award-winning ad creatives based on industry best practices. It takes **two image inputs**:

1. **Product Image** - Your product photo
2. **Reference Image(s)** - Award-winning creatives automatically found for your product category

The system analyzes both images to understand successful creative patterns and generates new creatives that combine your product with proven visual strategies.

## How It Works

### Step 1: Reference Image Discovery
The system automatically finds award-winning reference images relevant to your product category from:
- Curated database of award-winning creatives
- Industry-recognized campaigns
- Platform-specific best performers
- Category-specific successful patterns

### Step 2: AI Analysis (GPT-4 Vision)
GPT-4 Vision analyzes:
- **Product Image**: Key features, unique elements, visual identity
- **Reference Images**: Successful design patterns, color schemes, composition strategies
- **Platform Requirements**: Platform-specific best practices
- **Category Trends**: Industry-specific successful approaches

### Step 3: Creative Concept Generation
Based on the analysis, the system creates a detailed creative concept including:
- Visual style and design direction
- Composition and layout strategy
- Color palette and mood
- Typography approach
- Key visual elements to highlight
- Emotional tone and messaging
- Platform-specific optimizations

### Step 4: Image Generation (DALL-E 3)
DALL-E 3 generates the final creative image based on the concept, optimized for:
- Award-winning visual quality
- Platform specifications (Meta, Google, TikTok, LinkedIn)
- Professional advertising standards
- Brand consistency

## API Endpoint

### POST `/api/v1/creatives/generate-ai`

Generate award-winning creatives using AI.

**Authentication**: Required (Bearer token)

**Request Body**:
```json
{
  "product_image_url": "https://example.com/product.jpg",
  "category": "fashion",
  "platform": "meta",
  "brand_name": "Your Brand",
  "brand_guidelines": "Modern, minimalist, use blue tones",
  "key_message": "Summer Collection 2024",
  "target_audience": "Women 25-35, fashion-forward",
  "cta": "shop_now",
  "generate_variants": 3,
  "creative_id_prefix": "summer_2024",
  "campaign_id": "campaign_123"
}
```

**Required Fields**:
- `product_image_url` (string): URL to your product image
- `category` (string): Product category
- `platform` (string): Target platform

**Optional Fields**:
- `brand_name` (string): Brand name
- `brand_guidelines` (string): Brand style guidelines
- `key_message` (string): Marketing message
- `target_audience` (string): Target audience description
- `cta` (string): Call-to-action type
- `generate_variants` (integer, 1-5): Number of variants (default: 1)
- `creative_id_prefix` (string): Prefix for creative IDs
- `campaign_id` (string): Associate with campaign

**Supported Categories**:
- `ecommerce` - Online store products
- `fashion` - Clothing, accessories
- `beauty` - Cosmetics, skincare
- `food` - Food products, restaurants
- `tech` - Technology products, software
- `automotive` - Vehicles, automotive
- `travel` - Tourism, hotels
- `finance` - Fintech, banking
- `health` - Healthcare, wellness
- `real_estate` - Property, real estate

**Supported Platforms**:
- `meta` - Facebook/Instagram
- `google` - Google Ads
- `tiktok` - TikTok
- `linkedin` - LinkedIn

**Response**:
```json
{
  "status": "success",
  "results": [
    {
      "generated_image_url": "https://oaidalleapiprodscus.blob.core.windows.net/...",
      "revised_prompt": "Professional fashion ad showing...",
      "concept": {
        "concept_text": "Detailed creative concept...",
        "tokens_used": 1500,
        "model": "gpt-4-turbo-preview"
      },
      "analysis": {
        "analysis_text": "Product analysis and insights...",
        "tokens_used": 800,
        "model": "gpt-4-vision-preview"
      },
      "reference_images": [
        {
          "url": "https://example.com/reference1.jpg",
          "title": "Award-winning fashion campaign",
          "source": "curated_database"
        }
      ],
      "metadata": {
        "category": "fashion",
        "platform": "meta",
        "generated_at": "2024-01-15T10:30:00Z",
        "model": "dall-e-3"
      }
    }
  ],
  "creatives_created": [
    "summer_2024_fashion_meta_20240115_103000_1",
    "summer_2024_fashion_meta_20240115_103000_2",
    "summer_2024_fashion_meta_20240115_103000_3"
  ],
  "total_generated": 3,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The following packages are required:
- `openai>=1.12.0` - OpenAI API client
- `pillow>=10.2.0` - Image processing
- `beautifulsoup4>=4.12.3` - Web scraping
- `playwright>=1.41.0` - Browser automation

### 2. Configure Environment Variables

Add to your `.env` file:

```bash
# AI Creative Generation
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4-vision-preview
OPENAI_IMAGE_MODEL=dall-e-3
CREATIVE_GENERATION_MAX_RETRIES=3
REFERENCE_IMAGE_CACHE_TTL=86400  # 24 hours
```

### 3. Database Collections

The system uses these MongoDB collections:

**reference_creatives** - Curated award-winning creatives:
```javascript
{
  "category": "fashion",
  "image_url": "https://...",
  "title": "Nike Air Max Campaign",
  "description": "Award-winning campaign...",
  "platform": "meta",
  "quality_score": 0.95,
  "is_award_winning": true,
  "award_info": "Cannes Lions Gold 2023",
  "brand": "Nike",
  "year": 2023
}
```

**reference_cache** - Cached reference searches:
```javascript
{
  "cache_key": "md5_hash",
  "category": "fashion",
  "platform": "meta",
  "references": [...],
  "expires_at": ISODate("2024-01-16T10:00:00Z"),
  "created_at": ISODate("2024-01-15T10:00:00Z")
}
```

### 4. Seed Reference Database (Optional)

To populate the curated reference database:

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client.ipop_media_buying

# Add curated references
db.reference_creatives.insert_many([
    {
        "category": "fashion",
        "image_url": "https://example.com/award-winning-ad.jpg",
        "title": "Fashion Brand Award Winner",
        "description": "High-performing fashion ad",
        "platform": "meta",
        "quality_score": 0.9,
        "is_award_winning": True,
        "award_info": "Industry Award 2023",
        "brand": "Brand Name",
        "year": 2023
    },
    # Add more references...
])

# Create indexes
db.reference_creatives.create_index([("category", 1), ("quality_score", -1)])
db.reference_cache.create_index("cache_key", unique=True)
db.reference_cache.create_index("expires_at", expireAfterSeconds=0)
```

## Usage Examples

### Example 1: Generate Single Fashion Creative

```bash
curl -X POST "http://localhost:8000/api/v1/creatives/generate-ai" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_image_url": "https://example.com/dress.jpg",
    "category": "fashion",
    "platform": "meta",
    "brand_name": "StyleCo",
    "key_message": "Summer Collection - Limited Time",
    "target_audience": "Women 25-35, fashion-conscious",
    "cta": "shop_now"
  }'
```

### Example 2: Generate Multiple Variants for A/B Testing

```bash
curl -X POST "http://localhost:8000/api/v1/creatives/generate-ai" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_image_url": "https://example.com/product.jpg",
    "category": "tech",
    "platform": "google",
    "brand_name": "TechBrand",
    "key_message": "Revolutionary New Feature",
    "generate_variants": 3
  }'
```

### Example 3: With Brand Guidelines

```bash
curl -X POST "http://localhost:8000/api/v1/creatives/generate-ai" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_image_url": "https://example.com/product.jpg",
    "category": "beauty",
    "platform": "instagram",
    "brand_name": "BeautyBrand",
    "brand_guidelines": "Use soft pastel colors, minimalist design, luxury feel. Avoid busy patterns. Focus on product clarity.",
    "key_message": "Natural Beauty, Elevated",
    "target_audience": "Women 28-45, premium segment",
    "cta": "learn_more",
    "campaign_id": "beauty_launch_2024"
  }'
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      API Endpoint                            │
│              POST /api/v1/creatives/generate-ai             │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              AI Creative Generator Service                   │
│  - Orchestrates the generation process                      │
│  - Manages GPT-4 Vision and DALL-E 3 calls                 │
└─────┬───────────────────────────────────────────────┬───────┘
      │                                                 │
      ▼                                                 ▼
┌─────────────────────────┐              ┌────────────────────────┐
│  Reference Image Finder │              │   OpenAI Services      │
│  - Finds award-winning  │              │   - GPT-4 Vision       │
│    references           │              │   - DALL-E 3           │
│  - Manages cache        │              │                        │
│  - Curated database     │              │                        │
└─────────────────────────┘              └────────────────────────┘
```

## Key Features

✅ **Dual Image Input**: Product + Reference images
✅ **Automatic Reference Discovery**: Finds relevant award-winning examples
✅ **AI-Powered Analysis**: GPT-4 Vision analyzes both images
✅ **Industry Best Practices**: Leverages proven creative patterns
✅ **Platform Optimization**: Tailored for each ad platform
✅ **Multiple Variants**: Generate A/B test variants
✅ **Full Metadata**: Detailed generation info for transparency
✅ **Auto-Save**: Creatives saved directly to database
✅ **Caching**: Reference images cached for performance

## Cost Considerations

**OpenAI API Costs** (approximate):
- GPT-4 Vision analysis: ~$0.01-0.03 per generation
- DALL-E 3 HD image: ~$0.08 per image
- Total per creative: ~$0.10-0.15

**Optimization Tips**:
- Use reference cache (24hr default)
- Batch generate multiple variants at once
- Curate high-quality reference database to reduce online searches

## Troubleshooting

### Error: "OPENAI_API_KEY not configured"
**Solution**: Add `OPENAI_API_KEY` to your `.env` file

### Error: "No reference images found for category"
**Solution**:
1. Seed the `reference_creatives` collection with curated examples
2. Use fallback images (automatic)
3. Check category name spelling

### Generated image doesn't match brand
**Solution**: Provide detailed `brand_guidelines` in the request

### Rate limiting errors
**Solution**:
1. Increase `CREATIVE_GENERATION_MAX_RETRIES`
2. Add delays between requests
3. Upgrade OpenAI tier

## Future Enhancements

- [ ] Web scraping for live reference discovery
- [ ] Video creative generation
- [ ] Multi-image carousel generation
- [ ] Brand style learning from existing creatives
- [ ] Performance prediction based on reference data
- [ ] Custom fine-tuned models for specific industries

## Support

For issues or questions:
1. Check logs: `structlog` provides detailed generation logs
2. Review generated metadata in creative document
3. Test with different categories and platforms
4. Verify OpenAI API key and quota
