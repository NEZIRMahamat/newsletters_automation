from agents.rss_reader import RSSReader

def test_rss_reader():
    print("🧪 Test du RSS Reader...")
    
    # Créer une instance
    reader = RSSReader()
    
    # Tester la récupération des articles
    articles = reader.fetch_articles(days=7)
    
    # Afficher les résultats
    print(f"📰 {len(articles)} articles trouvés")
    print("\n" + "="*50)
    
    for i, article in enumerate(articles[:5], 1):  # Afficher seulement les 5 premiers
        print(f"{i}. {article['title']}")
        print(f"   📅 Date: {article['published']}")
        print(f"   🔗 Source: {article['source']}")
        print(f"   📝 Résumé: {article['summary'][:100]}...")
        print("-" * 50)

if __name__ == "__main__":
    test_rss_reader()