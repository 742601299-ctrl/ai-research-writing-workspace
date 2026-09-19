from app.models.search import SearchResult

from app.tools.abstract_extractor import AbstractExtractor

extractor = AbstractExtractor()

# Test 1: Source contains an Abstract section

result_with_abstract = SearchResult(

    title="Test Paper",

    url="https://example.com/paper",

    content="This is Tavily content.",

    raw_content="""

# Test Paper

Some introduction.

#### Abstract

AI agents can improve software engineering productivity

and assist developers with code review and testing.

## Introduction

This is the introduction.

"""

)

abstract = extractor.extract(result_with_abstract)

print("=== Test 1: Abstract Found ===")

print(abstract)

# Test 2: Source has no Abstract section

result_without_abstract = SearchResult(

    title="Test Blog",

    url="https://example.com/blog",

    content="AI agents are increasingly used in software development.",

    raw_content="""

# AI Agents in Software Development

AI agents can help developers write and test software.

## Benefits

They can automate repetitive tasks.

"""

)

abstract = extractor.extract(result_without_abstract)

print("\n=== Test 2: Fallback to Content ===")

print(abstract)