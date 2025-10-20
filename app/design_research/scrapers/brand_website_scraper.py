"""
Generic brand website scraper for extracting product and brand data.

This scraper works for ANY e-commerce brand website by:
1. Extracting product names, prices, descriptions
2. Detecting currency automatically
3. Finding brand messaging/taglines
4. Identifying category from metadata
5. Extracting price range (min/max)
6. Handling JavaScript-rendered sites with Playwright
7. Bypassing bot protection with proper headers

Supports common e-commerce platforms: Shopify, WooCommerce, custom sites.
"""

import re
import logging
import asyncio
from typing import Dict, List, Optional
import httpx
from bs4 import BeautifulSoup

from app.core.config import settings

logger = logging.getLogger(__name__)


class BrandWebsiteScraper:
    """Generic scraper for any brand e-commerce website."""

    def __init__(self, use_browser: bool = True):
        """
        Initialize the scraper.

        Args:
            use_browser: If True, will use Playwright for JS-rendered sites (slower but works everywhere)
                        If False, uses httpx only (faster but may miss JS-loaded content)
        """
        self.logger = logger
        self.timeout = settings.HTTP_TIMEOUT_SECONDS
        self.use_browser = use_browser

        # User-agent to avoid bot detection
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    async def _fetch_with_browser(self, url: str) -> str:
        """
        Fetch page content using Playwright (handles JavaScript rendering).

        Args:
            url: URL to fetch

        Returns:
            HTML content as string
        """
        try:
            from playwright.async_api import async_playwright

            self.logger.info(f"Using browser automation for: {url}")

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=self.headers['User-Agent'],
                    viewport={'width': 1920, 'height': 1080}
                )
                page = await context.new_page()

                # Navigate with more lenient wait
                await page.goto(url, wait_until='domcontentloaded', timeout=settings.PAGE_LOAD_TIMEOUT_MS)

                # Wait for content to load
                await page.wait_for_timeout(5000)

                # Get the HTML content
                html = await page.content()

                await browser.close()

                return html

        except Exception as e:
            self.logger.warning(f"Browser automation failed: {e}")
            raise

    async def _extract_products_with_browser(self, url: str) -> List[Dict]:
        """
        Extract products using Playwright for JS-heavy sites.

        Args:
            url: Page URL to scrape

        Returns:
            List of product dictionaries
        """
        try:
            from playwright.async_api import async_playwright

            self.logger.info(f"Extracting products with browser from: {url}")

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=self.headers['User-Agent'],
                    viewport={'width': 1920, 'height': 1080}
                )
                page = await context.new_page()

                await page.goto(url, wait_until='domcontentloaded', timeout=settings.PAGE_LOAD_TIMEOUT_MS)
                await page.wait_for_timeout(5000)

                # Try multiple product link patterns
                link_patterns = [
                    'a[href*="/products/"]',
                    'a[href*="/product/"]',
                    'a[href*="/eyeglasses/"]',
                    'a[href*="/p/"]',
                    'a[href*="/item/"]'
                ]

                products = []
                seen = set()

                for pattern in link_patterns:
                    elements = await page.query_selector_all(pattern)
                    if len(elements) > 5:
                        self.logger.info(f"Found {len(elements)} product links with pattern: {pattern}")

                        for elem in elements[:30]:  # Limit to 30
                            href = await elem.get_attribute('href')
                            if not href or href in seen:
                                continue
                            seen.add(href)

                            # Extract name from URL
                            name_part = href.split('/')[-1].split('?')[0]
                            name = name_part.replace('-', ' ').replace('_', ' ').title()

                            # Try to get price from nearby elements
                            price = '0'
                            try:
                                parent = elem
                                for _ in range(3):
                                    price_elem = await parent.query_selector('[class*="price"], [data-price]')
                                    if price_elem:
                                        price_text = await price_elem.inner_text()
                                        price = price_text.strip()
                                        break
                                    parent = await parent.evaluate_handle('el => el.parentElement')
                            except:
                                pass

                            if name:
                                products.append({
                                    'name': name,
                                    'price': price,
                                    'description': ''
                                })

                        break  # Found products, stop trying patterns

                await browser.close()

                self.logger.info(f"Extracted {len(products)} products with browser")
                return products

        except Exception as e:
            self.logger.warning(f"Browser product extraction failed: {e}")
            return []

    async def scrape_brand(self, url: str) -> Dict:
        """
        Scrape brand data from any e-commerce website.

        Args:
            url: Brand website URL (e.g., https://sarabkhanijou.com/)

        Returns:
            Dictionary with:
                - products: List of {name, price, description}
                - brand_messaging: Brand tagline/slogan
                - category_stated: Inferred category
                - currency: Detected currency
                - region: Inferred region
                - price_range: (min, max) tuple
        """
        self.logger.info(f"Scraping brand website: {url}")

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers=self.headers
            ) as client:
                # Step 1: Try Shopify JSON API first (faster and more reliable)
                base_domain = url.rstrip('/')
                products = []

                try:
                    json_url = f"{base_domain}/products.json"
                    self.logger.info(f"Trying Shopify JSON API: {json_url}")
                    json_response = await client.get(json_url)
                    if json_response.status_code == 200:
                        json_data = json_response.json()
                        if 'products' in json_data:
                            for product in json_data['products']:
                                variants = product.get('variants', [])
                                if variants:
                                    price = variants[0].get('price', '0')
                                    # Just store the numeric price - currency will be detected later
                                    products.append({
                                        'name': product.get('title', 'Unknown'),
                                        'price': str(price),
                                        'description': product.get('body_html', '')[:200] if product.get('body_html') else ''
                                    })
                            self.logger.info(f"Found {len(products)} products via Shopify JSON API")
                except Exception as e:
                    self.logger.info(f"Shopify JSON API not available: {e}")

                # Step 2: Get homepage for metadata
                # Add delay to avoid rate limiting
                await asyncio.sleep(1)

                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    html = response.text
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 403 and self.use_browser:
                        # Bot protection detected, use browser automation
                        self.logger.info("403 Forbidden detected, switching to browser automation")
                        html = await self._fetch_with_browser(url)
                    else:
                        raise

                soup = BeautifulSoup(html, 'html.parser')

                # Step 3: If no products from JSON API, fall back to HTML/browser scraping
                if not products:
                    self.logger.info("JSON API failed, falling back to HTML scraping")

                    # Check if HTML has product elements
                    has_products_in_html = len(soup.select('[class*="product"]')) > 0

                    # If no products in HTML and browser enabled, use direct browser extraction
                    if self.use_browser and not has_products_in_html:
                        self.logger.info("No products in static HTML, using direct browser extraction")
                        products = await self._extract_products_with_browser(url)

                    # If still no products, try HTML scraping from collections
                    collection_urls = []
                    if not products:
                        # Find all collection/category URLs
                        collection_urls = self._find_collection_urls(soup, url)
                        self.logger.info(f"Found {len(collection_urls)} collection pages")

                        # Scrape products from homepage
                        products = await self._extract_products(soup, url)
                        self.logger.info(f"Found {len(products)} products on homepage")

                        # Scrape ALL collection pages
                        for collection_url in collection_urls[:10]:  # Limit to 10 collections
                            try:
                                self.logger.info(f"Scraping collection: {collection_url}")
                                coll_response = await client.get(collection_url)
                                coll_response.raise_for_status()
                                coll_soup = BeautifulSoup(coll_response.text, 'html.parser')
                                coll_products = await self._extract_products(coll_soup, collection_url)
                                products.extend(coll_products)
                                self.logger.info(f"Found {len(coll_products)} products in collection")
                            except Exception as e:
                                self.logger.warning(f"Failed to scrape collection {collection_url}: {e}")
                                continue

                    # Remove duplicates by product name
                    unique_products = []
                    seen_names = set()
                    for product in products:
                        if product['name'] not in seen_names:
                            unique_products.append(product)
                            seen_names.add(product['name'])

                    products = unique_products

                # Extract metadata
                brand_messaging = self._extract_brand_messaging(soup)
                currency = self._detect_currency(soup, products)
                region = self._infer_region(url, currency)
                category = self._infer_category(soup, products)
                price_range = self._calculate_price_range(products)

                brand_data = {
                    "products": products,
                    "brand_messaging": brand_messaging,
                    "category_stated": category,
                    "currency": currency,
                    "region": region,
                    "price_range": price_range,
                    "source_url": url
                }

                self.logger.info(f"Scraped {len(products)} total unique products from {url}")
                return brand_data

        except Exception as e:
            self.logger.error(f"Failed to scrape {url}: {e}")
            raise

    def _find_collection_urls(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Find all collection/category page URLs.

        Looks for:
        - /collections/* URLs (Shopify)
        - /category/* URLs (WooCommerce)
        - /shop/* URLs
        - Navigation menu links
        """
        collection_urls = set()
        base_domain = base_url.rstrip('/')

        # Common collection URL patterns
        patterns = [
            '/collections/',
            '/category/',
            '/shop/',
            '/products/',
            '/catalog/'
        ]

        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']

            # Convert relative URLs to absolute
            if href.startswith('/'):
                href = base_domain + href
            elif not href.startswith('http'):
                continue

            # Check if it matches collection patterns
            if any(pattern in href for pattern in patterns):
                # Remove query params and fragments
                clean_url = href.split('?')[0].split('#')[0]
                collection_urls.add(clean_url)

        return list(collection_urls)

    async def _extract_products(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """
        Extract product data from page.

        Looks for common e-commerce patterns:
        - Product cards/items
        - Price elements
        - Product titles
        - Descriptions
        """
        products = []

        # Try multiple product selector patterns (Shopify, WooCommerce, custom)
        product_selectors = [
            '.product-item',
            '.product-card',
            '.product',
            '[data-product]',
            'article.product',
            '.grid-product',
            '.collection-product'
        ]

        product_elements = []
        for selector in product_selectors:
            product_elements = soup.select(selector)
            if product_elements:
                self.logger.info(f"Found {len(product_elements)} products using selector: {selector}")
                break

        if not product_elements:
            # Fallback: look for any element with price
            self.logger.warning("No standard product elements found, using fallback")
            product_elements = soup.find_all(class_=re.compile(r'product|item', re.I))

        for elem in product_elements[:20]:  # Limit to first 20 products
            product = self._parse_product_element(elem)
            if product and product.get('price'):
                products.append(product)

        return products

    def _parse_product_element(self, elem) -> Optional[Dict]:
        """Parse a single product element to extract name, price, description."""
        try:
            # Extract product name
            name = None
            for selector in ['.product-title', '.product-name', 'h3', 'h2', 'a[title]']:
                name_elem = elem.select_one(selector)
                if name_elem:
                    name = name_elem.get_text(strip=True) or name_elem.get('title')
                    if name:
                        break

            # Extract price
            price = None
            for selector in ['.price', '.product-price', '[data-price]', 'span.money']:
                price_elem = elem.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True) or price_elem.get('data-price')
                    if price_text:
                        price = price_text
                        break

            # Extract description (optional)
            description = None
            for selector in ['.product-description', '.description', 'p']:
                desc_elem = elem.select_one(selector)
                if desc_elem:
                    description = desc_elem.get_text(strip=True)
                    if len(description) > 20:  # Only use if substantial
                        break

            if name and price:
                return {
                    "name": name,
                    "price": price,
                    "description": description or ""
                }

            return None

        except Exception as e:
            self.logger.warning(f"Failed to parse product element: {e}")
            return None

    def _extract_brand_messaging(self, soup: BeautifulSoup) -> str:
        """
        Extract brand messaging/tagline.

        Looks for:
        - Meta description
        - Hero section text
        - Taglines
        - About section
        """
        # Try meta description first
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content']

        # Try og:description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content']

        # Look for hero/banner text
        for selector in ['.hero', '.banner', '.tagline', 'h1', '.site-description']:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                if text and len(text) < 200:  # Reasonable tagline length
                    return text

        return "Premium quality products"

    def _detect_currency(self, soup: BeautifulSoup, products: List[Dict]) -> str:
        """
        Detect currency from page or products.

        Returns: Currency code (INR, USD, EUR, etc.)
        """
        # Check products for currency symbols OR text
        if products:
            for product in products[:5]:  # Check first 5 products
                price = product.get('price', '')
                # Check for explicit currency codes first
                if 'INR' in price or '₹' in price:
                    return 'INR'
                elif 'EUR' in price or '€' in price:
                    return 'EUR'
                elif 'GBP' in price or '£' in price:
                    return 'GBP'
                elif 'JPY' in price or '¥' in price:
                    return 'JPY'
                elif 'USD' in price:
                    return 'USD'
                # If just $ symbol, likely USD (most common)
                elif '$' in price:
                    return 'USD'

        # Check meta tags
        currency_meta = soup.find('meta', attrs={'property': 'og:price:currency'})
        if currency_meta:
            return currency_meta.get('content', 'USD').upper()

        # Check URL domain for region hints
        url_lower = str(soup).lower() if hasattr(soup, 'lower') else ''
        if '.in/' in url_lower or '.in?' in url_lower:
            return 'INR'
        elif '.uk/' in url_lower or '.co.uk' in url_lower:
            return 'GBP'
        elif '.eu/' in url_lower:
            return 'EUR'

        # Default to USD (most common for international e-commerce)
        return 'USD'

    def _infer_region(self, url: str, currency: str) -> str:
        """
        Infer region from URL and currency.

        Returns: Region name
        """
        url_lower = url.lower()

        # Check TLD
        if '.in' in url_lower or 'india' in url_lower:
            return 'India'
        elif '.uk' in url_lower or '.co.uk' in url_lower:
            return 'United Kingdom'
        elif '.eu' in url_lower:
            return 'Europe'
        elif '.jp' in url_lower:
            return 'Japan'
        elif '.au' in url_lower:
            return 'Australia'

        # Infer from currency
        currency_to_region = {
            'INR': 'India',
            'GBP': 'United Kingdom',
            'EUR': 'Europe',
            'JPY': 'Japan',
            'AUD': 'Australia',
            'USD': 'United States'
        }

        return currency_to_region.get(currency, 'United States')

    def _infer_category(self, soup: BeautifulSoup, products: List[Dict]) -> str:
        """
        Infer product category from page content.

        Returns: Category string
        """
        # Check meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            keywords = meta_keywords.get('content', '').lower()
            if 'ethnic' in keywords or 'sherwani' in keywords or 'kurta' in keywords:
                return "Men's Indian Formal Wear / Ethnic Menswear"
            elif 'fashion' in keywords:
                return "Fashion"
            elif 'jewelry' in keywords or 'jewellery' in keywords:
                return "Jewelry"
            elif 'watch' in keywords:
                return "Watches"

        # Check product names
        if products:
            product_names = ' '.join([p['name'].lower() for p in products[:5]])
            if any(keyword in product_names for keyword in ['sherwani', 'kurta', 'bandhgala', 'ethnic']):
                return "Men's Indian Formal Wear / Ethnic Menswear"
            elif 'watch' in product_names:
                return "Watches"
            elif 'bag' in product_names or 'handbag' in product_names:
                return "Handbags & Accessories"

        # Check page title
        title = soup.find('title')
        if title:
            title_text = title.get_text().lower()
            if 'ethnic' in title_text or 'indian' in title_text:
                return "Men's Indian Formal Wear / Ethnic Menswear"
            elif 'fashion' in title_text:
                return "Fashion"

        return "Fashion & Apparel"

    def _calculate_price_range(self, products: List[Dict]) -> tuple:
        """
        Calculate min and max prices from products.

        Returns: (min_price, max_price) as floats
        """
        if not products:
            return (0.0, 0.0)

        prices = []
        for product in products:
            price_str = product.get('price', '')

            # Handle multiple price formats
            # Format 1: "₹67,000"
            # Format 2: "Regular priceINR 32,500.00Regular priceSale priceINR 32,500.00"
            # Format 3: "$1,299.99"

            # Find all numeric values with optional commas and decimals
            price_matches = re.findall(r'[\d,]+\.?\d*', price_str)

            for match in price_matches:
                try:
                    # Remove commas and convert to float
                    price = float(match.replace(',', ''))
                    # Only accept reasonable prices (> 10)
                    if price > 10:
                        prices.append(price)
                        break  # Take first valid price
                except ValueError:
                    continue

        if prices:
            return (min(prices), max(prices))

        return (0.0, 0.0)
