import pandas as pd
from pathlib import Path
from typing import Set


class CheckpointManager:
    """Odpowiada za sprawdzanie, co już zostało zrobione, by uniknąć duplikatów i marnowania API."""

    @staticmethod
    def get_processed_sources(csv_path: Path, required_label: int = 1) -> Set[str]:
        """Zwraca zbiór źródeł (source), które mają już wygenerowany odpowiednik AI."""
        if not csv_path.exists():
            return set()

        try:
            df = pd.read_csv(csv_path)
            if 'source' not in df.columns or 'label' not in df.columns:
                return set()
            # Zwracamy źródła, dla których istnieje wpis wygenerowany przez AI (label == 1)
            return set(df[df['label'] == required_label]['source'].unique())
        except Exception as e:
            print(f"[Checkpoint] Błąd odczytu pliku: {e}")
            return set()