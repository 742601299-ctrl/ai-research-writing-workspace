from app.models.search import SearchResult

from app.models.research_source import ResearchSource

from app.tools.abstract_extractor import AbstractExtractor

class ResearchSourceFactory:

    def __init__(self):

        self.abstract_extractor = AbstractExtractor()

    def from_search_result(

        self,

        search_result: SearchResult

    ) -> ResearchSource:

        abstract = self.abstract_extractor.extract(search_result)

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