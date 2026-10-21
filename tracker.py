#!/usr/bin/env python3
"""PS5 Pro Verfügbarkeits-Tracker -> Push aufs iPhone via ntfy.sh"""
import os, sys, json, time, urllib.request

PAGE = "https://www.playstation.com/de-de/ps5/ps5-pro/buy-now/"
BUY_LINK = "https://direct.playstation.com/de-de/buy-consoles/playstation5-pro-console-2-tb"
TOPIC = os.environ.get("NTFY_TOPIC", "")          # dein geheimer Topic-Name
INTERVAL = int(os.environ.get("INTERVAL", "0"))   # 0 = einmal prüfen, sonst Sekunden

# Texte, die auf der Seite stehen, solange die Konsole NICHT lieferbar ist
SOLD_OUT = ["Nicht zum Kauf erhältlich", "Derzeit nicht vorrätig"]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 19_0 like Mac OS X) AppleWebKit/605.1.15 "
                  "(KHTML, like Gecko) Version/19.0 Mobile/15E148 Safari/604.1",
    "Accept-Language": "de-DE,de;q=0.9",
}

def notify(title, msg, click):
    body = json.dumps({"topic": TOPIC, "title": title, "message": msg,
                       "click": click, "priority": 5, "tags": ["video_game", "rotating_light"],
                       "actions": [{"action": "view", "label": "Jetzt kaufen", "url": click}]}).encode()
    req = urllib.request.Request("https://ntfy.sh", data=body,
                                 headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=15).read()

def check():
    req = urllib.request.Request(PAGE, headers=HEADERS)
    html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
    if "PlayStation" not in html or "PS5 Pro" not in html:
        raise RuntimeError("Seite unerwartet (evtl. blockiert) - kein Urteil möglich")
    return not any(s in html for s in SOLD_OUT)

def run_once():
    try:
        if check():
            notify("PS5 Pro verfügbar!", "Jetzt schnell sein – tippen und bestellen.", BUY_LINK)
            print("VERFÜGBAR - Push gesendet")
        else:
            print("Nicht verfügbar")
    except Exception as e:
        print("Fehler:", e, file=sys.stderr)

if __name__ == "__main__":
    if not TOPIC:
        sys.exit("NTFY_TOPIC nicht gesetzt")
    if INTERVAL:
        while True:
            run_once(); time.sleep(INTERVAL)
    else:
        run_once()
