// Script to scrape ALL boards from a Pinterest profile
import { PinterestScraper, PinterestPin } from '../services/pinterest-scraper';
import * as fs from 'fs';
import * as path from 'path';

const PROFILE_URL = 'https://ca.pinterest.com/sangichandresh/';
const OUTPUT_DIR = './reference-cache/images/pinterest-profile';
const METADATA_FILE = './reference-cache/pinterest-profile-metadata.json';
const MAX_PINS_PER_BOARD = 200; // Limit per board to avoid overwhelming

interface BoardInfo {
  name: string;
  url: string;
  pinCount: number;
}

interface ProfileScrapeResult {
  profile: string;
  boards: {
    name: string;
    url: string;
    pins: PinterestPin[];
    downloadedImages: string[];
  }[];
  stats: {
    totalBoards: number;
    totalPins: number;
    totalDownloads: number;
    failedDownloads: number;
  };
}

async function discoverBoards(scraper: PinterestScraper, profileUrl: string): Promise<BoardInfo[]> {
  console.log('\n' + '='.repeat(80));
  console.log('DISCOVERING BOARDS FROM PROFILE');
  console.log('='.repeat(80));
  console.log(`Profile: ${profileUrl}\n`);

  // @ts-ignore - accessing private context for custom scraping
  const context = scraper['context'];
  if (!context) {
    throw new Error('Browser context not available');
  }

  const page = await context.newPage();
  const boards: BoardInfo[] = [];

  try {
    await page.goto(profileUrl, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(3000);

    // Scroll to load all boards
    console.log('Scrolling to load all boards...');
    for (let i = 0; i < 5; i++) {
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(2000);
    }

    // Extract board information
    const boardData = await page.evaluate(() => {
      const boardElements = document.querySelectorAll('a[href*="/"][href*="/"]');
      const extracted: { name: string; url: string; pinCount: string }[] = [];

      boardElements.forEach((el) => {
        const href = el.getAttribute('href');
        if (href && href.includes('/') && !href.includes('/pin/')) {
          // Look for board name
          const nameEl = el.querySelector('[data-test-id="board-name"]') || el;
          const name = nameEl.textContent?.trim() || '';

          // Look for pin count
          const countEl = el.querySelector('[data-test-id="board-pin-count"]');
          const pinCount = countEl?.textContent?.trim() || '0';

          if (name && href.length > 1) {
            const fullUrl = href.startsWith('http') ? href : `https://www.pinterest.com${href}`;
            extracted.push({ name, url: fullUrl, pinCount });
          }
        }
      });

      return extracted;
    });

    // Parse board data
    for (const board of boardData) {
      const count = parseInt(board.pinCount.replace(/\D/g, '')) || 0;
      if (board.url && board.name && !boards.find(b => b.url === board.url)) {
        boards.push({
          name: board.name,
          url: board.url,
          pinCount: count,
        });
      }
    }

    // Remove duplicates and sort by pin count
    const uniqueBoards = boards
      .filter((board, index, self) =>
        index === self.findIndex(b => b.url === board.url)
      )
      .sort((a, b) => b.pinCount - a.pinCount);

    console.log(`\n✅ Found ${uniqueBoards.length} boards:\n`);
    uniqueBoards.forEach((board, i) => {
      console.log(`${i + 1}. ${board.name} (${board.pinCount} pins)`);
      console.log(`   ${board.url}`);
    });

    await page.close();
    return uniqueBoards;
  } catch (error: any) {
    console.error(`Failed to discover boards: ${error.message}`);
    await page.close();
    return [];
  }
}

async function scrapeEntireProfile() {
  console.log('='.repeat(80));
  console.log('PINTEREST PROFILE SCRAPER - ALL BOARDS');
  console.log('='.repeat(80));

  const startTime = Date.now();

  const scraper = new PinterestScraper({
    email: process.env.PINTEREST_EMAIL || 'gagan@getfoolish.com',
    password: process.env.PINTEREST_PASSWORD || 'vandanchopra@114',
    headless: process.env.PINTEREST_HEADLESS !== 'false',
    cookiesFile: './config/pinterest-cookies.json',
  });

  const result: ProfileScrapeResult = {
    profile: PROFILE_URL,
    boards: [],
    stats: {
      totalBoards: 0,
      totalPins: 0,
      totalDownloads: 0,
      failedDownloads: 0,
    },
  };

  try {
    await scraper.launch();

    // Discover all boards
    const boards = await discoverBoards(scraper, PROFILE_URL);
    result.stats.totalBoards = boards.length;

    if (boards.length === 0) {
      console.error('\n❌ No boards found on this profile');
      await scraper.close();
      return;
    }

    // Scrape each board
    for (let i = 0; i < boards.length; i++) {
      const board = boards[i];

      console.log('\n' + '='.repeat(80));
      console.log(`BOARD ${i + 1}/${boards.length}: ${board.name}`);
      console.log('='.repeat(80));

      try {
        const pins = await scraper.scrapeBoard(board.url, MAX_PINS_PER_BOARD);
        result.stats.totalPins += pins.length;

        console.log(`\n✓ Scraped ${pins.length} pins from "${board.name}"`);

        // Download images for this board
        const boardOutputDir = path.join(OUTPUT_DIR, board.name.replace(/[^a-z0-9]/gi, '-').toLowerCase());
        const downloadedImages: string[] = [];
        let failedCount = 0;

        console.log(`\nDownloading images to: ${boardOutputDir}`);

        for (let j = 0; j < pins.length; j++) {
          const pin = pins[j];
          console.log(`  [${j + 1}/${pins.length}] ${pin.title.substring(0, 60)}...`);

          const localPath = await scraper.downloadImage(pin.imageUrl, boardOutputDir);

          if (localPath) {
            downloadedImages.push(localPath);
            result.stats.totalDownloads++;
          } else {
            failedCount++;
            result.stats.failedDownloads++;
          }

          // Rate limiting
          if (j % 10 === 0 && j > 0) {
            await new Promise(resolve => setTimeout(resolve, 5000));
          } else {
            await new Promise(resolve => setTimeout(resolve, 1000));
          }
        }

        result.boards.push({
          name: board.name,
          url: board.url,
          pins,
          downloadedImages,
        });

        console.log(`\n✓ Board complete: ${downloadedImages.length} images downloaded, ${failedCount} failed`);
      } catch (error: any) {
        console.error(`\n❌ Failed to scrape board "${board.name}": ${error.message}`);
      }
    }

    // Save metadata
    console.log('\n' + '='.repeat(80));
    console.log('SAVING METADATA');
    console.log('='.repeat(80));

    const metadataDir = path.dirname(METADATA_FILE);
    if (!fs.existsSync(metadataDir)) {
      fs.mkdirSync(metadataDir, { recursive: true });
    }

    const metadata = {
      scrapedAt: new Date().toISOString(),
      profileUrl: PROFILE_URL,
      ...result,
    };

    fs.writeFileSync(METADATA_FILE, JSON.stringify(metadata, null, 2));
    console.log(`✓ Metadata saved to: ${METADATA_FILE}`);

    // Print final summary
    const duration = Math.round((Date.now() - startTime) / 1000);

    console.log('\n' + '='.repeat(80));
    console.log('PROFILE SCRAPING COMPLETE!');
    console.log('='.repeat(80));
    console.log(`
📊 SUMMARY:
───────────────────────────────────────────────────────────────────────────────
Profile:                 ${PROFILE_URL}
Total boards:            ${result.stats.totalBoards}
Total pins scraped:      ${result.stats.totalPins}
───────────────────────────────────────────────────────────────────────────────
Images downloaded:       ${result.stats.totalDownloads}
Failed downloads:        ${result.stats.failedDownloads}
Success rate:            ${Math.round((result.stats.totalDownloads / result.stats.totalPins) * 100)}%
───────────────────────────────────────────────────────────────────────────────
Output directory:        ${OUTPUT_DIR}
Metadata file:           ${METADATA_FILE}
Duration:                ${Math.floor(duration / 60)}m ${duration % 60}s
───────────────────────────────────────────────────────────────────────────────

✅ Next steps:
   1. Run industry classification: npm run classify-pinterest
   2. Review and curate images
   3. Train LoRAs per industry
`);

    await scraper.close();
  } catch (error: any) {
    console.error('\n❌ PROFILE SCRAPING FAILED:', error.message);
    console.error(error.stack);
    await scraper.close();
    process.exit(1);
  }
}

// Run the scraper
scrapeEntireProfile()
  .then(() => {
    console.log('\n✅ Script completed successfully');
    process.exit(0);
  })
  .catch((error) => {
    console.error('\n❌ Script failed:', error);
    process.exit(1);
  });
