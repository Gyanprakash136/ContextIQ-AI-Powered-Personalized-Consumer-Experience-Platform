import asyncio
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
from crawlee.browsers import BrowserPool

async def scrape_with_crawlee(url: str) -> str:
    """
    Scrapes a single URL using Crawlee + Playwright.
    Returns the cleaned text content.
    """
    result = {"text": ""}

    crawler = PlaywrightCrawler(
        # Limit to 1 request since we just want this one page
        max_requests_per_crawl=1,
        headless=True,
    )

    @crawler.router.default_handler
    async def request_handler(context: PlaywrightCrawlerContext):
        # Wait for body to be visible
        await context.page.wait_for_selector("body")
        
        # Simple text extraction
        # You might want to enhance this with specific selectors for Amazon/Flipkart
        # e.g. await context.page.content() and use BS4, or use page.inner_text()
        
        # Let's use inner_text for simplicity and JS rendering
        text = await context.page.inner_text("body")
        result["text"] = text

    await crawler.run([url])
    return result["text"]

def scrape_url_dynamic(url: str) -> str:
    """
    Synchronous wrapper for the async crawler.
    """
    try:
        return asyncio.run(scrape_with_crawlee(url))
    except Exception as e:
        return f"Error scraping with Crawlee: {e}"
