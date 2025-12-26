import feedparser
from typing import List, Dict
import structlog

logger = structlog.get_logger()

# --------------------------------------------------
# Configuration
# --------------------------------------------------

RSS_FEEDS = [
    "https://feeds.bloomberg.com/markets/news.rss",
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "https://feeds.finance.yahoo.com/rss/2.0/headline",
    "https://www.nasdaq.com/feed/rssoutbound?category=Stocks",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (TradingCopilot/1.0)"
}

MAX_ARTICLES_PER_FEED = 10


# --------------------------------------------------
# RSS Parser (SAFE & SYNC)
# --------------------------------------------------

def get_financial_news() -> List[Dict]:
    """
    Fetch and parse financial news RSS feeds.

    Always returns a list.
    Never crashes.
    """

    all_articles: List[Dict] = []

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(
                feed_url,
                request_headers=HEADERS
            )

            # Guard: invalid or empty feed
            if not feed or not getattr(feed, "entries", None):
                logger.warning("⚠ Empty or invalid RSS feed", url=feed_url)
                continue

            feed_name = feed.feed.get("title", feed_url)

            for entry in feed.entries[:MAX_ARTICLES_PER_FEED]:
                article = {
                    "title": entry.get("title", "").strip(),
                    "summary": entry.get(
                        "summary",
                        entry.get("description", "")
                    ).strip(),
                    "link": entry.get("link", ""),
                    "published": entry.get(
                        "published",
                        entry.get("pubDate", "")
                    ),
                    "source": feed_name
                }

                # Skip completely empty articles
                if not article["title"] and not article["summary"]:
                    continue

                all_articles.append(article)

            logger.info(
                "✅ RSS parsed",
                feed=feed_name,
                count=len(feed.entries)
            )

        except Exception as e:
            # NEVER crash the backend
            logger.error(
                "❌ RSS parsing failed",
                url=feed_url,
                error=str(e)
            )
            continue

    return all_articles


# --------------------------------------------------
# Optional Test Helper
# --------------------------------------------------

def _test_rss_parser():
    articles = get_financial_news()
    print(f"\n📊 RSS Test Result: {len(articles)} articles\n")

    if articles:
        sample = articles[0]
        print("Sample article:")
        for k, v in sample.items():
            print(f"{k}: {str(v)[:80]}")


if __name__ == "__main__":
    _test_rss_parser()
