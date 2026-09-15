import re

from app.models.search import SearchResult

class AbstractExtractor:

    def extract(self, search_result: SearchResult) -> str:

        raw_content = search_result.raw_content

        if not raw_content:

            return search_result.content.strip()

        abstract = self._extract_abstract_section(raw_content)

        if abstract:

            return abstract

        return search_result.content.strip()

    def _extract_abstract_section(self, raw_content: str) -> str | None:

        pattern = r"(?im)^#{1,6}\s*Abstract\s*$"

        match = re.search(pattern, raw_content)

        if not match:

            return None

        start = match.end()

        remaining_text = raw_content[start:]

        next_heading = re.search(

            r"(?m)^#{1,6}\s+.+$",

            remaining_text

        )

        if next_heading:

            abstract = remaining_text[:next_heading.start()]

        else:

            abstract = remaining_text

        abstract = abstract.strip()

        # Tavily raw content sometimes contains Markdown separators.

        abstract = re.sub(

            r"^\s*\*\s*\*\s*\*\s*$",

            "",

            abstract,

            flags=re.MULTILINE

        ).strip()

        return abstract or None