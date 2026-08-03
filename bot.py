import os, requests, time, threading, json, random
from flask import Flask

app = Flask(__name__)
TOKEN = "8661051008:AAFXwGWhWR8ryn78yGIP1VtcYkUTaXEJAYo"
ADMIN_ID = "7854185047"
offset = 0

spam_messages = [
    "ты пидор", "ты пидорок", "пидор", "ты не прав, ты пидор",
    "самый настоящий пидор", "пидорок", "согласись, ты пидор",
    "ты пидор, это факт", "ты пидор, иди нахуй", "пидор, ты не человек",
    "ты даже не пидор, ты пидорище", "ты пидор, удали Telegram",
    "пидор, ты ошибка природы", "ты пидор, смирись", "пидор, ты проиграл",
    "пидор, ты смешон", "пидор, ты никто", "пидор, ты бесполезен",
    "пидор, ты просто шум", "пидор, ты не нужен", "пидор, ты пустота",
    "пидор, ты хуже спама", "пидор, ты даже не смешной", "пидор, ты просто цифра",
    "пидор, ты ошибка", "пидор, ты фейк", "пидор, ты баг", "пидор, ты глюк",
    "пидор, ты баян", "пидор, ты шутка", "пидор, ты кринж", "пидор, ты позор",
    "пидор, ты страх", "пидор, ты боль", "пидор, ты скука", "пидор, ты пустота",
    "пидор, ты никто", "пидор, ты просто точка", "пидор, ты конец",
    "пидор, ты свет", "пидор, ты тьма", "пидор, ты всё", "пидор, ты ничего"
]

targets = {}  # {id: {"active": False}}

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

def spam_loop():
    while True:
        for target_id, data in targets.items():
            if data.get("active", False):
                msg = random.choice(spam_messages)
                send_spam(target_id, msg)
        time.sleep(0.05)

admin_keyboard = [
    [{"text": "📋 Список целей", "callback_data": "list_targets"}],
    [{"text": "📊 Статус", "callback_data": "status"}],
    [{"text": "📝 Список фраз", "callback_data": "list_phrases"}],
    [{"text": "❌ Остановить всех", "callback_data": "stop_all"}]
]

def bot_loop():
    global offset
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
                        if data == "list_targets":
                            if targets:
                                text = "📋 Цели:\n"
                                for tid, info in targets.items():
                                    status = "🔴 выкл" if not info.get("active", False) else "🟢 вкл"
                                    text += f"- {tid} ({status})\n"
                                send(cid, text, admin_keyboard)
                            else:
                                send(cid, "❌ Нет целей", admin_keyboard)

                        elif data == "status":
                            total = len(targets)
                            active = sum(1 for t in targets.values() if t.get("active", False))
                            send(cid, f"📊 Всего целей: {total}\n🟢 Активных: {active}", admin_keyboard)

                        elif data == "list_phrases":
                            phrases = "\n".join(spam_messages)
                            send(cid, f"📝 Фразы ({len(spam_messages)}):\n{phrases}", admin_keyboard)

                        elif data == "stop_all":
                            for tid in targets:
                                targets[tid]["active"] = False
                            send(cid, "⏹ Все цели остановлены", admin_keyboard)

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
                        send(cid, "✅ Бот запущен. Управляй через кнопки и команды:", admin_keyboard)

                    elif text.startswith("/add_target"):
                        parts = text.split()
                        if len(parts) == 2 and parts[1].isdigit():
                            tid = parts[1]
                            if tid not in targets:
                                targets[tid] = {"active": False}
                                send(cid, f"✅ Цель {tid} добавлена. Используй /target_on {tid} для активации", admin_keyboard)
                            else:
                                send(cid, "⚠️ Цель уже есть", admin_keyboard)
                        else:
                            send(cid, "❌ Используй: /add_target ID", admin_keyboard)

                    elif text.startswith("/remove_target"):
                        parts = text.split()
                        if len(parts) == 2 and parts[1].isdigit():
                            tid = parts[1]
                            if tid in targets:
                                del targets[tid]
                                send(cid, f"✅ Цель {tid} удалена", admin_keyboard)
                            else:
                                send(cid, "❌ Цель не найдена", admin_keyboard)
                        else:
                            send(cid, "❌ Используй: /remove_target ID", admin_keyboard)

                    elif text.startswith("/target_on"):
                        parts = text.split()
                        if len(parts) == 2 and parts[1].isdigit():
                            tid = parts[1]
                            if tid in targets:
                                targets[tid]["active"] = True
                                send(cid, f"🟢 Спам для {tid} включен", admin_keyboard)
                            else:
                                send(cid, "❌ Цель не найдена", admin_keyboard)
                        else:
                            send(cid, "❌ Используй: /target_on ID", admin_keyboard)

                    elif text.startswith("/target_off"):
                        parts = text.split()
                        if len(parts) == 2 and parts[1].isdigit():
                            tid = parts[1]
                            if tid in targets:
                                targets[tid]["active"] = False
                                send(cid, f"🔴 Спам для {tid} выключен", admin_keyboard)
                            else:
                                send(cid, "❌ Цель не найдена", admin_keyboard)
                        else:
                            send(cid, "❌ Используй: /target_off ID", admin_keyboard)

                    elif text.startswith("/add_phrase"):
                        phrase = text[12:].strip()
                        if phrase:
                            spam_messages.append(phrase)
                            send(cid, f"✅ Фраза добавлена: {phrase}", admin_keyboard)
                        else:
                            send(cid, "❌ Напиши фразу после /add_phrase", admin_keyboard)

                    elif text.startswith("/del_phrase"):
                        phrase = text[12:].strip()
                        if phrase in spam_messages:
                            spam_messages.remove(phrase)
                            send(cid, f"✅ Фраза удалена: {phrase}", admin_keyboard)
                        else:
                            send(cid, "❌ Фраза не найдена", admin_keyboard)

                    elif text == "/list_phrases":
                        phrases = "\n".join(spam_messages)
                        send(cid, f"📝 Фразы ({len(spam_messages)}):\n{phrases}", admin_keyboard)

                    elif text == "/list_targets":
                        if targets:
                            text = "📋 Цели:\n"
                            for tid, info in targets.items():
                                status = "🔴 выкл" if not info.get("active", False) else "🟢 вкл"
                                text += f"- {tid} ({status})\n"
                            send(cid, text, admin_keyboard)
                        else:
                            send(cid, "❌ Нет целей", admin_keyboard)

                    elif text == "/stop_all":
                        for tid in targets:
                            targets[tid]["active"] = False
                        send(cid, "⏹ Все цели остановлены", admin_keyboard)

                    elif text == "/status":
                        total = len(targets)
                        active = sum(1 for t in targets.values() if t.get("active", False))
                        send(cid, f"📊 Всего целей: {total}\n🟢 Активных: {active}", admin_keyboard)

                    else:
                        send(cid, "❌ Неизвестная команда. Доступно:\n/add_target ID\n/remove_target ID\n/target_on ID\n/target_off ID\n/add_phrase текст\n/del_phrase текст\n/list_phrases\n/list_targets\n/stop_all\n/status", admin_keyboard)

        except Exception as e:
            time.sleep(3)

@app.route('/')
def home():
    return "Бот работает"

if __name__ == "__main__":
    threading.Thread(target=spam_loop, daemon=True).start()
    threading.Thread(target=bot_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
