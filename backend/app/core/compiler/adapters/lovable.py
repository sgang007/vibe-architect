from .base import AbstractPlatformAdapter, PromptSection


class LovableAdapter(AbstractPlatformAdapter):
    platform_name = "lovable"
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
            "You are building in Lovable. Generate a complete React application with a "
            "Supabase backend. Use shadcn/ui components throughout — do not use raw HTML "
            "elements where a shadcn component exists. Connect to Supabase using the "
            "official JavaScript client. The app should be production-ready from the "
            "first generation: no placeholder data, no mock APIs, real Supabase queries."
        )

    def get_postamble(self) -> str:
        return (
            "Ensure all Supabase tables have RLS enabled. Use Supabase Auth for "
            "authentication flows. All environment variables must reference "
            "VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY."
        )
