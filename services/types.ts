import { z } from 'zod'

export const petSchema = z.object({
  id: z.number(),
  name: z.string(),
  photoUrl: z.string(),
  status: z.enum(['available', 'pending', 'sold']).optional(),
  createdAt: z.string().optional(),
})

export const orderSchema = z.object({
  id: z.number(),
  petId: z.number(),
  quantity: z.number(),
  shipDate: z.string(),
  status: z.string(),
  complete: z.boolean().default(false),
  email: z.string().optional(),
})

export type Pet = z.infer<typeof petSchema>
export type Order = z.infer<typeof orderSchema>