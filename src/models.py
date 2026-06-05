from pydantic import BaseModel, Field

class TextEntry(BaseModel):
    """Główny model danych reprezentujący pojedynczą próbkę tekstu (okno)."""
    domain: str = Field(..., description="Dziedzina i kategoria (np. 'wikipedia (formal)')")
    source: str = Field(..., description="Unikalny identyfikator/źródło (np. 'wiki_Polska')")
    text: str = Field(..., description="Zawartość tekstowa (oczyszczona)")
    label: int = Field(default=0, description="0 = Człowiek, 1 = AI")
    generator: str = Field(default="human", description="Model, który wygenerował tekst")