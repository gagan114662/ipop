import axios from 'axios';
import * as cheerio from 'cheerio';
import https from 'https';
import { HttpsProxyAgent } from 'https-proxy-agent';

export interface ProductSKU {
  sku: string;
  name: string;
  price?: string;
  description?: string;
  imageUrl?: string;
  category?: string;
  url: string;
}

export interface BrandVisualData {
  colors: string[];
  logoUrl?: string;
  typography: string[];
  imageUrls: string[];
  rawHtml: string;
}

const RETRYABLE_CODES = ['ECONNRESET', 'ETIMEDOUT', 'EAI_AGAIN', 'ECONNABORTED'];
const DEFAULT_HEADERS = {
  'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
  Accept:
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'Accept-Language': 'en-US,en;q=0.9',
};
const PLAYWRIGHT_DISABLED = process.env.SCRAPER_DISABLE_PLAYWRIGHT === 'true';
const PLAYWRIGHT_HEADLESS = process.env.SCRAPER_HEADLESS !== 'false';

const proxySet = new Set<string>();
const proxyPoolEnv = process.env.SCRAPER_PROXY_POOL || process.env.SCRAPER_PROXY_URLS;
const explicitProxy =
  process.env.SCRAPER_PROXY_URL || process.env.HTTPS_PROXY || process.env.HTTP_PROXY;

if (proxyPoolEnv) {
  proxyPoolEnv
    .split(',')
    .map((entry) => entry.trim())
    .filter(Boolean)
    .forEach((entry) => proxySet.add(entry));
}
if (explicitProxy) {
  proxySet.add(explicitProxy.trim());
}

const proxyPool = Array.from(proxySet);
let proxyCursor = 0;
const proxyAgentCache = new Map<string, { httpAgent: any; httpsAgent: any }>();
const defaultAgents = {
  httpAgent: undefined as any,
  httpsAgent: new https.Agent({ keepAlive: true }),
};

let playwrightReady = false;
let chromiumModule: any;
const browserPool = new Map<string, Promise<any>>();
let cleanupRegistered = false;

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function buildJinaUrl(url: string) {
  if (url.startsWith('https://')) {
    return `https://r.jina.ai/https://${url.slice('https://'.length)}`;
  }
  if (url.startsWith('http://')) {
    return `https://r.jina.ai/http://${url.slice('http://'.length)}`;
  }
  return `https://r.jina.ai/https://${url}`;
}

interface PageSnapshot {
  html: string;
  jsonBlobs: string[];
}

function nextProxySequence(): (string | null)[] {
  if (proxyPool.length === 0) {
    return [null];
  }

  const start = proxyCursor % proxyPool.length;
  proxyCursor = (proxyCursor + 1) % proxyPool.length;
  const ordered = proxyPool.slice(start).concat(proxyPool.slice(0, start));

  const candidates: (string | null)[] = [...ordered];
  if (!candidates.includes(null)) {
    candidates.push(null);
  }

  return candidates;
}

function getAgentsForProxy(proxy: string | null) {
  if (!proxy) {
    return defaultAgents;
  }

  const key = proxy as string;

  if (!proxyAgentCache.has(key)) {
    const agent: any = new HttpsProxyAgent(key);
    proxyAgentCache.set(key, { httpAgent: agent, httpsAgent: agent });
  }

  return proxyAgentCache.get(key)!;
}

async function ensurePlaywright(): Promise<boolean> {
  if (PLAYWRIGHT_DISABLED) {
    return false;
  }

  if (playwrightReady) {
    return true;
  }

  try {
    const playwright = await import('playwright');
    chromiumModule = playwright.chromium;
    playwrightReady = true;
    return true;
  } catch (error: any) {
    console.warn(
      `Playwright not available, dynamic rendering disabled: ${error?.message || error}`
    );
    return false;
  }
}

async function getPlaywrightBrowser(proxy: string | null) {
  if (!(await ensurePlaywright())) {
    return null;
  }

  const key = proxy ?? 'no-proxy';

  if (!browserPool.has(key)) {
    const launchOptions: Record<string, unknown> = {
      headless: PLAYWRIGHT_HEADLESS,
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
    };

    if (proxy) {
      launchOptions.proxy = { server: proxy };
    }

    browserPool.set(key, chromiumModule.launch(launchOptions));

    if (!cleanupRegistered) {
      process.once('exit', async () => {
        await Promise.all(
          Array.from(browserPool.values()).map(async (browserPromise) => {
            try {
              const browser = await browserPromise;
              await browser.close();
            } catch {
              // ignore shutdown errors
            }
          })
        );
      });
      cleanupRegistered = true;
    }
  }

  return browserPool.get(key)!;
}

function extractJsonBlobsFromHtml(html: string): string[] {
  try {
    const blobs: string[] = [];
    const $ = cheerio.load(html);
    const selectors = [
      'script[type="application/ld+json"]',
      'script[type="application/json"]',
      'script[id="__NEXT_DATA__"]',
      'script[id="__NUXT_DATA__"]',
      'script[id="__NUXT__"]',
      'script[data-state]',
    ];
    $(selectors.join(',')).each((_, elem) => {
      const raw = $(elem).contents().text().trim();
      if (!raw) return;
      const startsWithBracket = raw.startsWith('{') || raw.startsWith('[');
      if (!startsWithBracket) return;
      blobs.push(raw);
    });
    return blobs;
  } catch {
    return [];
  }
}

async function fetchHtmlWithPlaywright(
  url: string,
  proxy: string | null
): Promise<PageSnapshot | null> {
  try {
    const browser = await getPlaywrightBrowser(proxy);
    if (!browser) {
      return null;
    }

    const context = await browser.newContext({
      userAgent: DEFAULT_HEADERS['User-Agent'],
      viewport: { width: 1280, height: 720 },
    });

    await context.route('**/*', (route: any) => {
      const type = route.request().resourceType();
      if (['stylesheet', 'image', 'media', 'font'].includes(type)) {
        return route.abort();
      }
      return route.continue();
    });

    const page = await context.newPage();
    const networkJsonBlobs: string[] = [];
    page.on('response', async (response: any) => {
      try {
        const headers = response.headers();
        const contentType = headers['content-type'] || headers['Content-Type'] || '';
        if (!contentType.includes('application/json')) return;
        const urlLower = response.url().toLowerCase();
        if (urlLower.includes('analytics') || urlLower.includes('adobedtm')) return;
        const body = await response.text();
        if (!body) return;
        if (body.length > 2_000_000) return;
        networkJsonBlobs.push(body);
      } catch {
        // ignore network response parsing errors
      }
    });

    await page.goto(url, { waitUntil: 'networkidle', timeout: 40000 });
    await page.waitForTimeout(1500);
    const [content, jsonBlobs] = await Promise.all([
      page.content(),
      page
        .evaluate(() => {
          const collected: string[] = [];
          const globalCandidates = [
            '__NEXT_DATA__',
            '__NUXT__',
            '__NUXT_DATA__',
            '__APOLLO_STATE__',
            '__INITIAL_STATE__',
            '__PRELOADED_STATE__',
            '__STATE__',
          ];
          for (const key of globalCandidates) {
            const value = (window as any)[key];
            if (value) {
              try {
                collected.push(JSON.stringify(value));
              } catch {
                // ignore serialisation issues
              }
            }
          }
          const scriptSelectors = [
            'script[type=\"application/json\"]',
            'script[type=\"application/ld+json\"]',
            'script[id=\"__NEXT_DATA__\"]',
            'script[id=\"__NUXT_DATA__\"]',
          ];
          document.querySelectorAll(scriptSelectors.join(',')).forEach((script) => {
            const text = script.textContent;
            if (!text) return;
            const trimmed = text.trim();
            if (!trimmed) return;
            if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
              collected.push(trimmed);
            }
          });
          return collected;
        })
        .catch(() => [] as string[]),
    ]);
    await context.close();
    return { html: content, jsonBlobs: [...jsonBlobs, ...networkJsonBlobs] };
  } catch (error: any) {
    console.warn(
      `Playwright failed to fetch ${url} ${proxy ? `via proxy ${proxy}` : ''}: ${
        error?.message || error
      }`
    );
    return null;
  }
}

async function fetchHtml(
  url: string,
  attempt: number,
  proxy: string | null
): Promise<string> {
  const agents = getAgentsForProxy(proxy);

  try {
    const response = await axios.get(url, {
      headers: DEFAULT_HEADERS,
      timeout: 22000,
      maxRedirects: 5,
      httpsAgent: agents.httpsAgent,
      httpAgent: agents.httpAgent,
    });
    return typeof response.data === 'string' ? response.data : JSON.stringify(response.data);
  } catch (error: any) {
    const shouldRetry =
      attempt < 3 &&
      (RETRYABLE_CODES.includes(error.code) ||
        (error.response?.status && error.response.status >= 500));

    if (shouldRetry) {
      await delay(1500 * attempt);
      return fetchHtml(url, attempt + 1, proxy);
    }

    if (!url.includes('r.jina.ai/')) {
      return fetchHtml(buildJinaUrl(url), 1, proxy);
    }

    throw new Error(`Failed to fetch ${url}: ${error.message}`);
  }
}

async function getPageSnapshot(url: string): Promise<PageSnapshot> {
  const proxyCandidates = nextProxySequence();
  let lastError: Error | null = null;

  for (const proxy of proxyCandidates) {
    try {
      const html = await fetchHtml(url, 1, proxy);
      return { html, jsonBlobs: extractJsonBlobsFromHtml(html) };
    } catch (error: any) {
      lastError = error;
      const rendered = await fetchHtmlWithPlaywright(url, proxy);
      if (rendered) {
        return {
          html: rendered.html,
          jsonBlobs: [
            ...rendered.jsonBlobs,
            ...extractJsonBlobsFromHtml(rendered.html),
          ],
        };
      }
    }
  }

  if (!url.includes('r.jina.ai/')) {
    try {
      const html = await fetchHtml(buildJinaUrl(url), 1, null);
      return { html, jsonBlobs: extractJsonBlobsFromHtml(html) };
    } catch (error: any) {
      lastError = lastError ?? error;
    }
  }

  if (lastError) {
    throw lastError;
  }

  throw new Error(`Failed to fetch ${url}: no successful transport`);
}

async function getPageHtml(url: string): Promise<string> {
  const snapshot = await getPageSnapshot(url);
  return snapshot.html;
}

function normaliseData(data: any): ProductSKU[] {
  const collected: ProductSKU[] = [];
  if (!data) return collected;

  const visit = (node: any) => {
    if (!node || typeof node !== 'object') return;

    if (Array.isArray(node)) {
      node.forEach(visit);
      return;
    }

    const type = node['@type'] || node.type;
    const isProduct =
      type === 'Product' ||
      node.productId ||
      node.sku ||
      node.styleCode ||
      node.styleId ||
      node.cloudProductId ||
      node.prodigyId ||
      node.pid ||
      node.partNumber ||
      node.productName ||
      node.product ||
      node.productInfo;

    if (isProduct) {
      const rawSku =
        node.sku ||
        node.productId ||
        node.styleCode ||
        node.styleId ||
        node.cloudProductId ||
        node.prodigyId ||
        node.partNumber ||
        node.part_numbers ||
        node.product?.partNumber ||
        node.product?.id ||
        node.id ||
        node.url ||
        node.href ||
        node.pid ||
        `AUTO_${collected.length + 1}`;

        const rawName =
          node.name ||
          node.title ||
          node.displayName ||
          node.productTitle ||
          node.productName ||
        node.headline ||
        '';

      if (rawSku && rawName) {
        const imageUrl =
          typeof node.image === 'string'
            ? node.image
            : Array.isArray(node.image)
            ? node.image[0]
            : node.imageUrl ||
              node.thumbnail ||
              node.previewImage ||
              node.images?.[0]?.url ||
              node.images?.[0]?.href ||
              node.pictures?.[0]?.url ||
              node.heroImage?.url ||
              node.productAssets?.images?.[0]?.url ||
              node.primaryImage?.url ||
              node.primaryImageUrl ||
              node.mainImage ||
              undefined;

        const priceValue =
          node.price ||
          node.priceText ||
          node.currentPrice ||
          node.price?.current ||
          node.price?.full ||
          node.price?.formattedCurrentPrice ||
          node.priceFormatted ||
          node.lowestPrice ||
          node.unitPrice ||
          node.product?.price ||
          node.productPrice?.priceData?.fullPrice?.raw?.price ||
          node.productPrice?.priceData?.fullPrice?.price ||
          node.productPrice?.priceData?.fullPrice?.amount ||
          node.productPrice?.fullPrice ||
          node.productPrice?.currentPrice;

        const productUrl =
          node.url ||
          node.pdpUrl ||
          node.href ||
          node.link ||
          node.seoUrl ||
          node.productDetailsUrl ||
          node.shopCtaUrl ||
          node.directPurchaseLink ||
          (node.titleLink && node.titleLink.href) ||
          '';

        collected.push({
          sku: String(rawSku),
          name: String(rawName),
          price: priceValue ? String(priceValue) : undefined,
          description: node.description || node.subtitle || node.productDescription,
          imageUrl,
          category: node.category || node.productCategory || node.type,
          url: productUrl,
        });
      }
    }

    Object.values(node).forEach(visit);
  };

  visit(data);
  return collected;
}

function extractStructuredProducts($: cheerio.CheerioAPI): ProductSKU[] {
  const aggregated: ProductSKU[] = [];

  $('script[type="application/ld+json"]').each((_, elem) => {
    const content = $(elem).contents().text().trim();
    if (!content) return;
    try {
      aggregated.push(...normaliseData(JSON.parse(content)));
    } catch {
      // ignored
    }
  });

  const nextDataScript = $('#__NEXT_DATA__').first().text();
  if (nextDataScript) {
    try {
      aggregated.push(...normaliseData(JSON.parse(nextDataScript)));
    } catch {
      // ignored
    }
  }

  $('script').each((_, elem) => {
    const text = $(elem).html();
    if (!text || text.length > 500000) return;
    if (!text.includes('sku') && !text.includes('product')) return;
    const match = text.trim().startsWith('{') || text.trim().startsWith('[');
    if (!match) return;
    try {
      aggregated.push(...normaliseData(JSON.parse(text)));
    } catch {
      // ignore script blobs that aren't pure JSON
    }
  });

  return aggregated;
}

interface VisualAccumulator {
  colors: Set<string>;
  typography: Set<string>;
  imageUrls: Set<string>;
  logoUrl?: string;
}

function harvestVisualSignals(
  $: cheerio.CheerioAPI,
  pageUrl: string,
  accumulator: VisualAccumulator
) {
  $('style, [style]').each((_, elem) => {
    const text = $(elem).text() || $(elem).attr('style') || '';
    const colorMatches = text.match(/#[0-9A-Fa-f]{3,6}|rgb\([^)]+\)|rgba\([^)]+\)/g);
    if (colorMatches) {
      colorMatches.forEach((color) => accumulator.colors.add(color));
    }
  });

  $('style, link[rel="stylesheet"]').each((_, elem) => {
    const text = $(elem).text() || '';
    const fontMatches = text.match(/font-family:\s*([^;}\n]+)/gi);
    if (fontMatches) {
      fontMatches.forEach((match) => {
        const font = match.replace(/font-family:\s*/i, '').trim();
        if (font) {
          accumulator.typography.add(font);
        }
      });
    }
  });

  $('img').each((_, elem) => {
    const src = $(elem).attr('src');
    if (src) {
      try {
        const fullUrl = new URL(src, pageUrl).href;
        accumulator.imageUrls.add(fullUrl);
      } catch {
        // ignore malformed image URLs
      }
    }
  });

  if (!accumulator.logoUrl) {
    const logoCandidate = $('img[class*="logo"], img[id*="logo"], .logo img, #logo img')
      .first()
      .attr('src');
    if (logoCandidate) {
      try {
        accumulator.logoUrl = new URL(logoCandidate, pageUrl).href;
      } catch {
        // ignore malformed logo URLs
      }
    }
  }
}

function collectProductsFromDom($: cheerio.CheerioAPI, baseUrl: string): ProductSKU[] {
  const collected: ProductSKU[] = [];

  collected.push(...extractStructuredProducts($));

  const productSelectors = [
    '.product',
    '.product-item',
    '[data-product]',
    '.woocommerce-LoopProduct-link',
    '.product-card',
    '.item',
    '[itemtype*="Product"]',
    '.shop-item',
  ];

  for (const selector of productSelectors) {
    $(selector).each((_, elem) => {
      const $elem = $(elem);

      const sku =
        $elem.attr('data-sku') ||
        $elem.find('[data-sku]').attr('data-sku') ||
        $elem.find('.sku').text() ||
        $elem.attr('data-product-id') ||
        '';

      const name =
        $elem.find('.product-title, .product-name, h2, h3, .title').first().text().trim() ||
        $elem.attr('title') ||
        '';

      if (!sku && !name) {
        return;
      }

      const price = $elem.find('.price, .product-price, [class*="price"]').first().text().trim();
      const description = $elem.find('.description, .product-description, p').first().text().trim();

      const imgSrc = $elem.find('img').first().attr('src');
      let imageUrl: string | undefined;
      if (imgSrc) {
        try {
          imageUrl = new URL(imgSrc, baseUrl).href;
        } catch {
          imageUrl = undefined;
        }
      }

      const category =
        $elem.attr('data-category') ||
        $elem.find('[data-category]').attr('data-category') ||
        '';

      const productUrl =
        $elem.find('a').first().attr('href') ||
        $elem.attr('href') ||
        '';

      let fullProductUrl = baseUrl;
      if (productUrl) {
        try {
          fullProductUrl = new URL(productUrl, baseUrl).href;
        } catch {
          fullProductUrl = baseUrl;
        }
      }

      collected.push({
        sku: sku || `AUTO_${collected.length + 1}`,
        name,
        price,
        description,
        imageUrl,
        category,
        url: fullProductUrl,
      });
    });

    if (collected.length > 0) break;
  }

  if (collected.length === 0) {
    $('a').each((_, elem) => {
      const href = $(elem).attr('href');
      const text = $(elem).text().trim();
      if (
        href &&
        text &&
        (href.includes('/product') || href.includes('/shop') || href.includes('/item'))
      ) {
        try {
          const fullUrl = new URL(href, baseUrl).href;
          collected.push({
            sku: `AUTO_${collected.length + 1}`,
            name: text,
            url: fullUrl,
          });
        } catch {
          // ignore malformed URLs
        }
      }
    });
  }

  return collected;
}

function collectProductsFromJsonBlobs(blobs: string[]): ProductSKU[] {
  const aggregated: ProductSKU[] = [];
  for (const blob of blobs) {
    try {
      const parsed = JSON.parse(blob);
      aggregated.push(...normaliseData(parsed));
    } catch (error: any) {
      console.warn(
        `Failed to parse JSON blob for structured product extraction: ${error?.message || error}`
      );
    }
  }
  return aggregated;
}

export async function scrapeWebsite(url: string): Promise<{
  products: ProductSKU[];
  visualData: BrandVisualData;
  rawContent: string;
}> {
  async function resolvePrimaryImage(productUrl: string): Promise<string | undefined> {
    try {
      const snapshot = await getPageSnapshot(productUrl);
      const productPage = cheerio.load(snapshot.html);
      const ogImage = productPage('meta[property="og:image"]').attr('content');
      if (ogImage) {
        const resolved = new URL(ogImage, productUrl).href;
        return resolved.replace(/^http:/, 'https:');
      }

      const firstImage = productPage('img').first().attr('src');
      if (firstImage) {
        const resolved = new URL(firstImage, productUrl).href;
        return resolved.replace(/^http:/, 'https:');
      }
    } catch (detailError: any) {
      console.warn(`Failed to resolve product image for ${productUrl}: ${detailError.message}`);
    }

    return undefined;
  }

  try {
    const visualAccumulator: VisualAccumulator = {
      colors: new Set<string>(),
      typography: new Set<string>(),
      imageUrls: new Set<string>(),
      logoUrl: undefined,
    };

    let snapshot = await getPageSnapshot(url);
    let html = snapshot.html;
    let $ = cheerio.load(html);

    harvestVisualSignals($, url, visualAccumulator);

    const products: ProductSKU[] = [];
    products.push(...collectProductsFromDom($, url));
    const jsonProducts = collectProductsFromJsonBlobs(snapshot.jsonBlobs);
    products.push(...jsonProducts);

    if (products.length < 6) {
      const renderedSnapshot = await fetchHtmlWithPlaywright(url, null);
      if (renderedSnapshot) {
        html = renderedSnapshot.html;
        snapshot = {
          html,
          jsonBlobs: [
            ...renderedSnapshot.jsonBlobs,
            ...extractJsonBlobsFromHtml(renderedSnapshot.html),
          ],
        };
        $ = cheerio.load(html);
        harvestVisualSignals($, url, visualAccumulator);
        products.push(...collectProductsFromDom($, url));
        products.push(...collectProductsFromJsonBlobs(snapshot.jsonBlobs));
      }
    }

    if (products.length < 10) {
      const categoryLinks = new Set<string>();
      $('a[href]').each((_, elem) => {
        const href = $(elem).attr('href');
        if (!href) return;
        if (href.startsWith('#') || href.startsWith('javascript')) return;
        if (
          !href.includes('/product') &&
          !href.includes('/shop') &&
          !href.includes('/w/') &&
          !href.includes('/t/')
        )
          return;
        try {
          const fullUrl = new URL(href, url).href;
          if (!fullUrl.startsWith('http')) return;
          categoryLinks.add(fullUrl);
        } catch {
          // ignore malformed URLs
        }
      });

      const extraLinks = Array.from(categoryLinks).slice(0, 4);
      for (const link of extraLinks) {
        try {
          const subSnapshot = await getPageSnapshot(link);
          const sub$ = cheerio.load(subSnapshot.html);
          harvestVisualSignals(sub$, link, visualAccumulator);
          products.push(...collectProductsFromDom(sub$, link));
          products.push(...collectProductsFromJsonBlobs(subSnapshot.jsonBlobs));
        } catch (err: any) {
          console.warn(`Failed to enrich products from ${link}: ${err.message}`);
        }
      }
    }

    const rawContent = $('body').text().slice(0, 10000);

    const dedupedProductsMap = new Map<string, ProductSKU>();
    for (const product of products) {
      const key = (product.url || product.sku).toLowerCase();
      if (!dedupedProductsMap.has(key) && product.name) {
        dedupedProductsMap.set(key, product);
      }
    }

    let uniqueProducts = Array.from(dedupedProductsMap.values());
    const hasStructuredProducts = uniqueProducts.some((product) => !product.sku.startsWith('AUTO_'));
    if (hasStructuredProducts) {
      uniqueProducts = uniqueProducts.filter((product) => !product.sku.startsWith('AUTO_'));
    }

    const imageFetchLimit = 25;
    const productsNeedingImages = uniqueProducts
      .filter((product) => !product.imageUrl && product.url)
      .slice(0, imageFetchLimit);

    await Promise.all(
      productsNeedingImages.map(async (product) => {
        try {
          product.imageUrl = await resolvePrimaryImage(product.url!);
        } catch (error: any) {
          console.warn(`Failed to resolve image for ${product.url}: ${error?.message || error}`);
        }
      })
    );

    return {
      products: uniqueProducts,
      visualData: {
        colors: Array.from(visualAccumulator.colors).slice(0, 20),
        logoUrl: visualAccumulator.logoUrl,
        typography: Array.from(visualAccumulator.typography).slice(0, 10),
        imageUrls: Array.from(visualAccumulator.imageUrls).slice(0, 50),
        rawHtml: html.slice(0, 20000),
      },
      rawContent,
    };
  } catch (error: any) {
    throw new Error(`Failed to scrape website: ${error.message}`);
  }
}
