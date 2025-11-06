// @ts-nocheck
import axios from 'axios';
import * as fs from 'fs';
import * as path from 'path';
import crypto from 'crypto';
import https from 'https';
import { HttpsProxyAgent } from 'https-proxy-agent';
import { openai, RESEARCH_MODEL } from './openai-client';
import { searchAwardWinningCampaigns, webSearch, scrapeAdsOfTheWorld } from './web-search-tool';
import { searchBehanceProjects } from './behance-scraper';

export interface ReferenceCitation {
  sourceName: string;
  sourceUrl: string;
  publishedAt?: string;
  awards?: string[];
  notes?: string;
}

export interface ReferenceSceneTemplate {
  id: string;
  imageUrl: string;
  localImagePath: string;
  headline?: string;
  description?: string;
  source: ReferenceCitation;
  promptSummary: string;
  sceneComposition: {
    camera: string;
    lighting: string;
    foreground: string;
    midground: string;
    background: string;
    props: string;
    postProcessing: string;
    emotion: string;
  };
}

export interface ReferenceHarvestRequest {
  category: string;
  targetAudience?: string;
  brandName?: string;
  focusRegion?: string;
  keywords?: string[];
}

interface RawReferenceAsset {
  title: string;
  url: string;
  imageUrl: string;
  source: string;
  publishedAt?: string;
  awards?: string[];
  blurb?: string;
}

const AWARD_SOURCES: Array<{ name: string; url: string; yearsBack: number }> = [
  { name: 'Behance', url: 'https://www.behance.net/galleries/advertising', yearsBack: 2 },
  { name: 'Dribbble', url: 'https://dribbble.com/tags/advertising', yearsBack: 2 },
  { name: 'Pinterest', url: 'https://www.pinterest.com/search/pins/?q=award%20winning%20advertising', yearsBack: 2 },
];

const MAGAZINE_SOURCES: Array<{ name: string; url: string; yearsBack: number }> = [
  { name: 'Behance Fashion', url: 'https://www.behance.net/galleries/fashion', yearsBack: 2 },
  { name: 'Dribbble Fashion', url: 'https://dribbble.com/tags/fashion', yearsBack: 2 },
  { name: 'Pinterest Fashion Ads', url: 'https://www.pinterest.com/search/pins/?q=fashion%20advertising%20campaign', yearsBack: 2 },
  { name: 'Unsplash Athletic', url: 'https://unsplash.com/s/photos/athletic-advertising', yearsBack: 2 },
];

const REFERENCE_CACHE_DIR =
  process.env.REFERENCE_CACHE_DIR || path.join(process.cwd(), 'reference-cache');
const REFERENCE_IMAGE_CACHE_DIR = path.join(REFERENCE_CACHE_DIR, 'images');
const REFERENCE_HTML_CACHE_DIR = path.join(REFERENCE_CACHE_DIR, 'html');

const referenceProxySet = new Set<string>();
const referenceProxyEnv = process.env.SCRAPER_PROXY_POOL || process.env.SCRAPER_PROXY_URLS;
const referenceExplicitProxy =
  process.env.SCRAPER_PROXY_URL || process.env.HTTPS_PROXY || process.env.HTTP_PROXY;

if (referenceProxyEnv) {
    referenceProxyEnv
      .split(',')
      .map((entry) => entry.trim())
      .filter(Boolean)
      .forEach((entry) => referenceProxySet.add(entry));
}

if (referenceExplicitProxy) {
  referenceProxySet.add(referenceExplicitProxy.trim());
}

const referenceProxyPool = Array.from(referenceProxySet);
let referenceProxyCursor = 0;
const referenceProxyAgentCache = new Map<
  string,
  { httpAgent: HttpsProxyAgent; httpsAgent: HttpsProxyAgent }
>();
const referenceDefaultAgents = {
  httpAgent: undefined as any,
  httpsAgent: new https.Agent({ keepAlive: true }),
};

function nextReferenceProxyCandidates(): (string | null)[] {
  if (referenceProxyPool.length === 0) {
    return [null];
  }

  const start = referenceProxyCursor % referenceProxyPool.length;
  referenceProxyCursor = (referenceProxyCursor + 1) % referenceProxyPool.length;
  const ordered = referenceProxyPool.slice(start).concat(referenceProxyPool.slice(0, start));

  const candidates = [...ordered];
  if (!candidates.includes(null)) {
    candidates.push(null);
  }
  return candidates;
}

function getReferenceAgents(proxy: string | null) {
  if (!proxy) {
    return referenceDefaultAgents;
  }

  if (!referenceProxyAgentCache.has(proxy)) {
    const agent = new HttpsProxyAgent(proxy);
    referenceProxyAgentCache.set(proxy, { httpAgent: agent, httpsAgent: agent });
  }

  return referenceProxyAgentCache.get(proxy)!;
}

function ensureCacheDir() {
  [REFERENCE_CACHE_DIR, REFERENCE_IMAGE_CACHE_DIR, REFERENCE_HTML_CACHE_DIR].forEach((dir) => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });
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

function htmlCachePath(url: string) {
  const hash = crypto.createHash('sha1').update(url).digest('hex');
  return path.join(REFERENCE_HTML_CACHE_DIR, `${hash}.html`);
}

function readHtmlCache(url: string): string | null {
  try {
    const filePath = htmlCachePath(url);
    if (fs.existsSync(filePath)) {
      return fs.readFileSync(filePath, 'utf-8');
    }
  } catch {
    // ignore cache read errors
  }
  return null;
}

function writeHtmlCache(url: string, html: string) {
  try {
    const filePath = htmlCachePath(url);
    fs.writeFileSync(filePath, html, 'utf-8');
  } catch {
    // ignore cache write errors
  }
}

async function fetchReferenceHtml(url: string): Promise<string | null> {
  ensureCacheDir();

  const cached = readHtmlCache(url);
  if (cached) {
    return cached;
  }

  const proxies = nextReferenceProxyCandidates();
  let lastError: any = null;

  for (const proxy of proxies) {
    const agents = getReferenceAgents(proxy);
    try {
      const response = await axios.get(url, {
        timeout: 18000,
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; MotiaReferenceBot/1.0)',
          Accept:
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
          'Accept-Language': 'en-US,en;q=0.9',
        },
        httpsAgent: agents.httpsAgent,
        httpAgent: agents.httpAgent,
      });

      const { data } = response;
      if (typeof data === 'string') {
        writeHtmlCache(url, data);
        return data;
      }
      if (Buffer.isBuffer(data)) {
        const html = data.toString('utf8');
        writeHtmlCache(url, html);
        return html;
      }
      if (data && typeof data === 'object') {
        const html = JSON.stringify(data);
        writeHtmlCache(url, html);
        return html;
      }
      return null;
    } catch (error: any) {
      console.warn(
        `Reference fetch failed for ${url}${proxy ? ` via proxy ${proxy}` : ''}: ${
          error?.message || error
        }`
      );
      lastError = error;
      if (error?.response?.status === 429) {
        await delay(1000);
      }
    }
  }

  if (!url.includes('r.jina.ai/')) {
    return fetchReferenceHtml(buildJinaUrl(url));
  }

  console.warn(`Reference fetch failed for ${url}: ${lastError?.message || lastError}`);
  return null;
}

async function tryFetch(url: string): Promise<string | null> {
  return fetchReferenceHtml(url);
}

async function cacheReferenceImage(
  imageUrl: string,
  referer?: string
): Promise<{ localPath: string; base64: string; mimeType: string } | null> {
  const proxies = nextReferenceProxyCandidates();
  let lastError: any = null;

  for (const proxy of proxies) {
    const agents = getReferenceAgents(proxy);
    try {
      const response = await axios.get<ArrayBuffer>(imageUrl, {
        responseType: 'arraybuffer',
        timeout: 15000,
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; MotiaReferenceBot/1.0)',
          Referer: referer || imageUrl,
        },
        httpsAgent: agents.httpsAgent,
        httpAgent: agents.httpAgent,
      });

      if (response.status !== 200) {
        lastError = new Error(`status ${response.status}`);
        continue;
      }

      const buffer = Buffer.from(response.data);
      if (buffer.length === 0) {
        lastError = new Error('empty response body');
        continue;
      }

      ensureCacheDir();
      const hash = crypto.createHash('sha1').update(imageUrl).digest('hex');

      // Sanitize file extension properly to avoid malformed names like "plain; charset=utf-8"
      let ext = response.headers['content-type']?.split('/')[1]?.split(';')[0] ||
                imageUrl.split('.').pop()?.split('?')[0] ||
                'jpg';

      // Remove any non-alphanumeric characters
      ext = ext.toLowerCase().replace(/[^a-z0-9]/g, '');

      // Validate extension is actually an image format
      const validExtensions = ['jpg', 'jpeg', 'png', 'webp', 'gif'];
      if (!validExtensions.includes(ext)) {
        ext = 'jpg'; // Default to jpg if unknown
      }

      const fileName = `${hash}.${ext}`;
      const localPath = path.join(REFERENCE_IMAGE_CACHE_DIR, fileName);
      fs.writeFileSync(localPath, buffer);

      const mimeType =
        response.headers['content-type']?.split(';')[0] ||
        (ext === 'jpg' || ext === 'jpeg' ? 'image/jpeg' : `image/${ext}`);

      return { localPath, base64: buffer.toString('base64'), mimeType };
    } catch (error: any) {
      lastError = error;
    }
  }

  // DO NOT fallback to Jina.ai for images - it converts them to markdown text!
  // If all proxies failed, just return null
  console.warn(`Failed to cache reference image ${imageUrl}: ${lastError?.message || lastError}`);
  return null;
}

async function validateImageQuality(imageUrl: string): Promise<boolean> {
  // Quick validation checks before downloading full image

  // 1. Check URL pattern - reject obvious non-images
  const lowerUrl = imageUrl.toLowerCase();

  // Reject favicons
  if (lowerUrl.includes('.ico') || lowerUrl.includes('favicon') || lowerUrl.includes('/icon')) {
    console.warn(`Rejected favicon URL: ${imageUrl}`);
    return false;
  }

  // Reject external-content proxy URLs (DuckDuckGo favicons)
  if (lowerUrl.includes('external-content.duckduckgo.com/ip3/')) {
    console.warn(`Rejected DuckDuckGo favicon proxy: ${imageUrl}`);
    return false;
  }

  // Must be image file extension
  const validExtensions = ['.jpg', '.jpeg', '.png', '.webp'];
  const hasValidExtension = validExtensions.some(ext => lowerUrl.includes(ext));
  if (!hasValidExtension) {
    console.warn(`Rejected non-image URL (no valid extension): ${imageUrl}`);
    return false;
  }

  try {
    // 2. Download first few KB to check file signature and size
    const proxies = nextReferenceProxyCandidates();

    for (const proxy of proxies) {
      const agents = getReferenceAgents(proxy);

      try {
        const response = await axios.get<ArrayBuffer>(imageUrl, {
          responseType: 'arraybuffer',
          timeout: 10000,
          headers: {
            'User-Agent': 'Mozilla/5.0 (compatible; MotiaReferenceBot/1.0)',
            'Range': 'bytes=0-10000', // First 10KB only
          },
          httpsAgent: agents.httpsAgent,
          httpAgent: agents.httpAgent,
        });

        const buffer = Buffer.from(response.data);

        // Check file signature (magic numbers)
        const isJPEG = buffer[0] === 0xFF && buffer[1] === 0xD8 && buffer[2] === 0xFF;
        const isPNG = buffer[0] === 0x89 && buffer[1] === 0x50 && buffer[2] === 0x4E && buffer[3] === 0x47;
        const isWebP = buffer.toString('ascii', 8, 12) === 'WEBP';

        if (!isJPEG && !isPNG && !isWebP) {
          console.warn(`Invalid image format (not JPEG/PNG/WebP): ${imageUrl}`);
          return false;
        }

        // Check FULL file size from content-range header (not content-length which is partial)
        // Content-Range format: "bytes 0-9999/3840000" where 3840000 is the full size
        const contentRange = response.headers['content-range'];
        let fullSize = 0;

        if (contentRange) {
          const match = contentRange.match(/\/(\d+)$/);
          if (match) {
            fullSize = parseInt(match[1]);
          }
        }

        // If no content-range, fall back to content-length (for non-partial responses)
        if (fullSize === 0) {
          fullSize = parseInt(response.headers['content-length'] || '0');
        }

        // Reject tiny images (thumbnails/favicons) - must be at least 50KB
        if (fullSize > 0 && fullSize < 50000) {
          console.warn(`Image too small (${(fullSize / 1024).toFixed(1)}KB): ${imageUrl}`);
          return false;
        }

        console.info(`✓ Image validation passed: ${(fullSize / 1024 / 1024).toFixed(2)}MB`);
        return true;
      } catch (error: any) {
        // Try next proxy
        continue;
      }
    }

    // If all proxies failed, reject
    return false;
  } catch (error: any) {
    console.warn(`Image validation failed: ${error.message}`);
    return false;
  }
}

async function discoverAwardReferences(request: ReferenceHarvestRequest): Promise<RawReferenceAsset[]> {
  // Use Behance to get high-quality award-winning project images
  console.info(`Discovering award-winning ${request.category} projects from Behance...`);

  try {
    // Step 1: Search Behance for actual high-quality campaign images (15 references)
    const imageResults = await searchBehanceProjects(request.category, 15);

    if (imageResults.length === 0) {
      console.warn('No projects found on Behance');
      return [];
    }

    console.info(`Found ${imageResults.length} high-quality Behance projects`);

    // Step 2: Convert to RawReferenceAsset format
    const entries: RawReferenceAsset[] = imageResults.map((item, index) => ({
      title: item.title || `Award-Winning Project ${index + 1}`,
      url: item.sourceUrl,
      imageUrl: item.imageUrl,
      source: 'Behance',
      publishedAt: new Date().getFullYear().toString(),
      awards: ['500+ Behance Appreciations'],
      blurb: `Award-winning ${request.category} project from Behance`,
    }));

    console.info(
      `Processed ${entries.length} award-winning references with actual images`,
      entries.slice(0, 3).map((entry) => ({
        title: entry.title,
        imageUrl: entry.imageUrl,
        hasValidImage: entry.imageUrl.startsWith('http'),
      }))
    );

    return entries;
  } catch (error: any) {
    console.warn(`Award reference discovery failed: ${error.message}`);
    return [];
  }
}

async function discoverEditorialReferences(request: ReferenceHarvestRequest): Promise<RawReferenceAsset[]> {
  // Use web search tool to find high-quality editorial references
  const searchQuery = `best ${request.category} editorial photography campaigns ${request.targetAudience || ''} Vogue GQ Dazed magazine`;

  console.info(`Searching for editorial references: "${searchQuery}"`);

  try {
    // Step 1: Use web search to find editorial campaigns
    const searchResults = await webSearch(searchQuery, 10);

    if (searchResults.length === 0) {
      console.warn('No editorial references found via web search');
      return [];
    }

    console.info(`Found ${searchResults.length} editorial search results`);

    // Step 2: Ask AI to analyze search results and extract structured data
    const searchResultsSummary = searchResults.map((result, index) => ({
      index,
      title: result.title,
      url: result.url,
      snippet: result.snippet,
    }));

    const completion = await openai.chat.completions.create({
      model: RESEARCH_MODEL,
      messages: [
        {
          role: 'system',
          content: 'You are an expert at analyzing high-quality editorial and campaign photography. Given search results, extract structured data about each editorial/campaign.',
        },
        {
          role: 'user',
          content: `Analyze these search results for ${request.category} editorial/campaign photography and extract structured data. For each result, provide: title, url (from search results), imageUrl (infer from URL pattern or leave empty), source (publication name), year (if mentioned), and blurb. Return as JSON object with "editorials" array containing fields: title, url, imageUrl, source, publishedAt, blurb.\n\nSearch Results:\n${JSON.stringify(searchResultsSummary, null, 2)}`
        },
      ],
      response_format: { type: 'json_object' },
    });

    const content = completion.choices[0]?.message?.content || '{}';
    const data = JSON.parse(content);

    const entries: RawReferenceAsset[] = (data.editorials || data.campaigns || data.items || []).map((item: any, index: number) => ({
      title: item.title || searchResults[index]?.title || `Editorial Reference ${index + 1}`,
      url: item.url || searchResults[index]?.url || '',
      imageUrl: item.imageUrl || item.image || searchResults[index]?.imageUrl || '',
      source: item.source || item.publication || 'Editorial Source',
      publishedAt: item.publishedAt || item.year,
      awards: item.awards,
      blurb: item.blurb || item.description || searchResults[index]?.snippet || '',
    }));

    console.info(
      `Processed ${entries.length} editorial references`,
      entries.slice(0, 3).map((entry) => ({
        title: entry.title,
        url: entry.url,
        hasImage: Boolean(entry.imageUrl),
        source: entry.source,
      }))
    );

    return entries;
  } catch (error: any) {
    console.warn(`Web search for editorial references failed: ${error.message}`);
    return [];
  }
}

async function extractVisualPrompt(reference: RawReferenceAsset, request: ReferenceHarvestRequest): Promise<ReferenceSceneTemplate | null> {
  if (!reference.imageUrl) {
    console.warn(`Skipping reference "${reference.title}" - no image URL`);
    return null;
  }

  // CRITICAL: Validate image quality BEFORE downloading
  const isValid = await validateImageQuality(reference.imageUrl);
  if (!isValid) {
    console.warn(`Skipping reference "${reference.title}" - failed image quality validation`);
    return null;
  }

  const cachedImage = await cacheReferenceImage(reference.imageUrl, reference.url);

  if (!cachedImage || !cachedImage.localPath) {
    console.warn(`Skipping reference "${reference.title}" - failed to download image from ${reference.imageUrl}`);
    return null;
  }

  // Verify the cached file exists and has content
  if (!fs.existsSync(cachedImage.localPath)) {
    console.warn(`Skipping reference "${reference.title}" - cached file missing at ${cachedImage.localPath}`);
    return null;
  }

  const fileStats = fs.statSync(cachedImage.localPath);
  if (fileStats.size === 0) {
    console.warn(`Skipping reference "${reference.title}" - cached file is empty`);
    return null;
  }

  console.info(`✓ Successfully cached reference image: ${path.basename(cachedImage.localPath)} (${(fileStats.size / 1024).toFixed(2)}KB)`);

  const remoteImageUrl = buildJinaUrl(reference.imageUrl);

  const systemContent = `You are a senior creative director analysing award-winning imagery. Extract the actionable scene composition so we can recreate the shot for a new campaign. Focus on lighting, camera placement, foreground/midground/background, emotional tone, props, and post-processing.`;

  const userContent = `Analyse this reference image${reference.title ? ` titled "${reference.title}"` : ''} from ${reference.source}. Category: ${request.category}. Target audience: ${request.targetAudience ?? 'modern affluent consumers'}. Provide a structured JSON object with fields: promptSummary, sceneComposition (camera, lighting, foreground, midground, background, props, postProcessing, emotion).`;

  try {
    // Use Andromeda Alpha for image analysis
    const messages: any[] = [
      { role: 'system', content: systemContent },
      {
        role: 'user',
        content: cachedImage
          ? [
              {
                type: 'text',
                text: `${userContent}\nRespond only with valid JSON.`,
              },
              {
                type: 'image_url',
                image_url: {
                  url: `data:${cachedImage.mimeType};base64,${cachedImage.base64}`,
                },
              },
            ]
          : `${userContent}\nImage could not be downloaded; use the descriptive fields available (title, blurb, awards) to infer composition. Respond only with valid JSON.`,
      },
    ];

    const completion = await openai.chat.completions.create({
      model: RESEARCH_MODEL,
      messages,
      response_format: { type: 'json_object' },
      max_tokens: 2000,
    });

    const content = completion.choices[0]?.message?.content || '{}';
    const parsed = JSON.parse(content);

    const sceneComposition = parsed.sceneComposition || {};
    const referenceIdSource = reference.imageUrl || reference.url || reference.title || 'reference';
    const template: ReferenceSceneTemplate = {
      id: `${reference.source}-${crypto.createHash('sha1').update(referenceIdSource).digest('hex').slice(0, 12)}`,
      imageUrl: reference.imageUrl,
      localImagePath: cachedImage?.localPath || '',
      headline: reference.title,
      description: reference.blurb,
      source: {
        sourceName: reference.source,
        sourceUrl: reference.url,
        publishedAt: reference.publishedAt,
        awards: reference.awards,
      },
      promptSummary: parsed.promptSummary || parsed.summary || '',
      sceneComposition: {
        camera: sceneComposition.camera || 'Not specified',
        lighting: sceneComposition.lighting || 'Not specified',
        foreground: sceneComposition.foreground || 'Not specified',
        midground: sceneComposition.midground || 'Not specified',
        background: sceneComposition.background || 'Not specified',
        props: sceneComposition.props || 'Not specified',
        postProcessing: sceneComposition.postProcessing || 'Not specified',
        emotion: sceneComposition.emotion || 'Not specified',
      },
    };

    console.info(`Generated template for ${reference.source}: ${template.headline || template.id}`);

    return template;
  } catch (error: any) {
    console.warn(`Visual prompt extraction failed for ${reference.imageUrl}: ${error.message}`);
    return null;
  }
}

export async function curateReferenceLibrary(request: ReferenceHarvestRequest): Promise<ReferenceSceneTemplate[]> {
  const [awards, editorials] = await Promise.all([
    discoverAwardReferences(request),
    discoverEditorialReferences(request),
  ]);

  const combined = [...awards, ...editorials]
    .filter((ref) => ref.imageUrl || ref.blurb)
    .slice(0, 12);

  console.info(
    `Total references before templating: ${combined.length}`,
    combined.slice(0, 3).map((entry) => ({
      title: entry.title,
      source: entry.source,
      hasImage: Boolean(entry.imageUrl),
      hasBlurb: Boolean(entry.blurb),
    }))
  );

  const templates: ReferenceSceneTemplate[] = [];

  for (const reference of combined) {
    const template = await extractVisualPrompt(reference, request);
    if (template) {
      templates.push(template);
    }
  }

  if (templates.length === 0) {
    console.warn(
      `Reference library empty for ${request.category || 'brand'} - proceeding without visual templates.`
    );
  }

  console.info(`Reference templates generated: ${templates.length}`);

  return templates;
}
