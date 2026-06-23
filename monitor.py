import json
import os
import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

URL = "https://online.maavaishnodevi.org/api/v1/eHelicopter/HelicopterAvailability"

DATES = [
    "2026-07-22",
    "2026-08-27"
]

PAYLOAD_TEMPLATE = {
    "routeId": "12",
    "vendorId": "2",
    "pilgrimCategoryId": "1",
    "sectorId": 1,
    "noOfPilgrims": "1"
}


def send(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": msg
        },
        timeout=30
    )


def load_state():
    try:
        with open("state.json", "r") as f:
            return json.load(f)
    except:
        return {}


def save_state(data):
    with open("state.json", "w") as f:
        json.dump(data, f, indent=2)


previous = load_state()
current = {}
alerts = []

for journey_date in DATES:

    payload = PAYLOAD_TEMPLATE.copy()
    payload["date"] = journey_date

    try:
        r = requests.post(URL, json=payload, timeout=30)

        data = r.json()

        slots = data.get("heliSlots", [])

        available_slots = []

        for slot in slots:

            availability = int(slot.get("availability", 0))

            if availability > 0:

                available_slots.append({
                    "time": slot.get("slotTime"),
                    "availability": availability
                })

        current[journey_date] = available_slots

        old = previous.get(journey_date, [])

        if available_slots != old:

            if available_slots:

                msg = (
                    f"🚁 Helicopter Available\n\n"
                    f"Date: {journey_date}\n\n"
                )

                for s in available_slots:
                    msg += (
                        f"{s['time']} "
                        f"(Seats: {s['availability']})\n"
                    )

                alerts.append(msg)

    except Exception as e:
        print(e)

save_state(current)

for alert in alerts:
    send(alert)
