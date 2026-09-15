import os

from tavily import TavilyClient

from app.models.search import SearchResult


class WebSearchTool:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")

        if not self.api_key:
            raise ValueError("TAVILY_API_KEY is not configured")

        self.client = TavilyClient(api_key=self.api_key)

    def search(self, query: str, max_results: int = 3) -> list[SearchResult]:
        response = self.client.search(
            query=query,
            max_results=max_results,
            # search_depth="advanced",
            include_raw_content=True
        )

        results = []

        for item in response.get("results", []):
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    raw_content=item.get("raw_content"),
                )
            )

        return results
