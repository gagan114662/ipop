// Manual login script - opens browser for you to login manually, then saves cookies
import { chromium } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';

const COOKIES_FILE = './config/pinterest-cookies.json';

async function manualLogin() {
  console.log('='.repeat(80));
  console.log('PINTEREST MANUAL LOGIN');
  console.log('='.repeat(80));
  console.log('\nThis script will:');
  console.log('1. Open a browser window');
  console.log('2. Navigate to Pinterest');
  console.log('3. Wait for YOU to manually login (use Google or any method)');
  console.log('4. Save your cookies for future automated scraping');
  console.log('\nPress Ctrl+C to cancel, or press Enter to continue...\n');

  // Wait for user confirmation
  await new Promise(resolve => {
    process.stdin.once('data', resolve);
  });

  const browser = await chromium.launch({
    headless: false,
    args: [
      '--disable-blink-features=AutomationControlled',
      '--no-sandbox',
      '--disable-setuid-sandbox',
    ],
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  });

  const page = await context.newPage();

  console.log('\n✓ Browser launched');
  console.log('✓ Navigating to Pinterest...\n');

  await page.goto('https://www.pinterest.com/login/');
  await page.waitForTimeout(2000);

  console.log('='.repeat(80));
  console.log('MANUAL LOGIN REQUIRED');
  console.log('='.repeat(80));
  console.log('\nPlease complete the following steps in the browser window:');
  console.log('1. Click "Continue with Google" (or use email/password)');
  console.log('2. Complete the login process');
  console.log('3. Wait until you see your Pinterest feed/homepage');
  console.log('4. Come back here and press Enter\n');
  console.log('Waiting for you to login...\n');

  // Wait for user to press Enter after logging in
  await new Promise(resolve => {
    process.stdin.once('data', resolve);
  });

  console.log('\n✓ Checking if login was successful...');

  const currentUrl = page.url();
  console.log(`Current URL: ${currentUrl}`);

  if (currentUrl.includes('/login') || currentUrl.includes('/auth')) {
    console.error('\n❌ Still on login page. Please try again and make sure you\'re logged in.');
    await browser.close();
    process.exit(1);
  }

  console.log('✓ Login detected!');
  console.log('✓ Saving cookies...');

  // Save cookies
  const cookies = await context.cookies();
  const cookieDir = path.dirname(COOKIES_FILE);

  if (!fs.existsSync(cookieDir)) {
    fs.mkdirSync(cookieDir, { recursive: true });
  }

  fs.writeFileSync(COOKIES_FILE, JSON.stringify(cookies, null, 2));

  console.log(`\n✅ SUCCESS! Cookies saved to: ${COOKIES_FILE}`);
  console.log(`\nYou can now run the scraper and it will use these cookies:`);
  console.log(`  npm run scrape-pinterest\n`);

  await browser.close();
  process.exit(0);
}

manualLogin().catch(error => {
  console.error('\n❌ Error:', error.message);
  process.exit(1);
});
