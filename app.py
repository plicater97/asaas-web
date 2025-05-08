from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import datetime

app = Flask(__name__)
app.secret_key = 'chave_secreta'

ASAAS_API_KEY = "$aact_hmlg_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OjI0MTYwODIzLTc4MjItNDRiNC05NWVmLTk1MjdiYzZiZWYyYzo6JGFhY2hfNGVkOTIzZDktMDBjMy00MjMzLTlkNmUtNGU1N2EyMjhmMmRh"
ASAAS_BASE_URL = "https://sandbox.asaas.com/api/v3"

@app.route("/", methods=["GET", "POST"])
def index():
    links = []
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        cpf = request.form.get("cpf")
        telefone = "55" + request.form.get("telefone")
        valor = request.form.get("valor")
        parcelas = int(request.form.get("parcelas"))
        intervalo = int(request.form.get("intervalo"))

        if not nome or not email or not cpf or not telefone or not valor:
            flash("Preencha todos os campos.", "warning")
            return render_template("index.html")

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
            flash("Erro ao cadastrar cliente: " + cliente_resp.text, "danger")
            return render_template("index.html")

        cliente_id = cliente_resp.json()['id']
        hoje = datetime.datetime.now()

        for i in range(parcelas):
            vencimento = (hoje + datetime.timedelta(days=i*intervalo)).strftime("%Y-%m-%d")
            cobranca_data = {
                "customer": cliente_id,
                "billingType": "PIX",
                "value": float(valor),
                "dueDate": vencimento,
                "description": f"Parcela {i+1}/{parcelas}"
            }

            resp = requests.post(f"{ASAAS_BASE_URL}/payments", headers=headers, json=cobranca_data)
            if resp.status_code in [200, 201]:
                link = resp.json()['invoiceUrl']
                links.append(link)
            else:
                flash(f"Erro na parcela {i+1}: {resp.text}", "danger")
                return render_template("index.html")

        flash("Cobranças geradas com sucesso!", "success")
        return render_template("index.html", links=links)

    return render_template("index.html")