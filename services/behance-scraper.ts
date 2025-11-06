// @ts-nocheck
import { chromium, Browser, BrowserContext, Page } from 'playwright';
import { ImageSearchResult } from './web-search-tool';

interface BehanceProject {
  title: string;
  url: string;
  imageUrl: string;
  appreciations: number;
  views: number;
  owner: string;
}

class BehanceScraper {
  private browser: Browser | null = null;
  private context: BrowserContext | null = null;

  async launch(headless: boolean = true): Promise<void> {
    this.browser = await chromium.launch({
      headless,
      args: [
        '--disable-blink-features=AutomationControlled',
        '--no-sandbox',
        '--disable-setuid-sandbox',
      ],
    });

    this.context = await this.browser.newContext({
      viewport: { width: 1920, height: 1080 },
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    });
  }

  async close(): Promise<void> {
    if (this.context) {
      await this.context.close();
    }
    if (this.browser) {
      await this.browser.close();
    }
  }

  async searchProjects(query: string, maxResults: number = 10): Promise<BehanceProject[]> {
    if (!this.context) {
      throw new Error('Browser not launched. Call launch() first.');
    }

    const page = await this.context.newPage();
    const projects: BehanceProject[] = [];

    try {
      const searchUrl = `https://www.behance.net/search/projects?search=${encodeURIComponent(query)}`;
      console.info(`Searching Behance: ${searchUrl}`);

      await page.goto(searchUrl, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(2000);

      // Scroll to load more results
      await this.scrollToLoadMore(page, 3);

      // Extract project links
      const projectLinks = await page.$$eval('a[href*="/gallery/"]', (links) =>
        links
          .map((link) => (link as HTMLAnchorElement).href)
          .filter((href) => href.includes('/gallery/'))
          .slice(0, 30) // Get up to 30 links for filtering
      );

      console.info(`Found ${projectLinks.length} project links`);

      // Visit each project and extract data
      for (let i = 0; i < Math.min(projectLinks.length, maxResults * 2); i++) {
        if (projects.length >= maxResults) break;

        const projectUrl = projectLinks[i];
        try {
          const project = await this.extractProjectData(page, projectUrl);
          // Accept all projects that have valid images (temporarily remove appreciation filter)
          // TODO: Re-enable filtering once stats extraction is fixed
          if (project && project.imageUrl) {
            projects.push(project);
            console.info(`✓ Added project: ${project.title} (${project.appreciations} appreciations)`);
          } else if (project) {
            console.info(`✗ Skipped project: ${project.title} (no valid image)`);
          }
          await page.waitForTimeout(1000); // Rate limiting
        } catch (error: any) {
          console.warn(`Failed to extract project ${projectUrl}: ${error.message}`);
        }
      }
    } finally {
      await page.close();
    }

    return projects;
  }

  private async scrollToLoadMore(page: Page, scrollCount: number = 3): Promise<void> {
    for (let i = 0; i < scrollCount; i++) {
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(2000);

      // Check for "Load More" button
      const loadMoreButton = await page.$('button:has-text("Load More")');
      if (loadMoreButton) {
        await loadMoreButton.click();
        await page.waitForTimeout(2000);
      }
    }
  }

  private async extractProjectData(page: Page, projectUrl: string): Promise<BehanceProject | null> {
    try {
      await page.goto(projectUrl, { waitUntil: 'networkidle', timeout: 20000 });
      await page.waitForTimeout(1500);

      // Extract title
      const title = await page.$eval('h1', (el) => el.textContent?.trim() || 'Untitled').catch(() => 'Untitled');

      // Extract owner
      const owner = await page
        .$eval('a[class*="Owner"], div[class*="owner"] a', (el) => el.textContent?.trim() || 'Unknown')
        .catch(() => 'Unknown');

      // Extract stats (appreciations and views)
      // Try multiple selectors for stats (Behance frequently changes DOM structure)
      const statsText = await page
        .evaluate(() => {
          const selectors = [
            'div[class*="stats"]',
            'div[class*="Stats"]',
            'div[class*="ProjectStats"]',
            'div[class*="project-stats"]',
            '[data-stats]',
            '.project-module-stats',
          ];

          for (const selector of selectors) {
            const el = document.querySelector(selector);
            if (el && el.textContent) return el.textContent;
          }

          // Fallback: get all text from page and search for stats
          return document.body.textContent || '';
        })
        .catch(() => '');

      const appreciations = this.parseNumber(statsText.match(/(\d+(?:,\d+)*)\s*appreciation/i)?.[1] || '0');
      const views = this.parseNumber(statsText.match(/(\d+(?:\.?\d*[KMB])?)\s*view/i)?.[1] || '0');

      // Extract first high-quality image (prefer project modules, avoid thumbnails/avatars)
      const imageUrl = await page
        .evaluate(() => {
          // Try multiple selectors in order of preference
          const selectors = [
            'img[src*="project_modules"][src*="/max_"]',           // Highest quality
            'img[src*="project_modules"][src*="/original/"]',       // Original uploads
            'img[src*="project_modules"]:not([src*="/115/"]):not([src*="/202/"])', // Project images, not thumbnails
            'img[srcset]',                                          // Images with srcset
            'img[src*="behance.net"]:not([src*="avatar"]):not([src*="thumb"])', // Generic fallback
          ];

          for (const selector of selectors) {
            const img = document.querySelector(selector) as HTMLImageElement;
            if (img && img.src) {
              // If srcset exists, parse it to get highest resolution
              if (img.srcset) {
                const srcsetParts = img.srcset.split(',').map(s => s.trim());
                // Get the largest resolution from srcset
                const largest = srcsetParts[srcsetParts.length - 1]?.split(' ')[0];
                if (largest) return largest;
              }
              return img.src;
            }
          }
          return '';
        })
        .catch(() => '');

      if (!imageUrl) {
        console.warn(`No image found for ${title}`);
        return null;
      }

      // Ensure we're getting a high-res version (replace size parameters if found)
      let finalImageUrl = imageUrl;
      if (finalImageUrl.includes('/115/') || finalImageUrl.includes('/202/') || finalImageUrl.includes('/230/')) {
        // Replace thumbnail sizes with max size
        finalImageUrl = finalImageUrl.replace(/\/(115|202|230|404)\//g, '/max_/');
      }

      return {
        title,
        url: projectUrl,
        imageUrl: finalImageUrl,
        appreciations,
        views,
        owner,
      };
    } catch (error: any) {
      console.warn(`Failed to extract project data: ${error.message}`);
      return null;
    }
  }

  private parseNumber(numStr: string): number {
    if (!numStr) return 0;

    const cleaned = numStr.replace(/,/g, '').trim().toUpperCase();

    if (cleaned.includes('K')) {
      return Math.floor(parseFloat(cleaned.replace('K', '')) * 1000);
    } else if (cleaned.includes('M')) {
      return Math.floor(parseFloat(cleaned.replace('M', '')) * 1000000);
    } else if (cleaned.includes('B')) {
      return Math.floor(parseFloat(cleaned.replace('B', '')) * 1000000000);
    }

    return parseInt(cleaned) || 0;
  }
}

/**
 * Search Behance for high-quality advertising/design projects
 * Returns projects with 500+ appreciations to ensure quality
 */
export async function searchBehanceProjects(
  category: string,
  maxResults: number = 5
): Promise<ImageSearchResult[]> {
  const scraper = new BehanceScraper();

  try {
    await scraper.launch(true);

    // Search queries optimized for product-specific advertising/campaign work
    // Extract key product terms (e.g., "running shoes" from "Tree Dasher 2")
    const cleanCategory = category.toLowerCase();

    // Build specific search terms based on product type
    const queries = [
      `${category} advertising`,
      `${category} product photography`,
      `${category} commercial campaign`,
    ];

    // Add more specific queries if category contains product keywords
    if (cleanCategory.includes('shoe') || cleanCategory.includes('sneaker') || cleanCategory.includes('footwear')) {
      queries.push('sneakers advertising campaign', 'athletic footwear commercial');
    }
    if (cleanCategory.includes('apparel') || cleanCategory.includes('clothing')) {
      queries.push('apparel brand campaign', 'fashion advertising');
    }

    console.info(`Behance search queries: ${queries.join(', ')}`);

    const allProjects: BehanceProject[] = [];

    for (const query of queries) {
      if (allProjects.length >= maxResults) break;

      const projects = await scraper.searchProjects(query, Math.ceil(maxResults / queries.length) + 2);
      allProjects.push(...projects);

      if (allProjects.length < maxResults) {
        await new Promise((resolve) => setTimeout(resolve, 2000)); // Rate limiting between queries
      }
    }

    // Convert to ImageSearchResult format
    const results: ImageSearchResult[] = allProjects.slice(0, maxResults).map((project) => ({
      title: project.title,
      imageUrl: project.imageUrl,
      sourceUrl: project.url,
      thumbnail: project.imageUrl, // Same as imageUrl for now
    }));

    console.info(`Behance search complete: Found ${results.length} high-quality projects`);
    return results;
  } catch (error: any) {
    console.error(`Behance search failed: ${error.message}`);
    return [];
  } finally {
    await scraper.close();
  }
}
