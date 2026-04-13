from .base import AbstractPlatformAdapter, PromptSection


class ReplitAdapter(AbstractPlatformAdapter):
    platform_name = "replit"
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
            "You are building on Replit. Use the Replit environment — all dependencies "
            "should be installable via npm or pip. The backend should run on port 8080 "
            "(Replit default). Use Replit Secrets for all API keys and environment variables. "
            "Do not hard-code credentials. Use the .replit file to configure the run command."
        )

    def get_postamble(self) -> str:
        return (
            "Before finishing, verify: (1) The app runs with a single click in Replit. "
            "(2) All secrets are stored in Replit Secrets, not in code. "
            "(3) The server listens on process.env.PORT or 8080."
        )
