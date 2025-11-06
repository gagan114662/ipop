// Script to scrape most appreciated projects from Behance
import { chromium, Browser, BrowserContext, Page } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';
import * as https from 'https';
import * as http from 'http';

const OUTPUT_DIR = './reference-cache/images/behance/appreciated';
const METADATA_FILE = './reference-cache/behance-appreciated-metadata.json';
const TARGET_PROJECTS = parseInt(process.env.MAX_PROJECTS || '10000');
const MIN_APPRECIATIONS = parseInt(process.env.MIN_APPRECIATIONS || '500');

interface BehanceProject {
  title: string;
  url: string;
  imageUrls: string[];
  appreciations: number;
  views: number;
  owner: string;
  downloadedImages: string[];
}

class BehanceAppreciatedScraper {
  private browser: Browser | null = null;
  private context: BrowserContext | null = null;
  private projects: BehanceProject[] = [];

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

  async scrapeMostAppreciatedProjects(): Promise<BehanceProject[]> {
    if (!this.context) {
      throw new Error('Browser not launched. Call launch() first.');
    }

    const page = await this.context.newPage();

    try {
      // Start from Behance discover page sorted by appreciations
      const discoverUrl = 'https://www.behance.net/search/projects?sort=appreciations&time=all';
      console.log(`\nNavigating to: ${discoverUrl}`);

      await page.goto(discoverUrl, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(3000);

      let scrollAttempts = 0;
      const maxScrollAttempts = 200; // Limit scroll attempts to prevent infinite loops
      let lastProjectCount = 0;
      let stuckCount = 0;

      console.log(`\nStarting to collect project links (target: ${TARGET_PROJECTS} projects)...`);

      while (this.projects.length < TARGET_PROJECTS && scrollAttempts < maxScrollAttempts) {
        // Scroll gradually to trigger lazy loading
        const scrollSteps = 5;
        for (let i = 0; i < scrollSteps; i++) {
          await page.evaluate((step) => {
            const scrollHeight = document.documentElement.scrollHeight;
            const currentScroll = window.pageYOffset;
            const stepSize = (scrollHeight - currentScroll) / 5;
            window.scrollBy(0, stepSize);
          }, i);
          await page.waitForTimeout(300);
        }

        // Wait for content to load
        await page.waitForTimeout(3000);

        // Extract project links from current view
        const projectLinks = await page.$$eval('a[href*="/gallery/"]', (links) =>
          links
            .map((link) => (link as HTMLAnchorElement).href)
            .filter((href) => href.includes('/gallery/'))
        );

        console.log(`Scroll ${scrollAttempts + 1}: Found ${projectLinks.length} project links on page`);

        // Process new projects
        const beforeCount = this.projects.length;
        for (const projectUrl of projectLinks) {
          if (this.projects.length >= TARGET_PROJECTS) break;

          // Skip if already processed
          if (this.projects.some(p => p.url === projectUrl)) continue;

          // Add placeholder (we'll extract full data later)
          this.projects.push({
            title: '',
            url: projectUrl,
            imageUrls: [],
            appreciations: 0,
            views: 0,
            owner: '',
            downloadedImages: [],
          });
        }

        const newProjectsFound = this.projects.length - beforeCount;
        console.log(`Total unique projects collected: ${this.projects.length}/${TARGET_PROJECTS} (+${newProjectsFound} new)`);

        // Check if we're stuck (no new projects loaded)
        if (this.projects.length === lastProjectCount) {
          stuckCount++;
          console.log(`⚠️  No new projects loaded (stuck count: ${stuckCount}/10)`);

          // Try clicking "Load More" or "Show More" buttons
          const loadMoreSelectors = [
            'button:has-text("Load More")',
            'button:has-text("Show More")',
            'button[class*="load"]',
            'button[class*="more"]',
            'a:has-text("Load More")',
          ];

          let buttonClicked = false;
          for (const selector of loadMoreSelectors) {
            try {
              const button = await page.$(selector);
              if (button) {
                await button.click();
                console.log(`✓ Clicked "${selector}" button`);
                await page.waitForTimeout(3000);
                buttonClicked = true;
                break;
              }
            } catch (e) {
              // Button not found or not clickable
            }
          }

          if (!buttonClicked && stuckCount >= 10) {
            console.log('\n⚠️  Unable to load more projects after 10 attempts. Proceeding with collected projects.');
            break;
          }
        } else {
          stuckCount = 0; // Reset stuck count when we find new projects
        }

        lastProjectCount = this.projects.length;
        scrollAttempts++;

        // Status update every 10 scrolls
        if (scrollAttempts % 10 === 0) {
          console.log(`\n⏸️  Progress check: ${this.projects.length} projects collected after ${scrollAttempts} scrolls`);
        }

        // Add longer pause every 20 scrolls to avoid rate limiting
        if (scrollAttempts % 20 === 0) {
          console.log('⏸️  Pausing for rate limiting (10 seconds)...');
          await new Promise(resolve => setTimeout(resolve, 10000));
        }
      }

      console.log(`\n✅ Collection phase complete: ${this.projects.length} project URLs collected`);
      await page.close();

      // Now extract full data from each project
      return await this.extractProjectsData();
    } catch (error: any) {
      console.error(`Failed to scrape projects: ${error.message}`);
      await page.close();
      throw error;
    }
  }

  private async extractProjectsData(): Promise<BehanceProject[]> {
    console.log('\n' + '='.repeat(80));
    console.log('EXTRACTING PROJECT DATA');
    console.log('='.repeat(80));

    if (!this.context) {
      throw new Error('Browser context not available');
    }

    const page = await this.context.newPage();
    const validProjects: BehanceProject[] = [];

    for (let i = 0; i < this.projects.length; i++) {
      const project = this.projects[i];

      try {
        console.log(`\n[${i + 1}/${this.projects.length}] Extracting: ${project.url}`);

        await page.goto(project.url, { waitUntil: 'networkidle', timeout: 20000 });
        await page.waitForTimeout(1500);

        // Extract title
        const title = await page.$eval('h1', (el) => el.textContent?.trim() || 'Untitled').catch(() => 'Untitled');

        // Extract owner
        const owner = await page
          .$eval('a[class*="Owner"], div[class*="owner"] a', (el) => el.textContent?.trim() || 'Unknown')
          .catch(() => 'Unknown');

        // Extract stats
        const statsText = await page.evaluate(() => document.body.textContent || '').catch(() => '');
        const appreciations = this.parseNumber(statsText.match(/(\d+(?:,\d+)*)\s*appreciation/i)?.[1] || '0');
        const views = this.parseNumber(statsText.match(/(\d+(?:\.?\d*[KMB])?)\s*view/i)?.[1] || '0');

        // Check minimum appreciations threshold
        if (appreciations < MIN_APPRECIATIONS) {
          console.log(`  ✗ Skipped: Only ${appreciations} appreciations (minimum: ${MIN_APPRECIATIONS})`);
          continue;
        }

        // Extract ALL high-quality images from the project
        const imageUrls = await page.evaluate(() => {
          const images: string[] = [];
          const selectors = [
            'img[src*="project_modules"][src*="/max_"]',
            'img[src*="project_modules"][src*="/original/"]',
            'img[src*="project_modules"]:not([src*="/115/"]):not([src*="/202/"])',
          ];

          for (const selector of selectors) {
            const imgs = document.querySelectorAll(selector) as NodeListOf<HTMLImageElement>;
            imgs.forEach((img) => {
              if (img.src && !images.includes(img.src)) {
                // Upgrade to max quality if possible
                let imgUrl = img.src;
                if (imgUrl.includes('/115/') || imgUrl.includes('/202/') || imgUrl.includes('/230/')) {
                  imgUrl = imgUrl.replace(/\/(115|202|230|404)\//g, '/max_/');
                }
                images.push(imgUrl);
              }
            });
          }

          return images;
        }).catch(() => []);

        if (imageUrls.length === 0) {
          console.log(`  ✗ No images found`);
          continue;
        }

        console.log(`  ✓ ${title} by ${owner}`);
        console.log(`    ${appreciations.toLocaleString()} appreciations, ${views.toLocaleString()} views, ${imageUrls.length} images`);

        validProjects.push({
          title,
          url: project.url,
          imageUrls,
          appreciations,
          views,
          owner,
          downloadedImages: [],
        });

        // Rate limiting
        if (i % 10 === 0 && i > 0) {
          console.log('\n⏸️  Pausing for rate limiting (5 seconds)...');
          await new Promise(resolve => setTimeout(resolve, 5000));
        } else {
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      } catch (error: any) {
        console.warn(`  ✗ Failed: ${error.message}`);
      }
    }

    await page.close();
    return validProjects;
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
      console.log(`  Owner: ${project.owner}`);
      console.log(`  Images: ${project.imageUrls.length}`);

      // Create sanitized project directory
      const sanitizedTitle = project.title.replace(/[^a-z0-9]/gi, '-').toLowerCase().substring(0, 50);
      const projectDir = path.join(OUTPUT_DIR, `${sanitizedTitle}-${project.appreciations}app`);

      if (!fs.existsSync(projectDir)) {
        fs.mkdirSync(projectDir, { recursive: true });
      }

      // Download each image
      for (let j = 0; j < project.imageUrls.length; j++) {
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

        // Rate limiting
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      console.log(`  Project complete: ${project.downloadedImages.length}/${project.imageUrls.length} images`);

      // Longer pause between projects
      if (i % 5 === 0 && i > 0) {
        console.log('\n⏸️  Pausing between projects (5 seconds)...');
        await new Promise(resolve => setTimeout(resolve, 5000));
      }
    }

    console.log(`\n✅ Download complete: ${totalDownloaded} images downloaded, ${totalFailed} failed`);
  }

  private async downloadImage(imageUrl: string, outputDir: string, index: number): Promise<string | null> {
    return new Promise((resolve) => {
      try {
        const ext = path.extname(new URL(imageUrl).pathname) || '.jpg';
        const filename = `image-${index}${ext}`;
        const filepath = path.join(outputDir, filename);

        // Skip if already exists
        if (fs.existsSync(filepath)) {
          resolve(filepath);
          return;
        }

        const client = imageUrl.startsWith('https') ? https : http;

        client.get(imageUrl, (response) => {
          if (response.statusCode !== 200) {
            resolve(null);
            return;
          }

          const chunks: Buffer[] = [];

          response.on('data', (chunk) => chunks.push(chunk));

          response.on('end', () => {
            const buffer = Buffer.concat(chunks);

            // Filter out small images
            if (buffer.length < 50 * 1024) {
              resolve(null);
              return;
            }

            fs.writeFileSync(filepath, buffer);
            resolve(filepath);
          });
        }).on('error', () => resolve(null));
      } catch (error) {
        resolve(null);
      }
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
  console.log('BEHANCE "MUCH APPRECIATED" PROJECTS SCRAPER');
  console.log('='.repeat(80));
  console.log(`Target: ${TARGET_PROJECTS.toLocaleString()} projects`);
  console.log(`Minimum appreciations: ${MIN_APPRECIATIONS.toLocaleString()}`);
  console.log('='.repeat(80));

  const scraper = new BehanceAppreciatedScraper();

  try {
    await scraper.launch(process.env.BEHANCE_HEADLESS !== 'false');

    // Step 1: Scrape project links and data
    console.log('\n' + '='.repeat(80));
    console.log('STEP 1: COLLECTING MOST APPRECIATED PROJECTS');
    console.log('='.repeat(80));

    const projects = await scraper.scrapeMostAppreciatedProjects();

    if (projects.length === 0) {
      console.error('\n❌ No projects found');
      await scraper.close();
      process.exit(1);
    }

    console.log(`\n✅ Found ${projects.length} projects with ${MIN_APPRECIATIONS}+ appreciations`);

    // Step 2: Download images
    await scraper.downloadProjectImages(projects);

    // Step 3: Save metadata
    console.log('\n' + '='.repeat(80));
    console.log('SAVING METADATA');
    console.log('='.repeat(80));

    const metadataDir = path.dirname(METADATA_FILE);
    if (!fs.existsSync(metadataDir)) {
      fs.mkdirSync(metadataDir, { recursive: true });
    }

    const totalImages = projects.reduce((sum, p) => sum + p.downloadedImages.length, 0);
    const totalExpected = projects.reduce((sum, p) => sum + p.imageUrls.length, 0);

    const metadata = {
      scrapedAt: new Date().toISOString(),
      targetProjects: TARGET_PROJECTS,
      minAppreciations: MIN_APPRECIATIONS,
      projectsFound: projects.length,
      totalImagesDownloaded: totalImages,
      totalImagesFailed: totalExpected - totalImages,
      projects: projects.map(p => ({
        title: p.title,
        url: p.url,
        appreciations: p.appreciations,
        views: p.views,
        owner: p.owner,
        imageCount: p.downloadedImages.length,
      })),
    };

    fs.writeFileSync(METADATA_FILE, JSON.stringify(metadata, null, 2));
    console.log(`✓ Metadata saved to: ${METADATA_FILE}`);

    // Final summary
    const duration = Math.round((Date.now() - startTime) / 1000);
    const avgAppreciations = Math.round(projects.reduce((sum, p) => sum + p.appreciations, 0) / projects.length);

    console.log('\n' + '='.repeat(80));
    console.log('SCRAPING COMPLETE!');
    console.log('='.repeat(80));
    console.log(`
📊 SUMMARY:
───────────────────────────────────────────────────────────────────────────────
Projects scraped:        ${projects.length.toLocaleString()}
Average appreciations:   ${avgAppreciations.toLocaleString()}
Total images:            ${totalImages.toLocaleString()}
Failed downloads:        ${(totalExpected - totalImages).toLocaleString()}
Success rate:            ${Math.round((totalImages / totalExpected) * 100)}%
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
