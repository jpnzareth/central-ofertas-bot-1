import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return "Central Ofertas Bot online!", 200


@app.route("/callback")
def callback():
    code = request.args.get("code")

    if not code:
        return "Erro: código de autorização não recebido.", 400

    client_id = os.getenv("ML_CLIENT_ID")
    client_secret = os.getenv("ML_CLIENT_SECRET")
    redirect_uri = os.getenv("ML_REDIRECT_URI")

    response = requests.post(
        "https://api.mercadolibre.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
        },
        timeout=15,
    )

    if response.status_code != 200:
        return f"Erro ao obter autorização: {response.status_code}", 400

    token_data = response.json()

    # Guarda temporariamente enquanto esta instância estiver ativa.
    app.config["ML_ACCESS_TOKEN"] = token_data.get("access_token")

    return "SUCESSO! Autorização concluída. Agora acesse /teste-api", 200


@app.route("/teste-api")
def teste_api():
    token = app.config.get("ML_ACCESS_TOKEN")

    if not token:
        return (
            "Nenhum token disponível. Faça a autorização novamente "
            "e depois volte para /teste-api."
        ), 401

    response = requests.get(
        "https://api.mercadolibre.com/users/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )

    return jsonify({
        "status_api": response.status_code,
        "funcionou": response.status_code == 200
    }), response.status_code

@app.route("/produto/<item_id>")
def produto(item_id):
    token = app.config.get("ML_ACCESS_TOKEN")

    if not token:
        return jsonify({
            "erro": "Nenhum token disponível. Faça a autorização novamente."
        }), 401

    response = requests.get(
        f"https://api.mercadolibre.com/items/{item_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )

    if response.status_code != 200:
        return jsonify({
            "funcionou": False,
            "status_api": response.status_code
        }), response.status_code

    dados = response.json()

    return jsonify({
        "funcionou": True,
        "id": dados.get("id"),
        "titulo": dados.get("title"),
        "preco": dados.get("price"),
        "preco_original": dados.get("original_price"),
        "disponivel": dados.get("available_quantity"),
        "link": dados.get("permalink")
    }), 200

@app.route("/notifications", methods=["POST"])
def notifications():
    data = request.get_json(silent=True)
    print("Notificação recebida:", data)
    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
