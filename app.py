from flask import Flask, request, jsonify
import requests
import json
import time   # добавь эту строку

app = Flask(__name__)

# === НАСТРОЙКИ ===
VK_TOKEN = "vk1.a.begJge3Zca-Xza97op_HJtuhNuuprZCl0kyCRRq6ZFGMetF3qpfW3DIDmwXDn8tO_fZ3B4LU6ulJZEJtOvQ_pM_Xa5Z03E_w68RKoJ-e3jXPUC4RzSPQq6AGpzspqPlheAAtngkuPN-HvsNnTgS-PI2n_n0bS9V8o1n9deecNbJY13pzg7NfE2pvgun1lj_Er_O5bPHFMDvKpZmAt2ovtw"  # ← обязательно в кавычках!

PEER_ID = 2000000037

VERIFY_STRING = "xsrv3r6zj2d5w"   # ← тоже в кавычках!

@app.route('/', methods=['GET'])
def verify():
    """Верификация URL при сохранении в Online Test Pad"""
    return VERIFY_STRING, 200

@app.route('/', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error"}), 400

        test_name = data.get('testName', 'Неизвестный тест')
        student_id = data.get('id', '—')
        
        # Извлечение результатов
        results = data.get('results', [])
        score = "—"
        percent = "—"
        
        for r in results:
            name = r.get('name', '').lower()
            value = r.get('value', '—')
            
            if any(word in name for word in ['балл', 'правильн', 'количеств', 'набранных']):
                score = value
            if any(word in name for word in ['процент', 'percent', '%']):
                percent = value

        # === ВРЕМЯ ПРОХОЖДЕНИЯ ===
        duration = "—"
        
        # Пытаемся найти время в разных возможных полях
        if 'time' in data or 'duration' in data or 'spent' in data:
            duration = data.get('time') or data.get('duration') or data.get('spent')
        
        # Если время есть в results (иногда бывает)
        for r in results:
            name = r.get('name', '').lower()
            if any(word in name for word in ['время', 'time', 'минут', 'секунд', 'duration']):
                duration = r.get('value', '—')
                break

        # Добавляем ник
        nickname = "—"
        regparams = data.get('regparams', [])
        for p in regparams:
            if p.get('name') == "Ник" and p.get('value'):
                nickname = p.get('value')

        # Текущее время (когда пришёл результат)
        current_time = time.strftime("%d.%m.%Y %H:%M")

        # Красивое сообщение
        message = f"✅ **Новый результат теста** ✅\n\n" \
                  f"#тест\n" \
                  f"Тест: {test_name}\n" \
                  f"*Ник: {nickname}\n" \
                  f"Баллы: {score}\n" \
                  f"Процент: {percent}%\n" \
                  f"Время прохождения: {duration}\n" \
                  f"Отправлено: {current_time}\n"

        # Отправка в ВК
        vk_url = "https://api.vk.com/method/messages.send"
        params = {
            "access_token": VK_TOKEN,
            "peer_id": PEER_ID,
            "message": message,
            "random_id": int(time.time() * 1000),
            "v": "5.199"
        }

        requests.post(vk_url, params=params)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"status": "error"}), 500
