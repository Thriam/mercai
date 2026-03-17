import json
import requests
from datetime import datetime

# =========================================================
# DAY 2 - AUTOMOBILE SERVICE CHATBOT DEVELOPMENT
# Single-file demo for Mercedes AI/ML training
# Local LLM via Ollama + simple tools + memory + flow
# =========================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"


# =========================================================
# MOCK DATABASES
# =========================================================
SERVICE_DB = {
    "VIN123": {
        "customer_name": "Amit Sharma",
        "vehicle_model": "Mercedes C-Class",
        "last_service_date": "2025-10-15",
        "last_service_km": 12000,
        "next_service_km": 20000,
        "service_type": "Periodic Maintenance"
    },
    "VIN456": {
        "customer_name": "Priya Verma",
        "vehicle_model": "Mercedes GLC",
        "last_service_date": "2025-08-02",
        "last_service_km": 25000,
        "next_service_km": 35000,
        "service_type": "Full Inspection"
    }
}

WARRANTY_DB = {
    "VIN123": {
        "status": "Active",
        "expires_on": "2027-03-31",
        "coverage": "Engine, transmission, electronics"
    },
    "VIN456": {
        "status": "Expired",
        "expires_on": "2025-01-10",
        "coverage": "No active warranty"
    }
}

SERVICE_CENTERS = [
    {"city": "Bangalore", "name": "Mercedes Service Center - Whitefield", "phone": "+91-9876500011"},
    {"city": "Bangalore", "name": "Mercedes Service Center - Electronic City", "phone": "+91-9876500012"},
    {"city": "Mumbai", "name": "Mercedes Service Center - Andheri", "phone": "+91-9876500021"},
    {"city": "Delhi", "name": "Mercedes Service Center - Gurgaon", "phone": "+91-9876500031"}
]


# =========================================================
# MEMORY
# =========================================================
class ConversationMemory:
    def __init__(self):
        self.messages = []
        self.current_vin = None
        self.current_city = None
        self.current_issue = None

    def add(self, role, content):
        self.messages.append({"role": role, "content": content})

    def get_recent_history_text(self, limit=8):
        recent = self.messages[-limit:]
        lines = []
        for msg in recent:
            lines.append(f"{msg['role'].upper()}: {msg['content']}")
        return "\n".join(lines)

    def set_vin_if_found(self, text):
        text = text.strip().upper()
        if text in SERVICE_DB or text in WARRANTY_DB:
            self.current_vin = text

    def set_city_if_found(self, text):
        lowered = text.lower()
        for center in SERVICE_CENTERS:
            if center["city"].lower() in lowered:
                self.current_city = center["city"]
                return

    def update_issue_if_found(self, text):
        lowered = text.lower()
        issue_keywords = [
            "battery", "brake", "noise", "engine", "temperature",
            "overheating", "service", "warranty", "light", "oil",
            "vibration", "starting", "start", "schedule"
        ]
        if any(word in lowered for word in issue_keywords):
            self.current_issue = text


# =========================================================
# TOOL FUNCTIONS
# =========================================================
def check_service_schedule(vin):
    record = SERVICE_DB.get(vin.upper())
    if not record:
        return f"No service record found for VIN {vin}."

    return (
        f"Service record for {vin.upper()}:\n"
        f"- Customer: {record['customer_name']}\n"
        f"- Vehicle: {record['vehicle_model']}\n"
        f"- Last service date: {record['last_service_date']}\n"
        f"- Last service odometer: {record['last_service_km']} km\n"
        f"- Next service due at: {record['next_service_km']} km\n"
        f"- Service type: {record['service_type']}"
    )


def lookup_warranty(vin):
    record = WARRANTY_DB.get(vin.upper())
    if not record:
        return f"No warranty record found for VIN {vin}."

    return (
        f"Warranty record for {vin.upper()}:\n"
        f"- Status: {record['status']}\n"
        f"- Expiry date: {record['expires_on']}\n"
        f"- Coverage: {record['coverage']}"
    )


def find_nearest_service_center(city):
    matches = [c for c in SERVICE_CENTERS if c["city"].lower() == city.lower()]
    if not matches:
        return f"No service center found for city '{city}'."

    lines = [f"Available service centers in {city.title()}:"]
    for idx, center in enumerate(matches, start=1):
        lines.append(f"{idx}. {center['name']} | Contact: {center['phone']}")
    return "\n".join(lines)


def diagnose_basic_issue(user_text):
    text = user_text.lower()

    if "overheat" in text or "temperature" in text:
        return (
            "Possible causes of overheating:\n"
            "- Low coolant level\n"
            "- Cooling fan malfunction\n"
            "- Radiator blockage\n"
            "- Water pump issue\n"
            "Recommendation: Stop the vehicle safely and inspect coolant / get service support."
        )

    if "battery" in text or "not start" in text or "starting" in text:
        return (
            "Possible battery / starting related causes:\n"
            "- Weak battery\n"
            "- Alternator issue\n"
            "- Loose terminals\n"
            "- Starter motor problem\n"
            "Recommendation: Check battery voltage and terminal condition."
        )

    if "brake" in text or "braking" in text or "noise" in text:
        return (
            "Possible brake-related causes:\n"
            "- Worn brake pads\n"
            "- Rotor wear\n"
            "- Brake dust buildup\n"
            "- Caliper issue\n"
            "Recommendation: Inspect brake pads and discs as soon as possible."
        )

    if "service" in text:
        return (
            "It sounds like a service-related query.\n"
            "You can provide your VIN to check the next due service schedule."
        )

    return (
        "I understand there is a vehicle issue, but I need more detail.\n"
        "Please tell me whether the issue is related to engine, battery, brakes, overheating, warning light, or service schedule."
    )


# =========================================================
# OLLAMA CALL
# =========================================================
def call_ollama(prompt, model=MODEL_NAME):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()

    data = response.json()
    return data.get("response", "").strip()


# =========================================================
# ROUTING / SIMPLE TOOL CALL DECISION
# =========================================================
def decide_tools(user_input, memory):
    text = user_input.lower()
    tools_used = []

    # update memory hints
    memory.set_vin_if_found(user_input)
    memory.set_city_if_found(user_input)
    memory.update_issue_if_found(user_input)

    tool_outputs = []

    # explicit VIN handling
    if user_input.strip().upper() in SERVICE_DB or user_input.strip().upper() in WARRANTY_DB:
        vin = user_input.strip().upper()
        memory.current_vin = vin
        tool_outputs.append(check_service_schedule(vin))
        tool_outputs.append(lookup_warranty(vin))
        tools_used.extend(["check_service_schedule", "lookup_warranty"])
        return tools_used, tool_outputs

    # service schedule intent
    if "service" in text and ("schedule" in text or "due" in text or "next service" in text):
        if memory.current_vin:
            tool_outputs.append(check_service_schedule(memory.current_vin))
            tools_used.append("check_service_schedule")
        else:
            tool_outputs.append("To check service schedule, please provide your VIN (example: VIN123).")
            tools_used.append("ask_for_vin")
        return tools_used, tool_outputs

    # warranty intent
    if "warranty" in text:
        if memory.current_vin:
            tool_outputs.append(lookup_warranty(memory.current_vin))
            tools_used.append("lookup_warranty")
        else:
            tool_outputs.append("To check warranty, please provide your VIN (example: VIN123).")
            tools_used.append("ask_for_vin")
        return tools_used, tool_outputs

    # service center intent
    if "service center" in text or "nearest center" in text or "nearest service center" in text:
        if memory.current_city:
            tool_outputs.append(find_nearest_service_center(memory.current_city))
            tools_used.append("find_nearest_service_center")
        else:
            tool_outputs.append("Please tell me your city so I can find the nearest service center.")
            tools_used.append("ask_for_city")
        return tools_used, tool_outputs

    # city-only follow-up
    known_cities = {c["city"].lower() for c in SERVICE_CENTERS}
    if text.strip() in known_cities:
        city = text.strip().title()
        memory.current_city = city
        tool_outputs.append(find_nearest_service_center(city))
        tools_used.append("find_nearest_service_center")
        return tools_used, tool_outputs

    # general diagnosis
    tool_outputs.append(diagnose_basic_issue(user_input))
    tools_used.append("diagnose_basic_issue")
    return tools_used, tool_outputs


# =========================================================
# PROMPT BUILDER
# =========================================================
def build_prompt(user_input, memory, tool_outputs):
    system_instruction = """
You are an Automobile Service Chatbot for Mercedes support.

Your behavior rules:
1. Be clear, professional, and helpful.
2. Use the provided tool results as the highest-priority facts.
3. Do not invent VIN records, warranty records, or service schedule records.
4. If data is missing, politely ask for the missing field.
5. Keep responses structured and service-oriented.
6. When useful, guide the user to next steps.
7. Maintain conversational continuity based on recent history.
8. Prefer bullet points when giving diagnosis or action steps.
"""

    prompt = f"""
{system_instruction}

RECENT CONVERSATION:
{memory.get_recent_history_text()}

MEMORY STATE:
- Current VIN: {memory.current_vin}
- Current City: {memory.current_city}
- Current Issue: {memory.current_issue}

TOOL OUTPUTS:
{chr(10).join(tool_outputs)}

CURRENT USER MESSAGE:
{user_input}

Now generate the best assistant response.
"""
    return prompt


# =========================================================
# CHATBOT LOGIC
# =========================================================
def chatbot_reply(user_input, memory):
    tools_used, tool_outputs = decide_tools(user_input, memory)
    prompt = build_prompt(user_input, memory, tool_outputs)

    try:
        llm_reply = call_ollama(prompt)
    except requests.exceptions.RequestException as ex:
        llm_reply = (
            "I could not connect to the local Ollama model.\n"
            "Please make sure Ollama is running and the model is available.\n"
            f"Technical details: {str(ex)}"
        )

    debug_info = {
        "tools_used": tools_used,
        "tool_outputs": tool_outputs
    }
    return llm_reply, debug_info


# =========================================================
# MAIN
# =========================================================
def print_banner():
    print("=" * 70)
    print("DAY 2 - AUTOMOBILE SERVICE CHATBOT DEVELOPMENT")
    print("Local LLM + Tools + Memory + Structured Conversation Flow")
    print("=" * 70)
    print("Example prompts:")
    print("- My car battery is dead")
    print("- My engine temperature warning is on")
    print("- Check my warranty")
    print("- Check next service schedule")
    print("- Nearest service center in Bangalore")
    print("- VIN123")
    print("Type 'exit' to quit.")
    print("=" * 70)


def main():
    memory = ConversationMemory()
    print_banner()

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            print("Assistant: Please enter a message.")
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("Assistant: Thank you. Ending the service chat session.")
            break

        memory.add("user", user_input)

        reply, debug_info = chatbot_reply(user_input, memory)

        memory.add("assistant", reply)
        print("\nAssistant:")
        print(reply)

        # Optional trainer/debug section
        print("\n[DEBUG - Training View]")
        print("Tools Used:", debug_info["tools_used"])
        print("Tool Outputs:")
        for i, item in enumerate(debug_info["tool_outputs"], start=1):
            print(f"{i}. {item}")
        print("-" * 70)


if __name__ == "__main__":
    main()