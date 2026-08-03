import os, requests, time, threading, json, random
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

# 🔥 НОВЫЙ СПИСОК (без родителей, 40+ фраз)
spam_messages = [
    "ты пидор",
    "ты пидорок",
    "пидор",
    "ты не прав, ты пидор",
    "самый настоящий пидор",
    "пидорок",
    "согласись, ты пидор",
    "ты пидор, это факт",
    "ты пидор, иди нахуй",
    "пидор, ты не человек",
    "ты даже не пидор, ты пидорище",
    "ты пидор, удали Telegram",
    "пидор, ты ошибка природы",
    "ты пидор, смирись",
    "пидор, ты проиграл",
    "пидор, ты смешон",
    "пидор, ты никто",
    "пидор, ты бесполезен",
    "пидор, ты просто шум",
    "пидор, ты не нужен",
    "пидор, ты пустота",
    "пидор, ты хуже спама",
    "пидор, ты даже не смешной",
    "пидор, ты просто цифра",
    "пидор, ты ошибка",
    "пидор, ты фейк",
    "пидор, ты баг",
    "пидор, ты глюк",
    "пидор, ты баян",
    "пидор, ты шутка",
    "пидор, ты кринж",
    "пидор, ты позор",
    "пидор, ты страх",
    "пидор, ты боль",
    "пидор, ты скука",
    "пидор, ты пустота",
    "пидор, ты никто",
    "пидор, ты просто точка",
    "пидор, ты конец",
    "пидор, ты свет",
    "пидор, ты тьма",
    "пидор, ты всё",
    "пидор, ты ничего"
]

def spam_loop(chat_id):
    global spam_active
    while spam_active:
        msg = random.choice(spam_messages)
        send_spam(chat_id, msg)
        time.sleep(0.05)  # пулемёт

admin_keyboard = [
    [{"text": "🔁 Включить спам", "callback_data": "spam_on"}],
    [{"text": "⏹ Выключить спам", "callback_data": "spam_off"}],
    [{"text": "🎯 Выбрать цель по ID", "callback_data": "set_target"}],
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
                            if spam_target is None:
                                send(cid, "⚠️ Сначала выбери цель через кнопку «Выбрать цель»", admin_keyboard)
                            elif not spam_active:
                                spam_active = True
                                send(cid, f"🔁 Спам включен для {spam_target}!", admin_keyboard)
                                threading.Thread(target=spam_loop, args=(spam_target,), daemon=True).start()
                            else:
                                send(cid, "⚠️ Спам уже включён", admin_keyboard)

                        elif data == "spam_off":
                            spam_active = False
                            send(cid, "⏹ Спам выключен.", admin_keyboard)

                        elif data == "set_target":
                            send(cid, "📝 Отправь ID цели (например, 123456789)\n\nБот запомнит этот ID и будет спамить на него.", admin_keyboard)

                        elif data == "status":
                            status = "включён" if spam_active else "выключен"
                            target = spam_target if spam_target else "не установлена"
                            send(cid, f"📊 Спам: {status}\n🎯 Цель: {target}", admin_keyboard)

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

                    elif text.startswith("/set_target"):
                        parts = text.split()
                        if len(parts) == 2 and parts[1].isdigit():
                            spam_target = parts[1]
                            send(cid, f"✅ Цель установлена: {spam_target}", admin_keyboard)
                        else:
                            send(cid, "❌ Используй: /set_target ID_ЦЕЛИ", admin_keyboard)

                    elif text == "/spam_on":
                        if spam_target is None:
                            send(cid, "⚠️ Сначала установи цель через /set_target ID", admin_keyboard)
                        elif not spam_active:
                            spam_active = True
                            send(cid, f"🔁 Спам включен для {spam_target}!", admin_keyboard)
                            threading.Thread(target=spam_loop, args=(spam_target,), daemon=True).start()
                        else:
                            send(cid, "⚠️ Спам уже включён", admin_keyboard)

                    elif text == "/spam_off":
                        spam_active = False
                        send(cid, "⏹ Спам выключен.", admin_keyboard)

                    elif text == "/status":
                        status = "включён" if spam_active else "выключен"
                        target = spam_target if spam_target else "не установлена"
                        send(cid, f"📊 Спам: {status}\n🎯 Цель: {target}", admin_keyboard)

                    elif text.isdigit():
                        spam_target = text
                        send(cid, f"✅ Цель установлена: {spam_target}", admin_keyboard)

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
