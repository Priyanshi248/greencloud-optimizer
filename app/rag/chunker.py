from dataclasses import dataclass


@dataclass
class DocumentChunk:
    content: str
    chunk_index: int


class DocumentChunker:
    """
    Splits a document into overlapping text chunks.

    Chunking is kept independent from embeddings and database storage
    so that each responsibility can be tested separately.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str) -> list[DocumentChunk]:
        """
        Split text into overlapping chunks.
        """

        text = text.strip()

        if not text:
            return []

        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + self.chunk_size

            content = text[start:end].strip()

            if content:
                chunks.append(
                    DocumentChunk(
                        content=content,
                        chunk_index=chunk_index,
                    )
                )

                chunk_index += 1

            if end >= len(text):
                break

            start = end - self.chunk_overlap

        return chunks