// Script to scrape top appreciated projects from Behance across multiple categories
import { chromium, Browser, BrowserContext, Page } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';
import * as https from 'https';
import * as http from 'http';

const OUTPUT_DIR = './reference-cache/images/behance/appreciated';
const METADATA_FILE = './reference-cache/behance-appreciated-metadata.json';
const PROJECTS_PER_CATEGORY = 60; // Aim for 60 projects per category
const MIN_APPRECIATIONS = parseInt(process.env.MIN_APPRECIATIONS || '500');

// Diverse search queries to get variety across advertising, branding, and design
const SEARCH_CATEGORIES = [
  'advertising campaign',
  'brand identity',
  'product photography',
  'commercial advertising',
  'graphic design poster',
  'creative advertising',
  'packaging design',
  'social media campaign',
  'print advertising',
  'digital advertising',
  'branding design',
  'visual identity',
  'art direction',
  'editorial design',
  'luxury branding',
  'fashion advertising',
  'food photography advertising',
  'real estate advertising',
  'automotive advertising',
  'tech product advertising',
];

interface BehanceProject {
  title: string;
  url: string;
  imageUrls: string[];
  appreciations: number;
  views: number;
  owner: string;
  category: string;
  downloadedImages: string[];
}

class BehanceMultiCategoryScraper {
  private browser: Browser | null = null;
  private context: BrowserContext | null = null;
  private allProjects: Map<string, BehanceProject> = new Map(); // Use Map to deduplicate by URL

  async launch(headless: boolean = true): Promise<void> {
    console.log('Launching browser...');
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

  async scrapeCategory(category: string, maxProjects: number): Promise<BehanceProject[]> {
    if (!this.context) {
      throw new Error('Browser not launched');
    }

    const page = await this.context.newPage();
    const projects: BehanceProject[] = [];

    try {
      const searchUrl = `https://www.behance.net/search/projects?search=${encodeURIComponent(category)}&sort=appreciations&time=all`;
      console.log(`  Navigating to: ${searchUrl}`);

      await page.goto(searchUrl, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(3000);

      // Scroll a few times to load more projects
      for (let i = 0; i < 3; i++) {
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await page.waitForTimeout(2000);
      }

      // Extract project links
      const projectLinks = await page.$$eval('a[href*="/gallery/"]', (links) =>
        links
          .map((link) => (link as HTMLAnchorElement).href)
          .filter((href, index, self) => href.includes('/gallery/') && self.indexOf(href) === index)
          .slice(0, 60) // Get up to 60 project links
      );

      console.log(`  Found ${projectLinks.length} project links`);

      // Extract data from each project
      for (let i = 0; i < Math.min(projectLinks.length, maxProjects); i++) {
        const projectUrl = projectLinks[i];

        // Skip if we've already scraped this project
        if (this.allProjects.has(projectUrl)) {
          console.log(`    [${i + 1}/${projectLinks.length}] Already scraped: ${projectUrl}`);
          continue;
        }

        try {
          const project = await this.extractProjectData(page, projectUrl, category);

          if (project && project.appreciations >= MIN_APPRECIATIONS && project.imageUrls.length > 0) {
            projects.push(project);
            this.allProjects.set(projectUrl, project); // Store in global map
            console.log(`    [${i + 1}/${projectLinks.length}] ✓ ${project.title} (${project.appreciations} app, ${project.imageUrls.length} images)`);
          } else {
            console.log(`    [${i + 1}/${projectLinks.length}] ✗ Skipped (low quality or no images)`);
          }

          // Rate limiting
          await page.waitForTimeout(1000);
        } catch (error: any) {
          console.warn(`    [${i + 1}/${projectLinks.length}] ✗ Error: ${error.message}`);
        }
      }

      await page.close();
      return projects;
    } catch (error: any) {
      console.error(`  Failed to scrape category "${category}": ${error.message}`);
      await page.close();
      return [];
    }
  }

  private async extractProjectData(page: Page, projectUrl: string, category: string): Promise<BehanceProject | null> {
    try {
      await page.goto(projectUrl, { waitUntil: 'networkidle', timeout: 20000 });
      await page.waitForTimeout(1500);

      // Extract title
      const title = await page.$eval('h1', (el) => el.textContent?.trim() || 'Untitled').catch(() => 'Untitled');

      // Extract owner
      const owner = await page
        .$eval('a[class*="Owner"], div[class*="owner"] a, a[class*="owner"]', (el) => el.textContent?.trim() || 'Unknown')
        .catch(() => 'Unknown');

      // Extract stats
      const statsText = await page.evaluate(() => document.body.textContent || '').catch(() => '');
      const appreciations = this.parseNumber(statsText.match(/(\d+(?:,\d+)*)\s*appreciation/i)?.[1] || '0');
      const views = this.parseNumber(statsText.match(/(\d+(?:\.?\d*[KMB])?)\s*view/i)?.[1] || '0');

      // Extract ALL high-quality images from the project
      const imageUrls = await page.evaluate(() => {
        const images: string[] = [];
        const selectors = [
          'img[src*="project_modules"]',
          'img[class*="ProjectModule"]',
          'img[class*="project"]',
        ];

        for (const selector of selectors) {
          const imgs = document.querySelectorAll(selector) as NodeListOf<HTMLImageElement>;
          imgs.forEach((img) => {
            if (img.src && !img.src.includes('avatar') && !images.includes(img.src)) {
              // Upgrade to max quality
              let imgUrl = img.src;
              if (imgUrl.includes('/115/') || imgUrl.includes('/202/') || imgUrl.includes('/230/')) {
                imgUrl = imgUrl.replace(/\/(115|202|230|404)\//g, '/max_/');
              }
              // Add /max_1200/ if no size parameter
              if (!imgUrl.includes('/max_') && imgUrl.includes('project_modules')) {
                imgUrl = imgUrl.replace('/project_modules/', '/project_modules/max_1200/');
              }
              images.push(imgUrl);
            }
          });
          if (images.length > 0) break; // Found images, stop trying other selectors
        }

        return images;
      }).catch(() => []);

      if (imageUrls.length === 0) {
        return null;
      }

      return {
        title,
        url: projectUrl,
        imageUrls,
        appreciations,
        views,
        owner,
        category,
        downloadedImages: [],
      };
    } catch (error: any) {
      return null;
    }
  }

  async downloadProjectImages(projects: BehanceProject[]): Promise<void> {
    console.log('\n' + '='.repeat(80));
    console.log('DOWNLOADING IMAGES');
    console.log('='.repeat(80));

    let totalDownloaded = 0;
    let totalFailed = 0;

    for (let i = 0; i < projects.length; i++) {
      const project = projects[i];

      console.log(`\n[${i + 1}/${projects.length}] ${project.title}`);
      console.log(`  Category: ${project.category} | Owner: ${project.owner} | Images: ${project.imageUrls.length}`);

      // Create sanitized project directory
      const sanitizedTitle = project.title.replace(/[^a-z0-9]/gi, '-').toLowerCase().substring(0, 50);
      const sanitizedCategory = project.category.replace(/[^a-z0-9]/gi, '-').toLowerCase();
      const projectDir = path.join(OUTPUT_DIR, sanitizedCategory, `${sanitizedTitle}-${project.appreciations}app`);

      if (!fs.existsSync(projectDir)) {
        fs.mkdirSync(projectDir, { recursive: true });
      }

      // Download each image
      for (let j = 0; j < Math.min(project.imageUrls.length, 10); j++) { // Limit to 10 images per project
        const imageUrl = project.imageUrls[j];

        try {
          const localPath = await this.downloadImage(imageUrl, projectDir, j);
          if (localPath) {
            project.downloadedImages.push(localPath);
            totalDownloaded++;
            console.log(`    [${j + 1}/${project.imageUrls.length}] ✓ Downloaded`);
          } else {
            totalFailed++;
            console.log(`    [${j + 1}/${project.imageUrls.length}] ✗ Failed`);
          }
        } catch (error: any) {
          totalFailed++;
          console.log(`    [${j + 1}/${project.imageUrls.length}] ✗ Error: ${error.message}`);
        }

        await new Promise(resolve => setTimeout(resolve, 500));
      }

      console.log(`  Complete: ${project.downloadedImages.length}/${Math.min(project.imageUrls.length, 10)} images`);

      // Pause between projects
      if (i % 5 === 0 && i > 0) {
        console.log('\n⏸️  Pausing (5 seconds)...');
        await new Promise(resolve => setTimeout(resolve, 5000));
      }
    }

    console.log(`\n✅ Download complete: ${totalDownloaded} images, ${totalFailed} failed`);
  }

  private async downloadImage(imageUrl: string, outputDir: string, index: number): Promise<string | null> {
    return new Promise((resolve) => {
      try {
        const ext = path.extname(new URL(imageUrl).pathname) || '.jpg';
        const filename = `image-${index}${ext}`;
        const filepath = path.join(outputDir, filename);

        if (fs.existsSync(filepath)) {
          resolve(filepath);
          return;
        }

        const client = imageUrl.startsWith('https') ? https : http;

        client.get(imageUrl, (response) => {
          if (response.statusCode === 301 || response.statusCode === 302) {
            // Handle redirects
            if (response.headers.location) {
              const redirectClient = response.headers.location.startsWith('https') ? https : http;
              redirectClient.get(response.headers.location, (redirectResponse) => {
                if (redirectResponse.statusCode !== 200) {
                  resolve(null);
                  return;
                }
                this.saveImageResponse(redirectResponse, filepath, resolve);
              }).on('error', () => resolve(null));
            } else {
              resolve(null);
            }
            return;
          }

          if (response.statusCode !== 200) {
            resolve(null);
            return;
          }

          this.saveImageResponse(response, filepath, resolve);
        }).on('error', () => resolve(null));
      } catch (error) {
        resolve(null);
      }
    });
  }

  private saveImageResponse(response: any, filepath: string, resolve: (value: string | null) => void): void {
    const chunks: Buffer[] = [];

    response.on('data', (chunk: Buffer) => chunks.push(chunk));

    response.on('end', () => {
      const buffer = Buffer.concat(chunks);

      if (buffer.length < 50 * 1024) {
        resolve(null);
        return;
      }

      fs.writeFileSync(filepath, buffer);
      resolve(filepath);
    });
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

async function main() {
  const startTime = Date.now();

  console.log('='.repeat(80));
  console.log('BEHANCE MULTI-CATEGORY SCRAPER');
  console.log('='.repeat(80));
  console.log(`Categories: ${SEARCH_CATEGORIES.length}`);
  console.log(`Target per category: ${PROJECTS_PER_CATEGORY} projects`);
  console.log(`Total target: ~${SEARCH_CATEGORIES.length * PROJECTS_PER_CATEGORY} projects`);
  console.log(`Minimum appreciations: ${MIN_APPRECIATIONS.toLocaleString()}`);
  console.log('='.repeat(80));

  const scraper = new BehanceMultiCategoryScraper();

  try {
    await scraper.launch(process.env.BEHANCE_HEADLESS !== 'false');

    // Scrape each category
    console.log('\n' + '='.repeat(80));
    console.log('SCRAPING CATEGORIES');
    console.log('='.repeat(80));

    for (let i = 0; i < SEARCH_CATEGORIES.length; i++) {
      const category = SEARCH_CATEGORIES[i];

      console.log(`\n[${i + 1}/${SEARCH_CATEGORIES.length}] "${category}"`);
      console.log('-'.repeat(80));

      try {
        await scraper.scrapeCategory(category, PROJECTS_PER_CATEGORY);
        console.log(`  Total unique projects collected so far: ${scraper['allProjects'].size}`);

        // Pause between categories
        if (i < SEARCH_CATEGORIES.length - 1) {
          console.log('  ⏸️  Pausing before next category (10 seconds)...');
          await new Promise(resolve => setTimeout(resolve, 10000));
        }
      } catch (error: any) {
        console.error(`  ✗ Category failed: ${error.message}`);
      }
    }

    const allProjects = Array.from(scraper['allProjects'].values());

    console.log('\n' + '='.repeat(80));
    console.log('CATEGORY SCRAPING COMPLETE');
    console.log('='.repeat(80));
    console.log(`Total unique projects: ${allProjects.length}`);

    // Download images
    await scraper.downloadProjectImages(allProjects);

    // Save metadata
    console.log('\n' + '='.repeat(80));
    console.log('SAVING METADATA');
    console.log('='.repeat(80));

    const metadataDir = path.dirname(METADATA_FILE);
    if (!fs.existsSync(metadataDir)) {
      fs.mkdirSync(metadataDir, { recursive: true });
    }

    const totalImages = allProjects.reduce((sum, p) => sum + p.downloadedImages.length, 0);

    const metadata = {
      scrapedAt: new Date().toISOString(),
      categories: SEARCH_CATEGORIES,
      minAppreciations: MIN_APPRECIATIONS,
      projectsFound: allProjects.length,
      totalImagesDownloaded: totalImages,
      projects: allProjects.map(p => ({
        title: p.title,
        url: p.url,
        category: p.category,
        appreciations: p.appreciations,
        views: p.views,
        owner: p.owner,
        imageCount: p.downloadedImages.length,
      })),
    };

    fs.writeFileSync(METADATA_FILE, JSON.stringify(metadata, null, 2));
    console.log(`✓ Metadata saved: ${METADATA_FILE}`);

    // Final summary
    const duration = Math.round((Date.now() - startTime) / 1000);
    const avgAppreciations = Math.round(allProjects.reduce((sum, p) => sum + p.appreciations, 0) / allProjects.length);

    console.log('\n' + '='.repeat(80));
    console.log('SCRAPING COMPLETE!');
    console.log('='.repeat(80));
    console.log(`
📊 SUMMARY:
───────────────────────────────────────────────────────────────────────────────
Categories scraped:      ${SEARCH_CATEGORIES.length}
Projects scraped:        ${allProjects.length.toLocaleString()}
Average appreciations:   ${avgAppreciations.toLocaleString()}
Total images:            ${totalImages.toLocaleString()}
───────────────────────────────────────────────────────────────────────────────
Output directory:        ${OUTPUT_DIR}
Metadata file:           ${METADATA_FILE}
Duration:                ${Math.floor(duration / 60)}m ${duration % 60}s
───────────────────────────────────────────────────────────────────────────────
`);

    await scraper.close();
    process.exit(0);
  } catch (error: any) {
    console.error('\n❌ SCRAPING FAILED:', error.message);
    console.error(error.stack);
    await scraper.close();
    process.exit(1);
  }
}

main();
