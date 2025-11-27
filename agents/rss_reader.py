# *-- coding: utf-8 --*

from feedparser import parse
from bs4 import BeautifulSoup
import requests
import html
import json
from feedparser import FeedParserDict
from typing import List, Optional, Dict
from datetime import datetime


"""
Outils pour analyser les flux RSS et extraire les articles.


"""

def load_rss_feed(url: str) -> Optional[FeedParserDict]:
    """
    Retourne l'objet feedparser pour le flux RSS donné.
    """
    try:
        feed = parse(url)
        return feed
    except Exception as e:
        print(f"Erreur lors de la récupération du flux RSS: {e}")
        return None

def get_content_from_entry_link(link: str) -> Optional[str]:
    """
    Récupère le contenu complet (à defaut le résumé pour certains flux, car
    certains sites ne fournissent pas le contenu complet dans le flux RSS) d'un article à partir de son lien.
    """
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        content = soup.get_text().strip()
        return content
    except Exception as e:
        print(f"Erreur lors de la récupération du contenu depuis le lien: {e}")
        return None
    
def parse_rss_entry(entry: dict) -> Optional[Dict[str, any]]:
    """
    Extrait les informations d'un article d'une entrée RSS.
    """
    try:
        title = entry.title
        link = entry.link
        published = entry.get('published', None) or entry.get('date', None)
        updated = entry.get('updated', None)
        created = entry.get('created', None)
        
        # Récupération des auteurs depuis plusieurs sources possibles
        authors = []
        if hasattr(entry, 'authors') and entry.authors:
            # arXiv et certains flux (liste d'objets)
            authors = [author.get('name', author) if isinstance(author, dict) else str(author) 
                      for author in entry.authors]
        elif hasattr(entry, 'author') and entry.author:
            # Le Monde et beaucoup d'autres flux (string unique)
            authors = [entry.author]
        elif entry.get('dc_creator'):
            # Dublin Core creator tag
            authors = [entry.dc_creator] if isinstance(entry.dc_creator, str) else entry.dc_creator
        
        summary = entry.get('summary', None)
        content = get_content_from_entry_link(link)
        result = {
            "title": title,
            "link": link,
            "dates": [{
                "published": published,
                "updated": updated,
                "created": created
            }],
            "authors": authors,
            "summary": summary,
            "content": content
        }
        return result
    except Exception as e:
        print(f"Erreur lors de l'analyse de l'article du flux RSS: {e}")
        return None
    
def fetch_all_rss_entries(url: str) -> List[Dict[str, any]]:
    """
    Récupère et analyse toutes les entrées d'un flux RSS.
    Retourne une liste de dictionnaires avec les informations extraites. (JSON serializable)
    """
    feed = load_rss_feed(url)
    if not feed:
        return []
    entries_data = []
    for entry in feed.entries:
        parsed_entry = parse_rss_entry(entry)
        if parsed_entry:
            entries_data.append(parsed_entry)
    return entries_data


def mathch_domain_to_rss_sources(file_rss_sources_path: str ="data/rss_sources.json", 
                                 domains: Optional[List[str]] = None) -> List[str]:
    """
    Retourne la liste des URLs de flux RSS correspondant au domaine donné.
    """
    with open(file_rss_sources_path, "r", encoding="utf-8") as f:
        rss_sources = json.load(f)
    return rss_sources.get(domains, [])

def fetch_all_rss_urls(file_rss_sources_path: str ="data/rss_sources.json", 
                       domains: Optional[List[str]] = None) -> List[Dict[str, any]]: 
    """
    Récupère et analyse les entrées de plusieurs flux RSS.
    Retourne une liste de dictionnaires de tous les elements de tous les flux RSS 
    à partir d'un fichier JSON fourni contenant les URLs des flux RSS.
    et renvoie strictement du JSON serializable.
    """
    with open(file_rss_sources_path, "r", encoding="utf-8") as f:
        rss_sources = json.load(f)
    
    domains_matched = mathch_domain_to_rss_sources(file_rss_sources_path, domains)
    
    print(f"{'=='*80}")
    print(f"Domains matched RSS feeds  {domains_matched} URLs...")
    print(f"{'=='*80}")
    
    rss_urls = rss_sources.get(domains_matched) #[source["rss_url"] for source in rss_sources]
    print(f"URLs RSS feeds from {rss_urls} URLs...")
    all_feeds_data = []
    for url in rss_urls:
        entries = fetch_all_rss_entries(url)
        all_feeds_data.extend(entries)
    
    return all_feeds_data

def save_to_json(data, output_path):
    """
    Sauvegarde les données fournies dans un fichier JSON.
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Données sauvegardées dans {output_path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des données: {e}")


def test_main():
    rss_file_path = "data/rss_sources.json"
    domains = ["nlp", "robotique"]
    all_rss_data = fetch_all_rss_urls(rss_file_path, domains)
    save_to_json(all_rss_data, "data/all_rss_data.json")


if __name__ == "__main__":
    test_main()


