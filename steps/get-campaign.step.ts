import { ApiRouteConfig, Handlers } from 'motia';
import { z } from 'zod';
import { MarketingCampaign } from '../services/marketing-types';

export const config: ApiRouteConfig = {
  type: 'api',
  name: 'GetCampaign',
  description: 'Retrieves campaign results including analysis, strategy, and generated creatives',
  flows: ['marketing-agency'],
  
  method: 'GET',
  path: '/api/campaign/:campaignId',
  responseSchema: {
    200: z.object({
      campaign: z.any(),
    }),
    404: z.object({
      error: z.string(),
    }),
  },
  emits: [],
};

export const handler: Handlers['GetCampaign'] = async (req: any, { logger, state }: any) => {
  const campaignId = req.params.campaignId;
  
  logger.info('Retrieving campaign', { campaignId });

  const campaign = await state.get('campaigns', campaignId);

  if (!campaign) {
    return {
      status: 404,
      body: {
        error: `Campaign ${campaignId} not found`,
      },
    };
  }

  return {
    status: 200,
    body: {
      campaign,
    },
  };
};
