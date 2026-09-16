from app.models.search import SearchResult

from app.services.research_source_factory import ResearchSourceFactory

factory = ResearchSourceFactory()

# Test 1: raw_content 中存在 Abstract

result_with_abstract = SearchResult(

    title="Test Research Paper",

    url="https://example.com/paper",

    content="This is Tavily content.",

    raw_content="""

# Test Research Paper

Some introduction.

## Abstract

AI agents can improve software engineering productivity

and assist developers with code review and testing.

## Introduction

This is the introduction.

"""

)

source = factory.from_search_result(result_with_abstract)

print("=== Test 1: Web SearchResult -> ResearchSource ===")

print("Source Type:", source.source_type)

print("Title:", source.title)

print("Locator:", source.locator)

print("Abstract:", source.abstract)

print("Content:", source.content)

assert source.source_type == "web"

assert source.title == "Test Research Paper"

assert source.locator == "https://example.com/paper"

assert "AI agents can improve software engineering productivity" in source.abstract

assert source.content == result_with_abstract.raw_content.strip()

# Test 2: raw_content 中没有 Abstract

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

source = factory.from_search_result(result_without_abstract)

print("\n=== Test 2: Fallback Abstract ===")

print("Source Type:", source.source_type)

print("Title:", source.title)

print("Locator:", source.locator)

print("Abstract:", source.abstract)

print("Content:", source.content)

assert source.source_type == "web"

assert source.title == "Test Blog"

assert source.locator == "https://example.com/blog"

assert source.abstract == result_without_abstract.content

assert source.content == result_without_abstract.raw_content.strip()

# Test 3: raw_content 为 None

result_without_raw_content = SearchResult(

    title="Test Simple Source",

    url="https://example.com/simple",

    content="AI agents can automate software testing.",

    raw_content=None

)

source = factory.from_search_result(result_without_raw_content)

print("\n=== Test 3: No Raw Content ===")

print("Source Type:", source.source_type)

print("Title:", source.title)

print("Locator:", source.locator)

print("Abstract:", source.abstract)

print("Content:", source.content)

assert source.source_type == "web"

assert source.title == "Test Simple Source"

assert source.locator == "https://example.com/simple"

assert source.abstract == result_without_raw_content.content

assert source.content == result_without_raw_content.content

print("\nAll ResearchSourceFactory tests passed.")