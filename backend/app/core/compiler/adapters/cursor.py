from .base import AbstractPlatformAdapter, PromptSection


class CursorAdapter(AbstractPlatformAdapter):
    platform_name = "cursor"
    max_prompt_tokens = 10000
    section_order = [
        PromptSection.PRODUCT_IDENTITY,
        PromptSection.USER_PERSONAS,
        PromptSection.SCREEN_INVENTORY,
        PromptSection.SCREEN_SPECS,
        PromptSection.DATA_MODELS,
        PromptSection.TECH_STACK,
        PromptSection.API_CONTRACTS,
        PromptSection.USER_STORIES,
        PromptSection.EDGE_CASES,
        PromptSection.NFR,
        PromptSection.BUILD_SEQUENCE,
        PromptSection.DESIGN_SYSTEM,
    ]

    def get_preamble(self) -> str:
        return (
            "You are writing a technical specification for Cursor AI. Structure this as "
            "a set of engineering implementation tickets. Each section represents a "
            "discrete implementation task. Use precise technical language — the developer "
            "reading this has full context. Specify exact file paths, function signatures, "
            "and data contracts where relevant. Do not describe UI in vague terms — "
            "reference specific component names and props."
        )

    def get_postamble(self) -> str:
        return (
            "Implementation checklist:\n"
            "- [ ] All TypeScript types are defined before use\n"
            "- [ ] All API endpoints have error handling\n"
            "- [ ] All async functions use try/catch\n"
            "- [ ] All forms have validation (client + server)\n"
            "- [ ] All acceptance criteria in user stories pass\n"
            "- [ ] No console.log statements in production code"
        )
