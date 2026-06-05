import re
from typing import List


class TextCleaner:
    """Klasa bazowa zawierająca metody czyszczenia i inteligentnego chunkingu."""

    @staticmethod
    def clean(text: str) -> str:
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'==.*?==', '', text)
        return text.strip()

    @staticmethod
    def chunk_by_sentences(text: str, target_size: int) -> List[str]:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks, current_chunk = [], []
        current_word_count = 0

        for sentence in sentences:
            words = sentence.split()
            word_count = len(words)

            if current_word_count + word_count > target_size * 1.2:
                if current_word_count > target_size * 0.5:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_word_count = word_count
            else:
                current_chunk.append(sentence)
                current_word_count += word_count

        if current_word_count > target_size * 0.5:
            chunks.append(' '.join(current_chunk))

        return chunks