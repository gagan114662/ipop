import { gmailAuthService } from './gmail-auth'

export interface AuthenticatedUser {
  userId: string
  email: string
  name: string
  picture?: string
  googleTokens: {
    accessToken: string
    refreshToken?: string
    expiryDate?: number
  }
}

export interface AuthContext {
  user: AuthenticatedUser
  gmail: any // Gmail client instance
}

/**
 * Authentication middleware for Motia steps
 * Verifies JWT token and adds user context to request
 */
export const withAuth = (handler: any) => {
  return async (req: any, context: any) => {
    const { logger, traceId } = context

    try {
      // Extract token from Authorization header
      const authHeader = req.headers?.authorization
      
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        logger.warn('Missing or invalid authorization header', { traceId })
        return {
          status: 401,
          body: {
            error: 'Authorization header with Bearer token is required',
            code: 'MISSING_AUTH_TOKEN'
          }
        }
      }

      const token = authHeader.substring(7) // Remove 'Bearer ' prefix

      // Verify JWT token
      const decoded = gmailAuthService.verifyJWT(token)
      
      if (!decoded) {
        logger.warn('Invalid JWT token provided', { traceId })
        return {
          status: 401,
          body: {
            error: 'Invalid or expired authentication token',
            code: 'INVALID_TOKEN'
          }
        }
      }

      // Check if token is expired
      const currentTime = Math.floor(Date.now() / 1000)
      if (decoded.exp && decoded.exp < currentTime) {
        logger.warn('Expired JWT token provided', { userId: decoded.userId, traceId })
        return {
          status: 401,
          body: {
            error: 'Authentication token has expired',
            code: 'TOKEN_EXPIRED'
          }
        }
      }

      // Create authenticated user object
      const authenticatedUser: AuthenticatedUser = {
        userId: decoded.userId,
        email: decoded.email,
        name: decoded.name,
        picture: decoded.picture,
        googleTokens: decoded.googleTokens
      }

      // Get Gmail client for the authenticated user
      const gmailClient = gmailAuthService.getGmailClient(decoded.googleTokens.accessToken)

      // Add auth context to request
      const authContext: AuthContext = {
        user: authenticatedUser,
        gmail: gmailClient
      }

      // Add auth context to the request context
      const enhancedContext = {
        ...context,
        auth: authContext
      }

      logger.info('Authentication successful', { 
        userId: authenticatedUser.userId, 
        email: authenticatedUser.email,
        traceId 
      })

      // Call the original handler with enhanced context
      return await handler(req, enhancedContext)

    } catch (error) {
      logger.error('Authentication middleware error', { error, traceId })
      
      // Handle specific JWT errors
      if (error.message?.includes('Invalid JWT token')) {
        return {
          status: 401,
          body: {
            error: 'Invalid authentication token format',
            code: 'MALFORMED_TOKEN'
          }
        }
      }

      // Handle token refresh scenarios
      if (error.message?.includes('access token')) {
        return {
          status: 401,
          body: {
            error: 'Authentication token needs to be refreshed',
            code: 'TOKEN_REFRESH_REQUIRED'
          }
        }
      }

      return {
        status: 500,
        body: {
          error: 'Authentication service error',
          code: 'AUTH_SERVICE_ERROR'
        }
      }
    }
  }
}

/**
 * Optional authentication middleware for routes that can work with or without auth
 * Adds auth context if token is present and valid, but doesn't fail if missing
 */
export const withOptionalAuth = (handler: any) => {
  return async (req: any, context: any) => {
    const { logger, traceId } = context

    try {
      const authHeader = req.headers?.authorization
      
      // If no auth header, proceed without authentication
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        logger.info('No authentication provided, proceeding without auth', { traceId })
        return await handler(req, context)
      }

      const token = authHeader.substring(7)
      
      try {
        const decoded = gmailAuthService.verifyJWT(token)
        
        if (decoded && decoded.exp && decoded.exp >= Math.floor(Date.now() / 1000)) {
          // Valid token - add auth context
          const authenticatedUser: AuthenticatedUser = {
            userId: decoded.userId,
            email: decoded.email,
            name: decoded.name,
            picture: decoded.picture,
            googleTokens: decoded.googleTokens
          }

          const gmailClient = gmailAuthService.getGmailClient(decoded.googleTokens.accessToken)
          
          const authContext: AuthContext = {
            user: authenticatedUser,
            gmail: gmailClient
          }

          const enhancedContext = {
            ...context,
            auth: authContext
          }

          logger.info('Optional authentication successful', { 
            userId: authenticatedUser.userId,
            traceId 
          })

          return await handler(req, enhancedContext)
        }
      } catch (error) {
        logger.warn('Optional auth token invalid, proceeding without auth', { error, traceId })
      }

      // If token is invalid or expired, proceed without authentication
      return await handler(req, context)

    } catch (error) {
      logger.warn('Optional authentication middleware error, proceeding without auth', { error, traceId })
      return await handler(req, context)
    }
  }
}

/**
 * Rate limiting decorator for authentication endpoints
 */
export const withRateLimit = (maxRequests: number = 10, windowMinutes: number = 15) => {
  const requestCounts = new Map<string, { count: number; resetTime: number }>()

  return (handler: any) => {
    return async (req: any, context: any) => {
      const { logger, traceId } = context
      const clientIp = req.headers?.['x-forwarded-for'] || req.headers?.['x-real-ip'] || 'unknown'
      const now = Date.now()
      const windowMs = windowMinutes * 60 * 1000

      // Clean up old entries
      for (const [ip, data] of requestCounts.entries()) {
        if (now > data.resetTime) {
          requestCounts.delete(ip)
        }
      }

      // Check current request count
      const current = requestCounts.get(clientIp) || { count: 0, resetTime: now + windowMs }
      
      if (current.count >= maxRequests && now < current.resetTime) {
        logger.warn('Rate limit exceeded', { clientIp, count: current.count, traceId })
        return {
          status: 429,
          body: {
            error: 'Too many requests. Please try again later.',
            code: 'RATE_LIMIT_EXCEEDED',
            resetTime: current.resetTime
          }
        }
      }

      // Increment request count
      current.count += 1
      requestCounts.set(clientIp, current)

      return await handler(req, context)
    }
  }
}