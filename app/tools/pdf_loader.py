from pathlib import Path

import pymupdf

from app.models.document import Document, DocumentPage

class PDFLoader:

    def load(self, file_path: str) -> Document:

        path = Path(file_path)

        if not path.exists():

            raise FileNotFoundError(

                f"PDF file not found: {file_path}"

            )

        pdf = pymupdf.open(file_path)

        pages = []

        try:

            for page_number, page in enumerate(

                pdf,

                start=1

            ):

                text = page.get_text().strip()

                document_page = DocumentPage(

                    page_number=page_number,

                    text=text

                )

                pages.append(document_page)

        finally:

            pdf.close()

        full_text = "\n\n".join(

            page.text

            for page in pages

            if page.text

        )

        return Document(

            filename=path.name,

            file_path=str(path),

            text=full_text,

            pages=pages

        )