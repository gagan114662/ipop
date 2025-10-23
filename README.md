# 🎨 Autonomous Marketing Agency

An AI-powered autonomous marketing agency that transforms brands through intelligent analysis and creative generation.

## 🚀 What It Does

This system takes any brand website and:
1. **Extracts all product SKUs** - Scrapes the website to identify products
2. **Analyzes brand quality** - Evaluates design, messaging, and visual identity
3. **Researches competitors** - Identifies and analyzes 5-7 top competitors
4. **Develops creative strategy** - Uses AI to create elevated brand direction
5. **Generates product creatives** - Creates professional marketing visuals for each SKU using Google's Gemini 2.5 Flash Image (Nano Banana)

Perfect for brands that need a complete design overhaul or modern creative campaigns!

## 🏗️ Architecture

### Powered By
- **OpenAI GPT-5** - Deep brand research, competitor analysis, strategic direction
- **Google Gemini 2.5 Flash Image (Nano Banana)** - Professional creative generation
- **Motia Framework** - Event-driven workflow orchestration

### Project Structure

```
├── services/                      # Core business logic
│   ├── openai-client.ts          # OpenAI GPT-5 integration
│   ├── gemini-client.ts          # Gemini image generation
│   ├── web-scraper.ts            # SKU extraction & brand data collection
│   ├── brand-analyzer.ts         # Brand quality assessment
│   ├── competitor-researcher.ts  # Competitive analysis
│   ├── creative-strategist.ts    # Strategic direction development
│   ├── creative-generator.ts     # Image generation for SKUs
│   └── marketing-types.ts        # TypeScript types
├── steps/                         # Motia workflow steps
│   ├── ingest-brand.step.ts      # API endpoint to start workflow
│   ├── process-brand.step.ts     # Main autonomous workflow
│   ├── campaign-complete.step.ts # Completion handler
│   └── get-campaign.step.ts      # Results retrieval API
└── generated-creatives/           # Output folder for creatives
```

## 🎯 API Endpoints

### Start Brand Analysis
```bash
POST /api/ingest-brand
{
  "websiteUrl": "https://example-brand.com",
  "brandName": "Example Brand" // optional
}
```

Returns:
```json
{
  "campaignId": "campaign_1234567890_abc123",
  "message": "Brand ingestion started...",
  "status": "processing"
}
```

### Get Campaign Results
```bash
GET /api/campaign/{campaignId}
```

Returns complete campaign data including:
- Extracted products with SKUs
- Brand quality analysis (score, strengths, weaknesses)
- Competitor insights
- Creative strategy
- Generated product creatives (images saved to disk)

## 🔧 Setup

### Prerequisites
- Node.js 18+
- OpenAI API Key
- Google Gemini API Key

### Environment Variables
Set these in Replit Secrets:
- `OPENAI_API_KEY` - From https://platform.openai.com/api-keys
- `GEMINI_API_KEY` - From https://aistudio.google.com/apikey

### Run Development Server
```bash
npm run dev
```

Opens workbench at: http://localhost:5000

## 📊 Workflow

```
Website URL → SKU Extraction → Brand Analysis → Competitor Research
     ↓              ↓                ↓                  ↓
  Products    Visual Data    Quality Score    Market Insights
     ↓              ↓                ↓                  ↓
     └──────────────┴────────────────┴──────────────────┘
                            ↓
                   Creative Strategy Development
                            ↓
              ┌─────────────┴─────────────┐
              ↓                           ↓
     Elevated Brand Identity    Campaign Concepts
              ↓                           ↓
              └─────────────┬─────────────┘
                            ↓
              Generate Creatives for Each SKU
              (Social Posts, Ads, Lifestyle, Packaging)
                            ↓
                    Save to Disk + Database
```

## 🎨 Creative Formats

For each product SKU, the system generates:
- **Social Media Posts** - Instagram/Pinterest-ready visuals
- **Product Ads** - High-end advertising creatives
- **Lifestyle Shots** - Products in aspirational contexts
- **Packaging Mockups** - Modern packaging designs

Each format gets **2 variations** for A/B testing.

## 🧠 AI Decision Making

The system autonomously:
- Scores brand quality (1-100)
- Decides if brand needs complete overhaul (< 60 score)
- Identifies industry category and target audience
- Researches cultural trends and market gaps
- Develops differentiation strategy
- Creates brand elevation roadmap
- Generates on-brand but elevated creative direction

## 📦 Technologies

- **Motia** - Event-driven backend framework
- **OpenAI API** - GPT-5 for research & strategy
- **Google Gemini API** - Image generation (Nano Banana)
- **Cheerio** - Web scraping
- **Axios** - HTTP client
- **TypeScript** - Type safety
- **Zod** - Schema validation

## 🔐 Security

- API keys stored securely in environment variables
- No sensitive data logged
- Generated images stored locally with unique IDs

## 📝 License

MIT

---

**Built with Motia Framework** - An event-driven backend for modern workflows
