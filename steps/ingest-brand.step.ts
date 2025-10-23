import { ApiRouteConfig, Handlers } from 'motia';
import { z } from 'zod';

export const config: ApiRouteConfig = {
  type: 'api',
  name: 'IngestBrand',
  description: 'Accepts a brand website URL and initiates the autonomous marketing agency workflow',
  flows: ['marketing-agency'],
  
  method: 'POST',
  path: '/api/ingest-brand',
  bodySchema: z.object({
    websiteUrl: z.string().url(),
    brandName: z.string().optional(),
  }),
  responseSchema: {
    200: z.object({
      campaignId: z.string(),
      message: z.string(),
      status: z.string(),
    }),
  },
  emits: ['process-brand'],
};

export const handler: Handlers['IngestBrand'] = async (req, { logger, emit, traceId }) => {
  logger.info('Starting brand ingestion', { body: req.body, traceId });

  const { websiteUrl, brandName } = req.body;
  const campaignId = `campaign_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

  // Emit event to process the brand asynchronously
  await emit({
    topic: 'process-brand',
    data: {
      campaignId,
      websiteUrl,
      brandName: brandName || new URL(websiteUrl).hostname,
      timestamp: new Date().toISOString(),
    },
  });

  return {
    status: 200,
    body: {
      campaignId,
      message: 'Brand ingestion started. Your autonomous marketing agency is now analyzing the brand and generating creatives.',
      status: 'processing',
    },
  };
};
