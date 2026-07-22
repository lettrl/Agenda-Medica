import os
from flask import Flask, jsonify, request

app = Flask(__name__)

AGENDAMENTOS = [

    {
        "paciente": "Maria da Silva",
        "cpf": "123.456.789-00",
        "medico": "Dr. João Pereira",
        "especialidade": "Cardiologia",
        "data": "2026-07-22",
        "horario": "09:00",
        "convenio": "Unimed",
        "status": "Confirmado",
    },
    {
        "paciente": "Carlos Souza",
        "cpf": "987.654.321-00",
        "medico": "Dra. Ana Lima",
        "especialidade": "Dermatologia",
        "data": "2026-07-22",
        "horario": "10:30",
        "convenio": "Particular",
        "status": "Pendente",
    },
    {
        "paciente": "Fernanda Costa",
        "cpf": "456.789.123-00",
        "medico": "Dr. João Pereira",
        "especialidade": "Cardiologia",
        "data": "2026-07-23",
        "horario": "14:00",
        "convenio": "Bradesco Saúde",
        "status": "Confirmado",
    },
    {
        "paciente": "Ricardo Alves",
        "cpf": "321.654.987-00",
        "medico": "Dra. Beatriz Ramos",
        "especialidade": "Ortopedia",
        "data": "2026-07-23",
        "horario": "16:30",
        "convenio": "SulAmérica",
        "status": "Cancelado",
    },
    {
        "paciente": "Juliana Martins",
        "cpf": "159.753.486-00",
        "medico": "Dra. Ana Lima",
        "especialidade": "Dermatologia",
        "data": "2026-07-24",
        "horario": "08:15",
        "convenio": "Unimed",
        "status": "Confirmado",
    },
]

@app.route("/agendamentos", methods=["GET"])
def listar_agendamentos():
    if request.args.get("vazio") == "1":
        return jsonify([])
    if request.args.get("invalido") == "1":
        return jsonify({"error": "Formato inválido"}), 400
    return jsonify(AGENDAMENTOS)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5001)), debug=True)