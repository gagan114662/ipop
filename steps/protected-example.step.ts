import { ApiRouteConfig, Handlers } from 'motia'
import { z } from 'zod'
import { withAuth } from '../services/auth-middleware'

export const config: ApiRouteConfig = {
  type: 'api',
  name: 'ProtectedGmailExample',
  description: 'Example protected route that requires Gmail authentication',
  flows: ['gmail-auth'],

  method: 'GET',
  path: '/protected/gmail-info',
  responseSchema: {
    200: z.object({
      user: z.object({
        userId: z.string(),
        email: z.string(),
        name: z.string(),
        picture: z.string().optional()
      }),
      gmailInfo: z.object({
        labels: z.array(z.object({
          id: z.string(),
          name: z.string()
        })),
        profile: z.object({
          emailAddress: z.string(),
          messagesTotal: z.number(),
          threadsTotal: z.number()
        })
      }),
      message: z.string()
    }),
    401: z.object({
      error: z.string(),
      code: z.string()
    }),
    500: z.object({
      error: z.string()
    })
  },
  emits: []
}

// Protect the handler with authentication middleware
export const handler: Handlers['ProtectedGmailExample'] = withAuth(
  async (req: any, { logger, traceId, auth }: any) => {
    try {
      logger.info('Accessing protected Gmail info', { 
        userId: auth.user.userId, 
        email: auth.user.email,
        traceId 
      })

      // Use the authenticated Gmail client
      const gmail = auth.gmail

      // Get user's Gmail labels
      const labelsResponse = await gmail.users.labels.list({
        userId: 'me'
      })

      // Get user's Gmail profile
      const profileResponse = await gmail.users.getProfile({
        userId: 'me'
      })

      const gmailInfo = {
        labels: labelsResponse.data.labels?.map((label: any) => ({
          id: label.id,
          name: label.name
        })) || [],
        profile: {
          emailAddress: profileResponse.data.emailAddress,
          messagesTotal: profileResponse.data.messagesTotal,
          threadsTotal: profileResponse.data.threadsTotal
        }
      }

      logger.info('Successfully retrieved Gmail info', { 
        userId: auth.user.userId,
        labelCount: gmailInfo.labels.length,
        traceId 
      })

      return {
        status: 200,
        body: {
          user: {
            userId: auth.user.userId,
            email: auth.user.email,
            name: auth.user.name,
            picture: auth.user.picture
          },
          gmailInfo,
          message: 'Successfully retrieved Gmail information'
        }
      }

    } catch (error) {
      logger.error('Failed to retrieve Gmail info', { 
        error, 
        userId: auth.user?.userId,
        traceId 
      })

      return {
        status: 500,
        body: {
          error: 'Failed to retrieve Gmail information'
        }
      }
    }
  }
)