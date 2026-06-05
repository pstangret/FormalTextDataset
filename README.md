# 📚 Formal Text Dataset Builder

Profesjonalny, modularny pipeline w Pythonie do ekstrakcji tekstów oraz generowania ich sztucznych odpowiedników (AI). Projekt powstał na potrzeby badań nad detekcją modeli językowych (AI Text Recognition). 

System pobiera teksty pisane przez człowieka (z Wikipedii i Wolnych Lektur), a następnie wykorzystuje modele LLM (Llama 3.1 / Gemini 2.0) do wygenerowania tekstów o identycznej tematyce i długości, tworząc wysokiej jakości, zbalansowany zbiór danych parzystych (Human vs AI).

---

## Główne cechy (Architektura Big Data)

* **Superszybkie środowisko (`uv`):** Zarządzanie zależnościami i wirtualnym środowiskiem za pomocą nowoczesnego narzędzia `uv` firmy Astral.
* **Optymalizacja pamięci (Append Storage):** Zapis wiersz po wierszu bezpośrednio na dysk (O(1) Memory). Gotowy na zbiory rzędu kilkudziesięciu tysięcy rekordów bez wycieków pamięci.
* **Inteligentny Checkpointing:** System automatycznie rozpoznaje pobrane i wygenerowane już teksty. Po restarcie wznawia pracę dokładnie tam, gdzie skończył.
* **Smart Rate Limiting & Rotacja Kluczy:** Wbudowany `RotatingAPIKeyManager` automatycznie rotuje kluczami w przypadku błędu 429 (Rate Limit).
* **Graceful Exit:** Kiedy wszystkie klucze wyczerpią swój dzienny limit (Quota Exhausted), program zapisuje postęp i bezpiecznie się wyłącza, co pozwala na pełną automatyzację (np. przez Cron / Task Scheduler).

---

## 🛠️ Wymagania wstępne

Do uruchomienia projektu potrzebujesz jedynie zainstalowanego menedżera pakietów **uv**. 

**Instalacja `uv` (Windows):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"

```

*(Dla macOS/Linux instrukcje znajdziesz na [docs.astral.sh](https://docs.astral.sh/uv/))*

---

## Instalacja i konfiguracja

**1. Sklonuj repozytorium:**

```bash
git clone [https://github.com/TwojaNazwaUzytkownika/FormalTextDataset.git](https://github.com/TwojaNazwaUzytkownika/FormalTextDataset.git)
cd FormalTextDataset

```

**2. Pobierz zależności:**
Dzięki plikowi `uv.lock`, poniższa komenda automatycznie zainstaluje odpowiednią wersję Pythona i zablokowane wersje bibliotek:

```bash
uv sync

```

**3. Skonfiguruj klucze API (.env):**
W głównym folderze projektu utwórz plik `.env` (plik ten jest ignorowany przez Gita dla bezpieczeństwa). Dodaj do niego swoje klucze API oddzielone przecinkami (bez spacji) oraz limity pobierania.

**Wzór pliku `.env`:**

```env
# Klucze API (oddzielone przecinkiem)
GROQ_API_KEYS=gsk_klucz_1,gsk_klucz_2,gsk_klucz_3
GOOGLE_API_KEYS=AIza_klucz_1,AIza_klucz_2

# Konfiguracja wielkości zbioru
TARGET_CHUNK_SIZE=300
WIKI_ARTICLES_LIMIT=1000
LEKTURY_BOOKS_LIMIT=1000

```

---

## 💻 Użytkowanie

Aby uruchomić pełny cykl życia pipeline'u (akwizycja -> parzysta generacja AI), użyj komendy:

```bash
uv run python src/main.py

```

### Jak działa przepływ pracy (Pipeline)?

1. **Faza 1 (Akwizycja):** Skrypt pobiera artykuły i lektury, czyści je (usuwa tagi, normalizuje spacje) i dzieli na fragmenty (chunks). Jeśli dany tekst już istnieje w bazie, jest pomijany.
2. **Faza 2 (Inicjalizacja):** Ładowanie kluczy z pliku `.env` i przygotowanie klientów API.
3. **Faza 3 (Generowanie):** AI czyta metadane ludzkiego tekstu (dziedzina, tytuł, długość) i generuje sztuczny odpowiednik. Każdy sukces jest od razu zapisywany do `data/paired_dataset.csv`.

### 💡 Wskazówka: Automatyzacja (Task Scheduler)

Ponieważ system jest odporny na przerwania i sam zamyka się po wyczerpaniu dziennych limitów API, zaleca się dodanie skryptu do Harmonogramu Zadań (Windows) lub demona Cron (Linux), aby uruchamiał się automatycznie np. raz dziennie o 08:00 rano. System sam dobije do docelowej liczby tekstów na przestrzeni wielu dni.

---

## 📁 Struktura projektu

```text
FormalTextDataset/
├── .env                  # (Zignorowany) Klucze i ustawienia
├── pyproject.toml        # Konfiguracja środowiska uv
├── README.md             # przeczytajmnie.md
├── uv.lock               # Zablokowane wersje paczek
├── data/
│   └── paired_dataset.csv # Wygenerowany zbiór danych
└── src/
    ├── scrapers/          <-- Logika pobierania z Wikipedii i Wolnych Lektur
    │   ├── __init__.py
    │   ├── wikipedia_client.py
    │   └── lektury_client.py
    ├── generators/        <-- generatory AI i menedżer rotacji kluczy
    │   ├── __init__.py
    │   ├── api_keys.py
    │   └── llm_client.py
    ├── __init__.py
    ├── main.py           # Orkiestrator (Punkt wejścia)
    ├── config.py         # Zarządzanie zmiennymi środowiskowymi (Pydantic Settings)
    ├── models.py         # Modele danych Pydantic (TextEntry)
    ├── checkpoint.py     # Logika wznawiania (Resume)
    ├── storage.py        # Moduł atomowego zapisu (AppendStorage)
    └── scrapers/         # Moduły pobierające dane (Wiki, Lektury)


```

```

```
