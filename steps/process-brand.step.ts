import { EventConfig, Handlers } from 'motia';
import { z } from 'zod';
import { scrapeWebsite } from '../services/web-scraper';
import { analyzeBrand } from '../services/brand-analyzer';
import { researchCompetitors } from '../services/competitor-researcher';
import { developCreativeStrategy } from '../services/creative-strategist';
import { generateCreativesForAllProducts } from '../services/creative-generator';
import { MarketingCampaign } from '../services/marketing-types';

export const config: EventConfig = {
  type: 'event',
  name: 'ProcessBrand',
  description: 'Autonomous workflow that extracts SKUs, analyzes brand, researches competitors, and generates elevated creatives',
  flows: ['marketing-agency'],
  subscribes: ['process-brand'],
  emits: ['campaign-complete'],
  input: z.object({
    campaignId: z.string(),
    websiteUrl: z.string(),
    brandName: z.string(),
    timestamp: z.string(),
  }),
};

export const handler: Handlers['ProcessBrand'] = async (input, { logger, state, emit, traceId }) => {
  logger.info('Processing brand workflow started', { input, traceId });

  const { campaignId, websiteUrl, brandName } = input;

  try {
    // Initialize campaign
    const campaign: MarketingCampaign = {
      id: campaignId,
      websiteUrl,
      brandName,
      status: 'processing',
      createdAt: new Date().toISOString(),
      products: [],
      visualData: {
        colors: [],
        typography: [],
        imageUrls: [],
        rawHtml: '',
      },
      generatedCreatives: [],
    };

    await state.set('campaigns', campaignId, campaign);

    // Step 1: Scrape website and extract SKUs
    logger.info('Step 1: Scraping website and extracting SKUs', { websiteUrl });
    const { products, visualData, rawContent } = await scrapeWebsite(websiteUrl);
    logger.info('Scraping complete', { productsFound: products.length });

    campaign.products = products;
    campaign.visualData = visualData;
    await state.set('campaigns', campaignId, campaign);

    // Step 2: Analyze brand quality and design
    logger.info('Step 2: Analyzing brand quality and design');
    const brandAnalysis = await analyzeBrand(websiteUrl, visualData, rawContent, products);
    logger.info('Brand analysis complete', { qualityScore: brandAnalysis.qualityScore, needsOverhaul: brandAnalysis.needsOverhaul });

    campaign.brandAnalysis = brandAnalysis;
    await state.set('campaigns', campaignId, campaign);

    // Step 3: Research competitors
    logger.info('Step 3: Researching competitors');
    const competitorAnalysis = await researchCompetitors(brandName, brandAnalysis.industry, websiteUrl);
    logger.info('Competitor research complete', { competitorsFound: competitorAnalysis.competitors.length });

    campaign.competitorAnalysis = competitorAnalysis;
    await state.set('campaigns', campaignId, campaign);

    // Step 4: Develop creative strategy
    logger.info('Step 4: Developing elevated creative strategy');
    const creativeStrategy = await developCreativeStrategy(brandAnalysis, competitorAnalysis, products);
    logger.info('Creative strategy developed', { campaignConcepts: creativeStrategy.campaignConcepts.length });

    campaign.creativeStrategy = creativeStrategy;
    await state.set('campaigns', campaignId, campaign);

    // Step 5: Generate creatives for each SKU
    logger.info('Step 5: Generating creatives for products');
    
    // Only generate creatives if we have products and strategy
    let generatedCreatives: any[] = [];
    if (products.length > 0 && creativeStrategy) {
      generatedCreatives = await generateCreativesForAllProducts(
        products,
        creativeStrategy,
        ['social-post', 'product-ad'],
        2 // 2 variations per format
      );
      logger.info('Creative generation complete', { creativesGenerated: generatedCreatives.length });
    } else {
      logger.warn('Skipping creative generation - no products or strategy available');
    }

    campaign.generatedCreatives = generatedCreatives;
    campaign.status = 'completed';
    campaign.completedAt = new Date().toISOString();
    await state.set('campaigns', campaignId, campaign);

    // Emit completion event
    await emit({
      topic: 'campaign-complete',
      data: {
        campaignId,
        brandName,
        productsProcessed: products.length,
        creativesGenerated: generatedCreatives.length,
        qualityScore: brandAnalysis.qualityScore,
        completedAt: campaign.completedAt,
      },
    });

    logger.info('Brand processing workflow completed successfully', {
      campaignId,
      productsProcessed: products.length,
      creativesGenerated: generatedCreatives.length,
    });
  } catch (error: any) {
    logger.error('Brand processing failed', { error: error.message, campaignId });

    const failedCampaign = await state.get<MarketingCampaign>('campaigns', campaignId);
    if (failedCampaign) {
      failedCampaign.status = 'failed';
      failedCampaign.error = error.message;
      await state.set('campaigns', campaignId, failedCampaign);
    }

    throw error;
  }
};
