import { ApiRouteConfig, Handlers } from 'motia'
import { z } from 'zod'

export const config: ApiRouteConfig = {
  type: 'api',
  name: 'PythonWorkflowTrigger',
  description: 'API endpoint that triggers Python AI workflow',
  flows: ['python-workflow'],

  method: 'POST',
  path: '/python/analyze-pet',
  bodySchema: z.object({
    pet: z.object({
      id: z.number(),
      name: z.string(),
      description: z.string().optional(),
    }),
  }),
  responseSchema: {
    200: z.object({
      message: z.string(),
      workflow: z.string(),
      pet_id: z.number(),
    }),
  },
  emits: ['py.pet.analyze'],
}

export const handler: Handlers['PythonWorkflowTrigger'] = async (req, { logger, traceId, emit }) => {
  logger.info('🟦 TypeScript API → 🐍 Python Workflow: Triggering AI analysis', { body: req.body })

  const { pet } = req.body

  await emit({
    topic: 'py.pet.analyze',
    data: {
      id: pet.id,
      name: pet.name,
      description: pet.description || `Analyzing pet: ${pet.name}`,
    },
  })

  return { 
    status: 200, 
    body: { 
      message: `Python AI analysis started for ${pet.name}`,
      workflow: 'python-ai-analysis',
      pet_id: pet.id,
      traceId 
    } 
  }
}