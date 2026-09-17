from app.models.search import SearchResult

from app.models.document import Document

from app.models.research_source import ResearchSource

from app.tools.abstract_extractor import AbstractExtractor

from app.tools.pdf_paper_extractor import PDFPaperExtractor

class ResearchSourceFactory:

    def __init__(self):

        self.abstract_extractor = AbstractExtractor()

        self.pdf_paper_extractor = PDFPaperExtractor()

    def from_search_result(

        self,

        search_result: SearchResult

    ) -> ResearchSource:

        abstract = self.abstract_extractor.extract(

            search_result

        )

        content = (

            search_result.raw_content

            or search_result.content

        ).strip()

        return ResearchSource(

            source_type="web",

            title=search_result.title,

            locator=search_result.url,

            abstract=abstract,

            content=content

        )

    def from_document(

        self,

        document: Document

    ) -> ResearchSource:

        title = self.pdf_paper_extractor.extract_title(

            document

        )

        abstract = self.pdf_paper_extractor.extract_abstract(

            document

        )

        return ResearchSource(

            source_type="pdf",

            title=title,

            locator=document.file_path,

            abstract=abstract,

            content=document.text

        )