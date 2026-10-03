from enum import StrEnum


class LLMProvider(StrEnum):
    ANTHROPIC = "anthropic"


class LLMModel(StrEnum):
    CLAUDE_OPUS_5_5 = "claude-opus-5-5"
