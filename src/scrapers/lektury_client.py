import requests
import time
from tqdm import tqdm
from typing import List
from models import TextEntry
from scrapers import TextCleaner
from config import settings


class LekturyScraper:
    def __init__(self):
        self.chunk_size = settings.chunk_size

    def scrape(self, num_books: int) -> List[TextEntry]:
        print(f"[*] Pobieranie {num_books} książek z Wolnych Lektur...")
        entries = []

        try:
            response = requests.get("https://wolnelektury.pl/api/books/")
            response.raise_for_status()
            books = response.json()[:num_books]
        except Exception as e:
            print(f"[Lektury] Błąd połączenia: {e}")
            return []

        for book in tqdm(books, desc="Wolne Lektury"):
            slug = book.get("slug")
            title = book.get("title", "nieznana_ksiazka")
            if not slug: continue

            txt_url = f"https://wolnelektury.pl/media/book/txt/{slug}.txt"
            try:
                r = requests.get(txt_url, timeout=15)
                r.raise_for_status()
                r.encoding = 'utf-8'

                clean_text = TextCleaner.clean(r.text)
                chunks = TextCleaner.chunk_by_sentences(clean_text, self.chunk_size)

                for chunk in chunks[:15]:
                    entries.append(TextEntry(
                        domain="literature (long)",
                        source=f"wl_{title.replace(' ', '_')}",
                        text=chunk
                    ))
            except Exception:
                continue
            time.sleep(0.5)

        return entries