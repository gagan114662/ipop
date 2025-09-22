import { ApiRouteConfig, Handlers } from 'motia'
import { z } from 'zod'
import { gmailAuthService } from '../services/gmail-auth'

export const config: ApiRouteConfig = {
  type: 'api',
  name: 'GmailAuthInit',
  description: 'Initiate Gmail OAuth authentication flow',
  flows: ['gmail-auth'],

  method: 'GET',
  path: '/auth/gmail',
  responseSchema: {
    200: z.object({
      authUrl: z.string(),
      message: z.string()
    }),
    500: z.object({
      error: z.string()
    })
  },
  emits: []
}

export const handler: Handlers['GmailAuthInit'] = async (req, { logger, traceId }) => {
  try {
    logger.info('Initiating Gmail OAuth flow', { traceId })

    const authUrl = gmailAuthService.generateAuthUrl()

    return {
      status: 200,
      body: {
        authUrl,
        message: 'Redirect user to this URL to complete authentication'
      }
    }
  } catch (error) {
    logger.error('Failed to initiate Gmail OAuth', { error, traceId })
    return {
      status: 500,
      body: {
        error: 'Failed to initiate authentication'
      }
    }
  }
}