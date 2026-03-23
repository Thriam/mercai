from app.config.logging_config import setup_logging
from app.config.settings import AppSettings
from app.core.orchestrator import AutomotiveRAGOrchestrator
import json

def main() -> None:
    setup_logging()
    settings = AppSettings()
    orchestrator = AutomotiveRAGOrchestrator(settings)

    print("=" * 70)
    print(f"{settings.app_name} started")
    print("Type your automotive issue. Type 'exit' to quit.")
    print("=" * 70)

    while True:
        user_query = input("\nEnter automotive issue: ").strip()

        if user_query.lower() in {"exit", "quit"}:
            print("Exiting AutomotiveRAGFlow...")
            break

        if not user_query:
            print("Please enter a valid query.")
            continue

        result = orchestrator.handle_query(user_query)

        print("\n--- FINAL RESPONSE ---")
        print(result["response"])

        if result.get("needs_clarification"):
            print("\n--- CLARIFICATION NEEDED ---")
            print(result["clarification_question"])

        print("\n--- CONFIDENCE ---")
        print(result["diagnosis_result"].get("confidence", 0.0))
        print("\n--- RAW JSON OUTPUT ---")
        print(json.dumps(result["diagnosis_result"], indent=2))

if __name__ == "__main__":
    main()