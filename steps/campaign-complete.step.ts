import { EventConfig, Handlers } from 'motia';
import { z } from 'zod';

export const config: EventConfig = {
  type: 'event',
  name: 'CampaignComplete',
  description: 'Handles campaign completion notifications',
  flows: ['marketing-agency'],
  subscribes: ['campaign-complete'],
  emits: [],
  input: z.object({
    campaignId: z.string(),
    brandName: z.string(),
    productsProcessed: z.number(),
    creativesGenerated: z.number(),
    qualityScore: z.number(),
    completedAt: z.string(),
  }),
};

export const handler: Handlers['CampaignComplete'] = async (input, { logger, traceId }) => {
  logger.info('Campaign completed successfully!', {
    ...input,
    traceId,
  });

  logger.info('Campaign Summary', {
    campaignId: input.campaignId,
    brand: input.brandName,
    productsAnalyzed: input.productsProcessed,
    creativesGenerated: input.creativesGenerated,
    brandQualityScore: `${input.qualityScore}/100`,
    completedAt: input.completedAt,
  });
};
