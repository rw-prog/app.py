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

        # Основная информация
        test_name = data.get('testName', 'Неизвестный тест')
        student_id = data.get('id', '—')
        
        # Извлекаем результаты
        results = data.get('results', [])
        
        score = "—"
        percent = "—"
        for r in results:
            name = r.get('name', '')
            if any(x in name for x in ['баллов', 'правильных ответов', 'Количество']):
                score = r.get('value', '—')
            elif 'Процент' in name:
                percent = r.get('value', '—')

        # Формируем красивое сообщение
        message = f"✅ Новый результат теста\n\n" \
                  f"Тест: {test_name}\n" \
                  f"Участник ID:  {student_id}\n" \
                  f"Баллы: {score}\n" \
                  f"Процент: {percent}%\n"

        # Добавляем ник, если есть
        regparams = data.get('regparams', [])
        for p in regparams:
            if p.get('name') == "Ник" and p.get('value'):
                message += f"Ник: {p.get('value')}\n"

        # Отправка в ВК
        vk_url = "https://api.vk.com/method/messages.send"
        params = {
            "access_token": VK_TOKEN,
            "peer_id": PEER_ID,
            "message": message,
            "random_id": int(time.time() * 1000),
            "v": "5.199"
        }

        response = requests.post(vk_url, params=params)
        print("VK response:", response.json())

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"status": "error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
