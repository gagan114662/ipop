import { ApiRouteConfig, Handlers } from 'motia'
import { z } from 'zod'

export const config: ApiRouteConfig = {
  type: 'api',
  name: 'RubyWorkflowTrigger',
  description: 'API endpoint that triggers Ruby email notification service',
  flows: ['ruby-workflow'],

  method: 'POST',
  path: '/ruby/send-notification',
  bodySchema: z.object({
    pet: z.object({
      name: z.string(),
      owner_email: z.string().email(),
    }),
    notification_type: z.enum(['welcome', 'reminder', 'update']).optional(),
    custom_message: z.string().optional(),
  }),
  responseSchema: {
    200: z.object({
      message: z.string(),
      workflow: z.string(),
      pet_name: z.string(),
    }),
  },
  emits: ['rb.send.email'],
}

export const handler: Handlers['RubyWorkflowTrigger'] = async (req, { logger, traceId, emit }) => {
  logger.info('🟦 TypeScript API → 💎 Ruby Workflow: Triggering email service', { body: req.body })

  const { pet, notification_type, custom_message } = req.body

  await emit({
    topic: 'rb.send.email',
    data: {
      pet_name: pet.name,
      recommendations: [
        { recommendation: '🎾 Interactive toys for energetic play', priority: 'high', estimated_cost: '$25-50' },
        { recommendation: '🦴 Premium treats for good behavior', priority: 'medium', estimated_cost: '$15-30' },
      ],
      sentiment: notification_type || 'POSITIVE',
      owner_email: pet.owner_email,
      custom_message: custom_message,
    },
  })

  return { 
    status: 200, 
    body: { 
      message: `Ruby email notification started for ${pet.name}`,
      workflow: 'ruby-email-service',
      pet_name: pet.name,
      traceId 
    } 
  }
}