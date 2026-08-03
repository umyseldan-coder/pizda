import os, requests, time, threading, json
from flask import Flask

app = Flask(__name__)
TOKEN = "8661051008:AAFXwGWhWR8ryn78yGIP1VtcYkUTaXEJAYo"
ADMIN_ID = "7854185047"
offset = 0
spam_active = False
spam_target = None

def send(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = json.dumps({"inline_keyboard": keyboard})
    try:
        requests.post(url, data=data, timeout=10)
    except:
        pass

def send_spam(chat_id, text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": chat_id, "text": text},
            timeout=10
        )
    except:
        pass

def spam_loop(chat_id):
    global spam_active
    messages = [
        "ты пидорок",
        "ты пидор",
        "пидор",
        "ты не прав, ты пидор",
        "самый настоящий пидор",
        "пидорок",
        "согласись, ты пидор",
        "пидор"
    ]
    while spam_active:
        for msg in messages:
            if not spam_active:
                break
            send_spam(chat_id, msg)
            time.sleep(0.5)

admin_keyboard = [
    [{"text": "🔁 Включить спам", "callback_data": "spam_on"}],
    [{"text": "⏹ Выключить спам", "callback_data": "spam_off"}],
    [{"text": "📊 Статус", "callback_data": "status"}]
]

def bot_loop():
    global offset, spam_active, spam_target
    while True:
        try:
            r = requests.get(
                f"https://api.telegram.org/bot{TOKEN}/getUpdates",
                params={"offset": offset, "timeout": 10},
                timeout=15
            )
            for u in r.json().get("result", []):
                offset = u["update_id"] + 1

                if "callback_query" in u:
                    q = u["callback_query"]
                    cid = str(q["message"]["chat"]["id"])
                    data = q["data"]

                    if cid != ADMIN_ID:
                        send(cid, "⛔ Доступ запрещён", None)
                    else:
                        if data == "spam_on":
                            if not spam_active:
                                spam_active = True
                                spam_target = cid
                                send(cid, "🔁 Спам включен!", admin_keyboard)
                                threading.Thread(target=spam_loop, args=(cid,), daemon=True).start()
                            else:
                                send(cid, "⚠️ Спам уже включён", admin_keyboard)

                        elif data == "spam_off":
                            spam_active = False
                            send(cid, "⏹ Спам выключен.", admin_keyboard)

                        elif data == "status":
                            status = "включён" if spam_active else "выключен"
                            send(cid, f"📊 Спам: {status}", admin_keyboard)

                    try:
                        requests.get(
                            f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
                            params={"callback_query_id": q["id"]}
                        )
                    except:
                        pass

                else:
                    text = u.get("message", {}).get("text", "")
                    cid = str(u.get("message", {}).get("chat", {}).get("id"))
                    username = u.get("message", {}).get("chat", {}).get("first_name", "друг")

                    if not text:
                        continue

                    if cid != ADMIN_ID:
                        if text == "/start":
                            send(cid, f"Привет, {username}! Бот перезагружается. Ожидайте...")
                        else:
                            send(cid, "Бот временно недоступен. Напишите /start")
                        continue

                    if text == "/start":
                        send(cid, "✅ Бот запущен. Управляй через кнопки:", admin_keyboard)
                    elif text == "/spam_on":
                        if not spam_active:
                            spam_active = True
                            spam_target = cid
                            send(cid, "🔁 Спам включен!", admin_keyboard)
                            threading.Thread(target=spam_loop, args=(cid,), daemon=True).start()
                        else:
                            send(cid, "⚠️ Спам уже включён", admin_keyboard)
                    elif text == "/spam_off":
                        spam_active = False
                        send(cid, "⏹ Спам выключен.", admin_keyboard)
                    elif text == "/status":
                        status = "включён" if spam_active else "выключен"
                        send(cid, f"📊 Спам: {status}", admin_keyboard)
                    else:
                        send(cid, "❌ Неизвестная команда. Используй кнопки:", admin_keyboard)

        except Exception as e:
            time.sleep(3)

@app.route('/')
def home():
    return "Бот работает"

if __name__ == "__main__":
    threading.Thread(target=bot_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
