from dotenv import load_dotenv

from openai import OpenAI

import os

from app.services.research_planner import ResearchPlanner

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

model = os.getenv("OPENAI_MODEL")

client = OpenAI(api_key=api_key)

planner = ResearchPlanner(

    client=client,

    model=model

)

topic = input("请输入你的研究主题：")

try:

    plan = planner.create_plan(topic)

    print("\n=== Research Plan ===")

    print("研究主题：", plan.topic)

    print("研究目标：", plan.objective)

    print("\n研究问题：")

    for i, item in enumerate(plan.research_questions, start=1):

        print(f"\n{i}. {item.question}")

        for query in item.search_queries:

            print(f"   - {query}")

except Exception as e:

    print("生成研究计划失败：", e)