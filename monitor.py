from playwright.sync_api import sync_playwright
import requests
import json
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL = "https://online.maavaishnodevi.org/#/helicopter"

def send_alert(msg):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": msg
        }
    )

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(URL)

    page.wait_for_timeout(10000)

    page.screenshot(path="page.png")

    content = page.content()

    if "Availability:1" in content:

        send_alert(
            "🚁 Helicopter tickets available!\n\n"
            "https://online.maavaishnodevi.org/#/helicopter"
        )

    browser.close()
