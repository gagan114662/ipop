import { EventConfig, Handlers } from 'motia'
import { z } from 'zod'
import { petStoreService } from '../services/pet-store'

export const config: EventConfig = {
  type: 'event',
  name: 'ProcessFoodOrder',
  description: 'basic-tutorial event step, demonstrates how to consume an event from a topic and persist data in state',
  flows: ['basic-tutorial'],
  subscribes: ['ts.pet.created'],
  emits: ['ts.order.processed'],
  input: z.object({
    id: z.number(),
    name: z.string(),
    photoUrl: z.string(),
    foodOrder: z.object({
      id: z.string(),
      quantity: z.number(),
    }).optional(),
    email: z.string(),
  }),
}

export const handler: Handlers['ProcessFoodOrder'] = async (input, { traceId, logger, state, emit }) => {
  logger.info('🟦 TypeScript Step: Processing food order', { input, traceId })

  if (input.foodOrder) {
    const order = await petStoreService.createOrder({
      email: input.email,
      quantity: input.foodOrder.quantity,
      petId: input.id,
      shipDate: new Date().toISOString(),
      status: 'placed',
    })

    await state.set('ts-orders', order.id, order)

    await emit({
      topic: 'ts.order.processed',
      data: {
        email: input.email,
        templateId: 'ts-order-confirmation',
        order: order,
        pet: { id: input.id, name: input.name },
      },
    })

    return { order_processed: true, order_id: order.id }
  }
  
  return { order_processed: false, reason: 'no_food_order' }
}