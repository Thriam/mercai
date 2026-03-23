class IntentDetector:
    def detect(self, query: str) -> dict:
        lower_query = query.lower()

        symptom_words = [
            "overheat",
            "hot",
            "noise",
            "vibration",
            "smoke",
            "warning light",
            "battery",
            "brake",
            "start",
            "starting",
            "stall",
            "leak",
        ]

        detected_symptom = "unknown"
        for word in symptom_words:
            if word in lower_query:
                detected_symptom = word
                break

        if "overheat" in lower_query or "hot" in lower_query:
            system = "cooling system"
        elif "battery" in lower_query or "start" in lower_query:
            system = "electrical system"
        elif "brake" in lower_query:
            system = "brake system"
        elif "noise" in lower_query or "vibration" in lower_query:
            system = "mechanical system"
        else:
            system = "unknown"

        return {
            "intent": "diagnostic_symptom",
            "entities": {
                "symptom": detected_symptom,
                "system": system,
            },
        }