import hashlib


def create_chunk_id(
    source: str,
    page: int,
    chunk_number: int
) -> str:

    raw_id = (
        f"{source}|"
        f"{page}|"
        f"{chunk_number}"
    )

    return hashlib.sha1(
        raw_id.encode("utf-8")
    ).hexdigest()


def chunk_documents(
    documents: list[dict],
    chunk_size: int = 220,
    overlap: int = 40
) -> list[dict]:

    if overlap >= chunk_size:

        raise ValueError(
            "Overlap must be smaller "
            "than chunk size."
        )

    chunks = []

    for document in documents:

        words = document[
            "text"
        ].split()

        start = 0
        chunk_number = 1

        while start < len(words):

            end = start + chunk_size

            chunk_words = words[
                start:end
            ]

            chunk_text = " ".join(
                chunk_words
            )

            if chunk_text.strip():

                chunk_id = create_chunk_id(
                    document["source"],
                    document["page"],
                    chunk_number,
                )

                chunks.append(
                    {
                        "id": chunk_id,
                        "source": document[
                            "source"
                        ],
                        "page": document[
                            "page"
                        ],
                        "chunk_number":
                            chunk_number,
                        "text": chunk_text,
                    }
                )

            start += (
                chunk_size - overlap
            )

            chunk_number += 1

    return chunks