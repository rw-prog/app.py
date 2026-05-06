from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# === НАСТРОЙКИ ===
VK_TOKEN = vk1.a.begJge3Zca-Xza97op_HJtuhNuuprZCl0kyCRRq6ZFGMetF3qpfW3DIDmwXDn8tO_fZ3B4LU6ulJZEJtOvQ_pM_Xa5Z03E_w68RKoJ-e3jXPUC4RzSPQq6AGpzspqPlheAAtngkuPN-HvsNnTgS-PI2n_n0bS9V8o1n9deecNbJY13pzg7NfE2pvgun1lj_Er_O5bPHFMDvKpZmAt2ovtw          # ← Замени
PEER_ID = 2000000520                           # ← peer_id твоей беседы
VERIFY_STRING = xsrv3r6zj2d5w                # из скриншота

@app.route('/', methods=['GET'])
def verify():
    """Верификация URL при сохранении в Online Test Pad"""
    return VERIFY_STRING, 200

@app.route('/', methods=['POST'])
def webhook():
    """Приём результатов теста"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON"}), 400

        # Основная информация
        test_name = data.get('testName', 'Неизвестный тест')
        student_id = data.get('id', '—')
        
        # Результаты
        results = data.get('results', [])
        score = next((r['value'] for r in results if 'правильных ответов' in r.get('name', '')), '—')
        percent = next((r['value'] for r in results if 'Процент' in r.get('name', '')), '—')

        # Формируем красивое сообщение
        message = f"✅ **Новый результат теста**\n\n" \
                  f"**Тест:** {test_name}\n" \
                  f"**Участник ID:** {student_id}\n" \
                  f"**Правильных ответов:** {score}\n" \
                  f"**Процент:** {percent}%\n\n" \
                  f"Полные данные: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}..."  # можно убрать

        # Отправка в ВК
        vk_url = "https://api.vk.com/method/messages.send"
        params = {
            "access_token": VK_TOKEN,
            "peer_id": PEER_ID,
            "message": message,
            "random_id": int(__import__('time').time() * 1000),
            "v": "5.199"
        }

        response = requests.post(vk_url, params=params)
        vk_result = response.json()

        print("VK response:", vk_result)  # для отладки
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
