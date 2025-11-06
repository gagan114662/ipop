// Script to scrape Ads of the World professional advertising archive
import { chromium, Browser, BrowserContext, Page } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';
import * as https from 'https';
import * as http from 'http';

const BASE_URL = 'https://www.adsoftheworld.com';
const OUTPUT_DIR = './reference-cache/images/adsoftheworld';
const METADATA_FILE = './reference-cache/adsoftheworld-metadata.json';
const MAX_PAGES = parseInt(process.env.MAX_PAGES || '50'); // Limit pages to scrape
const IMAGES_PER_AD = parseInt(process.env.IMAGES_PER_AD || '5'); // Max images per ad

interface Ad {
  title: string;
  url: string;
  brand: string;
  agency: string;
  industry: string;
  country: string;
  date: string;
  imageUrls: string[];
  videoUrls: string[];
  downloadedImages: string[];
  downloadedVideos: string[];
  description?: string;
}

class AdsOfTheWorldScraper {
  private browser: Browser | null = null;
  private context: BrowserContext | null = null;
  private allAds: Map<string, Ad> = new Map();

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

  async scrapeProfessionalAds(): Promise<Ad[]> {
    if (!this.context) {
      throw new Error('Browser not launched');
    }

    const page = await this.context.newPage();
    const ads: Ad[] = [];

    try {
      console.log('Navigating to Ads of the World...');
      // Try main page first, then navigate to professional
      await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.waitForTimeout(3000);

      console.log('Navigating to professional section...');
      await page.goto(`${BASE_URL}/professional`, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.waitForTimeout(5000);

      // Extract all ad links from the main page
      console.log('Extracting ad links...');
      console.log('Page URL:', page.url());

      // Take screenshot for debugging
      await page.screenshot({ path: './debug-aotw.png', fullPage: false });
      console.log('Screenshot saved to debug-aotw.png');

      let currentPage = 1;
      let hasNextPage = true;
      const SCROLL_ITERATIONS = parseInt(process.env.SCROLL_ITERATIONS || '20'); // How many times to scroll per "page"

      while (hasNextPage && currentPage <= MAX_PAGES) {
        console.log(`\n[Page ${currentPage}/${MAX_PAGES}]`);
        console.log(`  Scrolling ${SCROLL_ITERATIONS} times to load more campaigns...`);

        // Scroll multiple times to load content via infinite scroll
        await this.scrollPage(page, SCROLL_ITERATIONS);

        // Extract ad links - look for ANY non-navigation links
        const { adLinks, debug } = await page.evaluate(() => {
          const links: string[] = [];
          const debug: string[] = [];

          // Get all links
          const allLinks = Array.from(document.querySelectorAll('a')) as HTMLAnchorElement[];

          for (const link of allLinks) {
            const href = link.href;

            if (href && href.includes('adsoftheworld.com')) {
              // ONLY accept /campaigns/ URLs, exclude /campaigns/new
              const isCampaign = href.includes('/campaigns/') && !href.includes('/campaigns/new');

              if (isCampaign && !links.includes(href)) {
                links.push(href);

                // Debug: collect what we're finding
                if (debug.length < 20) {
                  debug.push(`${href} | text: ${link.textContent?.trim().substring(0, 40)}`);
                }
              }
            }
          }

          return { adLinks: links, debug };
        });

        console.log(`  Found ${adLinks.length} potential campaign links on page ${currentPage}`);

        if (currentPage === 1) {
          console.log('\n  Sample campaign candidates:');
          debug.slice(0, 10).forEach((item, i) => console.log(`    ${i + 1}. ${item}`));
        }

        // Extract data from each ad
        for (let i = 0; i < adLinks.length; i++) {
          const adUrl = adLinks[i];

          if (this.allAds.has(adUrl)) {
            console.log(`  [${i + 1}/${adLinks.length}] Already scraped: ${adUrl}`);
            continue;
          }

          try {
            const ad = await this.extractAdData(page, adUrl);
            if (ad && (ad.imageUrls.length > 0 || ad.videoUrls.length > 0)) {
              ads.push(ad);
              this.allAds.set(adUrl, ad);
              console.log(`  [${i + 1}/${adLinks.length}] ✓ ${ad.title} (${ad.imageUrls.length} images, ${ad.videoUrls.length} videos)`);
            } else {
              console.log(`  [${i + 1}/${adLinks.length}] ✗ Skipped (no media)`);
            }
            await page.waitForTimeout(1000);
          } catch (error: any) {
            console.warn(`  [${i + 1}/${adLinks.length}] ✗ Error: ${error.message}`);
          }
        }

        // Continue scrolling for next iteration (infinite scroll simulation)
        currentPage++;
        if (currentPage <= MAX_PAGES) {
          // Check if we loaded new campaigns by comparing link count
          const previousLinkCount = adLinks.length;
          console.log(`  Continuing to scroll for more campaigns (currently have ${previousLinkCount} campaigns)...`);

          // Just continue - the next iteration will scroll more and find new campaigns
        } else {
          console.log(`  Reached max pages (${MAX_PAGES}), ending scrape`);
          hasNextPage = false;
        }
      }

      await page.close();
      return ads;
    } catch (error: any) {
      console.error(`Failed to scrape professional ads: ${error.message}`);
      await page.close();
      return [];
    }
  }

  private async scrollPage(page: Page, iterations: number = 5): Promise<void> {
    for (let i = 0; i < iterations; i++) {
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(2000);
    }
  }

  private async extractAdData(page: Page, adUrl: string): Promise<Ad | null> {
    try {
      await page.goto(adUrl, { waitUntil: 'networkidle', timeout: 20000 });
      await page.waitForTimeout(1500);

      // Extract title
      const title = await page.$eval('h1, .title, [class*="title"]', (el) => el.textContent?.trim() || 'Untitled')
        .catch(() => 'Untitled');

      // Extract brand
      const brand = await page.$eval('[class*="brand"], .brand, a[href*="/brand/"]', (el) => el.textContent?.trim() || 'Unknown')
        .catch(() => 'Unknown');

      // Extract agency
      const agency = await page.$eval('[class*="agency"], .agency, a[href*="/agency/"]', (el) => el.textContent?.trim() || 'Unknown')
        .catch(() => 'Unknown');

      // Extract industry
      const industry = await page.$eval('[class*="industry"], .industry, a[href*="/industry/"]', (el) => el.textContent?.trim() || 'Unknown')
        .catch(() => 'Unknown');

      // Extract country
      const country = await page.$eval('[class*="country"], .country, a[href*="/country/"]', (el) => el.textContent?.trim() || 'Unknown')
        .catch(() => 'Unknown');

      // Extract date
      const date = await page.evaluate(() => {
        const timeEl = document.querySelector('time');
        if (timeEl) return timeEl.getAttribute('datetime') || timeEl.textContent?.trim() || '';
        const dateText = document.body.textContent?.match(/\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4}/)?.[0];
        return dateText || 'Unknown';
      }).catch(() => 'Unknown');

      // Extract description
      const description = await page.$eval('p, .description, [class*="description"]', (el) => el.textContent?.trim())
        .catch(() => undefined);

      // Extract all images
      const imageUrls = await page.evaluate(() => {
        const images: string[] = [];
        const selectors = [
          'img[src*="adsoftheworld"]',
          'img.ad-image',
          'img[class*="media"]',
          'img[class*="gallery"]',
          'picture img',
          'figure img',
        ];

        for (const selector of selectors) {
          const imgs = document.querySelectorAll(selector) as NodeListOf<HTMLImageElement>;
          imgs.forEach((img) => {
            if (img.src && !img.src.includes('avatar') && !img.src.includes('logo') && !images.includes(img.src)) {
              // Try to get largest version
              let imgUrl = img.src;

              // Check srcset for larger versions
              if (img.srcset) {
                const srcsetParts = img.srcset.split(',').map(s => s.trim());
                const largest = srcsetParts[srcsetParts.length - 1]?.split(' ')[0];
                if (largest) imgUrl = largest;
              }

              // Upgrade URL to higher quality if possible
              imgUrl = imgUrl.replace(/\/thumb\//, '/large/')
                             .replace(/\/small\//, '/large/')
                             .replace(/\/medium\//, '/large/')
                             .replace(/_thumb\./, '_large.')
                             .replace(/_small\./, '_large.')
                             .replace(/_medium\./, '_large.');

              images.push(imgUrl);
            }
          });
          if (images.length > 0) break;
        }

        return images;
      }).catch(() => []);

      // Extract all videos
      const videoUrls = await page.evaluate(() => {
        const videos: string[] = [];

        // Look for video tags
        const videoElements = document.querySelectorAll('video') as NodeListOf<HTMLVideoElement>;
        videoElements.forEach((video) => {
          if (video.src && !videos.includes(video.src)) {
            videos.push(video.src);
          }
          // Check source tags within video
          const sources = video.querySelectorAll('source') as NodeListOf<HTMLSourceElement>;
          sources.forEach((source) => {
            if (source.src && !videos.includes(source.src)) {
              videos.push(source.src);
            }
          });
        });

        // Look for iframe embeds (YouTube, Vimeo, etc.)
        const iframes = document.querySelectorAll('iframe') as NodeListOf<HTMLIFrameElement>;
        iframes.forEach((iframe) => {
          const src = iframe.src;
          if (src && (
            src.includes('youtube.com') ||
            src.includes('youtu.be') ||
            src.includes('vimeo.com') ||
            src.includes('player.vimeo')
          ) && !videos.includes(src)) {
            videos.push(src);
          }
        });

        return videos;
      }).catch(() => []);

      if (imageUrls.length === 0 && videoUrls.length === 0) {
        return null;
      }

      return {
        title,
        url: adUrl,
        brand,
        agency,
        industry,
        country,
        date,
        imageUrls,
        videoUrls,
        downloadedImages: [],
        downloadedVideos: [],
        description,
      };
    } catch (error: any) {
      console.warn(`Failed to extract ad data: ${error.message}`);
      return null;
    }
  }

  async downloadAdImages(ads: Ad[]): Promise<void> {
    console.log('\n' + '='.repeat(80));
    console.log('DOWNLOADING IMAGES');
    console.log('='.repeat(80));

    let totalDownloaded = 0;
    let totalFailed = 0;

    for (let i = 0; i < ads.length; i++) {
      const ad = ads[i];

      console.log(`\n[${i + 1}/${ads.length}] ${ad.title}`);
      console.log(`  Brand: ${ad.brand} | Agency: ${ad.agency} | Industry: ${ad.industry}`);
      console.log(`  Media: ${ad.imageUrls.length} images, ${ad.videoUrls.length} videos`);

      // Create directory structure
      const sanitizedBrand = ad.brand.replace(/[^a-z0-9]/gi, '-').toLowerCase().substring(0, 30);
      const sanitizedTitle = ad.title.replace(/[^a-z0-9]/gi, '-').toLowerCase().substring(0, 40);
      const sanitizedIndustry = ad.industry.replace(/[^a-z0-9]/gi, '-').toLowerCase();
      const adDir = path.join(OUTPUT_DIR, sanitizedIndustry, `${sanitizedBrand}-${sanitizedTitle}`);

      if (!fs.existsSync(adDir)) {
        fs.mkdirSync(adDir, { recursive: true });
      }

      // Download images (limit to IMAGES_PER_AD)
      for (let j = 0; j < Math.min(ad.imageUrls.length, IMAGES_PER_AD); j++) {
        const imageUrl = ad.imageUrls[j];

        try {
          const localPath = await this.downloadImage(imageUrl, adDir, j);
          if (localPath) {
            ad.downloadedImages.push(localPath);
            totalDownloaded++;
            console.log(`  [${j + 1}/${Math.min(ad.imageUrls.length, IMAGES_PER_AD)}] ✓ Downloaded`);
          } else {
            totalFailed++;
            console.log(`  [${j + 1}/${Math.min(ad.imageUrls.length, IMAGES_PER_AD)}] ✗ Failed`);
          }
        } catch (error: any) {
          totalFailed++;
          console.log(`  [${j + 1}/${Math.min(ad.imageUrls.length, IMAGES_PER_AD)}] ✗ Error: ${error.message}`);
        }

        await new Promise(resolve => setTimeout(resolve, 500));
      }

      // Save video URLs to a text file in the ad directory
      if (ad.videoUrls.length > 0) {
        const videoLinksFile = path.join(adDir, 'video-urls.txt');
        const videoContent = ad.videoUrls.map((url, i) => `${i + 1}. ${url}`).join('\n');
        fs.writeFileSync(videoLinksFile, videoContent);
        console.log(`  ✓ Saved ${ad.videoUrls.length} video URLs`);
      }

      console.log(`  Complete: ${ad.downloadedImages.length}/${Math.min(ad.imageUrls.length, IMAGES_PER_AD)} images, ${ad.videoUrls.length} video URLs saved`);

      // Pause between ads
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

      if (buffer.length < 10 * 1024) {
        resolve(null);
        return;
      }

      fs.writeFileSync(filepath, buffer);
      resolve(filepath);
    });
  }
}

async function main() {
  const startTime = Date.now();

  console.log('='.repeat(80));
  console.log('ADS OF THE WORLD SCRAPER');
  console.log('='.repeat(80));
  console.log(`Max pages: ${MAX_PAGES}`);
  console.log(`Images per ad: ${IMAGES_PER_AD}`);
  console.log('='.repeat(80));

  const scraper = new AdsOfTheWorldScraper();

  try {
    await scraper.launch(process.env.AOTW_HEADLESS !== 'false');

    // Scrape professional ads
    const ads = await scraper.scrapeProfessionalAds();

    console.log('\n' + '='.repeat(80));
    console.log('SCRAPING COMPLETE');
    console.log('='.repeat(80));
    console.log(`Total ads found: ${ads.length}`);

    // Download images
    if (ads.length > 0) {
      await scraper.downloadAdImages(ads);
    }

    // Save metadata
    console.log('\n' + '='.repeat(80));
    console.log('SAVING METADATA');
    console.log('='.repeat(80));

    const metadataDir = path.dirname(METADATA_FILE);
    if (!fs.existsSync(metadataDir)) {
      fs.mkdirSync(metadataDir, { recursive: true });
    }

    const totalImages = ads.reduce((sum, ad) => sum + ad.downloadedImages.length, 0);
    const totalVideos = ads.reduce((sum, ad) => sum + ad.videoUrls.length, 0);

    const metadata = {
      scrapedAt: new Date().toISOString(),
      adsFound: ads.length,
      totalImagesDownloaded: totalImages,
      totalVideosFound: totalVideos,
      ads: ads.map(ad => ({
        title: ad.title,
        url: ad.url,
        brand: ad.brand,
        agency: ad.agency,
        industry: ad.industry,
        country: ad.country,
        date: ad.date,
        description: ad.description,
        imageCount: ad.downloadedImages.length,
        videoCount: ad.videoUrls.length,
        videoUrls: ad.videoUrls,
      })),
    };

    fs.writeFileSync(METADATA_FILE, JSON.stringify(metadata, null, 2));
    console.log(`✓ Metadata saved: ${METADATA_FILE}`);

    // Final summary
    const duration = Math.round((Date.now() - startTime) / 1000);

    console.log('\n' + '='.repeat(80));
    console.log('SCRAPING COMPLETE!');
    console.log('='.repeat(80));
    console.log(`
📊 SUMMARY:
───────────────────────────────────────────────────────────────────────────────
Ads scraped:             ${ads.length.toLocaleString()}
Total images:            ${totalImages.toLocaleString()}
Total videos:            ${totalVideos.toLocaleString()}
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
