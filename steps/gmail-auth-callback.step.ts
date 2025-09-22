import { ApiRouteConfig, Handlers } from 'motia'
import { z } from 'zod'
import { gmailAuthService } from '../services/gmail-auth'

export const config: ApiRouteConfig = {
  type: 'api',
  name: 'GmailAuthCallback',
  description: 'Handle Gmail OAuth callback and generate JWT token',
  flows: ['gmail-auth'],

  method: 'GET',
  path: '/auth/google/callback',
  responseSchema: {
    200: z.object({
      token: z.string(),
      user: z.object({
        id: z.string(),
        email: z.string(),
        name: z.string(),
        picture: z.string().optional()
      }),
      message: z.string()
    }),
    400: z.object({
      error: z.string()
    }),
    500: z.object({
      error: z.string()
    })
  },
  emits: []
}

export const handler: Handlers['GmailAuthCallback'] = async (req, { logger, traceId }) => {
  try {
    const { code, error } = req.query

    if (error) {
      logger.warn('OAuth callback error', { error, traceId })
      return {
        status: 400,
        body: {
          error: `Authentication failed: ${error}`
        }
      }
    }

    if (!code) {
      logger.warn('No authorization code provided', { traceId })
      return {
        status: 400,
        body: {
          error: 'Authorization code is required'
        }
      }
    }

    logger.info('Processing OAuth callback', { traceId })

    // Exchange code for tokens
    const authToken = await gmailAuthService.getTokensFromCode(code)
    
    // Get user profile
    const userProfile = await gmailAuthService.getUserProfile(authToken.accessToken)
    
    // Generate JWT token
    const jwtToken = gmailAuthService.generateJWT(userProfile, authToken)

    logger.info('Gmail authentication successful', { 
      userId: userProfile.id, 
      email: userProfile.email,
      traceId 
    })

    return {
      status: 200,
      body: {
        token: jwtToken,
        user: {
          id: userProfile.id,
          email: userProfile.email,
          name: userProfile.name,
          picture: userProfile.picture
        },
        message: 'Authentication successful'
      }
    }
  } catch (error) {
    logger.error('Gmail OAuth callback failed', { error, traceId })
    return {
      status: 500,
      body: {
        error: 'Authentication failed'
      }
    }
  }
}