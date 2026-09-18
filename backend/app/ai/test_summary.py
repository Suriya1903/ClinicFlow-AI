import asyncio

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from backend.app.core.config import settings


llm = ChatOllama(
    model=settings.ollama_model,
    base_url=settings.ollama_base_url,
    temperature=0,
)


async def main() -> None:
    print("Testing final Qwen summary generation...")

    response = await llm.ainvoke(
        [
            SystemMessage(
                content=(
                    "You are a clinic operations assistant. "
                    "Give a short summary using only the supplied data."
                )
            ),
            HumanMessage(
                content=(
                    "Active patients: 1\n"
                    "Today's appointments: None scheduled.\n\n"
                    "Give me a short clinic summary."
                )
            ),
        ]
    )

    print()
    print("===== QWEN SUMMARY =====")
    print(response.content)


if __name__ == "__main__":
    asyncio.run(main())