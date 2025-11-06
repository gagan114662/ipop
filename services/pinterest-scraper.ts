// @ts-nocheck
import { chromium, Browser, BrowserContext, Page } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';

interface PinterestPin {
  id: string;
  title: string;
  description: string;
  imageUrl: string;
  sourceUrl: string;
  saves: number;
  boardName?: string;
}

interface PinterestScraperConfig {
  email: string;
  password: string;
  headless?: boolean;
  cookiesFile?: string;
}

class PinterestScraper {
  private browser: Browser | null = null;
  private context: BrowserContext | null = null;
  private config: PinterestScraperConfig;
  private isLoggedIn: boolean = false;

  constructor(config: PinterestScraperConfig) {
    this.config = {
      headless: true,
      cookiesFile: './config/pinterest-cookies.json',
      ...config,
    };
  }

  async launch(): Promise<void> {
    console.info('Launching Pinterest scraper...');

    this.browser = await chromium.launch({
      headless: this.config.headless,
      args: [
        '--disable-blink-features=AutomationControlled',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-web-security',
      ],
    });

    this.context = await this.browser.newContext({
      viewport: { width: 1920, height: 1080 },
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    });

    // Load saved cookies if available
    if (this.config.cookiesFile && fs.existsSync(this.config.cookiesFile)) {
      console.info('Loading saved Pinterest cookies...');
      const cookies = JSON.parse(fs.readFileSync(this.config.cookiesFile, 'utf-8'));
      await this.context.addCookies(cookies);
      this.isLoggedIn = true;
    }
  }

  async login(): Promise<boolean> {
    if (this.isLoggedIn) {
      console.info('Already logged in (using saved cookies)');
      return true;
    }

    if (!this.context) {
      throw new Error('Browser not launched. Call launch() first.');
    }

    const page = await this.context.newPage();

    try {
      console.info('Navigating to Pinterest login...');
      await page.goto('https://www.pinterest.com/login/', { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(3000);

      // Check if already logged in
      const currentUrl = page.url();
      if (!currentUrl.includes('/login')) {
        console.info('Already logged in!');
        this.isLoggedIn = true;
        await this.saveCookies();
        await page.close();
        return true;
      }

      console.info('Looking for "Continue with Google" button...');

      // Click "Continue with Google" button
      const googleButton = await page.$('button:has-text("Continue with Google"), div[data-test-id="google-connect-button"]');

      if (!googleButton) {
        console.warn('Google login button not found, trying alternative selectors...');
        // Try clicking any element that contains Google-related text
        await page.click('div:has-text("Continue with Google")').catch(() => {});
      } else {
        await googleButton.click();
      }

      console.info('Clicked Google button, waiting for Google login popup...');
      await page.waitForTimeout(3000);

      // Google login form should appear - fill it in
      console.info('Filling Google email...');
      await page.waitForSelector('input[type="email"]', { timeout: 10000 });
      await page.type('input[type="email"]', this.config.email, { delay: 100 });
      await page.waitForTimeout(1000);

      // Click Next button
      await page.click('button:has-text("Next"), #identifierNext');
      console.info('Clicked Next, waiting for password field...');
      await page.waitForTimeout(3000);

      // Fill password
      console.info('Filling Google password...');
      await page.waitForSelector('input[type="password"]', { timeout: 10000 });
      await page.type('input[type="password"]', this.config.password, { delay: 100 });
      await page.waitForTimeout(1000);

      // Click Next/Sign in button
      await page.click('button:has-text("Next"), #passwordNext');
      console.info('Submitted Google login, waiting for redirect to Pinterest...');
      await page.waitForTimeout(8000);

      const finalUrl = page.url();
      console.info(`Final URL after login: ${finalUrl}`);

      // Check if login was successful
      if (finalUrl.includes('/login') || finalUrl.includes('/auth') || finalUrl.includes('google.com')) {
        await page.screenshot({ path: './pinterest-login-failed.png' });
        console.warn('Login may have failed - screenshot saved to pinterest-login-failed.png');
        console.warn('You may need to manually verify the login or handle 2FA');
      } else {
        console.info('Login successful!');
      }

      this.isLoggedIn = true;

      // Save cookies for future use
      await this.saveCookies();
      await page.close();
      return true;
    } catch (error: any) {
      console.error(`Login failed: ${error.message}`);
      await page.screenshot({ path: './pinterest-login-error.png' }).catch(() => {});
      await page.close();
      return false;
    }
  }

  private async saveCookies(): Promise<void> {
    if (!this.context || !this.config.cookiesFile) return;

    const cookies = await this.context.cookies();
    const cookieDir = path.dirname(this.config.cookiesFile);

    if (!fs.existsSync(cookieDir)) {
      fs.mkdirSync(cookieDir, { recursive: true });
    }

    fs.writeFileSync(this.config.cookiesFile, JSON.stringify(cookies, null, 2));
    console.info(`Saved cookies to ${this.config.cookiesFile}`);
  }

  async scrapeBoard(boardUrl: string, maxPins: number = 200): Promise<PinterestPin[]> {
    if (!this.context) {
      throw new Error('Browser not launched. Call launch() first.');
    }

    if (!this.isLoggedIn) {
      const loginSuccess = await this.login();
      if (!loginSuccess) {
        throw new Error('Failed to login to Pinterest');
      }
    }

    const page = await this.context.newPage();
    const pins: PinterestPin[] = [];

    try {
      console.info(`Scraping board: ${boardUrl}`);
      await page.goto(boardUrl, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(3000);

      // Extract board name
      const boardName = await page.$eval('h1', (el) => el.textContent?.trim() || 'Unknown Board')
        .catch(() => 'Unknown Board');

      console.info(`Board name: ${boardName}`);

      // Scroll and extract pins
      let previousPinCount = 0;
      let scrollAttempts = 0;
      const maxScrollAttempts = 50; // Prevent infinite scrolling

      while (pins.length < maxPins && scrollAttempts < maxScrollAttempts) {
        // Scroll to bottom
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await page.waitForTimeout(2000);

        // Extract pin data from the page
        const newPins = await page.evaluate(() => {
          const pinElements = document.querySelectorAll('div[data-test-id="pin"]');
          const extracted: any[] = [];

          pinElements.forEach((pinEl) => {
            try {
              // Get the link element
              const linkEl = pinEl.querySelector('a[href*="/pin/"]') as HTMLAnchorElement;
              if (!linkEl) return;

              const pinUrl = linkEl.href;
              const pinId = pinUrl.match(/\/pin\/(\d+)/)?.[1] || '';

              // Get the image
              const img = pinEl.querySelector('img') as HTMLImageElement;
              if (!img || !img.src) return;

              // Get title from alt text or aria-label
              const title = img.alt || linkEl.getAttribute('aria-label') || 'Untitled';

              // Get high-res image URL (replace size parameters)
              let imageUrl = img.src;
              // Pinterest uses different URL formats, try to get original
              if (imageUrl.includes('/236x/')) {
                imageUrl = imageUrl.replace('/236x/', '/originals/');
              } else if (imageUrl.includes('/474x/')) {
                imageUrl = imageUrl.replace('/474x/', '/originals/');
              } else if (imageUrl.includes('/736x/')) {
                imageUrl = imageUrl.replace('/736x/', '/originals/');
              }

              extracted.push({
                id: pinId,
                title,
                imageUrl,
                sourceUrl: pinUrl,
              });
            } catch (err) {
              // Skip this pin if extraction fails
            }
          });

          return extracted;
        });

        // Add new unique pins
        for (const pin of newPins) {
          if (pin.id && !pins.find(p => p.id === pin.id)) {
            pins.push({
              ...pin,
              description: '',
              saves: 0,
              boardName,
            });
          }
        }

        console.info(`Extracted ${pins.length} pins so far...`);

        // Check if we're making progress
        if (pins.length === previousPinCount) {
          scrollAttempts++;
        } else {
          scrollAttempts = 0; // Reset if we found new pins
        }

        previousPinCount = pins.length;

        // Stop if we've reached the target
        if (pins.length >= maxPins) {
          break;
        }
      }

      console.info(`Finished scraping board. Found ${pins.length} pins.`);
      await page.close();
      return pins.slice(0, maxPins);
    } catch (error: any) {
      console.error(`Failed to scrape board: ${error.message}`);
      await page.close();
      return pins;
    }
  }

  async scrapeMoreIdeas(boardUrl: string, maxPins: number = 300): Promise<PinterestPin[]> {
    if (!this.context) {
      throw new Error('Browser not launched. Call launch() first.');
    }

    const page = await this.context.newPage();
    const pins: PinterestPin[] = [];

    try {
      console.info(`Scraping "More ideas" from: ${boardUrl}`);
      await page.goto(boardUrl, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(3000);

      // Scroll down to find "More ideas" section
      console.info('Scrolling to find "More ideas" section...');
      for (let i = 0; i < 5; i++) {
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await page.waitForTimeout(2000);
      }

      // Look for "More ideas" or similar section
      const moreIdeasFound = await page.evaluate(() => {
        const headings = Array.from(document.querySelectorAll('h2, h3, div'));
        return headings.some(el =>
          el.textContent?.toLowerCase().includes('more ideas') ||
          el.textContent?.toLowerCase().includes('more like this') ||
          el.textContent?.toLowerCase().includes('recommended')
        );
      });

      if (!moreIdeasFound) {
        console.warn('Could not find "More ideas" section - scraping similar pins from page');
      }

      // Continue scrolling and extracting recommended pins
      let previousPinCount = 0;
      let scrollAttempts = 0;
      const maxScrollAttempts = 60; // More attempts for recommendations

      while (pins.length < maxPins && scrollAttempts < maxScrollAttempts) {
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await page.waitForTimeout(2000);

        const newPins = await page.evaluate(() => {
          const pinElements = document.querySelectorAll('div[data-test-id="pin"]');
          const extracted: any[] = [];

          pinElements.forEach((pinEl) => {
            try {
              const linkEl = pinEl.querySelector('a[href*="/pin/"]') as HTMLAnchorElement;
              if (!linkEl) return;

              const pinUrl = linkEl.href;
              const pinId = pinUrl.match(/\/pin\/(\d+)/)?.[1] || '';

              const img = pinEl.querySelector('img') as HTMLImageElement;
              if (!img || !img.src) return;

              const title = img.alt || linkEl.getAttribute('aria-label') || 'Untitled';

              let imageUrl = img.src;
              if (imageUrl.includes('/236x/')) imageUrl = imageUrl.replace('/236x/', '/originals/');
              else if (imageUrl.includes('/474x/')) imageUrl = imageUrl.replace('/474x/', '/originals/');
              else if (imageUrl.includes('/736x/')) imageUrl = imageUrl.replace('/736x/', '/originals/');

              extracted.push({ id: pinId, title, imageUrl, sourceUrl: pinUrl });
            } catch (err) {}
          });

          return extracted;
        });

        for (const pin of newPins) {
          if (pin.id && !pins.find(p => p.id === pin.id)) {
            pins.push({
              ...pin,
              description: '',
              saves: 0,
              boardName: 'More Ideas',
            });
          }
        }

        console.info(`Extracted ${pins.length} recommended pins so far...`);

        if (pins.length === previousPinCount) {
          scrollAttempts++;
        } else {
          scrollAttempts = 0;
        }

        previousPinCount = pins.length;
      }

      console.info(`Finished scraping "More ideas". Found ${pins.length} pins.`);
      await page.close();
      return pins.slice(0, maxPins);
    } catch (error: any) {
      console.error(`Failed to scrape "More ideas": ${error.message}`);
      await page.close();
      return pins;
    }
  }

  async searchPins(query: string, maxPins: number = 100): Promise<PinterestPin[]> {
    if (!this.context) {
      throw new Error('Browser not launched. Call launch() first.');
    }

    const page = await this.context.newPage();
    const pins: PinterestPin[] = [];

    try {
      const searchUrl = `https://www.pinterest.com/search/pins/?q=${encodeURIComponent(query)}`;
      console.info(`Searching Pinterest for: ${query}`);

      await page.goto(searchUrl, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(3000);

      let previousPinCount = 0;
      let scrollAttempts = 0;
      const maxScrollAttempts = 40;

      while (pins.length < maxPins && scrollAttempts < maxScrollAttempts) {
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await page.waitForTimeout(2000);

        const newPins = await page.evaluate(() => {
          const pinElements = document.querySelectorAll('div[data-test-id="pin"]');
          const extracted: any[] = [];

          pinElements.forEach((pinEl) => {
            try {
              const linkEl = pinEl.querySelector('a[href*="/pin/"]') as HTMLAnchorElement;
              if (!linkEl) return;

              const pinUrl = linkEl.href;
              const pinId = pinUrl.match(/\/pin\/(\d+)/)?.[1] || '';

              const img = pinEl.querySelector('img') as HTMLImageElement;
              if (!img || !img.src) return;

              const title = img.alt || linkEl.getAttribute('aria-label') || 'Untitled';

              let imageUrl = img.src;
              if (imageUrl.includes('/236x/')) imageUrl = imageUrl.replace('/236x/', '/originals/');
              else if (imageUrl.includes('/474x/')) imageUrl = imageUrl.replace('/474x/', '/originals/');
              else if (imageUrl.includes('/736x/')) imageUrl = imageUrl.replace('/736x/', '/originals/');

              extracted.push({ id: pinId, title, imageUrl, sourceUrl: pinUrl });
            } catch (err) {}
          });

          return extracted;
        });

        for (const pin of newPins) {
          if (pin.id && !pins.find(p => p.id === pin.id)) {
            pins.push({
              ...pin,
              description: '',
              saves: 0,
              boardName: `Search: ${query}`,
            });
          }
        }

        console.info(`Search "${query}": ${pins.length} pins found...`);

        if (pins.length === previousPinCount) {
          scrollAttempts++;
        } else {
          scrollAttempts = 0;
        }

        previousPinCount = pins.length;
      }

      console.info(`Search complete. Found ${pins.length} pins for "${query}"`);
      await page.close();
      return pins.slice(0, maxPins);
    } catch (error: any) {
      console.error(`Search failed for "${query}": ${error.message}`);
      await page.close();
      return pins;
    }
  }

  async downloadImage(imageUrl: string, outputDir: string): Promise<string | null> {
    try {
      const response = await fetch(imageUrl);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const buffer = Buffer.from(await response.arrayBuffer());

      // Validate image size (minimum 50KB like reference-curator)
      if (buffer.length < 50 * 1024) {
        console.warn(`Image too small (${Math.round(buffer.length / 1024)}KB): ${imageUrl}`);
        return null;
      }

      // Generate filename from URL hash
      const hash = crypto.createHash('sha1').update(imageUrl).digest('hex');
      const ext = imageUrl.includes('.png') ? '.png' : imageUrl.includes('.webp') ? '.webp' : '.jpg';
      const filename = `${hash}${ext}`;
      const filepath = path.join(outputDir, filename);

      // Create directory if it doesn't exist
      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
      }

      fs.writeFileSync(filepath, buffer);
      console.info(`✓ Downloaded: ${filename} (${Math.round(buffer.length / 1024)}KB)`);

      return filepath;
    } catch (error: any) {
      console.error(`Failed to download ${imageUrl}: ${error.message}`);
      return null;
    }
  }

  async close(): Promise<void> {
    if (this.context) {
      await this.context.close();
    }
    if (this.browser) {
      await this.browser.close();
    }
    console.info('Pinterest scraper closed.');
  }
}

export { PinterestScraper, PinterestPin, PinterestScraperConfig };
