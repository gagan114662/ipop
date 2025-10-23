import axios from 'axios';
import * as cheerio from 'cheerio';

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

export async function scrapeWebsite(url: string): Promise<{ 
  products: ProductSKU[], 
  visualData: BrandVisualData,
  rawContent: string 
}> {
  try {
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });

    const $ = cheerio.load(response.data);
    const products: ProductSKU[] = [];
    const colors: string[] = [];
    const typography: string[] = [];
    const imageUrls: string[] = [];

    // Extract color palette from CSS and inline styles
    $('style, [style]').each((_, elem) => {
      const text = $(elem).text() || $(elem).attr('style') || '';
      const colorMatches = text.match(/#[0-9A-Fa-f]{3,6}|rgb\([^)]+\)|rgba\([^)]+\)/g);
      if (colorMatches) {
        colors.push(...colorMatches);
      }
    });

    // Extract fonts
    $('style, link[rel="stylesheet"]').each((_, elem) => {
      const text = $(elem).text() || '';
      const fontMatches = text.match(/font-family:\s*([^;}\n]+)/gi);
      if (fontMatches) {
        fontMatches.forEach(match => {
          const font = match.replace(/font-family:\s*/i, '').trim();
          typography.push(font);
        });
      }
    });

    // Extract images
    $('img').each((_, elem) => {
      const src = $(elem).attr('src');
      if (src) {
        const fullUrl = new URL(src, url).href;
        imageUrls.push(fullUrl);
      }
    });

    // Logo detection
    const logoUrl = $('img[class*="logo"], img[id*="logo"], .logo img, #logo img').first().attr('src');
    const fullLogoUrl = logoUrl ? new URL(logoUrl, url).href : undefined;

    // Product extraction - multiple strategies
    const productSelectors = [
      '.product', '.product-item', '[data-product]', '.woocommerce-LoopProduct-link',
      '.product-card', '.item', '[itemtype*="Product"]', '.shop-item'
    ];

    for (const selector of productSelectors) {
      $(selector).each((_, elem) => {
        const $elem = $(elem);
        
        const sku = $elem.attr('data-sku') || 
                    $elem.find('[data-sku]').attr('data-sku') ||
                    $elem.find('.sku').text() ||
                    $elem.attr('data-product-id') ||
                    '';

        const name = $elem.find('.product-title, .product-name, h2, h3, .title').first().text().trim() ||
                     $elem.attr('title') || '';

        const price = $elem.find('.price, .product-price, [class*="price"]').first().text().trim();
        
        const description = $elem.find('.description, .product-description, p').first().text().trim();
        
        const imgSrc = $elem.find('img').first().attr('src');
        const imageUrl = imgSrc ? new URL(imgSrc, url).href : undefined;
        
        const category = $elem.attr('data-category') || 
                        $elem.find('[data-category]').attr('data-category') || '';

        const productUrl = $elem.find('a').first().attr('href') || 
                          $elem.attr('href') || '';
        const fullProductUrl = productUrl ? new URL(productUrl, url).href : url;

        if (name || sku) {
          products.push({
            sku: sku || `AUTO_${products.length + 1}`,
            name,
            price,
            description,
            imageUrl,
            category,
            url: fullProductUrl
          });
        }
      });

      if (products.length > 0) break;
    }

    // Fallback: Extract all links that might be products
    if (products.length === 0) {
      $('a').each((_, elem) => {
        const href = $(elem).attr('href');
        const text = $(elem).text().trim();
        if (href && text && (
          href.includes('/product') || 
          href.includes('/shop') || 
          href.includes('/item')
        )) {
          const fullUrl = new URL(href, url).href;
          products.push({
            sku: `AUTO_${products.length + 1}`,
            name: text,
            url: fullUrl
          });
        }
      });
    }

    // Get raw content for AI analysis
    const rawContent = $('body').text().slice(0, 10000); // First 10k chars

    return {
      products,
      visualData: {
        colors: [...new Set(colors)].slice(0, 20),
        logoUrl: fullLogoUrl,
        typography: [...new Set(typography)].slice(0, 10),
        imageUrls: imageUrls.slice(0, 50),
        rawHtml: response.data.slice(0, 20000)
      },
      rawContent
    };
  } catch (error: any) {
    throw new Error(`Failed to scrape website: ${error.message}`);
  }
}
