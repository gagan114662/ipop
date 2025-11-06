import { EventConfig, Handlers } from 'motia';
import { z } from 'zod';
import { scrapeWebsite } from '../services/web-scraper';
import { analyzeBrand } from '../services/brand-analyzer';
import { researchCompetitors } from '../services/competitor-researcher';
import { developCreativeStrategy } from '../services/creative-strategist';
import { curateReferenceLibrary } from '../services/reference-curator';
import { generateCreativesForAllProducts } from '../services/creative-generator';
import { resizeCreativeForAllFormats, getHighPriorityFormats } from '../services/creative-resizer';
import { MarketingCampaign } from '../services/marketing-types';
import { buildAssetInsights } from '../services/asset-insights';

export const config: EventConfig = {
  type: 'event',
  name: 'ProcessBrand',
  description: 'Autonomous workflow that extracts SKUs, analyzes brand, researches competitors, curates award references, and generates elevated creatives',
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
      referenceLibrary: [],
      assetInsights: {},
    };

    await state.set('campaigns', campaignId, campaign);

    logger.info('Step 1: Scraping website and extracting SKUs', { websiteUrl });
    const { products, visualData, rawContent } = await scrapeWebsite(websiteUrl);
    logger.info('Scraping complete', { productsFound: products.length });

    campaign.products = products;
    campaign.visualData = visualData;
    await state.set('campaigns', campaignId, campaign);

    logger.info('Step 2: Analyzing brand quality and design');
    const brandAnalysis = await analyzeBrand(websiteUrl, visualData, rawContent, products);
    logger.info('Brand analysis complete', { qualityScore: brandAnalysis.qualityScore, needsOverhaul: brandAnalysis.needsOverhaul });

    campaign.brandAnalysis = brandAnalysis;
    await state.set('campaigns', campaignId, campaign);

    logger.info('Step 3: Researching competitors');
    const competitorAnalysis = await researchCompetitors(brandName, brandAnalysis.industry, websiteUrl);
    logger.info('Competitor research complete', { competitorsFound: competitorAnalysis.competitors.length });

    campaign.competitorAnalysis = competitorAnalysis;
    await state.set('campaigns', campaignId, campaign);

    logger.info('Step 4: Curating award-winning reference scenes');

    // Extract product-specific keywords from actual SKUs for better reference search
    const productKeywords = products
      .map(p => {
        const name = p.name?.toLowerCase() || '';
        const category = p.category?.toLowerCase() || '';
        return `${name} ${category}`;
      })
      .join(' ')
      .split(/\s+/)
      .filter(word => word.length > 3)
      .slice(0, 10); // Top 10 keywords

    // Use specific product terms instead of generic industry category
    const searchCategory = products[0]?.category || products[0]?.name || brandAnalysis.industry;

    logger.info('Reference search category', {
      category: searchCategory,
      productKeywords: productKeywords.slice(0, 5)
    });

    const referenceTemplates = await curateReferenceLibrary({
      category: searchCategory, // Use actual product category/name instead of generic industry
      targetAudience: brandAnalysis.targetAudience,
      brandName,
      focusRegion: brandAnalysis.brandVoice?.tone,
      keywords: [
        ...productKeywords, // Add product-specific keywords
        ...(brandAnalysis.designElements?.visualStyle ? [brandAnalysis.designElements.visualStyle] : []),
        ...(brandAnalysis.designElements?.colorPalette ?? []),
      ],
    });
    logger.info('Reference curation complete', { referencesFound: referenceTemplates.length });

    campaign.referenceLibrary = referenceTemplates;

    logger.info('Step 5: Developing elevated creative strategy');
    const creativeStrategy = await developCreativeStrategy(brandAnalysis, competitorAnalysis, products);
    logger.info('Creative strategy developed', { campaignConcepts: creativeStrategy.campaignConcepts.length });

    campaign.creativeStrategy = creativeStrategy;
    campaign.assetInsights = buildAssetInsights({
      products,
      brandAnalysis,
      strategy: creativeStrategy,
      references: referenceTemplates,
    });
    await state.set('campaigns', campaignId, campaign);

    logger.info('Step 6: Generating master creative (1080x1080 square format)');

    let generatedCreatives: any[] = [];
    if (products.length > 0 && creativeStrategy) {
      // Generate ONE master creative per product (square format as master)
      generatedCreatives = await generateCreativesForAllProducts(
        products,
        creativeStrategy,
        referenceTemplates,
        ['product-ad'], // Master format only
        1 // Single variation
      );
      logger.info('Master creative generation complete', { creativesGenerated: generatedCreatives.length });
    } else {
      logger.warn('Skipping creative generation - no products or strategy available');
    }

    campaign.generatedCreatives = generatedCreatives;
    await state.set('campaigns', campaignId, campaign);

    logger.info('Step 7: AI-powered resizing to all ad formats');

    let allResizedCreatives: any[] = [];
    if (generatedCreatives.length > 0 && creativeStrategy) {
      // Get high-priority formats (most commonly used)
      const targetFormats = getHighPriorityFormats();
      logger.info('Resizing to formats', {
        formats: targetFormats.map(f => `${f.name} (${f.width}x${f.height})`),
        count: targetFormats.length
      });

      // Resize each master creative to all formats
      for (const masterCreative of generatedCreatives) {
        const product = products.find(p => p.sku === masterCreative.skuId);
        if (product) {
          try {
            const resizedVariations = await resizeCreativeForAllFormats(
              masterCreative.imagePath,
              product.imageUrl,
              creativeStrategy,
              product,
              targetFormats
            );

            allResizedCreatives.push(...resizedVariations);
            logger.info('Resized creatives for product', {
              product: product.name,
              variationsCreated: resizedVariations.length
            });
          } catch (error: any) {
            logger.error('Failed to resize creatives for product', {
              product: product.name,
              error: error.message
            });
          }
        }
      }

      logger.info('All format resizing complete', { totalResizedCreatives: allResizedCreatives.length });
    } else {
      logger.warn('Skipping resizing - no master creatives available');
    }

    campaign.resizedCreatives = allResizedCreatives;
    campaign.status = 'completed';
    campaign.completedAt = new Date().toISOString();
    await state.set('campaigns', campaignId, campaign);

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
      masterCreatives: generatedCreatives.length,
      resizedCreatives: allResizedCreatives.length,
      totalCreatives: generatedCreatives.length + allResizedCreatives.length,
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
