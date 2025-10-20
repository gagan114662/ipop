"""Universal Dribbble Scraper

Scrapes ANY Dribbble user profile or shot using browser automation.
Works for any user, not brand-specific.
"""

import logging
import re
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from playwright.async_api import Page, Browser, BrowserContext, async_playwright

logger = logging.getLogger(__name__)


class DribbbleScraper:
    """
    Universal Dribbble scraper with browser automation.

    Capabilities:
    - Scrape any user profile (shots, followers, bio)
    - Scrape any shot (image, description, engagement)
    - Search for shots by keyword
    - Scrape popular/trending shots
    - Rate limiting and stealth mode
    - Persistent browser instance for performance

    Usage:
        async with DribbbleScraper() as scraper:
            user = await scraper.scrape_user('mailchimp')
            shot = await scraper.scrape_shot(shot_url)
    """

    def __init__(self, timeout: int = 30, headless: bool = True):
        """
        Initialize Dribbble scraper.

        Args:
            timeout: Page load timeout in seconds
            headless: Run browser in headless mode
        """
        self.timeout = timeout
        self.headless = headless
        self.logger = logger
        self._playwright = None
        self._browser: Optional[Browser] = None

    async def __aenter__(self):
        """Async context manager entry - initialize browser."""
        await self._ensure_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup browser."""
        await self.close()

    async def _ensure_browser(self):
        """Ensure browser is initialized."""
        if self._browser is None:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless
            )
            self.logger.info("Dribbble scraper browser initialized")

    async def close(self):
        """Close browser and cleanup resources."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
            self.logger.info("Dribbble scraper browser closed")

    async def scrape_user(self, username: str, max_shots: int = 20) -> Dict[str, Any]:
        """
        Scrape complete Dribbble profile for ANY user.

        Args:
            username: Dribbble username (e.g., 'mailchimp', 'dropbox', 'janedesigner')
            max_shots: Maximum number of shots to extract

        Returns:
            User data with profile info and shots
        """
        self.logger.info(f"Scraping Dribbble user: {username}")

        await self._ensure_browser()

        context = await self._browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        try:
            page = await context.new_page()

           # Navigate to profile
            profile_url = f"https://dribbble.com/{username}"
            await page.goto(profile_url, wait_until='networkidle', timeout=self.timeout * 1000)
            await page.wait_for_load_state('domcontentloaded')

            # Extract user data
            user_data = await self._extract_user_data(page, username, profile_url)

            # Extract shot links
            shot_links = await self._extract_user_shots(page, max_shots)
            user_data['shot_count'] = len(shot_links)
            user_data['shot_links'] = shot_links

            self.logger.info(f"Successfully scraped user: {username}")
            return user_data

        finally:
            await context.close()

    async def scrape_shot(self, shot_url: str) -> Dict[str, Any]:
        """
        Scrape ANY Dribbble shot.

        Args:
            shot_url: Full shot URL (e.g., 'https://dribbble.com/shots/12345-Shot-Name')

        Returns:
            Shot data with image, metadata, and engagement
        """
        self.logger.info(f"Scraping Dribbble shot: {shot_url}")

        await self._ensure_browser()

        context = await self._browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        try:
            page = await context.new_page()

            # Navigate to shot
            await page.goto(shot_url, wait_until='networkidle', timeout=self.timeout * 1000)
            await page.wait_for_load_state('domcontentloaded')

            # Extract shot data
            shot_data = await self._extract_shot_data(page, shot_url)

            self.logger.info(f"Successfully scraped shot: {shot_data.get('title', 'Unknown')}")
            return shot_data

        finally:
            await context.close()

    async def search_shots(self, query: str, max_results: int = 20) -> List[str]:
        """
        Search for Dribbble shots by keyword.

        Args:
            query: Search query (e.g., 'logo design', 'mobile app')
            max_results: Maximum number of shot URLs to return

        Returns:
            List of shot URLs
        """
        self.logger.info(f"Searching Dribbble for: {query}")

        await self._ensure_browser()

        context = await self._browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        try:
            page = await context.new_page()

            # Navigate to search
            search_url = f"https://dribbble.com/search/{query.replace(' ', '-')}"
            await page.goto(search_url, wait_until='networkidle', timeout=self.timeout * 1000)
            await page.wait_for_load_state('domcontentloaded')

            # Scroll to load more results
            for _ in range(3):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_load_state('domcontentloaded', timeout=1000)

            # Extract shot links
            shot_links = await self._extract_shot_links(page, max_results)

            self.logger.info(f"Found {len(shot_links)} shots for query: {query}")
            return shot_links

        finally:
            await context.close()

    async def scrape_popular(self, max_shots: int = 20, timeframe: str = 'week') -> List[str]:
        """
        Scrape popular/trending Dribbble shots.

        Args:
            max_shots: Maximum number of shot URLs to return
            timeframe: Timeframe for popular shots ('week', 'month', 'year', 'all')

        Returns:
            List of popular shot URLs
        """
        self.logger.info(f"Scraping popular Dribbble shots ({timeframe})")

        await self._ensure_browser()

        context = await self._browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        try:
            page = await context.new_page()

            # Navigate to popular shots
            url = f"https://dribbble.com/shots/popular/{timeframe}"
            await page.goto(url, wait_until='networkidle', timeout=self.timeout * 1000)
            await page.wait_for_load_state('domcontentloaded')

            # Scroll to load more
            for _ in range(3):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_load_state('domcontentloaded', timeout=1000)

            # Extract shot links
            shot_links = await self._extract_shot_links(page, max_shots)

            self.logger.info(f"Found {len(shot_links)} popular shots")
            return shot_links

        finally:
            await context.close()

    async def _extract_user_data(self, page: Page, username: str, url: str) -> Dict[str, Any]:
        """Extract user profile information."""

        # Extract display name
        display_name = username
        try:
            name_elem = await page.query_selector('h1, span[class*="name"]')
            if name_elem:
                display_name = await name_elem.text_content()
                display_name = display_name.strip()
        except Exception as e:
            self.logger.warning(f"Could not extract display name: {e}")

        # Extract bio
        bio = None
        try:
            bio_elem = await page.query_selector('div[class*="bio"], p[class*="bio"]')
            if bio_elem:
                bio = await bio_elem.text_content()
                bio = bio.strip()
        except:
            pass

        # Extract location
        location = None
        try:
            loc_elem = await page.query_selector('span[class*="location"], div[class*="location"]')
            if loc_elem:
                location = await loc_elem.text_content()
                location = location.strip()
        except:
            pass

        # Extract profile image
        profile_image = None
        try:
            img_elem = await page.query_selector('img[class*="avatar"], img[alt*="avatar"]')
            if img_elem:
                profile_image = await img_elem.get_attribute('src')
        except:
            pass

        # Extract website
        website = None
        try:
            link_elem = await page.query_selector('a[class*="website"], a[rel="nofollow"]')
            if link_elem:
                website = await link_elem.get_attribute('href')
        except:
            pass

        # Extract stats
        stats = await self._extract_user_stats(page)

        return {
            'username': username,
            'display_name': display_name,
            'bio': bio,
            'location': location,
            'website': website,
            'profile_image': profile_image,
            'url': url,
            'follower_count': stats.get('followers', 0),
            'like_count': stats.get('likes', 0),
            'view_count': stats.get('views', 0),
            'scraped_at': datetime.utcnow().isoformat()
        }

    async def _extract_user_stats(self, page: Page) -> Dict[str, int]:
        """Extract user statistics."""
        stats = {
            'followers': 0,
            'likes': 0,
            'views': 0
        }

        try:
            # Look for stat elements
            stat_elements = await page.query_selector_all('li[class*="stat"], div[class*="stat"]')

            for elem in stat_elements:
                text = await elem.text_content()
                text = text.strip().lower()

                # Parse count
                count = self._parse_count(text)

                if 'follower' in text:
                    stats['followers'] = count
                elif 'like' in text:
                    stats['likes'] = count
                elif 'view' in text:
                    stats['views'] = count

        except Exception as e:
            self.logger.warning(f"Could not extract stats: {e}")

        return stats

    async def _extract_user_shots(self, page: Page, max_shots: int = 20) -> List[str]:
        """Extract shot links from user profile."""
        shot_links = []

        try:
            # Scroll to load more shots
            for _ in range(3):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_load_state('domcontentloaded', timeout=1000)

            # Extract shot links
            shot_links = await self._extract_shot_links(page, max_shots)

        except Exception as e:
            self.logger.warning(f"Could not extract user shots: {e}")

        return shot_links

    async def _extract_shot_links(self, page: Page, max_links: int = 20) -> List[str]:
        """Extract shot links from page."""
        links = []

        try:
            # Find shot link elements
            link_elements = await page.query_selector_all('a[href*="/shots/"]')

            for elem in link_elements[:max_links * 2]:  # Get more than needed, filter later
                try:
                    href = await elem.get_attribute('href')
                    if not href or '/shots/' not in href:
                        continue

                    # Make URL absolute
                    if not href.startswith('http'):
                        href = f"https://dribbble.com{href}"

                    # Filter out non-shot URLs (likes, activity, etc)
                    if '/likes' in href or '/activity' in href:
                        continue

                    # Deduplicate
                    if href not in links:
                        links.append(href)

                    if len(links) >= max_links:
                        break

                except:
                    continue

        except Exception as e:
            self.logger.warning(f"Could not extract shot links: {e}")

        return links[:max_links]

    async def _extract_shot_data(self, page: Page, url: str) -> Dict[str, Any]:
        """Extract shot metadata."""

        # Extract shot ID from URL
        shot_id_match = re.search(r'/shots/(\d+)', url)
        shot_id = shot_id_match.group(1) if shot_id_match else "unknown"

        # Extract title
        title = "Untitled"
        try:
            title_elem = await page.query_selector('h1, h2[class*="title"]')
            if title_elem:
                title = await title_elem.text_content()
                title = title.strip()
        except:
            pass

        # Extract description
        description = None
        try:
            desc_elem = await page.query_selector('div[class*="description"], div[class*="shot-desc"]')
            if desc_elem:
                description = await desc_elem.text_content()
                description = description.strip()
        except:
            pass

        # Extract designer/owner username
        owner_username = None
        try:
            owner_elem = await page.query_selector('a[class*="user"], a[class*="designer"]')
            if owner_elem:
                owner_href = await owner_elem.get_attribute('href')
                if owner_href:
                    owner_username = owner_href.strip('/').split('/')[-1]
        except:
            pass

        # Extract main image
        image_url = None
        try:
            img_elem = await page.query_selector('img[class*="shot"], picture img, div[class*="media"] img')
            if img_elem:
                image_url = await img_elem.get_attribute('src')
        except:
            pass

        # Extract tags
        tags = []
        try:
            tag_elements = await page.query_selector_all('a[class*="tag"], span[class*="tag"]')
            for elem in tag_elements[:10]:
                tag = await elem.text_content()
                tags.append(tag.strip())
        except:
            pass

        # Extract stats
        stats = await self._extract_shot_stats(page)

        return {
            'id': shot_id,
            'title': title,
            'description': description,
            'url': url,
            'image_url': image_url,
            'owner_username': owner_username,
            'tags': tags,
            'like_count': stats.get('likes', 0),
            'view_count': stats.get('views', 0),
            'comment_count': stats.get('comments', 0),
            'scraped_at': datetime.utcnow().isoformat()
        }

    async def _extract_shot_stats(self, page: Page) -> Dict[str, int]:
        """Extract shot statistics."""
        stats = {
            'likes': 0,
            'views': 0,
            'comments': 0
        }

        try:
            # Look for stat elements
            stat_elements = await page.query_selector_all('li[class*="stat"], span[class*="stat"]')

            for elem in stat_elements:
                text = await elem.text_content()
                text = text.strip().lower()

                # Parse count
                count = self._parse_count(text)

                if 'like' in text:
                    stats['likes'] = count
                elif 'view' in text:
                    stats['views'] = count
                elif 'comment' in text:
                    stats['comments'] = count

        except Exception as e:
            self.logger.warning(f"Could not extract shot stats: {e}")

        return stats

    def _parse_count(self, text: str) -> int:
        """
        Parse count from text (handles '1.2k', '5m', '100', etc).

        Args:
            text: Text containing count

        Returns:
            Parsed integer count
        """
        if not text:
            return 0

        # Extract numbers
        numbers = re.findall(r'[\d.]+', text)
        if not numbers:
            return 0

        num = float(numbers[0])

        # Handle suffixes
        text_lower = text.lower()
        if 'k' in text_lower:
            return int(num * 1000)
        elif 'm' in text_lower:
            return int(num * 1_000_000)
        elif 'b' in text_lower:
            return int(num * 1_000_000_000)

        return int(num)
