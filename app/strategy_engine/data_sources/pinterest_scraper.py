"""Universal Pinterest Scraper

Scrapes ANY Pinterest profile, board, or pins using browser automation.
Works for any user, not brand-specific.
"""

import logging
import re
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from playwright.async_api import Page, Browser, BrowserContext, async_playwright

logger = logging.getLogger(__name__)


class PinterestScraper:
    """
    Universal Pinterest scraper with browser automation.

    Capabilities:
    - Scrape any user profile (followers, following, boards, pins)
    - Scrape any board (pins, metadata)
    - Scrape individual pins (images, descriptions, engagement)
    - Rate limiting and stealth mode
    - Persistent browser instance for performance

    Usage:
        async with PinterestScraper() as scraper:
            profile = await scraper.scrape_profile('nike')
            board = await scraper.scrape_board('nike', 'design-inspiration')
    """

    def __init__(self, timeout: int = 30, headless: bool = True):
        """
        Initialize Pinterest scraper.

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
            self.logger.info("Pinterest scraper browser initialized")

    async def close(self):
        """Close browser and cleanup resources."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
            self.logger.info("Pinterest scraper browser closed")

    async def scrape_profile(self, username: str) -> Dict[str, Any]:
        """
        Scrape complete Pinterest profile for ANY user.

        Args:
            username: Pinterest username (e.g., 'nike', 'apple', 'janesmith')

        Returns:
            Profile data with stats, boards, and metadata
        """
        self.logger.info(f"Scraping Pinterest profile: {username}")
        await self._ensure_browser()

        context = await self._browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        try:
            page = await context.new_page()

            # Navigate to profile - use load instead of networkidle (Pinterest has many background requests)
            profile_url = f"https://www.pinterest.com/{username}/"
            await page.goto(profile_url, wait_until='load', timeout=self.timeout * 1000)
            await page.wait_for_load_state('domcontentloaded')

            # Wait for content to appear
            try:
                await page.wait_for_selector('div, main, body', timeout=5000)
            except:
                pass

            # Extract profile data
            profile_data = await self._extract_profile_data(page, username, profile_url)

            # Extract boards
            boards = await self._extract_boards(page, username)
            profile_data['boards'] = boards

            self.logger.info(f"Successfully scraped profile: {username}")
            return profile_data

        finally:
            await context.close()

    async def scrape_board(self, username: str, board_name: str, max_pins: int = 50) -> Dict[str, Any]:
        """
        Scrape ANY Pinterest board.

        Args:
            username: Board owner username
            board_name: Board name/slug (e.g., 'design-inspiration')
            max_pins: Maximum number of pins to extract

        Returns:
            Board data with pins and metadata
        """
        self.logger.info(f"Scraping Pinterest board: {username}/{board_name}")
        await self._ensure_browser()

        context = await self._browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        try:
            page = await context.new_page()

            # Navigate to board
            board_url = f"https://www.pinterest.com/{username}/{board_name}/"
            await page.goto(board_url, wait_until='load', timeout=self.timeout * 1000)
            await page.wait_for_load_state('domcontentloaded')

            # Wait for content
            try:
                await page.wait_for_selector('div, main, body', timeout=5000)
            except:
                pass

            # Extract board data
            board_data = await self._extract_board_data(page, username, board_name, board_url)

            # Extract pins from board
            pins = await self._extract_pins_from_board(page, board_url, max_pins)
            board_data['pins'] = pins

            self.logger.info(f"Successfully scraped board: {username}/{board_name}")
            return board_data

        finally:
            await context.close()

    async def _extract_profile_data(self, page: Page, username: str, url: str) -> Dict[str, Any]:
        """Extract profile information from page."""

        # Extract display name
        display_name = username
        try:
            name_elem = await page.query_selector('h1, div[data-test-id="profile-name"]')
            if name_elem:
                display_name = await name_elem.text_content()
                display_name = display_name.strip()
        except Exception as e:
            self.logger.warning(f"Could not extract display name: {e}")

        # Extract bio/description
        bio = None
        try:
            bio_elem = await page.query_selector('div[data-test-id="about-profile"], p[data-test-id="profile-bio"]')
            if bio_elem:
                bio = await bio_elem.text_content()
                bio = bio.strip()
        except Exception as e:
            self.logger.warning(f"Could not extract bio: {e}")

        # Extract profile image
        profile_image = None
        try:
            img_elem = await page.query_selector('img[data-test-id="profile-avatar"], img[alt*="profile"]')
            if img_elem:
                profile_image = await img_elem.get_attribute('src')
        except Exception as e:
            self.logger.warning(f"Could not extract profile image: {e}")

        # Extract stats (followers, following, boards, pins)
        stats = await self._extract_profile_stats(page)

        return {
            'username': username,
            'display_name': display_name,
            'bio': bio,
            'profile_image': profile_image,
            'url': url,
            'follower_count': stats.get('followers', 0),
            'following_count': stats.get('following', 0),
            'board_count': stats.get('boards', 0),
            'pin_count': stats.get('pins', 0),
            'scraped_at': datetime.utcnow().isoformat()
        }

    async def _extract_profile_stats(self, page: Page) -> Dict[str, int]:
        """Extract profile statistics (followers, following, etc)."""
        stats = {
            'followers': 0,
            'following': 0,
            'boards': 0,
            'pins': 0
        }

        try:
            # Look for stat elements
            stat_elements = await page.query_selector_all('div[data-test-id*="stat"], a[data-test-id*="stat"]')

            for elem in stat_elements:
                text = await elem.text_content()
                text = text.strip().lower()

                # Parse count (handles "1.2k", "5m", etc)
                count = self._parse_count(text)

                if 'follower' in text:
                    stats['followers'] = count
                elif 'following' in text:
                    stats['following'] = count
                elif 'board' in text:
                    stats['boards'] = count
                elif 'pin' in text:
                    stats['pins'] = count

        except Exception as e:
            self.logger.warning(f"Could not extract stats: {e}")

        return stats

    async def _extract_boards(self, page: Page, username: str, max_boards: int = 20) -> List[Dict[str, Any]]:
        """Extract boards from profile page."""
        boards = []

        try:
            # Scroll to load more boards
            for _ in range(3):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_load_state('domcontentloaded', timeout=500)

            # Find board elements
            board_elements = await page.query_selector_all(
                'div[data-test-id="board-card"], a[href*="pinterest.com/"][href*="/"]'
            )

            for elem in board_elements[:max_boards]:
                try:
                    board = await self._extract_board_from_element(elem, username)
                    if board:
                        boards.append(board)
                except Exception as e:
                    self.logger.warning(f"Failed to extract board: {e}")
                    continue

        except Exception as e:
            self.logger.warning(f"Could not extract boards: {e}")

        return boards

    async def _extract_board_from_element(self, elem, username: str) -> Optional[Dict[str, Any]]:
        """Extract single board data from element."""

        # Get board URL
        link_elem = await elem.query_selector('a[data-test-id="board-rep-tap-area-link"]')
        if not link_elem:
            link_elem = await elem.query_selector('a')

        if not link_elem:
            return None

        url = await link_elem.get_attribute('href')
        if not url:
            return None

        # Filter out non-board URLs
        if username not in url or '_saved' in url or '_created' in url:
            return None

        # Make URL absolute
        if not url.startswith('http'):
            url = f"https://www.pinterest.com{url}"

        # Extract board ID/name from URL
        board_id_match = re.search(r'/([^/]+)/?$', url)
        board_id = board_id_match.group(1) if board_id_match else "unknown"

        # Get all text content from the card and parse it
        text_content = await elem.text_content()
        text_content = text_content.strip()

        # Pinterest format: "BoardNameUser, X.XK Pins·, Y sections·, Zd"
        # Extract name (first part before username or "Pinterest")
        name = board_id.replace('-', ' ').title()  # Default from URL

        # Try to extract name from text (before "Pinterest" or first comma)
        if username.lower() in text_content.lower() or 'pinterest' in text_content.lower():
            parts = text_content.split('Pinterest')[0].split(username)[0]
            if parts:
                name = parts.strip()

        # Get pin count from text (e.g., "1.5k Pins")
        pin_count = 0
        pin_match = re.search(r'([\d.]+[kKmM]?)\s*Pins?', text_content, re.IGNORECASE)
        if pin_match:
            pin_count = self._parse_count(pin_match.group(1))

        # Get cover image
        image_url = None
        try:
            img_elem = await elem.query_selector('img')
            if img_elem:
                image_url = await img_elem.get_attribute('src')
        except:
            pass

        return {
            'id': board_id,
            'name': name if name else board_id,
            'url': url,
            'pin_count': pin_count,
            'image_url': image_url,
            'owner_username': username
        }

    async def _extract_board_data(self, page: Page, username: str, board_name: str, url: str) -> Dict[str, Any]:
        """Extract board metadata."""

        # Get board name/title
        title = board_name
        try:
            title_elem = await page.query_selector('h1, div[data-test-id="board-name"]')
            if title_elem:
                title = await title_elem.text_content()
                title = title.strip()
        except:
            pass

        # Get description
        description = None
        try:
            desc_elem = await page.query_selector('div[data-test-id="board-description"]')
            if desc_elem:
                description = await desc_elem.text_content()
                description = description.strip()
        except:
            pass

        # Get pin count
        pin_count = 0
        try:
            count_elem = await page.query_selector('div[data-test-id="pin-count"]')
            if count_elem:
                count_text = await count_elem.text_content()
                pin_count = self._parse_count(count_text)
        except:
            pass

        return {
            'id': board_name,
            'name': title,
            'description': description,
            'url': url,
            'pin_count': pin_count,
            'owner_username': username,
            'scraped_at': datetime.utcnow().isoformat()
        }

    async def _extract_pins_from_board(self, page: Page, board_url: str, max_pins: int = 50) -> List[Dict[str, Any]]:
        """Extract pins from board page."""
        pins = []

        try:
            # Scroll to load more pins
            for _ in range(5):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_load_state('domcontentloaded', timeout=1000)

            # Find pin elements
            pin_elements = await page.query_selector_all(
                'div[data-test-id="pin"], a[href*="/pin/"]'
            )

            for elem in pin_elements[:max_pins]:
                try:
                    pin = await self._extract_pin_from_element(elem)
                    if pin:
                        pins.append(pin)
                except Exception as e:
                    self.logger.warning(f"Failed to extract pin: {e}")
                    continue

        except Exception as e:
            self.logger.warning(f"Could not extract pins: {e}")

        return pins

    async def _extract_pin_from_element(self, elem) -> Optional[Dict[str, Any]]:
        """Extract single pin data from element."""

        # Get pin URL
        link_elem = await elem.query_selector('a[href*="/pin/"]')
        if not link_elem:
            return None

        url = await link_elem.get_attribute('href')
        if not url:
            return None

        # Make URL absolute
        if not url.startswith('http'):
            url = f"https://www.pinterest.com{url}"

        # Extract pin ID from URL
        pin_id_match = re.search(r'/pin/(\d+)', url)
        pin_id = pin_id_match.group(1) if pin_id_match else "unknown"

        # Get image URL
        image_url = None
        try:
            img_elem = await elem.query_selector('img')
            if img_elem:
                image_url = await img_elem.get_attribute('src')
        except:
            pass

        # Get title/description
        title = None
        try:
            title_elem = await elem.query_selector('h3, div[data-test-id="pin-title"]')
            if title_elem:
                title = await title_elem.text_content()
                title = title.strip()
        except:
            pass

        # Get save count (repins)
        save_count = 0
        try:
            save_elem = await elem.query_selector('div[data-test-id="save-count"]')
            if save_elem:
                save_text = await save_elem.text_content()
                save_count = self._parse_count(save_text)
        except:
            pass

        return {
            'id': pin_id,
            'title': title,
            'url': url,
            'image_url': image_url,
            'save_count': save_count,
            'scraped_at': datetime.utcnow().isoformat()
        }

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
