// Script to scrape a single Pinterest board
import { PinterestScraper } from '../services/pinterest-scraper';
import * as fs from 'fs';
import * as path from 'path';

const BOARD_URL = process.env.BOARD_URL || 'https://ca.pinterest.com/sangichandresh/vama/';
const OUTPUT_DIR = './reference-cache/images/pinterest/boards';
const MAX_PINS = 300;

async function scrapeSingleBoard() {
  console.log('='.repeat(80));
  console.log('PINTEREST SINGLE BOARD SCRAPER');
  console.log('='.repeat(80));
  console.log(`Board: ${BOARD_URL}\n`);

  const scraper = new PinterestScraper({
    email: process.env.PINTEREST_EMAIL || 'gagan@getfoolish.com',
    password: process.env.PINTEREST_PASSWORD || 'vandanchopra@114',
    headless: process.env.PINTEREST_HEADLESS !== 'false',
    cookiesFile: './config/pinterest-cookies.json',
  });

  try {
    await scraper.launch();

    // Scrape board
    console.log('\nScraping board...');
    const pins = await scraper.scrapeBoard(BOARD_URL, MAX_PINS);

    console.log(`\n✓ Scraped ${pins.length} pins`);

    // Determine board name from URL or pins
    const boardName = pins[0]?.boardName || BOARD_URL.split('/').filter(s => s).pop() || 'unknown';
    const sanitizedName = boardName.replace(/[^a-z0-9]/gi, '-').toLowerCase();
    const boardDir = path.join(OUTPUT_DIR, sanitizedName);

    // Download images
    console.log(`\nDownloading images to: ${boardDir}`);

    let downloadedCount = 0;
    let failedCount = 0;

    for (let i = 0; i < pins.length; i++) {
      const pin = pins[i];
      console.log(`\n[${i + 1}/${pins.length}] ${pin.title.substring(0, 60)}...`);

      const localPath = await scraper.downloadImage(pin.imageUrl, boardDir);

      if (localPath) {
        downloadedCount++;
      } else {
        failedCount++;
      }

      // Rate limiting
      if (i % 10 === 0 && i > 0) {
        console.log('\n⏸️  Pausing for rate limiting (5 seconds)...');
        await new Promise(resolve => setTimeout(resolve, 5000));
      } else {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    // Save metadata
    const metadata = {
      scrapedAt: new Date().toISOString(),
      boardUrl: BOARD_URL,
      boardName,
      totalPins: pins.length,
      downloadedImages: downloadedCount,
      failedDownloads: failedCount,
      pins,
    };

    const metadataFile = path.join(boardDir, 'metadata.json');
    fs.writeFileSync(metadataFile, JSON.stringify(metadata, null, 2));

    console.log('\n' + '='.repeat(80));
    console.log('SCRAPING COMPLETE!');
    console.log('='.repeat(80));
    console.log(`
📊 SUMMARY:
───────────────────────────────────────────────────────────────────────────────
Board:                   ${boardName}
Total pins:              ${pins.length}
Images downloaded:       ${downloadedCount}
Failed downloads:        ${failedCount}
Success rate:            ${Math.round((downloadedCount / pins.length) * 100)}%
───────────────────────────────────────────────────────────────────────────────
Output directory:        ${boardDir}
Metadata file:           ${metadataFile}
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

scrapeSingleBoard();
