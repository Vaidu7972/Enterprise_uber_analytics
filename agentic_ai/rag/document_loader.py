from pathlib import Path

from pypdf import PdfReader


def load_txt_file(file_path: Path) -> list[dict]:

    text = file_path.read_text(
        encoding="utf-8"
    )

    return [
        {
            "source": file_path.name,
            "page": 1,
            "text": text,
        }
    ]


def load_pdf_file(file_path: Path) -> list[dict]:

    reader = PdfReader(
        str(file_path)
    )

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        text = page.extract_text()

        if text and text.strip():

            pages.append(
                {
                    "source": file_path.name,
                    "page": page_number,
                    "text": text,
                }
            )

    return pages


def load_support_documents(
    folder_path: str | Path
) -> list[dict]:

    folder_path = Path(
        folder_path
    )

    if not folder_path.exists():

        raise FileNotFoundError(
            f"Support document folder not found: "
            f"{folder_path}"
        )

    documents = []

    for file_path in sorted(
        folder_path.iterdir()
    ):

        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()

        if suffix == ".txt":

            documents.extend(
                load_txt_file(
                    file_path
                )
            )

        elif suffix == ".pdf":

            documents.extend(
                load_pdf_file(
                    file_path
                )
            )

    return documents