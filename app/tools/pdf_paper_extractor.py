import re

from app.models.document import Document

class PDFPaperExtractor:

    def extract_abstract(

        self,

        document: Document

    ) -> str:

        # Only search the first 3 pages.

        search_text = "\n".join(

            page.text

            for page in document.pages[:3]

        )

        if not search_text.strip():

            return ""

        # Match:

        # Abstract

        # ABSTRACT

        # A B S T R A C T

        abstract_pattern = (

            r"(?im)^\s*"

            r"A\s*B\s*S\s*T\s*R\s*A\s*C\s*T"

            r"\s*$"

        )

        abstract_match = re.search(

            abstract_pattern,

            search_text

        )

        if not abstract_match:

            return ""

        # Everything after the Abstract heading.

        remaining_text = search_text[

            abstract_match.end():

        ]

        # Possible sections that indicate

        # the end of the abstract.

        end_patterns = [

            r"(?im)^\s*keywords?\s*[:\-]?",

            r"(?im)^\s*key\s+words?\s*[:\-]?",

            r"(?im)^\s*index\s+terms?\s*[:\-]?",

            r"(?im)^\s*(?:\d+\s*[\.\)]?\s*)?introduction\s*$",

            r"(?im)^\s*[IVX]+\s*[\.\)]?\s*introduction\s*$",

        ]

        end_positions = []

        for pattern in end_patterns:

            match = re.search(

                pattern,

                remaining_text

            )

            if match:

                end_positions.append(

                    match.start()

                )

        # Use the earliest valid end marker.

        if end_positions:

            abstract = remaining_text[

                :min(end_positions)

            ]

        else:

            abstract = remaining_text

        return abstract.strip()
    
    def extract_title(

        self,

        document: Document

    ) -> str:

        if not document.pages:

            return ""

        first_page_text = document.pages[0].text

        if not first_page_text.strip():

            return ""

        # Get non-empty lines from the first page.

        lines = [

            line.strip()

            for line in first_page_text.splitlines()

            if line.strip()

        ]

        if not lines:

            return ""

        # Common markers that usually indicate

        # affiliation or metadata rather than title.

        stop_markers = [

            "department of",

            "university",

            "institute of",

            "faculty of",

            "school of",

            "article info",

            "abstract",

            "keywords",

        ]

        title_lines = []

        # Academic paper titles are usually located

        # at the beginning of the first page.

        # Stop when the next line looks like author information.

        for line in lines[:3]:

            lower_line = line.lower()

            if any(

                marker in lower_line

                for marker in stop_markers

            ):

                break

            # PyMuPDF often extracts author affiliation markers

            # such as "a,b,*" or "c" after author names.

            author_marker_pattern = (

                r"\s+[a-z](?:\s*,\s*[a-z*]+)+\s*(?:,|$)"

                r"|\s+[a-z]\s*(?:,|$)"

            )

            if title_lines and re.search(

                author_marker_pattern,

                line,

                flags=re.IGNORECASE

            ):

                break

            title_lines.append(line)

        if not title_lines:

            return ""

        return " ".join(title_lines).strip()