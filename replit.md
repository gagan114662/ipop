# Autonomous Marketing Agency

## Project Overview
An AI-powered autonomous marketing agency that transforms brands through intelligent analysis and creative generation. The system analyzes any brand website, extracts products, researches competitors, and generates professional marketing creatives using Google's Gemini 2.5 Flash Image (Nano Banana) model.

## Current State
✅ Complete MVP implementation with:
- Brand website scraping and SKU extraction
- AI-powered brand quality analysis (OpenAI GPT-5)
- Autonomous competitor research
- Creative strategy development
- Product-specific creative generation (Gemini 2.5 Flash Image)
- Event-driven workflow orchestration (Motia)
- API endpoints for ingestion and retrieval

## Architecture
### Technology Stack
- **Backend**: Motia Framework (event-driven)
- **AI Models**: 
  - OpenAI GPT-5 for research and strategy
  - Google Gemini 2.5 Flash Image for creative generation
- **Language**: TypeScript
- **Web Scraping**: Cheerio + Axios

### Key Workflows
1. **Ingestion Flow**: POST /api/ingest-brand → process-brand event → autonomous execution
2. **Processing Flow**: Extract SKUs → Analyze brand → Research competitors → Develop strategy → Generate creatives
3. **Retrieval Flow**: GET /api/campaign/:id → Returns complete campaign data

## Recent Changes (Oct 23, 2025)
- ✅ Implemented complete autonomous marketing workflow
- ✅ Added defensive fallbacks for AI responses
- ✅ Set up OpenAI GPT-5 and Gemini 2.5 Flash Image integrations
- ✅ Created brand analysis, competitor research, and creative strategy services
- ✅ Built SKU-based creative generation system
- ✅ Implemented Motia event-driven architecture
- ✅ Removed old pet store example code

## API Endpoints
### POST /api/ingest-brand
Starts autonomous brand analysis workflow
```json
{
  "websiteUrl": "https://brand.com",
  "brandName": "Optional Brand Name"
}
```

### GET /api/campaign/:campaignId
Retrieves campaign results including:
- Products and SKUs
- Brand quality analysis (score, strengths, weaknesses)
- Competitor insights
- Creative strategy
- Generated creatives (image paths)

## User Preferences
- Focus on brands needing complete design overhauls
- Generate creatives featuring actual product SKUs
- Use OpenAI for deep research (not Pinterest API)
- Autonomous decision-making throughout the workflow

## Project Goals
Build a system that acts like a top creative agency (like Animal), analyzing brands holistically and generating elevated marketing campaigns with minimal human intervention.

## Environment Variables Required
- `OPENAI_API_KEY` - OpenAI API for GPT-5
- `GEMINI_API_KEY` - Google Gemini API for image generation

## Next Steps
- Test with real brand websites
- Add more creative format options
- Implement caching for expensive API calls
- Add rate limiting for API endpoints
