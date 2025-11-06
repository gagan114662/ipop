// Script to scrape a Pinterest board + "More ideas" section
import { PinterestScraper } from '../services/pinterest-scraper';
import * as fs from 'fs';
import * as path from 'path';

const BOARD_URL = process.env.BOARD_URL || '';
const OUTPUT_DIR = './reference-cache/images/pinterest/boards';
const MAX_BOARD_PINS = 300;
const MAX_IDEAS_PINS = 500;

async function scrapeBoardWithIdeas() {
  console.log('='.repeat(80));
  console.log('PINTEREST BOARD + MORE IDEAS SCRAPER');
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

    // STEP 1: Scrape main board
    console.log('\n' + '='.repeat(80));
    console.log('STEP 1: Scraping main board');
    console.log('='.repeat(80));

    const boardPins = await scraper.scrapeBoard(BOARD_URL, MAX_BOARD_PINS);
    console.log(`\n✓ Board scraping complete: ${boardPins.length} pins found`);

    // STEP 2: Scrape "More ideas"
    console.log('\n' + '='.repeat(80));
    console.log('STEP 2: Scraping "More ideas" recommendations');
    console.log('='.repeat(80));

    const moreIdeasPins = await scraper.scrapeMoreIdeas(BOARD_URL, MAX_IDEAS_PINS);
    console.log(`\n✓ "More ideas" scraping complete: ${moreIdeasPins.length} pins found`);

    // Combine all pins
    const allPins = [...boardPins, ...moreIdeasPins];
    console.log(`\n✅ TOTAL PINS SCRAPED: ${allPins.length}`);

    // Determine board name
    const boardName = boardPins[0]?.boardName || BOARD_URL.split('/').filter(s => s).pop() || 'unknown';
    const sanitizedName = boardName.replace(/[^a-z0-9]/gi, '-').toLowerCase();
    const boardDir = path.join(OUTPUT_DIR, `${sanitizedName}-with-ideas`);

    // STEP 3: Download all images
    console.log('\n' + '='.repeat(80));
    console.log('STEP 3: Downloading images');
    console.log('='.repeat(80));
    console.log(`Output directory: ${boardDir}\n`);

    let downloadedCount = 0;
    let failedCount = 0;

    for (let i = 0; i < allPins.length; i++) {
      const pin = allPins[i];
      const source = i < boardPins.length ? 'board' : 'ideas';
      console.log(`\n[${i + 1}/${allPins.length}] [${source}] ${pin.title.substring(0, 60)}...`);

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
      boardPins: boardPins.length,
      moreIdeasPins: moreIdeasPins.length,
      totalPins: allPins.length,
      downloadedImages: downloadedCount,
      failedDownloads: failedCount,
      pins: allPins,
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
Board pins:              ${boardPins.length}
"More ideas" pins:       ${moreIdeasPins.length}
Total pins:              ${allPins.length}
───────────────────────────────────────────────────────────────────────────────
Images downloaded:       ${downloadedCount}
Failed downloads:        ${failedCount}
Success rate:            ${Math.round((downloadedCount / allPins.length) * 100)}%
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

scrapeBoardWithIdeas();
