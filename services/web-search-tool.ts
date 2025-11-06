import axios from 'axios';
import * as cheerio from 'cheerio';

export interface SearchResult {
  title: string;
  url: string;
  snippet: string;
  imageUrl?: string;
}

export interface ImageSearchResult {
  title: string;
  imageUrl: string;
  sourceUrl: string;
  thumbnail?: string;
}

/**
 * Performs web search using DuckDuckGo HTML scraping (no API key required)
 * This is a systemic solution that works for any search query
 */
export async function webSearch(query: string, maxResults: number = 10): Promise<SearchResult[]> {
  try {
    // Use DuckDuckGo HTML (doesn't require API key, respects robots.txt)
    const searchUrl = `https://html.duckduckgo.com/html/?q=${encodeURIComponent(query)}`;

    const response = await axios.get(searchUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      },
      timeout: 10000,
    });

    const $ = cheerio.load(response.data);
    const results: SearchResult[] = [];

    $('.result').each((i, elem) => {
      if (results.length >= maxResults) return false;

      const $elem = $(elem);
      const $link = $elem.find('.result__a');
      const title = $link.text().trim();
      const url = $link.attr('href') || '';
      const snippet = $elem.find('.result__snippet').text().trim();

      // Try to extract image if available
      const $img = $elem.find('img');
      const imageUrl = $img.attr('src') || undefined;

      if (title && url) {
        // Clean up DuckDuckGo redirect URLs
        const cleanUrl = url.startsWith('//duckduckgo.com/l/?uddg=')
          ? decodeURIComponent(url.split('uddg=')[1]?.split('&')[0] || url)
          : url;

        results.push({
          title,
          url: cleanUrl,
          snippet,
          imageUrl,
        });
      }
    });

    return results;
  } catch (error: any) {
    console.error('Web search failed:', error.message);
    return [];
  }
}

/**
 * Searches specifically for award-winning advertising campaigns
 * Returns results from credible sources like Cannes Lions, D&AD, One Show, etc.
 */
export async function searchAwardWinningCampaigns(
  category: string,
  maxResults: number = 10
): Promise<SearchResult[]> {
  const queries = [
    `cannes lions ${category} advertising winners`,
    `D&AD ${category} advertising awards`,
    `one show ${category} creative awards`,
    `clio awards ${category} advertising`,
  ];

  const allResults: SearchResult[] = [];

  for (const query of queries) {
    const results = await webSearch(query, Math.ceil(maxResults / queries.length));
    allResults.push(...results);

    if (allResults.length >= maxResults) break;

    // Small delay to be respectful to the search engine
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }

  // Filter for credible award sources
  const credibleDomains = [
    'canneslions.com',
    'dandad.org',
    'oneshow.org',
    'clioawards.com',
    'adweek.com',
    'adsoftheworld.com',
    'thedrum.com',
    'lbbonline.com',
    'campaignlive.com',
  ];

  const filteredResults = allResults.filter((result) =>
    credibleDomains.some((domain) => result.url.includes(domain))
  );

  return filteredResults.length > 0 ? filteredResults.slice(0, maxResults) : allResults.slice(0, maxResults);
}

/**
 * Scrapes Ads of the World for actual award-winning campaign images using Playwright
 * This is a free public database with actual high-quality campaign visuals
 */
export async function scrapeAdsOfTheWorld(category: string, maxResults: number = 10): Promise<ImageSearchResult[]> {
  const usePlaywright = process.env.SCRAPER_DISABLE_PLAYWRIGHT !== 'true';

  if (!usePlaywright) {
    console.warn('Playwright disabled, skipping Ads of the World scraping');
    return [];
  }

  let browser;
  try {
    const { chromium } = await import('playwright');

    browser = await chromium.launch({
      headless: true,
      args: ['--disable-blink-features=AutomationControlled', '--no-sandbox'],
    });

    const context = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    });

    const page = await context.newPage();
    const searchUrl = `https://www.adsoftheworld.com/search?q=${encodeURIComponent(category)}`;

    console.info(`Scraping Ads of the World: ${searchUrl}`);
    await page.goto(searchUrl, { waitUntil: 'networkidle', timeout: 20000 });
    await page.waitForTimeout(2000);

    // Scroll to load more content
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(1500);

    // Extract campaign data
    const campaigns = await page.$$eval('article, .campaign-item, .post-item', (articles) => {
      return articles.slice(0, 20).map((article) => {
        // Find image
        const img = article.querySelector('img');
        let imageUrl = img?.src || img?.getAttribute('data-src') || '';

        // Clean up thumbnail URLs
        imageUrl = imageUrl.replace(/\/thumbnail\//, '/').replace(/\?w=\d+/, '');

        // Find link
        const link = article.querySelector('a');
        const href = link?.href || '';

        // Find title
        const title = article.querySelector('h2, h3, .title')?.textContent?.trim() ||
                     link?.getAttribute('title') ||
                     'Award-Winning Campaign';

        return { imageUrl, sourceUrl: href, title };
      }).filter(c => c.imageUrl && c.sourceUrl);
    });

    await browser.close();

    const results: ImageSearchResult[] = campaigns
      .filter(c => c.imageUrl.includes('http')) // Valid URLs only
      .slice(0, maxResults)
      .map(c => ({
        title: c.title,
        imageUrl: c.imageUrl,
        sourceUrl: c.sourceUrl,
      }));

    console.info(`Scraped ${results.length} campaign images from Ads of the World`);
    return results;
  } catch (error: any) {
    console.error('Failed to scrape Ads of the World:', error.message);
    if (browser) {
      await browser.close().catch(() => {});
    }
    return [];
  }
}

