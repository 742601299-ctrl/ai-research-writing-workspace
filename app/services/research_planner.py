from openai import OpenAI

from app.models.research import ResearchPlan

class ResearchPlanner:

    def __init__(self, client: OpenAI, model: str):

        self.client = client

        self.model = model

    def create_plan(self, topic: str) -> ResearchPlan:

        prompt = f"""

你是一名专业的研究规划助手。

请针对下面的研究主题生成研究计划：

{topic}

要求：

- 明确研究目标

- 生成 5 个核心研究问题

- 每个研究问题生成 2 个适合搜索引擎使用的英文搜索查询

- 搜索查询应具体、具有研究价值

- 避免不同研究问题之间的搜索查询高度重复

- 搜索查询优先使用英文，因为技术资料通常更丰富

- 使用中文描述研究目标和研究问题

研究主题：

{topic}

"""

        response = self.client.responses.parse(

            model=self.model,

            input=[

                {

                    "role": "user",

                    "content": prompt

                }

            ],

            text_format=ResearchPlan

        )

        return response.output_parsed