import pandas as pd
from pathlib import Path
from models import TextEntry


class AppendStorage:
    """Zoptymalizowany zapis dla dużych zbiorów danych (O(1) I/O)."""

    @staticmethod
    def append_entry(entry: TextEntry, output_path: Path) -> None:
        """Dopisuje pojedynczy rekord na koniec pliku CSV."""
        df = pd.DataFrame([entry.model_dump()])

        # Jeśli plik nie istnieje, dodaj nagłówki. W przeciwnym razie po prostu dopisz dane (mode='a')
        write_header = not output_path.exists()

        df.to_csv(
            output_path,
            mode='a',
            header=write_header,
            index=False,
            encoding='utf-8-sig'
        )