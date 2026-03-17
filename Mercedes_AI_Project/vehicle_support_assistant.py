import requests
import json
import textwrap

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "tinyllama"

SYSTEM_PROMPT = """
You are an automotive vehicle support assistant for a professional service center.

Your task is to help classify and respond to common vehicle issues.

Rules:
- Be practical, safe, and concise
- Do not invent advanced repair certainty
- Do not tell users to perform dangerous actions
- Prefer inspection and service-center advice when risk is present
- Keep output structured and readable

You must return output in EXACT JSON format:

{
  "issue_category": "...",
  "severity": "...",
  "possible_causes": ["...", "..."],
  "immediate_actions": ["...", "..."],
  "visit_service_center_when": ["...", "..."],
  "customer_message": "..."
}

Severity must be one of:
- Low
- Medium
- High
- Critical

Possible issue_category values may include:
- Cooling System
- Electrical System
- Engine Warning
- Battery / Charging
- Tire / Wheel

- Brake System
- General Diagnostics
"""

SAMPLE_ISSUES = [
    "Engine overheating while driving uphill",
    "Battery not charging and headlights are dim",
    "Engine warning light turned on after a long drive",
    "Car temperature rises after 20 minutes of driving",
    "Brake warning light is on",
    "Tire pressure warning appeared on dashboard"
]


def ask_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()["response"]


def build_prompt(user_issue: str) -> str:
    return f"""
{SYSTEM_PROMPT}

User issue:
{user_issue}
""".strip()


def try_parse_json(raw_text: str):
    """
    Try to safely extract JSON from model output.
    """
    raw_text = raw_text.strip()

    # direct parse
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    # extract first {...} block if model adds extra text
    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = raw_text[start:end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    return None


def print_result(data: dict):
    print("\n" + "=" * 80)
    print("VEHICLE SUPPORT ASSISTANT RESPONSE")
    print("=" * 80)

    print(f"Issue Category : {data.get('issue_category', 'N/A')}")
    print(f"Severity       : {data.get('severity', 'N/A')}")

    print("\nPossible Causes:")
    for item in data.get("possible_causes", []):
        print(f"  - {item}")

    print("\nImmediate Actions:")
    for item in data.get("immediate_actions", []):
        print(f"  - {item}")

    print("\nVisit Service Center When:")
    for item in data.get("visit_service_center_when", []):
        print(f"  - {item}")

    print("\nCustomer Message:")
    customer_message = data.get("customer_message", "")
    print(textwrap.fill(customer_message, width=78))

    print("=" * 80 + "\n")


def main():
    print("\nOLLAMA  Local AI Demo small")
    print("Vehicle Support Assistant using Ollama")
    print("-" * 80)
    print("Type your own issue, or choose a sample number.")
    print("Type 'samples' to view examples.")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("Enter vehicle issue / sample number: ").strip()

        if user_input.lower() == "exit":
            print("\nExiting Vehicle Support Assistant.")
            break

        if user_input.lower() == "samples":
            print("\nSample Issues:")
            for i, issue in enumerate(SAMPLE_ISSUES, start=1):
                print(f"  {i}. {issue}")
            print()
            continue

        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(SAMPLE_ISSUES):
                issue = SAMPLE_ISSUES[idx]
                print(f"\nSelected Sample: {issue}")
            else:
                print("Invalid sample number.\n")
                continue
        else:
            issue = user_input

        if not issue:
            continue

        prompt = build_prompt(issue)

        try:
            raw_output = ask_ollama(prompt)
            parsed = try_parse_json(raw_output)

            if parsed is not None:
                print_result(parsed)
            else:
                print("\nModel returned non-JSON output:")
                print("-" * 80)
                print(raw_output)
                print("-" * 80)
                print("Tip: tighten the prompt or retry.\n")

        except requests.exceptions.ConnectionError:
            print("\nError: Could not connect to Ollama.")
            print("Make sure Ollama is installed and the model is running.\n")
        except requests.exceptions.Timeout:
            print("\nError: Request timed out. The model may still be loading.\n")
        except Exception as e:
            print(f"\nUnexpected error: {e}\n")


if __name__ == "__main__":
    main()