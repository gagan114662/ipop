// Script to scrape Pinterest board + "More ideas" at scale
import { PinterestScraper, PinterestPin } from '../services/pinterest-scraper';
import * as fs from 'fs';
import * as path from 'path';

const BOARD_URL = 'https://ca.pinterest.com/sangichandresh/winners-campaign/';
const OUTPUT_DIR = './reference-cache/images/pinterest';
const METADATA_FILE = './reference-cache/pinterest-metadata.json';

interface ScrapingResult {
  boardPins: PinterestPin[];
  moreIdeasPins: PinterestPin[];
  downloadedImages: {
    pinId: string;
    localPath: string;
    imageUrl: string;
    title: string;
  }[];
  stats: {
    totalPinsScraped: number;
    totalImagesDownloaded: number;
    boardPinsCount: number;
    moreIdeasCount: number;
    failedDownloads: number;
  };
}

async function scrapeAtScale() {
  console.log('='.repeat(80));
  console.log('PINTEREST SCRAPING AT SCALE');
  console.log('='.repeat(80));

  const startTime = Date.now();

  // Initialize scraper
  const scraper = new PinterestScraper({
    email: process.env.PINTEREST_EMAIL || 'gagan@getfoolish.com',
    password: process.env.PINTEREST_PASSWORD || 'vandanchopra@114',
    headless: process.env.PINTEREST_HEADLESS !== 'false', // Default to headless
    cookiesFile: './config/pinterest-cookies.json',
  });

  const result: ScrapingResult = {
    boardPins: [],
    moreIdeasPins: [],
    downloadedImages: [],
    stats: {
      totalPinsScraped: 0,
      totalImagesDownloaded: 0,
      boardPinsCount: 0,
      moreIdeasCount: 0,
      failedDownloads: 0,
    },
  };

  try {
    // Launch browser
    await scraper.launch();

    // Step 1: Scrape main board
    console.log('\n' + '='.repeat(80));
    console.log('STEP 1: Scraping main board');
    console.log('='.repeat(80));

    result.boardPins = await scraper.scrapeBoard(BOARD_URL, 200);
    result.stats.boardPinsCount = result.boardPins.length;

    console.log(`\n✓ Board scraping complete: ${result.boardPins.length} pins found`);

    // Step 2: Scrape "More ideas"
    console.log('\n' + '='.repeat(80));
    console.log('STEP 2: Scraping "More ideas" recommendations');
    console.log('='.repeat(80));

    result.moreIdeasPins = await scraper.scrapeMoreIdeas(BOARD_URL, 500);
    result.stats.moreIdeasCount = result.moreIdeasPins.length;

    console.log(`\n✓ "More ideas" scraping complete: ${result.moreIdeasPins.length} pins found`);

    // Combine all pins
    const allPins = [...result.boardPins, ...result.moreIdeasPins];
    result.stats.totalPinsScraped = allPins.length;

    console.log('\n' + '='.repeat(80));
    console.log(`TOTAL PINS SCRAPED: ${allPins.length}`);
    console.log('='.repeat(80));

    // Step 3: Download images
    console.log('\n' + '='.repeat(80));
    console.log('STEP 3: Downloading images');
    console.log('='.repeat(80));

    const rawOutputDir = path.join(OUTPUT_DIR, 'raw');
    let downloadedCount = 0;
    let failedCount = 0;

    for (let i = 0; i < allPins.length; i++) {
      const pin = allPins[i];
      console.log(`\n[${i + 1}/${allPins.length}] Downloading: ${pin.title.substring(0, 60)}...`);

      const localPath = await scraper.downloadImage(pin.imageUrl, rawOutputDir);

      if (localPath) {
        result.downloadedImages.push({
          pinId: pin.id,
          localPath,
          imageUrl: pin.imageUrl,
          title: pin.title,
        });
        downloadedCount++;
      } else {
        failedCount++;
      }

      // Rate limiting - be gentle with Pinterest
      if (i % 10 === 0 && i > 0) {
        console.log('\n⏸️  Pausing for rate limiting (5 seconds)...');
        await new Promise(resolve => setTimeout(resolve, 5000));
      } else {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    result.stats.totalImagesDownloaded = downloadedCount;
    result.stats.failedDownloads = failedCount;

    // Step 4: Save metadata
    console.log('\n' + '='.repeat(80));
    console.log('STEP 4: Saving metadata');
    console.log('='.repeat(80));

    const metadataDir = path.dirname(METADATA_FILE);
    if (!fs.existsSync(metadataDir)) {
      fs.mkdirSync(metadataDir, { recursive: true });
    }

    const metadata = {
      scrapedAt: new Date().toISOString(),
      boardUrl: BOARD_URL,
      pins: allPins,
      downloads: result.downloadedImages,
      stats: result.stats,
    };

    fs.writeFileSync(METADATA_FILE, JSON.stringify(metadata, null, 2));
    console.log(`✓ Metadata saved to: ${METADATA_FILE}`);

    // Step 5: Print summary
    const duration = Math.round((Date.now() - startTime) / 1000);

    console.log('\n' + '='.repeat(80));
    console.log('SCRAPING COMPLETE!');
    console.log('='.repeat(80));
    console.log(`
📊 SUMMARY:
───────────────────────────────────────────────────────────────────────────────
Board pins:              ${result.stats.boardPinsCount}
"More ideas" pins:       ${result.stats.moreIdeasCount}
Total pins scraped:      ${result.stats.totalPinsScraped}
───────────────────────────────────────────────────────────────────────────────
Images downloaded:       ${result.stats.totalImagesDownloaded}
Failed downloads:        ${result.stats.failedDownloads}
Success rate:            ${Math.round((result.stats.totalImagesDownloaded / result.stats.totalPinsScraped) * 100)}%
───────────────────────────────────────────────────────────────────────────────
Output directory:        ${rawOutputDir}
Metadata file:           ${METADATA_FILE}
Duration:                ${duration} seconds
───────────────────────────────────────────────────────────────────────────────

✅ Next steps:
   1. Run industry classification: npm run classify-pinterest
   2. Identify gaps in industries
   3. Fill gaps with targeted searches
   4. Train LoRAs per industry
`);

    await scraper.close();

    return result;
  } catch (error: any) {
    console.error('\n❌ SCRAPING FAILED:', error.message);
    console.error(error.stack);
    await scraper.close();
    process.exit(1);
  }
}

// Run the scraper
scrapeAtScale()
  .then(() => {
    console.log('\n✅ Script completed successfully');
    process.exit(0);
  })
  .catch((error) => {
    console.error('\n❌ Script failed:', error);
    process.exit(1);
  });
