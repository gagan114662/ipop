import { google } from 'googleapis'
import { OAuth2Client } from 'google-auth-library'
import jwt from 'jsonwebtoken'

export interface GoogleAuthCredentials {
  clientId: string
  clientSecret: string
  redirectUri: string
}

export interface AuthToken {
  accessToken: string
  refreshToken?: string
  expiryDate?: number
}

export interface UserProfile {
  id: string
  email: string
  name: string
  picture?: string
}

export class GmailAuthService {
  private oauth2Client: OAuth2Client
  private jwtSecret: string

  constructor(credentials: GoogleAuthCredentials, jwtSecret: string) {
    this.jwtSecret = jwtSecret
    this.oauth2Client = new google.auth.OAuth2(
      credentials.clientId,
      credentials.clientSecret,
      credentials.redirectUri
    )
  }

  /**
   * Generate authorization URL for Gmail OAuth
   */
  generateAuthUrl(): string {
    const scopes = [
      'https://www.googleapis.com/auth/gmail.readonly',
      'https://www.googleapis.com/auth/userinfo.profile',
      'https://www.googleapis.com/auth/userinfo.email'
    ]

    return this.oauth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: scopes,
      prompt: 'consent'
    })
  }

  /**
   * Exchange authorization code for tokens
   */
  async getTokensFromCode(code: string): Promise<AuthToken> {
    try {
      const { tokens } = await this.oauth2Client.getToken(code)
      
      return {
        accessToken: tokens.access_token!,
        refreshToken: tokens.refresh_token,
        expiryDate: tokens.expiry_date
      }
    } catch (error) {
      throw new Error(`Failed to exchange code for tokens: ${error}`)
    }
  }

  /**
   * Get user profile information from Google
   */
  async getUserProfile(accessToken: string): Promise<UserProfile> {
    try {
      this.oauth2Client.setCredentials({ access_token: accessToken })
      
      const oauth2 = google.oauth2({ version: 'v2', auth: this.oauth2Client })
      const { data } = await oauth2.userinfo.get()

      return {
        id: data.id!,
        email: data.email!,
        name: data.name!,
        picture: data.picture
      }
    } catch (error) {
      throw new Error(`Failed to get user profile: ${error}`)
    }
  }

  /**
   * Generate JWT token for authenticated user
   */
  generateJWT(userProfile: UserProfile, authToken: AuthToken): string {
    const payload = {
      userId: userProfile.id,
      email: userProfile.email,
      name: userProfile.name,
      picture: userProfile.picture,
      googleTokens: {
        accessToken: authToken.accessToken,
        refreshToken: authToken.refreshToken,
        expiryDate: authToken.expiryDate
      },
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60) // 24 hours
    }

    return jwt.sign(payload, this.jwtSecret)
  }

  /**
   * Verify JWT token
   */
  verifyJWT(token: string): any {
    try {
      return jwt.verify(token, this.jwtSecret)
    } catch (error) {
      throw new Error(`Invalid JWT token: ${error}`)
    }
  }

  /**
   * Refresh access token using refresh token
   */
  async refreshAccessToken(refreshToken: string): Promise<AuthToken> {
    try {
      this.oauth2Client.setCredentials({ refresh_token: refreshToken })
      const { credentials } = await this.oauth2Client.refreshAccessToken()

      return {
        accessToken: credentials.access_token!,
        refreshToken: credentials.refresh_token || refreshToken,
        expiryDate: credentials.expiry_date
      }
    } catch (error) {
      throw new Error(`Failed to refresh access token: ${error}`)
    }
  }

  /**
   * Get Gmail client for authenticated user
   */
  getGmailClient(accessToken: string) {
    this.oauth2Client.setCredentials({ access_token: accessToken })
    return google.gmail({ version: 'v1', auth: this.oauth2Client })
  }
}

// Service instance factory
export const createGmailAuthService = (
  credentials?: GoogleAuthCredentials,
  jwtSecret?: string
): GmailAuthService => {
  const defaultCredentials: GoogleAuthCredentials = {
    clientId: process.env.GOOGLE_CLIENT_ID || '',
    clientSecret: process.env.GOOGLE_CLIENT_SECRET || '',
    redirectUri: process.env.GOOGLE_REDIRECT_URI || 'http://localhost:5000/auth/google/callback'
  }

  const defaultJwtSecret = process.env.JWT_SECRET || 'your-super-secret-jwt-key'

  return new GmailAuthService(
    credentials || defaultCredentials,
    jwtSecret || defaultJwtSecret
  )
}

export const gmailAuthService = createGmailAuthService()