from abc import ABC, abstractmethod
from enum import Enum


class PromptSection(str, Enum):
    PRODUCT_IDENTITY = "product_identity"
    DESIGN_INTENT = "design_intent"
    USER_PERSONAS = "user_personas"
    SCREEN_INVENTORY = "screen_inventory"
    SCREEN_SPECS = "screen_specs"
    DATA_MODELS = "data_models"
    TECH_STACK = "tech_stack"
    USER_STORIES = "user_stories"
    EDGE_CASES = "edge_cases"
    NFR = "nfr"
    API_CONTRACTS = "api_contracts"
    BUILD_SEQUENCE = "build_sequence"
    DESIGN_SYSTEM = "design_system"
    ENHANCEMENT_LAYER = "enhancement_layer"


class AbstractPlatformAdapter(ABC):
    platform_name: str = ""
    max_prompt_tokens: int = 8000
    section_order: list[PromptSection] = [
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
        return ""

    def get_postamble(self) -> str:
        return ""

    def assemble(self, sections: dict[str, str]) -> str:
        parts = []
        preamble = self.get_preamble()
        if preamble:
            parts.append(preamble)
            parts.append("")

        for section in self.section_order:
            content = sections.get(section.value, "")
            if content:
                parts.append(content)
                parts.append("")

        postamble = self.get_postamble()
        if postamble:
            parts.append(postamble)

        return "\n".join(parts)
