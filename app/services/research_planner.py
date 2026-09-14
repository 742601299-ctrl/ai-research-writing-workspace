from openai import OpenAI

from app.models.research import ResearchPlan

class ResearchPlanner:

    def __init__(self, client: OpenAI, model: str):

        self.client = client

        self.model = model

    def create_plan(self, topic: str) -> ResearchPlan:

        prompt = f"""

你是一名专业的研究规划助手。

请针对下面的主题生成研究计划：

{topic}

要求：

- 明确研究目标

- 生成 5 个核心研究问题

- 问题应该能够指导后续资料搜索和研究

- 使用中文

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