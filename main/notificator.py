import time
import os
from twilio.rest import Client

# Twilio config
account_sid = 'ACc9c9b0ed84b8cc25a69a3308e2ff8796'
auth_token = '6318040a3abbee9f887eaa48192478d7'
client = Client(account_sid, auth_token)

twilio_whatsapp_number = 'whatsapp:+14155238886'
your_whatsapp_number = 'whatsapp:+40748111788'

# Trimite mesaj WhatsApp dacă jucătorul a fost inactiv
def send_reminder():
    message = client.messages.create(
        body="👾 Hei! Nu ai mai jucat Doodle Jump de 5 minute! Revino și urcă mai sus! 🚀🕹️",
        from_=twilio_whatsapp_number,
        to=your_whatsapp_number
    )
    print("Mesaj trimis:", message.sid)

# Verifică cât timp a trecut de la ultima sesiune
def check_last_played():
    if not os.path.exists("last_played.txt"):
        print("Fișierul last_played.txt nu există încă.")
        return

    with open("last_played.txt", "r") as f:
        try:
            last_time = float(f.read())
        except ValueError:
            print("Eroare la citirea timpului.")
            return

    now = time.time()
    time_passed = now - last_time
    if time_passed >= 300:  # 5 minute = 300 secunde
        print("Au trecut mai mult de 5 minute. Trimitem notificare.")
        send_reminder()
    else:
        print(f"Mai sunt {int((300 - time_passed) // 60)} minute până la notificare.")

# Rulează verificarea periodic
while True:
    check_last_played()
    time.sleep(60)  # verifică o dată pe minut
