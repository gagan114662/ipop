// Script to scrape projects from Behance Best of Behance gallery
import { chromium, Browser, BrowserContext, Page } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';
import * as https from 'https';
import * as http from 'http';

const OUTPUT_DIR = './reference-cache/images/behance/best-of-behance';
const METADATA_FILE = './reference-cache/behance-best-metadata.json';
const MAX_PROJECTS = parseInt(process.env.MAX_PROJECTS || '200'); // How many projects to scrape
const SCROLL_ITERATIONS = parseInt(process.env.SCROLL_ITERATIONS || '20'); // How many times to scroll

interface BehanceProject {
  title: string;
  url: string;
  imageUrls: string[];
  appreciations: number;
  views: number;
  owner: string;
  downloadedImages: string[];
}

class BehanceBestScraper {
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

  async scrapeBestOfBehance(): Promise<void> {
    if (!this.context) {
      throw new Error('Browser not launched');
    }

    const page = await this.context.newPage();

    try {
      const url = 'https://www.behance.net/galleries/best-of-behance';
      console.log(`Navigating to: ${url}`);

      await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(3000);

      console.log(`Scrolling to load projects (${SCROLL_ITERATIONS} iterations)...`);

      // Scroll multiple times to load more projects
      for (let i = 0; i < SCROLL_ITERATIONS; i++) {
        await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await page.waitForTimeout(2000);
        console.log(`  Scroll ${i + 1}/${SCROLL_ITERATIONS}`);
      }

      // Extract project links
      const projectLinks = await page.$$eval('a[href*="/gallery/"]', (links) =>
        links
          .map((link) => (link as HTMLAnchorElement).href)
          .filter((href, index, self) => href.includes('/gallery/') && self.indexOf(href) === index)
      );

      console.log(`\nFound ${projectLinks.length} project links`);
      console.log(`Will scrape up to ${Math.min(projectLinks.length, MAX_PROJECTS)} projects\n`);

      // Extract data from each project
      const projectsToScrape = Math.min(projectLinks.length, MAX_PROJECTS);

      for (let i = 0; i < projectsToScrape; i++) {
        const projectUrl = projectLinks[i];

        try {
          const project = await this.extractProjectData(page, projectUrl);

          if (project && project.imageUrls.length > 0) {
            this.projects.push(project);
            console.log(`  [${i + 1}/${projectsToScrape}] ✓ ${project.title} (${project.appreciations} app, ${project.imageUrls.length} images)`);
          } else {
            console.log(`  [${i + 1}/${projectsToScrape}] ✗ Skipped (no images)`);
          }

          // Rate limiting
          await page.waitForTimeout(1000);
        } catch (error: any) {
          console.warn(`  [${i + 1}/${projectsToScrape}] ✗ Error: ${error.message}`);
        }
      }

      await page.close();
    } catch (error: any) {
      console.error(`Failed to scrape Best of Behance: ${error.message}`);
      await page.close();
      throw error;
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
        downloadedImages: [],
      };
    } catch (error) {
      return null;
    }
  }

  private parseNumber(str: string): number {
    str = str.replace(/,/g, '');
    if (str.includes('K')) return parseFloat(str) * 1000;
    if (str.includes('M')) return parseFloat(str) * 1000000;
    if (str.includes('B')) return parseFloat(str) * 1000000000;
    return parseInt(str) || 0;
  }

  async downloadAllImages(): Promise<void> {
    console.log('\n' + '='.repeat(80));
    console.log('DOWNLOADING IMAGES');
    console.log('='.repeat(80));
    console.log(`Total projects: ${this.projects.length}\n`);

    let totalDownloaded = 0;

    for (let i = 0; i < this.projects.length; i++) {
      const project = this.projects[i];
      console.log(`[${i + 1}/${this.projects.length}] ${project.title}`);

      const downloaded = await this.downloadProjectImages(project);
      totalDownloaded += downloaded;

      console.log(`  ✓ Downloaded ${downloaded}/${project.imageUrls.length} images\n`);

      // Rate limiting
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    console.log('='.repeat(80));
    console.log(`Total images downloaded: ${totalDownloaded}`);
    console.log('='.repeat(80));
  }

  private async downloadProjectImages(project: BehanceProject): Promise<number> {
    const sanitizedTitle = project.title.replace(/[^a-z0-9]/gi, '-').toLowerCase().substring(0, 50);
    const projectDirName = `${sanitizedTitle}-${project.appreciations}app`;
    const projectDir = path.join(OUTPUT_DIR, projectDirName);

    if (!fs.existsSync(projectDir)) {
      fs.mkdirSync(projectDir, { recursive: true });
    }

    let downloadedCount = 0;

    for (let i = 0; i < project.imageUrls.length; i++) {
      const imageUrl = project.imageUrls[i];
      const extension = imageUrl.split('.').pop()?.split('?')[0] || 'jpg';
      const filename = `image-${i + 1}.${extension}`;
      const filepath = path.join(projectDir, filename);

      try {
        await this.downloadImage(imageUrl, filepath);
        project.downloadedImages.push(filepath);
        downloadedCount++;
      } catch (error: any) {
        console.warn(`    ✗ Failed to download image ${i + 1}: ${error.message}`);
      }
    }

    return downloadedCount;
  }

  private downloadImage(url: string, filepath: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const protocol = url.startsWith('https') ? https : http;

      protocol
        .get(url, (response) => {
          if (response.statusCode === 200) {
            const fileStream = fs.createWriteStream(filepath);
            response.pipe(fileStream);

            fileStream.on('finish', () => {
              fileStream.close();
              resolve();
            });

            fileStream.on('error', (err) => {
              fs.unlinkSync(filepath);
              reject(err);
            });
          } else {
            reject(new Error(`HTTP ${response.statusCode}`));
          }
        })
        .on('error', (err) => {
          reject(err);
        });
    });
  }

  saveMetadata(): void {
    const metadata = {
      scrapedAt: new Date().toISOString(),
      source: 'Best of Behance',
      url: 'https://www.behance.net/galleries/best-of-behance',
      projectsFound: this.projects.length,
      totalImagesDownloaded: this.projects.reduce((sum, p) => sum + p.downloadedImages.length, 0),
      projects: this.projects.map((p) => ({
        title: p.title,
        url: p.url,
        appreciations: p.appreciations,
        views: p.views,
        owner: p.owner,
        imageCount: p.imageUrls.length,
        downloadedCount: p.downloadedImages.length,
      })),
    };

    fs.writeFileSync(METADATA_FILE, JSON.stringify(metadata, null, 2));
    console.log(`\n✓ Metadata saved to: ${METADATA_FILE}`);
  }

  printSummary(): void {
    console.log('\n' + '='.repeat(80));
    console.log('SCRAPING COMPLETE!');
    console.log('='.repeat(80));

    const totalImages = this.projects.reduce((sum, p) => sum + p.downloadedImages.length, 0);
    const avgAppreciations = Math.round(
      this.projects.reduce((sum, p) => sum + p.appreciations, 0) / this.projects.length
    );

    console.log(`\nProjects scraped: ${this.projects.length}`);
    console.log(`Total images: ${totalImages}`);
    console.log(`Average appreciations: ${avgAppreciations.toLocaleString()}`);
    console.log(`Output directory: ${OUTPUT_DIR}`);
    console.log(`Metadata file: ${METADATA_FILE}\n`);
    console.log('='.repeat(80));
  }
}

async function main() {
  const scraper = new BehanceBestScraper();

  try {
    const headless = process.env.BEHANCE_HEADLESS !== 'false';

    console.log('='.repeat(80));
    console.log('BEHANCE BEST OF BEHANCE SCRAPER');
    console.log('='.repeat(80));
    console.log(`Max projects: ${MAX_PROJECTS}`);
    console.log(`Scroll iterations: ${SCROLL_ITERATIONS}`);
    console.log(`Headless mode: ${headless}`);
    console.log('='.repeat(80) + '\n');

    await scraper.launch(headless);
    await scraper.scrapeBestOfBehance();
    await scraper.downloadAllImages();
    scraper.saveMetadata();
    scraper.printSummary();
  } catch (error: any) {
    console.error('Error:', error.message);
    process.exit(1);
  } finally {
    await scraper.close();
  }
}

main();
