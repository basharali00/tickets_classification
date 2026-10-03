import anthropic

from helpers.llm.enums import LLMModel
from packages.classification.schemas import ClassificationResult
from packages.settings import settings

ALLOWED_MODELS = [LLMModel.CLAUDE_OPUS_5_5]


class ClaudeApi:
    def __init__(self) -> None:
        raise Exception("CREATING INSTANCES OF THIS CLASS IS NOT ALLOWED NOR NEEDED")

    client = anthropic.Anthropic(
        api_key=settings.ANTHROPIC_API_KEY,
        timeout=60.0,
        max_retries=0,
    )

    @classmethod
    def classify_ticket(cls, prompt: str, model: LLMModel) -> ClassificationResult:
        assert model in ALLOWED_MODELS, f"{model} is not a Claude model"
        if settings.ANTHROPIC_API_KEY is None:
            raise Exception("ANTHROPIC_API_KEY is not set")

        response = cls.client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        if response.stop_reason == "refusal":
            raise Exception("model refused")

        text = "".join(block.text for block in response.content if block.type == "text")
        return ClassificationResult.model_validate_json(text)
