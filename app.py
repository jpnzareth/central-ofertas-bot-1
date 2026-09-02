import os
import requests
from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def home():
    return "Central Ofertas API online!", 200


@app.route("/callback")
def callback():
    code = request.args.get("code")

    if not code:
        return "Erro: código de autorização não recebido.", 400

    client_id = os.getenv("ML_CLIENT_ID")
    client_secret = os.getenv("ML_CLIENT_SECRET")
    redirect_uri = os.getenv("ML_REDIRECT_URI")

    if not client_id or not client_secret or not redirect_uri:
        return "Erro: credenciais da aplicação não configuradas.", 500

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

    if response.status_code == 200:
        return "SUCESSO! Autorização do Mercado Livre concluída.", 200

    return "Erro ao concluir autorização com o Mercado Livre.", 400


@app.route("/notifications", methods=["POST"])
def notifications():
    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
