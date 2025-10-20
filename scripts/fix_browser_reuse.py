#!/usr/bin/env python3
"""Fix browser instance reuse in Behance and Dribbble scrapers."""

import re

def fix_scraper_method(content: str) -> str:
    """Replace browser launch pattern with persistent browser usage."""

    # Pattern to match the async with async_playwright() block
    pattern = r'''        async with async_playwright\(\) as p:
            browser = await p\.chromium\.launch\(
                headless=self\.headless,
                args=\['--no-sandbox', '--disable-setuid-sandbox'\]
            \)

            try:
                context = await browser\.new_context\(
                    user_agent='Mozilla/5\.0 \(Macintosh; Intel Mac OS X 10_15_7\) AppleWebKit/537\.36',
                    viewport=\{'width': 1920, 'height': 1080\}
                \)
                page = await context\.new_page\(\)'''

    replacement = '''        await self._ensure_browser()

        context = await self._browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        try:
            page = await context.new_page()'''

    content = re.sub(pattern, replacement, content)

    # Replace browser.close() with context.close()
    content = content.replace('await browser.close()', 'await context.close()')

    return content


def main():
    """Fix both Behance and Dribbble scrapers."""

    scrapers = [
        'app/strategy_engine/data_sources/behance_scraper.py',
        'app/strategy_engine/data_sources/dribbble_scraper.py'
    ]

    for file_path in scrapers:
        print(f"Processing {file_path}...")

        with open(file_path, 'r') as f:
            content = f.read()

        fixed_content = fix_scraper_method(content)

        with open(file_path, 'w') as f:
            f.write(fixed_content)

        print(f"✓ Fixed {file_path}")


if __name__ == '__main__':
    main()
