from typing import List
import re


class HybridChunker:
    """
    A hybrid text chunker that combines paragraph-based splitting with
    size constraints and sentence-level overlap.
    """

    def __init__(
        self,
        target_chunk_size: int = 300,
        size_variance: int = 50,
        overlap_sentences: int = 2,
    ):
        """
        Initializes the HybridChunker.

        Args:
            target_chunk_size (int): The desired average size of a chunk in words.
            size_variance (int): The allowable variance from the target size.
            overlap_sentences (int): The number of sentences to overlap between chunks.
        """
        self.min_chunk_size = target_chunk_size - size_variance
        self.max_chunk_size = target_chunk_size + size_variance
        self.overlap_sentences = overlap_sentences

    def chunk_text(self, text: str) -> List[str]:
        """
        Chunks the input text using the hybrid strategy.

        Args:
            text (str): The text to be chunked.

        Returns:
            List[str]: A list of text chunks.
        """
        if not text:
            return []

        # Split text into sentences, preserving punctuation.
        sentences = re.split(r"(?<=[.!?])\s+", text.replace("\n", " "))
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return []

        chunks = []
        current_chunk_sentences = []
        word_count = 0

        for i, sentence in enumerate(sentences):
            sentence_word_count = len(sentence.split())

            if (
                word_count + sentence_word_count > self.max_chunk_size
                and current_chunk_sentences
            ):
                chunks.append(" ".join(current_chunk_sentences))

                # Create overlap for the next chunk
                overlap = current_chunk_sentences[-self.overlap_sentences :]
                current_chunk_sentences = overlap
                word_count = sum(len(s.split()) for s in overlap)

            current_chunk_sentences.append(sentence)
            word_count += sentence_word_count

        # Add the last remaining chunk if it meets the minimum size
        if current_chunk_sentences:
            final_chunk = " ".join(current_chunk_sentences)
            if len(final_chunk.split()) >= self.min_chunk_size or not chunks:
                chunks.append(final_chunk)
            else:
                # Append the small final chunk to the previous one
                if chunks:
                    chunks[-1] += " " + final_chunk

        return chunks


# Example usage:
if __name__ == "__main__":
    chunker = HybridChunker()
    sample_text = """
    In the beginning God created the heaven and the earth. And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of thewaters. And God said, Let there be light: and there was light. And God saw the light, that it was good: and God divided the light from the darkness. And God called the light Day, and the darkness he called Night. And the evening and the morning were the first day.
    And God said, Let there be a firmament in the midst of the waters, and let it divide the waters from the waters. And God made the firmament, and divided the waters which were under the firmament from the waters which were above the firmament: and it was so. And God called the firmament Heaven. And the evening and the morning were the second day.
    """
    chunks = chunker.chunk_text(sample_text)
    for i, chunk in enumerate(chunks):
        print(f"--- CHUNK {i+1} (words: {len(chunk.split())}) ---")
        print(chunk)
        print()
