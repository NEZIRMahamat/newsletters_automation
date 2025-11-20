import os
from dotenv import load_dotenv
from rss_reader import RSSReader
from llm_processor import LLMProcessor

# Load environment variables
load_dotenv()

# Main execution
def main():
    # Step 1: Fetch articles
    print("📡 Fetching AI articles from RSS feeds...")
    rss_reader = RSSReader()
    articles = rss_reader.fetch_articles(days=7)
    print(f"✅ Found {len(articles)} articles")
    
    # Step 2: Process with LLM
    print("🤖 Processing articles with Groq...")
    llm_processor = LLMProcessor()
    
    # Process each article
    for i, article in enumerate(articles[:5]):  # Limit to 5 for demo
        print(f"\n--- Article {i+1} ---")
        print(f"Title: {article['title']}")
        print(f"Source: {article['source']}")
        
        # Get summary
        summary = llm_processor.summarize_article(article)
        print(f"Summary:\n{summary}")
        
        # Get classification
        topic = llm_processor.classify_topic(article)
        print(f"Topic: {topic}")
        
        print("-" * 50)

if __name__ == "__main__":
    main()