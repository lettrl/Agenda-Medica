import os
import logging
import sqlite3
from functools import wraps

import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

try:
    from .init_db import init_db, get_connection
except ImportError:
    from init_db import init_db, get_connection

load_dotenv()

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), "front"))
app.secret_key = os.getenv("SECRET_KEY", "chave-de-desenvolvimento-troque-em-producao")

API_URL = os.getenv("API_URL", "http://localhost:5001/agendamentos")
API_TIMEOUT = float(os.getenv("API_TIMEOUT", "5"))


CAMPOS_OBRIGATORIOS = [
    "paciente", "cpf", "medico", "especialidade",
    "data", "horario", "convenio", "status",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("agenda-medica")

def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapper

def validar_agendamento(unico_agendamento):
    faltando = [c for c in CAMPOS_OBRIGATORIOS if not unico_agendamento.get(c)]
    if faltando:
        logger.warning(f"Agendamento descartado, campos ausentes {faltando}: {unico_agendamento}")
        return False
    return True

def buscar_agendamentos():
    try:
        response = requests.get(API_URL, timeout=API_TIMEOUT)
        response.raise_for_status()

    except requests.exceptions.ConnectionError:
        logger.error("Erro de conexão com a API de agendamentos:")
        return [], "Não foi possível conectar à API de agendamentos. Verifique se o serviço está em execução."

    except requests.exceptions.Timeout:
        logger.error("Limite de tempo excedido ao consultar a API de agendamentos.")
        return [], "O serviço de agendamentos demorou demais para responder. Tente novamente."
    
    except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP ao acessar a API: {e}")
            return [], "Erro ao acessar a API de agendamentos."
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro desconhecido ao acessar a API: {e}")
        return [], "Ocorreu um erro ao buscar os agendamentos. Tente novamente."

    #agendamentos = response.json()
    #if not isinstance(agendamentos, list):
        #logger.error(f"Resposta da API não é uma lista: {agendamentos}")
       # return []

    try:
        dados = response.json()
    except ValueError:
        logger.error(f"Resposta da API não é um JSON válido")
        return [], "A resposta da API de agendamentos não é válida."

    if not isinstance(dados, list):
        logger.error(f"Resposta da API não é uma lista: {dados}")
        return [], "A resposta da API de agendamentos não é válida."

    if not dados:
        return [], None


    agendamentos_validos = [unico_agendamento for unico_agendamento in dados if validar_agendamento(unico_agendamento)]

    if not agendamentos_validos:
        return [], "Nenhum agendamento válido foi encontrado."
    return agendamentos_validos, None


@app.route("/", methods=["GET"])
def index():
    if "usuario" in session:
        return redirect(url_for("agenda"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    identificador = (request.form.get("usuario") or "").strip()
    senha = request.form.get("senha") or ""

    if not identificador or not senha:
        flash("Por favor informe usuário/e-mail e senha.", "error")
        return render_template("login.html")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM usuarios WHERE username = ? OR email = ?",
            (identificador, identificador),
        )
        usuario = cur.fetchone()
        conn.close()
    except sqlite3.Error as e:
        logger.error(f"Erro de conexão/consulta ao banco de dados: {e}")
        flash("Erro ao acessar o sistema no momento. Tente novamente mais tarde.", "error")
        return render_template("login.html")

    if usuario is None or not check_password_hash(usuario["senha_hash"], senha):
        logger.info(f"Tentativa de login inválida para '{identificador}'.")
        flash("Usuário ou senha inválidos.", "error")
        return render_template("login.html")

    session["usuario"] = usuario["username"]
    logger.info(f"Login bem-sucedido: {usuario['username']}")
    return redirect(url_for("agenda"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/agenda")
@login_required
def agenda():
    return render_template("agenda.html", usuario=session["usuario"])


@app.route("/api/agendamentos")
@login_required
def api_agendamentos():
    agendamentos, erro = buscar_agendamentos()
    if erro:
        return jsonify({"sucesso": False, "mensagem": erro, "dados": []}), 200
    if not agendamentos:
        return jsonify({"sucesso": True, "mensagem": "Nenhum agendamento encontrado.", "dados": []}), 200
    return jsonify({"sucesso": True, "mensagem": None, "dados": agendamentos}), 200


@app.route("/api/agendamentos/buscar")
@login_required
def api_agendamentos_buscar():
    termo = (request.args.get("q") or "").strip().lower()

    agendamentos, erro = buscar_agendamentos()
    if erro:
        return jsonify({"sucesso": False, "mensagem": erro, "dados": []}), 200

    if not termo:
        return jsonify({"sucesso": True, "mensagem": None, "dados": agendamentos}), 200

    resultado = [
        a for a in agendamentos
        if termo in str(a.get("paciente", "")).lower()
        or termo in str(a.get("cpf", "")).lower()
        or termo in str(a.get("medico", "")).lower()
    ]

    if not resultado:
        return jsonify({"sucesso": True, "mensagem": "Nenhum registro encontrado para essa busca.", "dados": []}), 200

    return jsonify({"sucesso": True, "mensagem": None, "dados": resultado}), 200

with app.app_context():
    try:
        init_db()
    except sqlite3.Error as e:
        logger.error(f"Erro ao inicializar o banco de dados: {e}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)