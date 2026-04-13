from .base import AbstractPlatformAdapter, PromptSection


class EmergentAdapter(AbstractPlatformAdapter):
    platform_name = "emergent"
    max_prompt_tokens = 6000
    section_order = [
        PromptSection.PRODUCT_IDENTITY,
        PromptSection.DESIGN_INTENT,
        PromptSection.USER_PERSONAS,
        PromptSection.SCREEN_INVENTORY,
        PromptSection.SCREEN_SPECS,
        PromptSection.DATA_MODELS,
        PromptSection.TECH_STACK,
        PromptSection.USER_STORIES,
        PromptSection.EDGE_CASES,
        PromptSection.NFR,
        PromptSection.DESIGN_SYSTEM,
        PromptSection.ENHANCEMENT_LAYER,
    ]

    def get_preamble(self) -> str:
        return (
            "Build a complete, production-ready web application based on the "
            "specification below. Build all screens. Use the exact design style "
            "described. Do not ask clarifying questions — make all decisions "
            "based on what is specified. If something is not specified, choose "
            "the simplest, most common implementation."
        )

    def get_postamble(self) -> str:
        return (
            "After building all screens, apply the Enhancement Layer instructions "
            "in the final section. These are not optional — every point must be "
            "implemented before the build is complete."
        )
