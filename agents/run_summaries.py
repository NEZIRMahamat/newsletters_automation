from llm_processor import LLMProcessor
from rss_reader import RSSReader
from dotenv import load_dotenv
load_dotenv()
# Initialisation
rss_reader = RSSReader()
articles = rss_reader.fetch_articles(days=3)

processor = LLMProcessor()

# Boucle sur les articles
for article in articles:
    print(f"Article: {article['title']}")
    summary = processor.summarize_article(article)
    print(summary)
    topic = processor.classify_topic(article)
    print(f"Topic: {topic}\n")
