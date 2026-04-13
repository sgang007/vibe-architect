from .base import AbstractPlatformAdapter, PromptSection


class V0Adapter(AbstractPlatformAdapter):
    platform_name = "v0"
    max_prompt_tokens = 6000
    section_order = [
        PromptSection.PRODUCT_IDENTITY,
        PromptSection.USER_PERSONAS,
        PromptSection.SCREEN_INVENTORY,
        PromptSection.SCREEN_SPECS,
        PromptSection.DATA_MODELS,
        PromptSection.TECH_STACK,
        PromptSection.USER_STORIES,
        PromptSection.DESIGN_SYSTEM,
        PromptSection.BUILD_SEQUENCE,
    ]

    def get_preamble(self) -> str:
        return (
            "You are generating components for v0.dev. Use Next.js App Router with "
            "TypeScript. Use shadcn/ui exclusively for all UI components — import from "
            "'@/components/ui/*'. Use Tailwind CSS for all custom styles. Each component "
            "must be a complete, self-contained, copy-paste-ready file with all imports "
            "included. Use 'use client' directive only where client-side interactivity "
            "is required."
        )

    def get_postamble(self) -> str:
        return (
            "Generate one component per screen. Each file must include: all imports, "
            "TypeScript interfaces, the default export component, and any helper functions. "
            "Use realistic placeholder data — not lorem ipsum."
        )
