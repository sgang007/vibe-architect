from .base import AbstractPlatformAdapter, PromptSection


class BoltAdapter(AbstractPlatformAdapter):
    platform_name = "bolt"
    max_prompt_tokens = 8000
    section_order = [
        PromptSection.PRODUCT_IDENTITY,
        PromptSection.USER_PERSONAS,
        PromptSection.SCREEN_INVENTORY,
        PromptSection.SCREEN_SPECS,
        PromptSection.DATA_MODELS,
        PromptSection.TECH_STACK,
        PromptSection.USER_STORIES,
        PromptSection.EDGE_CASES,
        PromptSection.NFR,
        PromptSection.API_CONTRACTS,
        PromptSection.BUILD_SEQUENCE,
        PromptSection.DESIGN_SYSTEM,
    ]

    def get_preamble(self) -> str:
        return (
            "You are building in Bolt. Generate a complete, runnable web application. "
            "Use Vite + React for the frontend. All code must work in a browser sandbox "
            "environment — do not rely on native Node.js APIs that are unavailable in "
            "the browser. Generate all files in a single response. Structure the project "
            "with clear folder separation: src/components, src/pages, src/hooks, src/lib."
        )

    def get_postamble(self) -> str:
        return (
            "Output a complete file tree. Every file must be fully implemented — no "
            "placeholder comments like '// TODO' or '// implement later'. "
            "The app must render without errors on first load."
        )
