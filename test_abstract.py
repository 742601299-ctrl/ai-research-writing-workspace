from dotenv import load_dotenv
from tavily import TavilyClient
import os
import re

# 读取 .env
load_dotenv()

# 创建 Tavily client
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def extract_abstract(raw_content: str) -> str | None:

    if not raw_content:

        return None

    pattern = (

        r"(?is)"

        r"#{0,6}\s*abstract\s*"

        r"(.*?)"

        r"(?=\n\s*#{0,6}\s*(?:keywords|1\.?\s*introduction|introduction)\b)"

    )

    match = re.search(pattern, raw_content)

    if match:

        return match.group(1).strip()

    return None


# --------------------------------------------------
# 1. Tavily Search
# --------------------------------------------------

response = client.search(
    query="AI agents in software engineering research paper",
    max_results=3,
    search_depth="advanced",
    include_raw_content=True,
)


# --------------------------------------------------
# 2. 查看 Tavily 返回的数据
# --------------------------------------------------

results = response.get("results", [])

print(f"\nFound {len(results)} results")


for i, result in enumerate(results, start=1):

    print("\n" + "=" * 100)
    print(f"RESULT {i}")
    print("=" * 100)

    title = result.get("title")
    url = result.get("url")
    content = result.get("content")
    raw_content = result.get("raw_content")

    print("\nTITLE:")
    print(title)

    print("\nURL:")
    print(url)

    print("\nTAVILY CONTENT:")
    print(content)

    print("\nRAW CONTENT PREVIEW:")
    if raw_content:
        # 先只看前 3000 个字符，避免 terminal 爆炸
        print(raw_content[:3000])
    else:
        print("No raw_content returned")


    # --------------------------------------------------
    # 3. 尝试提取 Abstract
    # --------------------------------------------------

    abstract = extract_abstract(raw_content)

    print("\n" + "-" * 50)
    print("EXTRACTED ABSTRACT")
    print("-" * 50)

    if abstract:
        print(abstract)
    else:
        print("Abstract not found")

print("\nFinished.")