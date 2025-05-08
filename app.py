from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import datetime
import os

app = Flask(__name__)

ASAAS_API_KEY = "$aact_hmlg_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OjI0MTYwODIzLTc4MjItNDRiNC05NWVmLTk1MjdiYzZiZWYyYzo6JGFhY2hfNGVkOTIzZDktMDBjMy00MjMzLTlkNmUtNGU1N2EyMjhmMmRh"
ASAAS_BASE_URL = "https://sandbox.asaas.com/api/v3"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        cpf = request.form['cpf']
        telefone = "55" + request.form['telefone']
        valor = request.form['valor']

        if not nome or not email or not cpf or not telefone or not valor:
            return render_template('index.html', erro="Preencha todos os campos.")

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "access_token": ASAAS_API_KEY
        }

        cliente_data = {
            "name": nome,
            "email": email,
            "cpfCnpj": cpf,
            "phone": telefone
        }

        cliente_resp = requests.post(f"{ASAAS_BASE_URL}/customers", headers=headers, json=cliente_data)
        if cliente_resp.status_code not in [200, 201]:
            return render_template('index.html', erro="Erro ao cadastrar cliente.")

        cliente_id = cliente_resp.json()['id']

        hoje = datetime.datetime.now()
        cobrancas = []
        for i in range(10):
            vencimento = (hoje + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            cobranca_data = {
                "customer": cliente_id,
                "billingType": "PIX",
                "value": float(valor),
                "dueDate": vencimento,
                "description": f"Parcela {i+1}/10"
            }

            resp = requests.post(f"{ASAAS_BASE_URL}/payments", headers=headers, json=cobranca_data)
            if resp.status_code in [200, 201]:
                link = resp.json()['invoiceUrl']
                cobrancas.append(link)
            else:
                return render_template('index.html', erro=f"Erro ao gerar parcela {i+1}.")

        return render_template('index.html', sucesso="Cobranças criadas com sucesso!", links=cobrancas)

    return render_template('index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)