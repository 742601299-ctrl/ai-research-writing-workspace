from app.models.tool_args import (

    SearchWebArgs,

    RetrieveLiteratureArgs,

    GetSourceArgs,

    UpdateResearchStateArgs

)

class ToolRegistry:

    def get_tools(self) -> list[dict]:

        return [

            {

                "type": "function",

                "name": "search_web",

                "description": (

                    "Search the web for new research sources and add them "

                    "to the current research workspace."

                ),

                "parameters": SearchWebArgs.model_json_schema(),

            },

            {

                "type": "function",

                "name": "retrieve_literature",

                "description": (

                    "Retrieve relevant passages from research sources already "

                    "stored in the current research workspace. "

                    "Use this tool to examine, compare, and synthesize information "

                    "from the literature you have already collected. "

                    "By default, retrieve across the entire workspace by leaving "

                    "source_ids unspecified. "

                    "Only provide source_ids when you intentionally need to restrict "

                    "retrieval to one or more specific known sources. "

                    "Prefer retrieving from the existing workspace before searching "

                    "for additional sources when relevant sources have already been collected."

                ),

                "parameters": RetrieveLiteratureArgs.model_json_schema(),

            },

            {

                "type": "function",

                "name": "get_source",

                "description": (

                    "Get metadata for a specific research source already "

                    "stored in the current research workspace."

                ),

                "parameters": GetSourceArgs.model_json_schema(),

            },

            {

                "type": "function",

                "name": "update_research_state",

                "description": (

                    "Update the semantic research state when new evidence changes "

                    "the current understanding of the user's research goal. "

                    "Add a finding only when it is supported by evidence obtained "

                    "during the current research process. "

                    "Every new finding must include supporting_chunk_ids that identify "

                    "one or more chunks previously returned by retrieve_literature. "

                    "Use only chunks that directly support the specific finding. "

                    "Search results and source abstracts alone are not sufficient "

                    "support for a finding. "

                    "Add a gap only when missing information or evidence materially "

                    "weakens the ability to answer the user's current research goal. "

                    "Do not create gaps merely because a source mentions unanswered "

                    "questions, interesting adjacent topics, or information that "

                    "could optionally be explored. "

                    "Keep all findings and gaps tightly scoped to the user's research "

                    "goal. "

                    "Resolve an existing gap when newly obtained evidence sufficiently "

                    "addresses it. "

                    "A remaining gap does not automatically require further searching; "

                    "if the available evidence is already sufficient to answer the "

                    "user's research request, the research may stop and the remaining "

                    "limitation can be explained in the final answer."

                ),

                "parameters": UpdateResearchStateArgs.model_json_schema(),

            },

        ]