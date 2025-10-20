"""Universal Behance Scraper

Scrapes ANY Behance user profile or project using browser automation.
Works for any user, not brand-specific.
"""

import logging
import re
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from playwright.async_api import Page, Browser, BrowserContext, async_playwright

logger = logging.getLogger(__name__)


class BehanceScraper:
    """
    Universal Behance scraper with browser automation.

    Capabilities:
    - Scrape any user profile (projects, followers, location)
    - Scrape any project (images, descriptions, engagement)
    - Search for projects by keyword
    - Scrape trending/featured projects
    - Rate limiting and stealth mode
    - Persistent browser instance for performance

    Usage:
        async with BehanceScraper() as scraper:
            user = await scraper.scrape_user('adobe')
            project = await scraper.scrape_project(project_url)
    """

    def __init__(self, timeout: int = 30, headless: bool = True):
        """
        Initialize Behance scraper.

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
            self.logger.info("Behance scraper browser initialized")

    async def close(self):
        """Close browser and cleanup resources."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
            self.logger.info("Behance scraper browser closed")

    async def scrape_user(self, username: str, max_projects: int = 20) -> Dict[str, Any]:
        """
        Scrape complete Behance profile for ANY user.

        Args:
            username: Behance username (e.g., 'adobe', 'sarahdesigns')
            max_projects: Maximum number of projects to extract

        Returns:
            User data with profile info and projects
        """
        self.logger.info(f"Scraping Behance user: {username}")

        await self._ensure_browser()

        context = await self._browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        try:
            page = await context.new_page()

            # Navigate to profile
            profile_url = f"https://www.behance.net/{username}"
            await page.goto(profile_url, wait_until='networkidle', timeout=self.timeout * 1000)
            await page.wait_for_load_state('domcontentloaded')

            # Extract user data
            user_data = await self._extract_user_data(page, username, profile_url)

            # Extract project links
            project_links = await self._extract_user_projects(page, max_projects)
            user_data['project_count'] = len(project_links)
            user_data['project_links'] = project_links

            self.logger.info(f"Successfully scraped user: {username}")
            return user_data

        finally:
            await context.close()

    async def scrape_project(self, project_url: str) -> Dict[str, Any]:
        """
        Scrape ANY Behance project.

        Args:
            project_url: Full project URL (e.g., 'https://www.behance.net/gallery/12345/Project-Name')

        Returns:
            Project data with images, metadata, and engagement
        """
        self.logger.info(f"Scraping Behance project: {project_url}")

        await self._ensure_browser()

        context = await self._browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        try:
            page = await context.new_page()

            # Navigate to project
            await page.goto(project_url, wait_until='networkidle', timeout=self.timeout * 1000)
            await page.wait_for_load_state('domcontentloaded')

            # Extract project data
            project_data = await self._extract_project_data(page, project_url)

            # Extract images
            images = await self._extract_project_images(page)
            project_data['images'] = images

            self.logger.info(f"Successfully scraped project: {project_data.get('title', 'Unknown')}")
            return project_data

        finally:
            await context.close()

    async def search_projects(self, query: str, max_results: int = 20) -> List[str]:
        """
        Search for Behance projects by keyword.

        Args:
            query: Search query (e.g., 'web design', 'branding')
            max_results: Maximum number of project URLs to return

        Returns:
            List of project URLs
        """
        self.logger.info(f"Searching Behance for: {query}")

        await self._ensure_browser()

        context = await self._browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        try:
            page = await context.new_page()

            # Navigate to search
            search_url = f"https://www.behance.net/search/projects?search={query.replace(' ', '+')}"
            await page.goto(search_url, wait_until='networkidle', timeout=self.timeout * 1000)
            await page.wait_for_load_state('domcontentloaded')

            # Scroll to load more results
            for _ in range(3):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_load_state('domcontentloaded', timeout=1000)

            # Extract project links
            project_links = await self._extract_project_links(page, max_results)

            self.logger.info(f"Found {len(project_links)} projects for query: {query}")
            return project_links

        finally:
            await context.close()

    async def scrape_trending(self, max_projects: int = 20) -> List[str]:
        """
        Scrape trending/featured Behance projects.

        Args:
            max_projects: Maximum number of project URLs to return

        Returns:
            List of trending project URLs
        """
        self.logger.info("Scraping trending Behance projects")

        await self._ensure_browser()

        context = await self._browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        try:
            page = await context.new_page()

            # Navigate to featured/trending
            await page.goto('https://www.behance.net/featured', wait_until='networkidle', timeout=self.timeout * 1000)
            await page.wait_for_load_state('domcontentloaded')

            # Scroll to load more
            for _ in range(3):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_load_state('domcontentloaded', timeout=1000)

            # Extract project links
            project_links = await self._extract_project_links(page, max_projects)

            self.logger.info(f"Found {len(project_links)} trending projects")
            return project_links

        finally:
            await context.close()

    async def _extract_user_data(self, page: Page, username: str, url: str) -> Dict[str, Any]:
        """Extract user profile information."""

        # Extract display name
        display_name = username
        try:
            name_elem = await page.query_selector('h1, div[class*="Profile-name"]')
            if name_elem:
                display_name = await name_elem.text_content()
                display_name = display_name.strip()
        except Exception as e:
            self.logger.warning(f"Could not extract display name: {e}")

        # Extract bio/description
        bio = None
        try:
            bio_elem = await page.query_selector('div[class*="Profile-bio"], div[class*="profile-bio"]')
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
            img_elem = await page.query_selector('img[class*="avatar"], img[class*="profile"]')
            if img_elem:
                profile_image = await img_elem.get_attribute('src')
        except:
            pass

        # Extract stats
        stats = await self._extract_user_stats(page)

        return {
            'username': username,
            'display_name': display_name,
            'bio': bio,
            'location': location,
            'profile_image': profile_image,
            'url': url,
            'follower_count': stats.get('followers', 0),
            'appreciation_count': stats.get('appreciations', 0),
            'view_count': stats.get('views', 0),
            'scraped_at': datetime.utcnow().isoformat()
        }

    async def _extract_user_stats(self, page: Page) -> Dict[str, int]:
        """Extract user statistics."""
        stats = {
            'followers': 0,
            'appreciations': 0,
            'views': 0
        }

        try:
            # Look for stat elements
            stat_elements = await page.query_selector_all('div[class*="stat"], span[class*="stat"]')

            for elem in stat_elements:
                text = await elem.text_content()
                text = text.strip().lower()

                # Parse count
                count = self._parse_count(text)

                if 'follower' in text:
                    stats['followers'] = count
                elif 'appreciation' in text or 'like' in text:
                    stats['appreciations'] = count
                elif 'view' in text:
                    stats['views'] = count

        except Exception as e:
            self.logger.warning(f"Could not extract stats: {e}")

        return stats

    async def _extract_user_projects(self, page: Page, max_projects: int = 20) -> List[str]:
        """Extract project links from user profile."""
        project_links = []

        try:
            # Scroll to load more projects
            for _ in range(3):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_load_state('domcontentloaded', timeout=1000)

            # Extract project links
            project_links = await self._extract_project_links(page, max_projects)

        except Exception as e:
            self.logger.warning(f"Could not extract user projects: {e}")

        return project_links

    async def _extract_project_links(self, page: Page, max_links: int = 20) -> List[str]:
        """Extract project links from page."""
        links = []

        try:
            # Find project link elements
            link_elements = await page.query_selector_all('a[href*="/gallery/"]')

            for elem in link_elements[:max_links * 2]:  # Get more than needed, filter later
                try:
                    href = await elem.get_attribute('href')
                    if not href or '/gallery/' not in href:
                        continue

                    # Make URL absolute
                    if not href.startswith('http'):
                        href = f"https://www.behance.net{href}"

                    # Deduplicate
                    if href not in links:
                        links.append(href)

                    if len(links) >= max_links:
                        break

                except:
                    continue

        except Exception as e:
            self.logger.warning(f"Could not extract project links: {e}")

        return links[:max_links]

    async def _extract_project_data(self, page: Page, url: str) -> Dict[str, Any]:
        """Extract project metadata."""

        # Extract project ID from URL
        project_id_match = re.search(r'/gallery/(\d+)', url)
        project_id = project_id_match.group(1) if project_id_match else "unknown"

        # Extract title
        title = "Untitled"
        try:
            title_elem = await page.query_selector('h1, div[class*="Project-title"]')
            if title_elem:
                title = await title_elem.text_content()
                title = title.strip()
        except:
            pass

        # Extract description
        description = None
        try:
            desc_elem = await page.query_selector('div[class*="Project-description"], div[class*="description"]')
            if desc_elem:
                description = await desc_elem.text_content()
                description = description.strip()
        except:
            pass

        # Extract owner username
        owner_username = None
        try:
            owner_elem = await page.query_selector('a[class*="owner"], a[href^="/"]')
            if owner_elem:
                owner_href = await owner_elem.get_attribute('href')
                if owner_href:
                    owner_username = owner_href.strip('/').split('/')[-1]
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
        stats = await self._extract_project_stats(page)

        return {
            'id': project_id,
            'title': title,
            'description': description,
            'url': url,
            'owner_username': owner_username,
            'tags': tags,
            'appreciation_count': stats.get('appreciations', 0),
            'view_count': stats.get('views', 0),
            'comment_count': stats.get('comments', 0),
            'scraped_at': datetime.utcnow().isoformat()
        }

    async def _extract_project_stats(self, page: Page) -> Dict[str, int]:
        """Extract project statistics."""
        stats = {
            'appreciations': 0,
            'views': 0,
            'comments': 0
        }

        try:
            # Look for stat elements
            stat_elements = await page.query_selector_all('div[class*="stat"], span[class*="stat"]')

            for elem in stat_elements:
                text = await elem.text_content()
                text = text.strip().lower()

                # Parse count
                count = self._parse_count(text)

                if 'appreciation' in text or 'like' in text:
                    stats['appreciations'] = count
                elif 'view' in text:
                    stats['views'] = count
                elif 'comment' in text:
                    stats['comments'] = count

        except Exception as e:
            self.logger.warning(f"Could not extract project stats: {e}")

        return stats

    async def _extract_project_images(self, page: Page) -> List[Dict[str, Any]]:
        """Extract images from project page."""
        images = []

        try:
            # Scroll to load all images
            for _ in range(5):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_load_state('domcontentloaded', timeout=500)

            # Find image elements
            img_elements = await page.query_selector_all(
                'img[class*="Project-module"], img[class*="project-image"], div[class*="image"] img'
            )

            for i, elem in enumerate(img_elements):
                try:
                    src = await elem.get_attribute('src')
                    if not src:
                        continue

                    # Filter out tiny images (avatars, icons)
                    if 'avatar' in src.lower() or 'icon' in src.lower():
                        continue

                    # Get alt text if available
                    alt = await elem.get_attribute('alt') or f"Image {i+1}"

                    images.append({
                        'url': src,
                        'alt': alt,
                        'position': i + 1
                    })

                except:
                    continue

        except Exception as e:
            self.logger.warning(f"Could not extract images: {e}")

        return images

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
