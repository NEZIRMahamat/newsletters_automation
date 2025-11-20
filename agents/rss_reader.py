import feedparser
import requests
from datetime import datetime, timedelta

class RSSReader:
    def __init__(self):
        self.feeds = [
            'https://openai.com/blog/rss.xml',
            'https://blog.google/technology/ai/rss/',
            'https://aws.amazon.com/blogs/machine-learning/feed/',
            'https://cloud.google.com/blog/topics/developers-practitioners/feeds/rss',
            'https://blogs.nvidia.com/blog/category/artificial-intelligence/feed/',
            'https://techcrunch.com/feed/',
            'https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml',
            'https://feeds.arstechnica.com/arstechnica/index'
            # Ajoutez d'autres flux RSS sur l'IA
        ]
    
    def fetch_articles(self, days=7):
        """Récupère les articles des 7 derniers jours"""
        articles = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for feed_url in self.feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    published = self._parse_date(entry.get('published', ''))
                    if published and published >= cutoff_date:
                        articles.append({
                            'title': entry.title,
                            'link': entry.link,
                            'summary': entry.summary,
                            'published': published,
                            'source': feed_url
                        })
            except Exception as e:
                print(f"Erreur avec le flux {feed_url}: {e}")
        
        return articles
    
    def _parse_date(self, date_str):
        """Parse les différentes formats de date"""
        try:
            return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
        except:
            return datetime.now()