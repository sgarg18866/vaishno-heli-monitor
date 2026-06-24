import json
import os
import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "origin": "https://online.maavaishnodevi.org",
    "referer": "https://online.maavaishnodevi.org/",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/148.0.0.0 Safari/537.36"
    ),
    "tof-auth-token": os.environ["TOF_AUTH_TOKEN"]
}

API_URL = "https://online.maavaishnodevi.org/api/v1/eHelicopter/HelicopterAvailability"

# Change these dates as required
DATES = [
    "2026-07-17",
    "2026-07-18",
    "2026-07-19",
    "2026-07-20",
    "2026-08-27",
    "2026-08-28",
    "2026-08-29"
]

# Add more vendors if discovered
VENDORS = {
    1: "Himalayan",
    2: "Global Vectra"
}

# Alert when at least these many seats are available
MIN_SEATS_REQUIRED = 1

BASE_PAYLOAD = {
    "routeId": "12",
    "pilgrimCategoryId": "1",
    "sectorId": 1,
    "noOfPilgrims": "1"
}

def send_telegram(message):
    resp = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=30
    )

    print("Telegram status:", resp.status_code)
    print("Telegram response:", resp.text)

def load_state():
    try:
        with open("state.json", "r") as f:
            return json.load(f)
    except:
        return {}


def save_state(state):
    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)


def get_availability(date, vendor_id):
    payload = BASE_PAYLOAD.copy()
    payload["date"] = date
    payload["vendorId"] = str(vendor_id)

    response = requests.post(
        API_URL,
        json=payload,
        headers=HEADERS,
        timeout=30
    )

    print("Status:", response.status_code)
    print("Headers:", dict(response.headers))
    print("Body length:", len(response.text))
    print("Body repr:", repr(response.text[:500]))

    response.raise_for_status()

    #return response.json()
    if not response.text.strip():
        raise Exception("Empty response body")

    return response.json()


previous_state = load_state()
current_state = {}

alerts = []

for date in DATES:

    for vendor_id, vendor_name in VENDORS.items():

        try:

            data = get_availability(date, vendor_id)

            slots = data.get("heliSlots", [])

            for slot in slots:

                slot_time = slot.get("onwardSlotTime")
                seats = int(slot.get("noOfTicketsAvailable", 0))

                unique_key = f"{date}|{vendor_name}|{slot_time}"

                current_state[unique_key] = seats

                previous_seats = previous_state.get(unique_key, 0)
                print(
                    f"{date} {vendor_name} {slot_time} "
                    f"Seats={seats} Previous={previous_seats}"
                )

                # Alert only if availability increased
                #if seats >= MIN_SEATS_REQUIRED and seats > previous_seats:
                if seats >= MIN_SEATS_REQUIRED:

                    alerts.append(
                        f"🚁 Vaishno Devi Helicopter Available\n\n"
                        f"Date: {date}\n"
                        f"Operator: {vendor_name}\n"
                        f"Time: {slot_time}\n"
                        f"Seats Available: {seats}\n\n"
                        f"https://online.maavaishnodevi.org/#/helicopter"
                    )

        except Exception as e:
            print(f"Error for {date} {vendor_name}: {e}")

save_state(current_state)

#for alert in alerts:
#    send_telegram(alert)

message = "🚁 Helicopter Tickets Found\n\n"

for alert in alerts:
    message += alert + "\n\n"

send_telegram(message[:4000])

print(f"Checked {len(DATES)} dates")
print(f"Sent {len(alerts)} alerts")
