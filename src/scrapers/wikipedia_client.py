import wikipedia
import requests
import time
from tqdm import tqdm
from typing import List
from models import TextEntry
from scrapers import TextCleaner
from config import settings

wikipedia.set_lang("pl")
wikipedia.set_user_agent("AITextDetection_Project/2.0")


class WikipediaScraper:
    def __init__(self):
        self.chunk_size = settings.chunk_size

    def scrape(self, num_articles: int) -> List[TextEntry]:
        print(f"[*] Pobieranie {num_articles} artykułów z Wikipedii...")
        entries = []
        api_url = f"https://pl.wikipedia.org/w/api.php?action=query&list=random&rnnamespace=0&rnlimit={num_articles}&format=json"

        try:
            r = requests.get(api_url, headers={"User-Agent": "AITextDetection_Project/2.0"})
            r.raise_for_status()
            titles = [page['title'] for page in r.json()['query']['random']]
        except Exception as e:
            print(f"[Wiki] Błąd API: {e}")
            return []

        for title in tqdm(titles, desc="Wikipedia"):
            try:
                page = wikipedia.page(title, auto_suggest=False)
                clean_text = TextCleaner.clean(page.content)
                chunks = TextCleaner.chunk_by_sentences(clean_text, self.chunk_size)

                for chunk in chunks[:5]:
                    entries.append(TextEntry(
                        domain="wikipedia (formal)",
                        source=f"wiki_{title.replace(' ', '_')}",
                        text=chunk
                    ))
            except Exception:
                continue
            time.sleep(0.2)

        return entries