from ollama import Client

from backend.app.core.config import settings


class AIService:
    """
    Service responsible for communicating with the
    locally running Ollama LLM.
    """

    def __init__(self) -> None:
        self.client = Client(
            host=settings.ollama_base_url
        )

        self.model = settings.ollama_model

    def chat(self, message: str) -> str:
        """
        Send a user message to the configured Ollama model
        and return the model's response.
        """

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
        )

        return response["message"]["content"]


ai_service = AIService()