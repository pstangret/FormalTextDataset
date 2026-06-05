import time
import sys
from typing import Generic, TypeVar, Callable

ClientT = TypeVar("ClientT")


class QuotaExhaustedError(Exception):
    pass


class RotatingAPIKeyManager(Generic[ClientT]):
    def __init__(self, provider_name: str, keys_string: str, client_factory: Callable[[str], ClientT],
                 cooldown: int = 60):
        self.provider_name = provider_name
        self.keys = [k.strip() for k in keys_string.split(',') if k.strip()]
        self.client_factory = client_factory
        self.cooldown = cooldown
        self.current_index = 0
        self.consecutive_failures = 0  # Licznik spalonych kluczy

        if not self.keys:
            raise ValueError(f"Brak kluczy dla {provider_name}! Sprawdź plik .env")
        self.client = self.client_factory(self.keys[self.current_index])

    def get_client(self) -> ClientT:
        return self.client

    def switch_key(self) -> None:
        self.current_index = (self.current_index + 1) % len(self.keys)
        self.consecutive_failures += 1

        # Jeśli przeszliśmy przez WSZYSTKIE klucze i żaden nie działa:
        if self.consecutive_failures >= len(self.keys):
            print(f"\n[FATAL] Wszystkie {len(self.keys)} klucze API wyczerpały dzienny limit!")
            raise QuotaExhaustedError("Limity wyczerpane. Wróć jutro.")

        print(f"[{self.provider_name}] Zmiana klucza API (Indeks: {self.current_index})")
        self.client = self.client_factory(self.keys[self.current_index])

    def report_success(self):
        """Wywoływane po udanym API callu, resetuje licznik awarii."""
        self.consecutive_failures = 0