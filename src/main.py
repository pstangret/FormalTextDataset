"""
main.py — Główny orkiestrator projektu FormalTextDataset.
Zoptymalizowany pod zbiory rzędu kilkudziesięciu tysięcy tekstów.
"""
import sys
import pandas as pd
from tqdm import tqdm
from config import settings
from models import TextEntry
from storage import AppendStorage
from checkpoint import CheckpointManager

# Moduły
from scrapers.wikipedia_client import WikipediaScraper
from scrapers.lektury_client import LekturyScraper
from generators.api_keys import RotatingAPIKeyManager, QuotaExhaustedError
from generators.llm_client import generate_groq_text, generate_google_text

# Inicjalizacja Klientów API
from groq import Groq
from google import genai

def collect_human_data() -> list[TextEntry]:
    """Uruchamia scrapowanie i zwraca pobrane dane ludzkie."""
    human_dataset = []

    wiki = WikipediaScraper()
    human_dataset.extend(wiki.scrape(settings.wiki_limit))

    lektury = LekturyScraper()
    human_dataset.extend(lektury.scrape(settings.lektury_limit))

    return human_dataset

def main():
    output_csv = settings.data_dir / "paired_dataset.csv"

    # =========================================================
    # 1. FAZA: Pobieranie tekstów ludzkich (Tylko Nowości)
    # =========================================================
    print("\n[FAZA 1] Zbieranie korpusu referencyjnego...")
    new_human_data = collect_human_data()

    # Zabezpieczenie przed dublowaniem: sprawdzamy co już mamy w CSV (label=0 to człowiek)
    processed_human = CheckpointManager.get_processed_sources(output_csv, required_label=0)
    to_save_human = [e for e in new_human_data if e.source not in processed_human]

    if to_save_human:
        print(f"[Storage] Dopisuję {len(to_save_human)} nowych tekstów ludzkich do pliku...")
        for entry in to_save_human:
            AppendStorage.append_entry(entry, output_csv)
    else:
        print("[Storage] Brak nowych tekstów ludzkich. Pomijam zapis.")

    # =========================================================
    # 2. FAZA: Inicjalizacja LLM z pliku .env
    # =========================================================
    print("\n[FAZA 2] Przygotowanie generatorów AI...")
    try:
        # Automatycznie czyta klucze z pliku .env dzięki config.py
        groq_manager = RotatingAPIKeyManager(
            provider_name="Groq",
            keys_string=settings.groq_api_keys,
            client_factory=lambda key: Groq(api_key=key)
        )
    except ValueError as e:
        print(f"Błąd konfiguracji kluczy: {e}. Zakończono proces.")
        return

    # =========================================================
    # 3. FAZA: Paired Generation z natychmiastowym zapisem
    # =========================================================
    print("\n[FAZA 3] Rozpoczynam parzyste generowanie AI...")

    # Odczytujemy pełną listę ludzkich tekstów, aby wygenerować do nich AI
    if not output_csv.exists():
        print("Brak danych na dysku. Zakończono.")
        return

    df = pd.read_csv(output_csv)
    human_entries = [TextEntry(**row) for row in df[df['label'] == 0].to_dict('records')]

    # Sprawdzamy, które teksty mają już odpowiednik AI (label=1)
    processed_ai_sources = CheckpointManager.get_processed_sources(output_csv, required_label=1)
    to_process = [e for e in human_entries if e.source not in processed_ai_sources]

    print(f"Pominięto {len(processed_ai_sources)} gotowych par. Do wygenerowania: {len(to_process)}")

    try:
        for entry in tqdm(to_process, desc="Generowanie AI"):
            ai_text = generate_groq_text(entry, groq_manager)

            if ai_text:
                ai_entry = TextEntry(
                    domain=entry.domain,
                    source=entry.source,
                    text=ai_text,
                    label=1,
                    generator="llama-3.1-8b"
                )
                # O(1) Memory: Zapisujemy wiersz natychmiast na dysk i idziemy dalej!
                AppendStorage.append_entry(ai_entry, output_csv)

    except QuotaExhaustedError as e:
        print(f"\nZATRZYMANO (LIMIT DZIENNY): {e}")
        print("Wszystko co wygenerowałeś przed ułamkiem sekundy, jest bezpieczne na dysku.")
        print("Uruchom skrypt ponownie jutro!")
        sys.exit(0)
    except KeyboardInterrupt:
        print("\nRęcznie przerwano działanie skryptu (Ctrl+C). Postęp zapisany!")
        sys.exit(0)

    print("\nProces zakończony! Brak tekstów do wygenerowania.")

if __name__ == "__main__":
    main()