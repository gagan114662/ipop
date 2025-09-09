import { ApiRouteConfig, Handlers } from 'motia'
import { z } from 'zod'

export const config: ApiRouteConfig = {
  type: 'api',
  name: 'CrossLanguageWorkflow',
  description: 'Demonstrates intentional cross-language workflow communication',
  flows: ['cross-language-demo'],

  method: 'POST',
  path: '/cross-language/full-pipeline',
  bodySchema: z.object({
    pet: z.object({
      id: z.number(),
      name: z.string(),
      description: z.string(),
      owner_email: z.string().email(),
    }),
  }),
  responseSchema: {
    200: z.object({
      message: z.string(),
      workflow: z.string(),
      steps: z.array(z.string()),
    }),
  },
  emits: ['cross.python.analyze', 'cross.js.recommend', 'cross.ruby.notify'],
}

export const handler: Handlers['CrossLanguageWorkflow'] = async (req, { logger, traceId, emit }) => {
  logger.info('🌍 Cross-Language Workflow: Starting multi-language pipeline', { body: req.body })

  const { pet } = req.body

  // Intentionally trigger multiple language workflows in sequence
  // Note: Using 'cross.' prefix to distinguish from separate workflows
  
  // 1. Trigger Python AI Analysis
  await emit({
    topic: 'cross.python.analyze',
    data: {
      id: pet.id,
      name: pet.name,
      description: pet.description,
      source: 'cross-language-api'
    },
  })

  // 2. Trigger JavaScript Recommendations  
  await emit({
    topic: 'cross.js.recommend',
    data: {
      pet_id: pet.id,
      pet_name: pet.name,
      analysis: { sentiment: { label: 'POSITIVE', score: 0.8 } }, // Will be overridden by Python
      source: 'cross-language-api'
    },
  })

  // 3. Trigger Ruby Email Notification
  await emit({
    topic: 'cross.ruby.notify',
    data: {
      pet_name: pet.name,
      owner_email: pet.owner_email,
      recommendations: [], // Will be populated by JavaScript step
      sentiment: 'PROCESSING',
      source: 'cross-language-api'
    },
  })

  return { 
    status: 200, 
    body: { 
      message: `Cross-language pipeline started for ${pet.name}`,
      workflow: 'python-ai → javascript-recommendations → ruby-email',
      steps: ['🐍 Python AI Analysis', '🟡 JavaScript Recommendations', '💎 Ruby Email Service'],
      traceId 
    } 
  }
}