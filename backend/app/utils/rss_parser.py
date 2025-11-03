import feedparser
import aiohttp
from typing import List, Dict, Any
import asyncio

async def parse_rss_feed(url: str) -> List[Dict[str, Any]]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.text()
                feed = feedparser.parse(content)
                articles = []
                for entry in feed.entries[:20]:  # Limit to 20 recent articles
                    articles.append({
                        "title": entry.title,
                        "link": entry.link,
                        "published": entry.published if hasattr(entry, 'published') else "",
                        "summary": entry.summary if hasattr(entry, 'summary') else "",
                        "source": feed.feed.title if hasattr(feed.feed, 'title') else url,
                    })
                return articles
            else:
                raise Exception(f"Failed to fetch RSS feed from {url}")

async def get_financial_news() -> List[Dict[str, Any]]:
    rss_urls = [
        "https://feeds.finance.yahoo.com/rss/2.0/headline?s=yhoo&region=US&lang=en-US",
        "https://www.investing.com/rss/news.rss",
        # Add more financial RSS feeds as needed
    ]

    all_articles = []
    for url in rss_urls:
        try:
            articles = await parse_rss_feed(url)
            all_articles.extend(articles)
        except Exception as e:
            print(f"Error parsing RSS feed {url}: {e}")

    return all_articles
