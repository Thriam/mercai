"""
Store AI Agent Chatbot - Main Interactive Loop

Run this script to start an interactive session with the Store AI Agent.
The agent answers questions about products using CSV data.

Usage:
    python main.py
"""

import sys
from app.core.orchestrator import StoreAIOrchestrator
from app.config.logging_config import logger

def main():
    """Run the interactive chatbot loop."""
    logger.info("Starting Store AI Agent Chatbot...")

    try:
        orchestrator = StoreAIOrchestrator()
    except Exception as e:
        print(f"Error initializing agent: {e}")
        print("Make sure to create .env file with OPENROUTER_API_KEY")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("STORE AI AGENT CHATBOT")
    print("=" * 60)
    print("\nAsk me questions about our products!")
    print("Examples:")
    print("  - Show me products under $50")
    print("  - Find all 5-star rated products")
    print("  - What products are in stock with high ratings?")
    print("\nType 'exit' or 'quit' to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Thank you for using Store AI Agent. Goodbye!")
                break

            # Run query through pipeline
            state = orchestrator.run(user_input)

            # Display response
            print(state.final_response)

            if state.needs_clarification:
                clarification = input("\nCould you provide more info: ").strip()
                if clarification:
                    state = orchestrator.run(clarification)
                    print(state.final_response)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
