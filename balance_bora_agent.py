
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset, StdioTransport
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

BASE_DIR = Path(__file__).resolve().parent
AUDIT_FILE = BASE_DIR / "audit_log.jsonl"

# Ollama exposes a local OpenAI-compatible endpoint.
model = OpenAIChatModel(
    "qwen2.5:3b",
    provider=OpenAIProvider(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
    ),
)


SERVER_PYTHON = BASE_DIR / ".venv" / "Scripts" / "python.exe"

nutrient_server = MCPToolset(
    StdioTransport(
        command=str(SERVER_PYTHON),
        args=[str(BASE_DIR / "balance_bora_nutrient_mcp.py")],
        cwd=str(BASE_DIR),
    )
)

price_server = MCPToolset(
    StdioTransport(
        command=str(SERVER_PYTHON),
        args=[str(BASE_DIR / "balance_bora_price_mcp.py")],
        cwd=str(BASE_DIR),
    )
)

assessment_server = MCPToolset(
    StdioTransport(
        command=str(SERVER_PYTHON),
        args=[str(BASE_DIR / "balance_bora_assessment_mcp.py")],
        cwd=str(BASE_DIR),
    )
)


agent = Agent(
    model,
    toolsets=[nutrient_server, price_server, assessment_server],
    system_prompt=(
        "You are Balance Bora, a livestock feed advisory assistant supporting "
        "farmers and extension officers in Kenya. Use the available tools to "
        "retrieve nutrient observations and verified supplier quotations. "
        "Never invent prices, nutrient values, suppliers, or evidence. "
        "Distinguish missing data from zero. Explain that nutrient data units "
        "and analytical basis may need verification. Input completeness does "
        "not prove a ration is nutritionally adequate. You may draft advice "
        "for an extension officer, but must not claim to send it to a farmer, "
        "place an order, or approve a ration."
    ),
)


def log_event(event_type: str, details: dict) -> None:
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        "details": details,
    }
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


async def main():
    print("\n=== Balance Bora Local Advisory Agent ===")
    print("Model: qwen2.5:3b via local Ollama")
    print("Enter a request, or type exit to quit.\n")

    async with nutrient_server, price_server, assessment_server:
        while True:
            request = input("\nExtension request: ").strip()
            if request.lower() in {"exit", "quit"}:
                break
            if not request:
                continue

            log_event("request_received", {"request": request})

            try:
                result = await agent.run(request)
                draft = result.output

                log_event(
                    "draft_generated",
                    {
                        "request": request,
                        "draft": str(draft),
                        "tool_call_count": sum(
    1
    for message in result.all_messages()
    for part in getattr(message, "parts", [])
    if "toolcall" in type(part).__name__.lower()
),
                    },
                )

                print("\n--- DRAFT FOR EXTENSION OFFICER REVIEW ---")
                print(draft)
                print("\nThis is a draft, not approved advice.")

                
                print("\nReview decision applies ONLY to the draft above.")
                decision = input(
                    "Type APPROVE-DRAFT to record approval, "
                    "REJECT-DRAFT to reject, or press Enter to leave pending: "
                ).strip().upper()

                if decision == "APPROVE-DRAFT":
                    log_event(
                        "human_approval_recorded",
                        {
                            "request": request,
                            "draft": str(draft),
                            "approval_scope": "this exact draft only",
                            "message_sent": False,
                        },
                    )
                    print("Approval recorded for this draft only. No message was sent.")

                elif decision == "REJECT-DRAFT":
                    log_event(
                        "human_draft_rejected",
                        {
                            "request": request,
                            "draft": str(draft),
                            "message_sent": False,
                        },
                    )
                    print("Draft rejection recorded. No message was sent.")

                else:
                    log_event(
                        "human_approval_pending",
                        {
                            "request": request,
                            "draft": str(draft),
                            "message_sent": False,
                        },
                    )
                    print("Approval left pending. No message was sent.")


            except Exception as exc:
                log_event(
                    "agent_error",
                    {"request": request, "error": repr(exc)},
                )
                print(f"\nAgent error: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
