from app.services.tool_registry import ToolRegistry

tool_registry = ToolRegistry()

tools = tool_registry.get_tools()

print("\n=== Tool Registry Schema Test ===")

update_tool = next(

    tool

    for tool in tools

    if tool["name"] == "update_research_state"

)

parameters = update_tool["parameters"]

print("\nTop-level properties:")

print(

    list(

        parameters["properties"].keys()

    )

)

assert "new_findings" in parameters["properties"]

assert "new_gaps" in parameters["properties"]

assert "new_gap_research_questions" in parameters["properties"]

assert "resolved_gap_ids" in parameters["properties"]

print("\n=== NewGapInput Schema ===")

definitions = parameters["$defs"]

assert "NewGapInput" in definitions

new_gap_schema = definitions[

    "NewGapInput"

]

print(

    "Properties:",

    list(

        new_gap_schema["properties"].keys()

    )

)

assert "description" in new_gap_schema["properties"]

assert (

    "supporting_finding_ids"

    in new_gap_schema["properties"]

)

assert "description" in new_gap_schema["required"]

assert (

    "supporting_finding_ids"

    in new_gap_schema["required"]

)

print("\n=== NewGapResearchQuestionInput Schema ===")

assert (

    "NewGapResearchQuestionInput"

    in definitions

)

new_question_schema = definitions[

    "NewGapResearchQuestionInput"

]

print(

    "Properties:",

    list(

        new_question_schema["properties"].keys()

    )

)

assert "question" in new_question_schema["properties"]

assert "gap_ids" in new_question_schema["properties"]

assert "question" in new_question_schema["required"]

assert "gap_ids" in new_question_schema["required"]

print("\n=== Finding Schema Regression Check ===")

assert "NewFindingInput" in definitions

finding_schema = definitions[

    "NewFindingInput"

]

assert "claim" in finding_schema["properties"]

assert (

    "supporting_chunk_ids"

    in finding_schema["properties"]

)

print("\n=== ToolRegistry Integration Check ===")

print("new_findings schema -> PASS")

print("new_gaps schema -> PASS")

print("supporting_finding_ids schema -> PASS")

print("new_gap_research_questions schema -> PASS")

print("gap_ids schema -> PASS")

print("existing finding schema -> PASS")

print("ToolRegistry -> PASS")