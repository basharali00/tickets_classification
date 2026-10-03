from helpers.llm.claude.api import ClaudeApi
from helpers.llm.enums import LLMModel, LLMProvider

LLM_MODEL_PROVIDER: dict[LLMModel, LLMProvider] = {
    LLMModel.CLAUDE_OPUS_5_5: LLMProvider.ANTHROPIC,
}

LLM_PROVIDER_API: dict[LLMProvider, type[ClaudeApi]] = {
    LLMProvider.ANTHROPIC: ClaudeApi,
}
