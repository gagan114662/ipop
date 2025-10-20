"""Universal Brand Web Scraper

Scrapes ANY website to extract brand information using only Python standard library.
Handles real-world challenges: redirects, encoding issues, malformed HTML, etc.
Works universally - no brand-specific logic, no external dependencies.
"""

import logging
import re
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse, quote
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser
import asyncio
import time
import json
import ssl

logger = logging.getLogger(__name__)


class BrandHTMLParser(HTMLParser):
    """Robust HTML parser that handles malformed HTML and extracts brand data."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.meta_tags = {}
        self.images = []
        self.links = []
        self.text_chunks = []
        self.headings = []
        self.list_items = []
        self.current_tag = None
        self.in_script = False
        self.in_style = False
        self.json_ld_data = []

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attrs_dict = dict(attrs)

        # Track script/style tags to ignore their content
        if tag == "script":
            self.in_script = True
            # Check for JSON-LD structured data
            if attrs_dict.get("type") == "application/ld+json":
                self.current_tag = "json_ld"
        elif tag == "style":
            self.in_style = True

        if tag == "meta":
            name = attrs_dict.get("name", attrs_dict.get("property", ""))
            content = attrs_dict.get("content", "")
            if name and content:
                self.meta_tags[name] = content

        elif tag == "img":
            # Try multiple src attributes (lazy loading, responsive images)
            src = (attrs_dict.get("src") or
                   attrs_dict.get("data-src") or
                   attrs_dict.get("data-lazy-src"))

            # Try srcset if no src found
            if not src:
                srcset = attrs_dict.get("srcset", "")
                if srcset:
                    parts = srcset.split(",")[0].split()
                    src = parts[0] if parts else ""

            if src and not src.startswith("data:"):  # Skip data URLs
                self.images.append(src.strip())

        elif tag == "a":
            href = attrs_dict.get("href", "")
            if href and not href.startswith(("javascript:", "mailto:", "tel:")):
                self.links.append(href)

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False
        elif tag == "style":
            self.in_style = False
        self.current_tag = None

    def handle_data(self, data):
        # Skip script and style content
        if self.in_script or self.in_style:
            # Try to parse JSON-LD if in script tag
            if self.current_tag == "json_ld":
                try:
                    ld_data = json.loads(data)
                    self.json_ld_data.append(ld_data)
                except (json.JSONDecodeError, ValueError):
                    pass
            return

        data = data.strip()
        if not data:
            return

        if self.current_tag == "title":
            self.title = data
        elif self.current_tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            self.headings.append(data)
        elif self.current_tag == "li":
            self.list_items.append(data)
        elif self.current_tag in ["p", "div", "span", "article", "section"]:
            self.text_chunks.append(data)

    def error(self, message):
        # Ignore HTML parsing errors - be lenient with malformed HTML
        pass


class BrandScraper:
    """Universal web scraper for brand data extraction.

    Handles:
    - Multiple character encodings
    - Malformed HTML
    - Redirects
    - Retry logic
    - JavaScript-heavy sites (best effort)
    - Various content types
    """

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        Initialize scraper.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logger

    async def scrape_brand(self, brand_url: str) -> Dict[str, Any]:
        """
        Scrape complete brand data from any website.

        Args:
            brand_url: Brand website URL

        Returns:
            Dictionary with structured brand data

        Raises:
            ValueError: If URL is invalid
            Exception: If scraping fails
        """
        # Validate URL
        if not brand_url or not isinstance(brand_url, str):
            raise ValueError("Invalid brand URL")

        if not brand_url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")

        self.logger.info(f"Scraping brand data from: {brand_url}")

        try:
            # Fetch and parse
            html_content = await self._fetch_page(brand_url)
            parser = BrandHTMLParser()
            parser.feed(html_content)

            # Detect if site is JavaScript-heavy
            is_js_heavy = self._detect_javascript_heavy(parser, html_content)

            # If JavaScript-heavy and minimal content, use browser scraper
            if is_js_heavy and len(parser.text_chunks) < 3:
                self.logger.info(f"{brand_url} is JavaScript-heavy - switching to browser scraper")
                return await self._scrape_with_browser(brand_url, html_content, parser)

            # Extract structured data
            brand_data = {
                "name": self._extract_brand_name(parser, brand_url),
                "url": brand_url,
                "category": self._categorize_brand(parser),
                "description": self._extract_description(parser),
                "features": self._extract_features(parser),
                "images": self._extract_images(parser, brand_url),
                "content": self._extract_text_content(parser),
                "metadata": self._extract_metadata(parser),
                "links": self._extract_links(parser, brand_url),
                "social_media": self._extract_social_media(parser),
                "javascript_heavy": is_js_heavy  # Flag for downstream processing
            }

            self.logger.info(f"Successfully scraped {brand_url}")
            return brand_data

        except Exception as e:
            self.logger.error(f"Failed to scrape {brand_url}: {str(e)}")
            raise

    async def _fetch_page(self, url: str) -> str:
        """Fetch HTML content from URL."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._fetch_page_sync, url)

    def _fetch_page_sync(self, url: str) -> str:
        """Synchronous page fetch with retry logic and encoding detection."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        # Create SSL context that doesn't verify certificates (for compatibility)
        # Note: In production, you may want to verify certificates for security
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        last_error = None

        for attempt in range(self.max_retries):
            try:
                request = Request(url, headers=headers)

                with urlopen(request, timeout=self.timeout, context=ssl_context) as response:
                    # Get content and encoding
                    content_bytes = response.read()

                    # Try to detect encoding from headers
                    encoding = response.headers.get_content_charset()

                    # Try multiple encodings
                    encodings_to_try = [encoding, 'utf-8', 'latin-1', 'iso-8859-1', 'windows-1252']
                    encodings_to_try = [e for e in encodings_to_try if e]  # Remove None

                    for enc in encodings_to_try:
                        try:
                            return content_bytes.decode(enc)
                        except (UnicodeDecodeError, LookupError):
                            continue

                    # Last resort: decode with errors='replace'
                    return content_bytes.decode('utf-8', errors='replace')

            except HTTPError as e:
                last_error = f"HTTP Error {e.code}: {e.reason}"
                if e.code in [429, 503]:  # Rate limit or service unavailable
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                raise Exception(last_error)

            except URLError as e:
                last_error = f"URL Error: {e.reason}"
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                raise Exception(last_error)

            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                    continue
                raise Exception(last_error)

        raise Exception(f"Failed after {self.max_retries} attempts: {last_error}")

    def _extract_brand_name(self, parser: BrandHTMLParser, url: str) -> str:
        """Extract brand name from multiple sources."""
        # Try JSON-LD structured data first
        for ld_data in parser.json_ld_data:
            if isinstance(ld_data, dict):
                name = ld_data.get("name") or ld_data.get("legalName")
                if name:
                    return name

        # Try meta og:site_name
        og_name = parser.meta_tags.get("og:site_name")
        if og_name:
            return og_name

        # Try application-name
        app_name = parser.meta_tags.get("application-name")
        if app_name:
            return app_name

        # Try title tag
        if parser.title:
            # Clean common patterns
            name = parser.title
            for separator in ["-", "|", "—", "–", ":"]:
                if separator in name:
                    name = name.split(separator)[0]
            name = name.strip()
            if name and len(name) > 2:
                return name

        # Try first h1 heading
        if parser.headings:
            first_heading = parser.headings[0]
            if len(first_heading) < 50:  # Reasonable brand name length
                return first_heading

        # Fall back to domain name
        domain = urlparse(url).netloc
        name = domain.replace("www.", "").split(".")[0]
        return name.replace("-", " ").replace("_", " ").title()

    def _extract_description(self, parser: BrandHTMLParser) -> str:
        """Extract brand description from multiple sources."""
        # Try JSON-LD structured data
        for ld_data in parser.json_ld_data:
            if isinstance(ld_data, dict):
                desc = ld_data.get("description")
                if desc and len(desc) > 20:
                    return desc

        # Try meta description
        desc = parser.meta_tags.get("description") or parser.meta_tags.get("og:description")
        if desc and len(desc) > 20:
            return desc

        # Try Twitter description
        twitter_desc = parser.meta_tags.get("twitter:description")
        if twitter_desc and len(twitter_desc) > 20:
            return twitter_desc

        # Try first substantial text chunk
        for chunk in parser.text_chunks:
            if len(chunk) > 50:  # Skip very short chunks
                return chunk[:300]

        # Try combining first few text chunks
        if parser.text_chunks:
            combined = " ".join(parser.text_chunks[:3])
            if combined:
                return combined[:300]

        return "No description available"

    def _categorize_brand(self, parser: BrandHTMLParser) -> str:
        """Attempt to categorize the brand based on content."""
        text_content = " ".join(parser.text_chunks + parser.headings).lower()

        # Category keywords
        categories = {
            "e-commerce": ["shop", "buy", "cart", "product", "store"],
            "saas": ["software", "platform", "api", "solution", "cloud"],
            "agency": ["agency", "marketing", "creative", "design", "advertising"],
            "consulting": ["consulting", "strategy", "advisory", "expert"],
            "education": ["course", "learn", "training", "education"],
            "healthcare": ["health", "medical", "doctor", "wellness"],
            "finance": ["finance", "investment", "banking", "insurance"],
            "tech": ["technology", "tech", "innovation", "digital"]
        }

        # Count matches
        scores = {}
        for category, keywords in categories.items():
            score = sum(text_content.count(keyword) for keyword in keywords)
            if score > 0:
                scores[category] = score

        return max(scores, key=scores.get) if scores else "general_utility"

    def _extract_features(self, parser: BrandHTMLParser) -> List[str]:
        """Extract product/service features from content."""
        features = []

        # Use list items as features
        for item in parser.list_items[:15]:
            if len(item) < 200:  # Reasonable feature length
                features.append(item)

        # If no list items, use headings
        if not features:
            features = [h for h in parser.headings[:10] if len(h) < 100]

        return features

    def _extract_images(self, parser: BrandHTMLParser, base_url: str) -> List[str]:
        """Extract image URLs from page."""
        images = []

        for src in parser.images[:50]:
            # Convert to absolute URL
            absolute_url = urljoin(base_url, src)
            # Filter out icons
            if not any(skip in absolute_url.lower() for skip in ["icon", "favicon", "logo-small"]):
                images.append(absolute_url)

        return images[:20]

    def _extract_text_content(self, parser: BrandHTMLParser) -> str:
        """Extract main text content from page."""
        text = " ".join(parser.text_chunks)
        return text[:5000]  # Limit to 5000 characters

    def _extract_metadata(self, parser: BrandHTMLParser) -> Dict[str, str]:
        """Extract SEO and meta information."""
        metadata = {}

        if parser.title:
            metadata["title"] = parser.title

        # Include all meta tags
        for key, value in parser.meta_tags.items():
            metadata[key] = value

        return metadata

    def _extract_links(self, parser: BrandHTMLParser, base_url: str) -> Dict[str, List[str]]:
        """Extract internal and external links."""
        base_domain = urlparse(base_url).netloc
        internal = []
        external = []

        for href in parser.links[:100]:
            if href.startswith(("#", "javascript:", "mailto:")):
                continue

            absolute_url = urljoin(base_url, href)
            link_domain = urlparse(absolute_url).netloc

            if link_domain == base_domain:
                internal.append(absolute_url)
            else:
                external.append(absolute_url)

        return {
            "internal": list(set(internal))[:20],
            "external": list(set(external))[:20]
        }

    def _extract_social_media(self, parser: BrandHTMLParser) -> Dict[str, str]:
        """Extract social media profile links."""
        social_media = {
            "facebook": None,
            "twitter": None,
            "instagram": None,
            "linkedin": None,
            "youtube": None,
            "tiktok": None
        }

        for href in parser.links:
            href_lower = href.lower()
            for platform in social_media.keys():
                if platform in href_lower and not social_media[platform]:
                    social_media[platform] = href

        return social_media

    def _detect_javascript_heavy(self, parser: BrandHTMLParser, html_content: str) -> bool:
        """Detect if website is JavaScript-heavy (SPA/React/Vue/etc)."""
        # Indicators of JavaScript-heavy sites
        js_indicators = 0

        # Check for minimal content extracted
        if len(parser.text_chunks) < 5:
            js_indicators += 1

        # Check for common SPA frameworks in HTML
        spa_frameworks = ['react', 'vue', 'angular', 'next', 'nuxt', 'gatsby']
        html_lower = html_content.lower()
        for framework in spa_frameworks:
            if framework in html_lower:
                js_indicators += 1
                break

        # Check for root div pattern (common in SPAs)
        if '<div id="root"' in html_content or '<div id="app"' in html_content:
            js_indicators += 1

        # Check for minimal body content
        if len(parser.text_chunks) < 3 and len(parser.headings) < 2:
            js_indicators += 1

        # If multiple indicators present, likely JS-heavy
        return js_indicators >= 2

    async def _scrape_with_browser(self, brand_url: str, initial_html: str, initial_parser: BrandHTMLParser) -> Dict[str, Any]:
        """Scrape JavaScript-heavy site using browser automation."""
        try:
            from app.strategy_engine.data_sources.browser_scraper import BrowserScraper

            browser_scraper = BrowserScraper(timeout=self.timeout, headless=True)
            browser_data = await browser_scraper.scrape_with_browser(brand_url)

            # Parse the browser-rendered HTML
            parser = BrandHTMLParser()
            parser.feed(browser_data['html'])

            # Use browser data + parser extraction
            brand_data = {
                "name": browser_data.get('title', '').split('-')[0].split('|')[0].strip() or self._extract_brand_name(parser, brand_url),
                "url": brand_url,
                "category": self._categorize_brand(parser),
                "description": browser_data['meta_tags'].get('description') or self._extract_description(parser),
                "features": self._extract_features(parser),
                "images": browser_data.get('images', [])[:20],
                "content": browser_data.get('text_content', '')[:5000],
                "metadata": browser_data.get('meta_tags', {}),
                "links": self._categorize_links(browser_data.get('links', []), brand_url),
                "social_media": self._extract_social_media_from_links(browser_data.get('links', [])),
                "javascript_heavy": True,
                "scraper_used": browser_data.get('scraper_used', 'browser')
            }

            self.logger.info(f"Successfully scraped {brand_url} with {browser_data.get('scraper_used')}")
            return brand_data

        except ImportError:
            self.logger.warning("Browser scraper dependencies not available - returning static scrape")
            # Fall back to static scrape
            return {
                "name": self._extract_brand_name(initial_parser, brand_url),
                "url": brand_url,
                "category": "general_utility",
                "description": "JavaScript-heavy site - browser automation not available",
                "features": [],
                "images": [],
                "content": "",
                "metadata": {},
                "links": {"internal": [], "external": []},
                "social_media": {},
                "javascript_heavy": True,
                "scraper_used": "static_fallback"
            }
        except Exception as e:
            self.logger.error(f"Browser scraping failed: {e}")
            raise

    def _categorize_links(self, links: list, base_url: str) -> Dict[str, list]:
        """Categorize links as internal or external."""
        base_domain = urlparse(base_url).netloc
        internal = []
        external = []

        for link in links[:100]:
            if not link or link.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue

            try:
                link_domain = urlparse(link).netloc
                if link_domain == base_domain or not link_domain:
                    internal.append(link)
                else:
                    external.append(link)
            except Exception:
                continue

        return {
            "internal": list(set(internal))[:20],
            "external": list(set(external))[:20]
        }

    def _extract_social_media_from_links(self, links: list) -> Dict[str, Optional[str]]:
        """Extract social media links from list."""
        social_media = {
            "facebook": None,
            "twitter": None,
            "instagram": None,
            "linkedin": None,
            "youtube": None,
            "tiktok": None
        }

        for link in links:
            if not link:
                continue
            link_lower = link.lower()
            for platform in social_media.keys():
                if platform in link_lower and not social_media[platform]:
                    social_media[platform] = link

        return social_media
