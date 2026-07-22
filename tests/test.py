import os
import tempfile
import pytest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DB_FILE = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
DB_FILE.close()
os.environ.setdefault("DB_PATH", str(DB_FILE.name))

from app import app, init_db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            init_db()
            yield client

def test_login_valido(client):
    response = client.post("/login", data={"usuario": "admin", "senha": "123456"})
    assert response.status_code == 302
    assert "/agenda" in response.headers["Location"]

def test_login_invalido(client):
    response = client.post("/login", data={"usuario": "admin", "senha": "senhaerrada"})
    assert response.status_code == 200
    assert "Usuário ou senha inválidos" in response.get_data(as_text=True)

def test_api_retorna_sem_agendamentos(client, monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass
        def json(self):
            return []

    import importlib
    app_module = importlib.import_module("app.app")
    monkeypatch.setattr(app_module.requests, "get", lambda *args, **kwargs: FakeResponse())

    client.post("/login", data={"usuario": "admin", "senha": "123456"})
    response = client.get("/api/agendamentos")
    data = response.get_json()

    assert data["sucesso"] is True
    assert data["dados"] == []