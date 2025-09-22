import { ApiRouteConfig, Handlers } from 'motia'
import { z } from 'zod'
import { gmailAuthService } from '../services/gmail-auth'

export const config: ApiRouteConfig = {
  type: 'api',
  name: 'VerifyGmailToken',
  description: 'Verify JWT token and return user information',
  flows: ['gmail-auth'],

  method: 'GET',
  path: '/auth/verify',
  responseSchema: {
    200: z.object({
      user: z.object({
        userId: z.string(),
        email: z.string(),
        name: z.string(),
        picture: z.string().optional()
      }),
      valid: z.boolean()
    }),
    401: z.object({
      error: z.string(),
      valid: z.boolean()
    }),
    500: z.object({
      error: z.string()
    })
  },
  emits: []
}

export const handler: Handlers['VerifyGmailToken'] = async (req, { logger, traceId }) => {
  try {
    const authHeader = req.headers.authorization

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return {
        status: 401,
        body: {
          error: 'Authorization header required',
          valid: false
        }
      }
    }

    const token = authHeader.substring(7) // Remove 'Bearer ' prefix

    const decoded = gmailAuthService.verifyJWT(token)

    logger.info('Token verification successful', { userId: decoded.userId, traceId })

    return {
      status: 200,
      body: {
        user: {
          userId: decoded.userId,
          email: decoded.email,
          name: decoded.name,
          picture: decoded.picture
        },
        valid: true
      }
    }
  } catch (error) {
    logger.warn('Token verification failed', { error, traceId })
    return {
      status: 401,
      body: {
        error: 'Invalid or expired token',
        valid: false
      }
    }
  }
}