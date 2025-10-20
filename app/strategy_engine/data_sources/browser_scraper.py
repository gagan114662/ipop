"""Browser-Based Web Scraper

Handles JavaScript-heavy websites using browser automation.
Falls back through multiple strategies: Playwright -> Selenium -> Pyppeteer -> Static
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class BrowserType(Enum):
    """Available browser automation tools."""
    PLAYWRIGHT = "playwright"
    SELENIUM = "selenium"
    PYPPETEER = "pyppeteer"
    STATIC = "static"


class BrowserScraper:
    """
    Universal browser scraper with fallback strategies.

    Tries in order:
    1. Playwright (fastest, most modern)
    2. Selenium (most compatible)
    3. Pyppeteer (Puppeteer for Python)
    4. Static HTML (fallback for simple sites)
    """

    def __init__(self, timeout: int = 30, headless: bool = True):
        """
        Initialize browser scraper.

        Args:
            timeout: Page load timeout in seconds
            headless: Run browser in headless mode
        """
        self.timeout = timeout
        self.headless = headless
        self.logger = logger

    async def scrape_with_browser(self, url: str, preferred_browser: Optional[BrowserType] = None) -> Dict[str, Any]:
        """
        Scrape website using browser automation.

        Args:
            url: Website URL
            preferred_browser: Preferred browser type (or auto-detect)

        Returns:
            Scraped data dictionary
        """
        self.logger.info(f"Starting browser scrape for: {url}")

        # If no preference, try all in order
        if preferred_browser:
            browsers_to_try = [preferred_browser]
        else:
            browsers_to_try = [
                BrowserType.PLAYWRIGHT,
                BrowserType.SELENIUM,
                BrowserType.PYPPETEER
            ]

        last_error = None

        for browser_type in browsers_to_try:
            try:
                self.logger.info(f"Attempting scrape with {browser_type.value}")

                if browser_type == BrowserType.PLAYWRIGHT:
                    return await self._scrape_with_playwright(url)
                elif browser_type == BrowserType.SELENIUM:
                    return await self._scrape_with_selenium(url)
                elif browser_type == BrowserType.PYPPETEER:
                    return await self._scrape_with_pyppeteer(url)

            except ImportError as e:
                self.logger.warning(f"{browser_type.value} not available: {e}")
                last_error = f"{browser_type.value} not installed"
                continue
            except Exception as e:
                self.logger.warning(f"{browser_type.value} failed: {e}")
                last_error = str(e)
                continue

        raise Exception(f"All browser methods failed. Last error: {last_error}")

    async def _scrape_with_playwright(self, url: str) -> Dict[str, Any]:
        """Scrape using Playwright (preferred - fastest and most reliable)."""
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            # Try Chromium first, fallback to Firefox, then WebKit
            for browser_name in ['chromium', 'firefox', 'webkit']:
                try:
                    browser = await getattr(p, browser_name).launch(headless=self.headless)
                    break
                except Exception as e:
                    self.logger.warning(f"Playwright {browser_name} failed: {e}")
                    if browser_name == 'webkit':
                        raise Exception("All Playwright browsers failed")
                    continue

            try:
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                page = await context.new_page()

                # Navigate and wait for network idle
                await page.goto(url, wait_until='networkidle', timeout=self.timeout * 1000)

                # Wait a bit for any lazy-loaded content
                await page.wait_for_timeout(2000)

                # Extract data
                html_content = await page.content()
                title = await page.title()

                # Extract all text
                text_content = await page.evaluate('() => document.body.innerText')

                # Extract images
                images = await page.evaluate('''() => {
                    return Array.from(document.images).map(img => img.src);
                }''')

                # Extract links
                links = await page.evaluate('''() => {
                    return Array.from(document.links).map(a => a.href);
                }''')

                # Extract meta tags
                meta_tags = await page.evaluate('''() => {
                    const metas = {};
                    document.querySelectorAll('meta').forEach(meta => {
                        const name = meta.getAttribute('name') || meta.getAttribute('property');
                        const content = meta.getAttribute('content');
                        if (name && content) metas[name] = content;
                    });
                    return metas;
                }''')

                await browser.close()

                return {
                    'html': html_content,
                    'title': title,
                    'text_content': text_content,
                    'images': images,
                    'links': links,
                    'meta_tags': meta_tags,
                    'scraper_used': 'playwright'
                }

            finally:
                await browser.close()

    async def _scrape_with_selenium(self, url: str) -> Dict[str, Any]:
        """Scrape using Selenium (fallback)."""
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from webdriver_manager.chrome import ChromeDriverManager
        import time

        # Run in thread pool since Selenium is synchronous
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._scrape_with_selenium_sync, url)

    def _scrape_with_selenium_sync(self, url: str) -> Dict[str, Any]:
        """Synchronous Selenium scrape."""
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from webdriver_manager.chrome import ChromeDriverManager
        import time

        options = Options()
        if self.headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

        # Use webdriver-manager to auto-install chromedriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        try:
            driver.set_page_load_timeout(self.timeout)
            driver.get(url)

            # Wait for JavaScript to execute
            time.sleep(3)

            # Extract data
            html_content = driver.page_source
            title = driver.title

            # Extract text
            text_content = driver.find_element(By.TAG_NAME, 'body').text

            # Extract images
            images = [img.get_attribute('src') for img in driver.find_elements(By.TAG_NAME, 'img')]

            # Extract links
            links = [a.get_attribute('href') for a in driver.find_elements(By.TAG_NAME, 'a')]

            # Extract meta tags
            meta_elements = driver.find_elements(By.TAG_NAME, 'meta')
            meta_tags = {}
            for meta in meta_elements:
                name = meta.get_attribute('name') or meta.get_attribute('property')
                content = meta.get_attribute('content')
                if name and content:
                    meta_tags[name] = content

            return {
                'html': html_content,
                'title': title,
                'text_content': text_content,
                'images': images,
                'links': links,
                'meta_tags': meta_tags,
                'scraper_used': 'selenium'
            }

        finally:
            driver.quit()

    async def _scrape_with_pyppeteer(self, url: str) -> Dict[str, Any]:
        """Scrape using Pyppeteer (Puppeteer for Python)."""
        from pyppeteer import launch

        browser = await launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )

        try:
            page = await browser.newPage()
            await page.setViewport({'width': 1920, 'height': 1080})
            await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

            await page.goto(url, {'waitUntil': 'networkidle0', 'timeout': self.timeout * 1000})

            # Wait for content
            await asyncio.sleep(2)

            # Extract data
            html_content = await page.content()
            title = await page.title()

            # Extract text
            text_content = await page.evaluate('() => document.body.innerText')

            # Extract images
            images = await page.evaluate('() => Array.from(document.images).map(img => img.src)')

            # Extract links
            links = await page.evaluate('() => Array.from(document.links).map(a => a.href)')

            # Extract meta tags
            meta_tags = await page.evaluate('''() => {
                const metas = {};
                document.querySelectorAll('meta').forEach(meta => {
                    const name = meta.getAttribute('name') || meta.getAttribute('property');
                    const content = meta.getAttribute('content');
                    if (name && content) metas[name] = content;
                });
                return metas;
            }''')

            return {
                'html': html_content,
                'title': title,
                'text_content': text_content,
                'images': images,
                'links': links,
                'meta_tags': meta_tags,
                'scraper_used': 'pyppeteer'
            }

        finally:
            await browser.close()
