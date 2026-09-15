from dotenv import load_dotenv

from app.tools.web_search import WebSearchTool

import re

load_dotenv()

search_tool = WebSearchTool()

results = search_tool.search(

    query="AI agents in software engineering",

    max_results=3

)

for i, result in enumerate(results, start=1):

    print(f"\n{i}. {result.title}")

    print(result.url)

    print(result.content[:300])

    print("\n")

    print(result)

print("\nRAW CONTENT:")

print(result.raw_content[:1000] if result.raw_content else "No raw content")

print("\n=== Content ===")

print(result.content[:500])

print("\n=== Raw Content ===")

if result.raw_content:

    print(result.raw_content[:1000])

else:

    print("No raw content")