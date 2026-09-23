import os

import json

from dotenv import load_dotenv

from openai import OpenAI

from app.services.tool_registry import ToolRegistry

load_dotenv()

client = OpenAI(

    api_key=os.getenv("OPENAI_API_KEY")

)

tool_registry = ToolRegistry()

response = client.responses.create(

    model="gpt-5.6",

    instructions=(

        "You are a research agent. "

        "Use the available research tools when they are needed. "

        "The research workspace is currently empty."

    ),

    input=(

        "Research the main anomaly detection methods used "

        "in pharmaceutical cold chain logistics."

    ),

    tools=tool_registry.get_tools()

)

print("\n=== Response Output ===")

for item in response.output:

    print("\nType:", item.type)

    if item.type == "function_call":

        print("Tool Name:", item.name)

        print("Call ID:", item.call_id)

        print("Raw Arguments:", item.arguments)

        arguments = json.loads(

            item.arguments

        )

        print(

            "Parsed Arguments:",

            arguments

        )