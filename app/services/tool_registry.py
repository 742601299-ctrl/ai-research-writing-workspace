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

                    "Add a research gap only when it emerges from synthesis of the "

                    "current evidence and findings at the topic level. "

                    "A limitation or future-work statement from a single source is "

                    "not automatically a research gap. "

                    "Every new research gap must include supporting_finding_ids that "

                    "identify one or more existing findings that support the gap. "

                    "Prefer multiple relevant findings when the literature supports "

                    "them, but do not invent additional support. "

                    "Frame gaps relative to the literature reviewed in the current "

                    "research process rather than making unsupported claims that no "

                    "research exists. "

                    "After a research gap has been created and its real gap_id is "

                    "available in the research state, you may formulate a "

                    "gap_research_question that investigates that gap. "

                    "Every new gap research question must include gap_ids that "

                    "reference one or more existing research gaps. "

                    "Do not invent finding IDs or gap IDs. "

                    "Keep findings, gaps, and gap research questions tightly scoped "

                    "to the user's research goal. "

                    "Resolve an existing gap only when later evidence shows that the "

                    "current research state no longer supports treating it as a gap. "

                    "A remaining gap does not automatically require further searching; "

                    "if the available evidence is already sufficient for the user's "

                    "request, the research may stop and the limitation can be "

                    "explained in the final answer."

                ),

                "parameters": UpdateResearchStateArgs.model_json_schema(),

            },

        ]