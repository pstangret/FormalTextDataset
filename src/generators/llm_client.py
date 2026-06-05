import random
import time
from models import TextEntry
from generators.api_keys import RotatingAPIKeyManager, QuotaExhaustedError

# Import SDK
from groq import Groq
from google import genai
from google.genai import types


def build_prompt(entry: TextEntry) -> tuple[str, str]:
    """Buduje instrukcje dla AI na podstawie metadanych rekordu ludzkiego."""
    word_count = len(entry.text.split())
    if "wikipedia" in entry.domain:
        sys_p = "Jesteś redaktorem encyklopedii. Tworzysz obiektywne, encyklopedyczne hasła."
        usr_p = f"Napisz po polsku hasło na temat: {entry.source.replace('wiki_', '')}. Długość: ~{word_count} słów."
    else:
        sys_p = "Jesteś polskim pisarzem. Twój styl jest bogaty, literacki i obrazowy."
        usr_p = f"Napisz po polsku fragment prozy inspirowany utworem '{entry.source.replace('wl_', '')}'. Długość: ~{word_count} słów. Tylko treść."
    return sys_p, usr_p


def generate_groq_text(entry: TextEntry, manager: RotatingAPIKeyManager) -> str | None:
    """Generuje tekst używając LLaMA 3.1 przez Groq (z retry logic)."""
    sys_p, usr_p = build_prompt(entry)
    temp = round(random.uniform(0.4, 0.9), 2)

    while True:
        try:
            client = manager.get_client()
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": usr_p}],
                temperature=temp,
            )
            # Sukces! Informujemy menedżera, że obecny klucz działa
            manager.report_success()
            return response.choices[0].message.content.strip()

        except QuotaExhaustedError:
            # Wyczerpano limity dzienne wszystkich kluczy. Przerywamy pętlę i zamykamy program.
            raise

        except Exception as e:
            err = str(e).lower()
            if any(k in err for k in ["429", "quota", "rate", "limit"]):
                manager.switch_key()
                time.sleep(1)
            else:
                print(f"[Groq Błąd] {e}")
                time.sleep(2)
                manager.switch_key()


def generate_google_text(entry: TextEntry, manager: RotatingAPIKeyManager) -> str | None:
    """Generuje tekst używając Gemini 2.0 przez Google GenAI."""
    sys_p, usr_p = build_prompt(entry)
    temp = round(random.uniform(0.4, 0.9), 2)

    while True:
        try:
            client = manager.get_client()
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=usr_p,
                config=types.GenerateContentConfig(system_instruction=sys_p, temperature=temp),
            )
            # Sukces! Informujemy menedżera, że obecny klucz działa
            manager.report_success()
            return response.text.strip()

        except QuotaExhaustedError:
            # Wyczerpano limity dzienne wszystkich kluczy. Przerywamy pętlę i zamykamy program.
            raise

        except Exception as e:
            err = str(e).lower()
            if any(k in err for k in ["429", "quota", "exhausted", "limit"]):
                manager.switch_key()
                time.sleep(1)
            elif "safety" in err:
                return None
            else:
                time.sleep(2)
                manager.switch_key()