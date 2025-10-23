import { ApiRouteConfig, Handlers } from 'motia';
import { z } from 'zod';

export const config: ApiRouteConfig = {
  type: 'api',
  name: 'HealthCheck',
  description: 'Health check endpoint to verify system is running',
  flows: ['marketing-agency'],
  
  method: 'GET',
  path: '/api/health',
  responseSchema: {
    200: z.object({
      status: z.string(),
      message: z.string(),
      services: z.object({
        openai: z.boolean(),
        gemini: z.boolean(),
      }),
    }),
  },
  emits: [],
};

export const handler: Handlers['HealthCheck'] = async (req: any, { logger }: any) => {
  logger.info('Health check requested');

  const hasOpenAI = !!process.env.OPENAI_API_KEY;
  const hasGemini = !!process.env.GEMINI_API_KEY;

  return {
    status: 200,
    body: {
      status: 'healthy',
      message: 'Autonomous Marketing Agency is ready!',
      services: {
        openai: hasOpenAI,
        gemini: hasGemini,
      },
    },
  };
};
