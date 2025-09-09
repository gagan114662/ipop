import { ApiRouteConfig, Handlers } from 'motia'
import { z } from 'zod'

export const config: ApiRouteConfig = {
  type: 'api',
  name: 'JavaScriptWorkflowTrigger',
  description: 'API endpoint that triggers JavaScript recommendation engine',
  flows: ['javascript-workflow'],

  method: 'POST',
  path: '/javascript/recommend',
  bodySchema: z.object({
    pet: z.object({
      id: z.number(),
      name: z.string(),
      age: z.number().optional(),
      breed: z.string().optional(),
    }),
    preferences: z.object({
      budget: z.enum(['low', 'medium', 'high']).optional(),
      activity_level: z.enum(['low', 'moderate', 'high']).optional(),
    }).optional(),
  }),
  responseSchema: {
    200: z.object({
      message: z.string(),
      workflow: z.string(),
      pet_id: z.number(),
    }),
  },
  emits: ['js.pet.recommend'],
}

export const handler: Handlers['JavaScriptWorkflowTrigger'] = async (req, { logger, traceId, emit }) => {
  logger.info('🟦 TypeScript API → 🟡 JavaScript Workflow: Starting recommendation engine', { body: req.body })

  const { pet, preferences } = req.body

  await emit({
    topic: 'js.pet.recommend',
    data: {
      pet_id: pet.id,
      pet_name: pet.name,
      pet_details: pet,
      preferences: preferences || {},
      analysis: {
        sentiment: { label: 'POSITIVE', score: 0.8 } // Mock data for JS workflow
      }
    },
  })

  return { 
    status: 200, 
    body: { 
      message: `JavaScript recommendation engine started for ${pet.name}`,
      workflow: 'javascript-recommendations',
      pet_id: pet.id,
      traceId 
    } 
  }
}